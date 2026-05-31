-- Migration 041: Custom Locale Validators
-- Feature: 048-custom-locale-validators
-- Org-scoped regex validators with bilingual error messages
-- See: formcraft-specs/specs/048-custom-locale-validators/spec.md

-- =============================================================
-- 1. custom_validators table
-- =============================================================
CREATE TABLE IF NOT EXISTS custom_validators (
    id               UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id           UUID         NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name             VARCHAR(255) NOT NULL,
    description      TEXT,
    regex_pattern    VARCHAR(500) NOT NULL,
    error_message_ar TEXT         NOT NULL,
    error_message_en TEXT         NOT NULL,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    created_by       UUID         NOT NULL REFERENCES profiles(id),
    updated_by       UUID         NOT NULL REFERENCES profiles(id),
    deleted_at       TIMESTAMPTZ,

    -- Per spec FR-1: unique name per org
    CONSTRAINT custom_validators_unique_name_per_org UNIQUE (org_id, name),

    -- Per spec FR-1, FR-9
    CONSTRAINT custom_validators_name_nonempty       CHECK (char_length(name) > 0 AND char_length(name) <= 255),
    CONSTRAINT custom_validators_pattern_nonempty    CHECK (char_length(regex_pattern) > 0 AND char_length(regex_pattern) <= 500),
    CONSTRAINT custom_validators_msg_ar_nonempty     CHECK (char_length(error_message_ar) > 0),
    CONSTRAINT custom_validators_msg_en_nonempty     CHECK (char_length(error_message_en) > 0),
    CONSTRAINT custom_validators_updated_after_created CHECK (updated_at >= created_at)
);

-- Indexes (per data-model.md)
CREATE INDEX IF NOT EXISTS idx_custom_validators_org_active
    ON custom_validators(org_id)
    WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_custom_validators_org_name
    ON custom_validators(org_id, name)
    WHERE deleted_at IS NULL;

-- =============================================================
-- 2. Extend elements table with custom_validators_ids array
-- =============================================================
ALTER TABLE elements
    ADD COLUMN IF NOT EXISTS custom_validators_ids UUID[] NOT NULL DEFAULT '{}';

-- GIN index for fast "which elements use this validator" queries (FR-6)
CREATE INDEX IF NOT EXISTS idx_elements_custom_validators_ids
    ON elements USING GIN (custom_validators_ids);

-- =============================================================
-- 3. Row-Level Security
-- =============================================================
ALTER TABLE custom_validators ENABLE ROW LEVEL SECURITY;

-- Drop pre-existing policies (idempotent re-run)
DROP POLICY IF EXISTS custom_validators_org_select ON custom_validators;
DROP POLICY IF EXISTS custom_validators_admin_write ON custom_validators;

-- Read: any authenticated user within the org may read active validators
-- (Designer dropdown + form-fill need this)
CREATE POLICY custom_validators_org_select ON custom_validators
    FOR SELECT
    USING (
        org_id = (
            SELECT org_id FROM profiles WHERE id = auth.uid()
        )
    );

-- Write (INSERT/UPDATE/DELETE): admin role only, within their own org
CREATE POLICY custom_validators_admin_write ON custom_validators
    FOR ALL
    USING (
        org_id = (
            SELECT org_id FROM profiles WHERE id = auth.uid()
        )
        AND EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
              AND profiles.role = 'admin'
        )
    )
    WITH CHECK (
        org_id = (
            SELECT org_id FROM profiles WHERE id = auth.uid()
        )
        AND EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
              AND profiles.role = 'admin'
        )
    );

-- =============================================================
-- 4. Audit trail anchor
-- =============================================================
-- Reuses existing audit_logs table. Application code emits:
--   VALIDATOR_CREATED, VALIDATOR_UPDATED, VALIDATOR_DELETED, VALIDATOR_TIMEOUT
-- (No DB trigger to keep audit logic explicit and testable in service layer.)

COMMENT ON TABLE custom_validators IS
    'Feature 048: org-scoped custom regex validators with bilingual error messages. Built-in deterministic validators always take precedence at runtime (Constitution Principle IV).';
