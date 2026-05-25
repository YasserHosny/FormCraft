-- Migration 032: Customer Profiles & Auto-Populate
-- Feature: 030-customer-profiles
-- Date: 2026-05-25

-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name_ar TEXT NOT NULL,
    name_en TEXT,
    identifier_type TEXT NOT NULL CHECK (identifier_type IN ('national_id', 'iqama', 'commercial_register', 'passport', 'other')),
    identifier TEXT NOT NULL,
    contact_phone TEXT,
    contact_email TEXT,
    address TEXT,
    custom_fields JSONB DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT true,
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('simple', coalesce(name_ar, '') || ' ' || coalesce(name_en, '') || ' ' || coalesce(identifier, '') || ' ' || coalesce(contact_phone, '') || ' ' || coalesce(contact_email, ''))
    ) STORED,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (org_id, identifier_type, identifier)
);

-- Indexes for customers
CREATE INDEX IF NOT EXISTS idx_customers_search ON customers USING GIN (search_vector);
CREATE INDEX IF NOT EXISTS idx_customers_org_active ON customers(org_id, is_active);
CREATE INDEX IF NOT EXISTS idx_customers_org_updated ON customers(org_id, updated_at DESC);

-- Enable RLS
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

-- RLS policies
CREATE POLICY customers_select ON customers
    FOR SELECT
    USING (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND org_id = customers.org_id));

CREATE POLICY customers_insert ON customers
    FOR INSERT
    WITH CHECK (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND org_id = customers.org_id AND role IN ('operator', 'admin', 'org_admin')));

CREATE POLICY customers_update ON customers
    FOR UPDATE
    USING (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND org_id = customers.org_id AND role IN ('operator', 'admin', 'org_admin')));

CREATE POLICY customers_delete ON customers
    FOR DELETE
    USING (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND org_id = customers.org_id AND role IN ('admin', 'org_admin')));

-- Auto-update updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_customers_updated_at ON customers;
CREATE TRIGGER update_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create customer_field_mappings table
CREATE TABLE IF NOT EXISTS customer_field_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    element_key TEXT NOT NULL,
    customer_field TEXT NOT NULL CHECK (customer_field IN ('name_ar', 'name_en', 'identifier', 'identifier_type', 'contact_phone', 'contact_email', 'address')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (template_id, element_key)
);

CREATE INDEX IF NOT EXISTS idx_customer_field_mappings_template ON customer_field_mappings(template_id);

ALTER TABLE customer_field_mappings ENABLE ROW LEVEL SECURITY;

CREATE POLICY customer_field_mappings_select ON customer_field_mappings
    FOR SELECT
    USING (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND org_id = (SELECT org_id FROM templates WHERE id = customer_field_mappings.template_id)));

CREATE POLICY customer_field_mappings_insert ON customer_field_mappings
    FOR INSERT
    WITH CHECK (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role IN ('admin', 'designer', 'org_admin')));

CREATE POLICY customer_field_mappings_update ON customer_field_mappings
    FOR UPDATE
    USING (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role IN ('admin', 'designer', 'org_admin')));

CREATE POLICY customer_field_mappings_delete ON customer_field_mappings
    FOR DELETE
    USING (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role IN ('admin', 'designer', 'org_admin')));

-- Add customer_id to form_submissions
ALTER TABLE form_submissions
ADD COLUMN IF NOT EXISTS customer_id UUID REFERENCES customers(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_form_submissions_customer ON form_submissions(customer_id);
