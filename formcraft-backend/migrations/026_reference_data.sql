-- Migration 026: Reference Data Manager
-- Creates reference_lists and reference_entries tables

-- Reference Lists table
CREATE TABLE reference_lists (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name_ar TEXT NOT NULL,
  name_en TEXT NOT NULL,
  description TEXT,
  schema JSONB NOT NULL DEFAULT '[]'::JSONB,
  is_archived BOOLEAN NOT NULL DEFAULT false,
  org_id UUID NOT NULL REFERENCES organizations(id),
  created_by UUID NOT NULL REFERENCES auth.users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_reference_lists_org ON reference_lists(org_id);
CREATE INDEX idx_reference_lists_org_active ON reference_lists(org_id)
  WHERE is_archived = false;

ALTER TABLE reference_lists ENABLE ROW LEVEL SECURITY;

CREATE POLICY reference_lists_org_isolation ON reference_lists
  USING (org_id = current_setting('app.current_org_id', true)::UUID);

-- Reference Entries table
CREATE TABLE reference_entries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  list_id UUID NOT NULL REFERENCES reference_lists(id) ON DELETE CASCADE,
  values JSONB NOT NULL DEFAULT '{}'::JSONB,
  is_active BOOLEAN NOT NULL DEFAULT true,
  org_id UUID NOT NULL REFERENCES organizations(id),
  created_by UUID NOT NULL REFERENCES auth.users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_reference_entries_list ON reference_entries(list_id);
CREATE INDEX idx_reference_entries_list_active ON reference_entries(list_id)
  WHERE is_active = true;
CREATE INDEX idx_reference_entries_org ON reference_entries(org_id);

ALTER TABLE reference_entries ENABLE ROW LEVEL SECURITY;

CREATE POLICY reference_entries_org_isolation ON reference_entries
  USING (org_id = current_setting('app.current_org_id', true)::UUID);

COMMENT ON TABLE reference_lists IS
  'Centrally managed reference data lists with typed column schemas.';
COMMENT ON COLUMN reference_lists.schema IS
  'JSONB array of column definitions: [{key, label_ar, label_en, type, required, is_unique_key, options}]';
COMMENT ON TABLE reference_entries IS
  'Individual entries within a reference list. Values keyed by column key from parent list schema.';
COMMENT ON COLUMN reference_entries.is_active IS
  'Inactive entries preserved for historical submissions but excluded from form dropdowns.';
