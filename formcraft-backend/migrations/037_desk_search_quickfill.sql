-- Migration 037: Desk Search & Quick Fill
-- Feature: 037-desk-search-quickfill
-- Date: 2026-05-26

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

-- QuickFill mappings table (per-organization configurable field-to-customer-attribute mapping)
CREATE TABLE IF NOT EXISTS quickfill_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    field_key TEXT NOT NULL,
    customer_attribute TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (org_id, field_key)
);

CREATE INDEX IF NOT EXISTS idx_quickfill_mappings_org ON quickfill_mappings(org_id);

ALTER TABLE quickfill_mappings ENABLE ROW LEVEL SECURITY;

CREATE POLICY quickfill_mappings_select ON quickfill_mappings
    FOR SELECT
    USING (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND org_id = quickfill_mappings.org_id));

CREATE POLICY quickfill_mappings_insert ON quickfill_mappings
    FOR INSERT
    WITH CHECK (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND org_id = quickfill_mappings.org_id AND role IN ('admin', 'org_admin')));

CREATE POLICY quickfill_mappings_update ON quickfill_mappings
    FOR UPDATE
    USING (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND org_id = quickfill_mappings.org_id AND role IN ('admin', 'org_admin')));

CREATE POLICY quickfill_mappings_delete ON quickfill_mappings
    FOR DELETE
    USING (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND org_id = quickfill_mappings.org_id AND role IN ('admin', 'org_admin')));

-- Seed default mappings for existing organizations
INSERT INTO quickfill_mappings (org_id, field_key, customer_attribute)
SELECT DISTINCT org_id, 'full_name', 'name'
FROM profiles
WHERE org_id IS NOT NULL
ON CONFLICT (org_id, field_key) DO NOTHING;

INSERT INTO quickfill_mappings (org_id, field_key, customer_attribute)
SELECT DISTINCT org_id, 'name', 'name'
FROM profiles
WHERE org_id IS NOT NULL
ON CONFLICT (org_id, field_key) DO NOTHING;

INSERT INTO quickfill_mappings (org_id, field_key, customer_attribute)
SELECT DISTINCT org_id, 'national_id', 'identifier'
FROM profiles
WHERE org_id IS NOT NULL
ON CONFLICT (org_id, field_key) DO NOTHING;

INSERT INTO quickfill_mappings (org_id, field_key, customer_attribute)
SELECT DISTINCT org_id, 'id_number', 'identifier'
FROM profiles
WHERE org_id IS NOT NULL
ON CONFLICT (org_id, field_key) DO NOTHING;

INSERT INTO quickfill_mappings (org_id, field_key, customer_attribute)
SELECT DISTINCT org_id, 'phone', 'contact_phone'
FROM profiles
WHERE org_id IS NOT NULL
ON CONFLICT (org_id, field_key) DO NOTHING;

INSERT INTO quickfill_mappings (org_id, field_key, customer_attribute)
SELECT DISTINCT org_id, 'mobile', 'contact_phone'
FROM profiles
WHERE org_id IS NOT NULL
ON CONFLICT (org_id, field_key) DO NOTHING;

INSERT INTO quickfill_mappings (org_id, field_key, customer_attribute)
SELECT DISTINCT org_id, 'address', 'address'
FROM profiles
WHERE org_id IS NOT NULL
ON CONFLICT (org_id, field_key) DO NOTHING;

-- Add customer_id to form_submissions for Quick Fill linkage
ALTER TABLE form_submissions
    ADD COLUMN IF NOT EXISTS customer_id UUID REFERENCES customers(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_form_submissions_customer ON form_submissions(customer_id);

-- Unified search materialized view
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_global_search AS
SELECT
    id,
    'template' AS entity_type,
    org_id,
    NULL::UUID AS branch_id,
    NULL::UUID AS department_id,
    name AS title,
    COALESCE(description, '') AS subtitle,
    to_tsvector('simple', COALESCE(name, '') || ' ' || COALESCE(description, '') || ' ' || COALESCE(array_to_string(tags, ' '), '')) AS search_vector,
    COALESCE(name, '') AS name_trigram,
    jsonb_build_object(
        'status', status,
        'version', version,
        'category', category,
        'language', language
    ) AS metadata,
    updated_at
FROM templates
WHERE status = 'published'

UNION ALL

SELECT
    id,
    'submission' AS entity_type,
    org_id,
    branch_id,
    department_id,
    reference_number AS title,
    COALESCE((SELECT name_ar FROM customers WHERE id = form_submissions.customer_id), '') AS subtitle,
    to_tsvector('simple', COALESCE(reference_number, '')) AS search_vector,
    COALESCE(reference_number, '') AS name_trigram,
    jsonb_build_object(
        'template_id', template_id,
        'template_name', (SELECT name FROM templates WHERE id = form_submissions.template_id),
        'created_at', created_at,
        'status', status
    ) AS metadata,
    updated_at
FROM form_submissions

UNION ALL

SELECT
    id,
    'customer' AS entity_type,
    org_id,
    NULL::UUID AS branch_id,
    NULL::UUID AS department_id,
    COALESCE(name_ar, name_en, '') AS title,
    COALESCE(identifier, '') AS subtitle,
    to_tsvector('simple', COALESCE(name_ar, '') || ' ' || COALESCE(name_en, '') || ' ' || COALESCE(identifier, '') || ' ' || COALESCE(contact_phone, '')) AS search_vector,
    COALESCE(name_ar, name_en, '') AS name_trigram,
    jsonb_build_object(
        'identifier', identifier,
        'contact_phone', contact_phone,
        'recent_submissions_count', (
            SELECT COUNT(*) FROM form_submissions WHERE customer_id = customers.id
        )
    ) AS metadata,
    updated_at
FROM customers
WHERE is_active = true;

-- Indexes on materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_global_search_id_type ON mv_global_search(id, entity_type);
CREATE INDEX IF NOT EXISTS idx_mv_global_search_vector ON mv_global_search USING GIN (search_vector);
CREATE INDEX IF NOT EXISTS idx_mv_global_search_trigram ON mv_global_search USING GIN (name_trigram gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_mv_global_search_org_type ON mv_global_search(org_id, entity_type);
CREATE INDEX IF NOT EXISTS idx_mv_global_search_updated ON mv_global_search(updated_at);

-- Function to refresh materialized view concurrently
CREATE OR REPLACE FUNCTION refresh_global_search()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_global_search;
END;
$$;

-- Trigger function to refresh on significant changes
CREATE OR REPLACE FUNCTION trigger_refresh_global_search()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    PERFORM pg_notify('refresh_global_search', '');
    RETURN NULL;
END;
$$;

-- Triggers to notify refresh on changes (external worker or cron handles the actual refresh)
DROP TRIGGER IF EXISTS refresh_global_search_templates ON templates;
CREATE TRIGGER refresh_global_search_templates
    AFTER INSERT OR UPDATE OR DELETE ON templates
    FOR EACH STATEMENT
    EXECUTE FUNCTION trigger_refresh_global_search();

DROP TRIGGER IF EXISTS refresh_global_search_submissions ON form_submissions;
CREATE TRIGGER refresh_global_search_submissions
    AFTER INSERT OR UPDATE OR DELETE ON form_submissions
    FOR EACH STATEMENT
    EXECUTE FUNCTION trigger_refresh_global_search();

DROP TRIGGER IF EXISTS refresh_global_search_customers ON customers;
CREATE TRIGGER refresh_global_search_customers
    AFTER INSERT OR UPDATE OR DELETE ON customers
    FOR EACH STATEMENT
    EXECUTE FUNCTION trigger_refresh_global_search();
