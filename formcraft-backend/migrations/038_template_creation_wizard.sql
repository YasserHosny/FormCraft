-- Migration 038: Template Creation Wizard
-- Feature: 038-template-creation-wizard
-- Date: 2026-05-26

-- Extend templates table with currency and tags
ALTER TABLE templates
    ADD COLUMN IF NOT EXISTS currency VARCHAR(10) NOT NULL DEFAULT 'EGP',
    ADD COLUMN IF NOT EXISTS tags TEXT[] NOT NULL DEFAULT '{}';

-- Extend pages table with orientation and margins
ALTER TABLE pages
    ADD COLUMN IF NOT EXISTS orientation VARCHAR(20) NOT NULL DEFAULT 'portrait',
    ADD COLUMN IF NOT EXISTS margin_top_mm DECIMAL(6,2) NOT NULL DEFAULT 10.00,
    ADD COLUMN IF NOT EXISTS margin_bottom_mm DECIMAL(6,2) NOT NULL DEFAULT 10.00,
    ADD COLUMN IF NOT EXISTS margin_left_mm DECIMAL(6,2) NOT NULL DEFAULT 10.00,
    ADD COLUMN IF NOT EXISTS margin_right_mm DECIMAL(6,2) NOT NULL DEFAULT 10.00;

-- Create org_categories table for configurable template categories
CREATE TABLE IF NOT EXISTS org_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    is_system_default BOOLEAN NOT NULL DEFAULT false,
    sort_order INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_org_categories_org ON org_categories(org_id);
CREATE INDEX IF NOT EXISTS idx_org_categories_sort ON org_categories(org_id, sort_order);

ALTER TABLE org_categories ENABLE ROW LEVEL SECURITY;

CREATE POLICY org_categories_select ON org_categories
    FOR SELECT
    USING (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND org_id = org_categories.org_id));

CREATE POLICY org_categories_insert ON org_categories
    FOR INSERT
    WITH CHECK (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND org_id = org_categories.org_id AND role IN ('admin', 'org_admin')));

CREATE POLICY org_categories_update ON org_categories
    FOR UPDATE
    USING (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND org_id = org_categories.org_id AND role IN ('admin', 'org_admin')));

CREATE POLICY org_categories_delete ON org_categories
    FOR DELETE
    USING (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND org_id = org_categories.org_id AND role IN ('admin', 'org_admin')));

-- Seed system default categories for all existing organizations
INSERT INTO org_categories (org_id, name, is_system_default, sort_order)
SELECT DISTINCT org_id, 'KYC', true, 10
FROM profiles
WHERE org_id IS NOT NULL
ON CONFLICT DO NOTHING;

INSERT INTO org_categories (org_id, name, is_system_default, sort_order)
SELECT DISTINCT org_id, 'Application', true, 20
FROM profiles
WHERE org_id IS NOT NULL
ON CONFLICT DO NOTHING;

INSERT INTO org_categories (org_id, name, is_system_default, sort_order)
SELECT DISTINCT org_id, 'Contract', true, 30
FROM profiles
WHERE org_id IS NOT NULL
ON CONFLICT DO NOTHING;

INSERT INTO org_categories (org_id, name, is_system_default, sort_order)
SELECT DISTINCT org_id, 'Survey', true, 40
FROM profiles
WHERE org_id IS NOT NULL
ON CONFLICT DO NOTHING;

INSERT INTO org_categories (org_id, name, is_system_default, sort_order)
SELECT DISTINCT org_id, 'General', true, 50
FROM profiles
WHERE org_id IS NOT NULL
ON CONFLICT DO NOTHING;
