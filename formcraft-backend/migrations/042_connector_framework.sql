-- Migration 042: Connector Framework
-- Feature: 049-connector-framework
-- API keys, webhooks (4 event types), webhook_deliveries (async dispatch queue),
-- pre-built connectors (DMS, Email, CRM, Banking) with field mappings.
--
-- See: formcraft-specs/specs/049-connector-framework/spec.md
--      Constitution Scope: this implementation is bounded to 4 event types +
--      4 pre-built connector types — no marketplace, no custom builder.

-- =============================================================
-- 1. api_keys
-- =============================================================
CREATE TABLE IF NOT EXISTS api_keys (
    id           UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id       UUID         NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name         VARCHAR(255) NOT NULL,
    key_prefix   VARCHAR(16)  NOT NULL,    -- displayed in UI (e.g. "fck_AbC123") — first 12 chars of secret
    key_hash     VARCHAR(128) NOT NULL UNIQUE,  -- HMAC-SHA256 hash of the full secret (hex)
    scopes       TEXT[]       NOT NULL DEFAULT ARRAY['read'],
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    created_by   UUID         NOT NULL REFERENCES profiles(id),
    last_used_at TIMESTAMPTZ,
    expires_at   TIMESTAMPTZ,
    is_active    BOOLEAN      NOT NULL DEFAULT TRUE,
    deleted_at   TIMESTAMPTZ,

    CONSTRAINT api_keys_unique_name_per_org UNIQUE (org_id, name),
    CONSTRAINT api_keys_scopes_nonempty     CHECK (array_length(scopes, 1) > 0)
);

CREATE INDEX IF NOT EXISTS idx_api_keys_org_active
    ON api_keys(org_id) WHERE deleted_at IS NULL AND is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_api_keys_hash
    ON api_keys(key_hash) WHERE deleted_at IS NULL AND is_active = TRUE;

-- =============================================================
-- 2. webhooks
-- =============================================================
CREATE TABLE IF NOT EXISTS webhooks (
    id                 UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id             UUID         NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name               VARCHAR(255) NOT NULL,
    event_type         VARCHAR(50)  NOT NULL,
    endpoint_url       VARCHAR(2048) NOT NULL,
    -- Per spec FR-6: header VALUES stored encrypted; only header NAMES retrievable in cleartext.
    -- Stored as { "Authorization": "<ciphertext>", "X-Custom": "<ciphertext>" } where ciphertext
    -- is produced by encryption_service.encrypt_for_org(value, org_id).
    custom_headers_enc JSONB        NOT NULL DEFAULT '{}'::jsonb,
    -- webhook_secret is the per-webhook HMAC-SHA256 signing key (NOT a user secret).
    -- Stored encrypted at rest; loaded only inside the dispatcher worker.
    webhook_secret_enc TEXT         NOT NULL,
    is_active          BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    created_by         UUID         NOT NULL REFERENCES profiles(id),
    updated_by         UUID         NOT NULL REFERENCES profiles(id),
    last_triggered_at  TIMESTAMPTZ,
    deleted_at         TIMESTAMPTZ,

    CONSTRAINT webhooks_event_type_valid CHECK (
        event_type IN ('form_submitted', 'form_printed', 'template_published', 'batch_completed')
    ),
    CONSTRAINT webhooks_url_https        CHECK (endpoint_url LIKE 'https://%'),
    CONSTRAINT webhooks_unique_event_url UNIQUE (org_id, event_type, endpoint_url)
);

CREATE INDEX IF NOT EXISTS idx_webhooks_org_active
    ON webhooks(org_id, is_active) WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_webhooks_event_active
    ON webhooks(event_type) WHERE is_active = TRUE AND deleted_at IS NULL;

-- =============================================================
-- 3. webhook_deliveries (the async dispatch queue)
-- =============================================================
CREATE TABLE IF NOT EXISTS webhook_deliveries (
    id              UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id      UUID         NOT NULL REFERENCES webhooks(id) ON DELETE CASCADE,
    org_id          UUID         NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    event_type      VARCHAR(50)  NOT NULL,
    resource_id     UUID         NOT NULL,
    -- Pre-built canonical payload (not user-defined). Stored at enqueue time so
    -- retries replay identical bytes (signature stability).
    payload         JSONB        NOT NULL,
    attempt_number  SMALLINT     NOT NULL DEFAULT 1,
    status          VARCHAR(20)  NOT NULL DEFAULT 'pending',
    -- Response capture (sensitive request payload is NOT logged here)
    status_code     SMALLINT,
    response_body   TEXT,             -- first 1KB only
    error_message   TEXT,
    -- Timing
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    sent_at         TIMESTAMPTZ,
    next_retry_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,

    CONSTRAINT wd_status_valid  CHECK (status IN ('pending', 'sent', 'success', 'failed')),
    CONSTRAINT wd_attempts_1_3  CHECK (attempt_number BETWEEN 1 AND 3)
);

-- Hot path: dispatcher polling claim
CREATE INDEX IF NOT EXISTS idx_wd_pending_due
    ON webhook_deliveries(next_retry_at)
    WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_wd_webhook_created
    ON webhook_deliveries(webhook_id, created_at DESC);

-- =============================================================
-- 4. connectors
-- =============================================================
CREATE TABLE IF NOT EXISTS connectors (
    id              UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID         NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    connector_type  VARCHAR(50)  NOT NULL,
    name            VARCHAR(255) NOT NULL,
    -- Mixed plaintext + encrypted fields. Secret fields (tokens, passwords) are
    -- stored under config_enc.<key> and decrypted only at dispatch time.
    config          JSONB        NOT NULL DEFAULT '{}'::jsonb,
    config_enc      JSONB        NOT NULL DEFAULT '{}'::jsonb,
    webhook_id      UUID         REFERENCES webhooks(id) ON DELETE SET NULL,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    created_by      UUID         NOT NULL REFERENCES profiles(id),
    updated_by      UUID         NOT NULL REFERENCES profiles(id),
    last_sync_at    TIMESTAMPTZ,
    error_message   TEXT,
    deleted_at      TIMESTAMPTZ,

    CONSTRAINT connectors_type_valid CHECK (connector_type IN ('dms', 'email', 'crm', 'banking')),
    CONSTRAINT connectors_unique_name UNIQUE (org_id, connector_type, name)
);

CREATE INDEX IF NOT EXISTS idx_connectors_org_active
    ON connectors(org_id) WHERE is_active = TRUE AND deleted_at IS NULL;

-- =============================================================
-- 5. connector_field_mappings (CRM/Banking only)
-- =============================================================
CREATE TABLE IF NOT EXISTS connector_field_mappings (
    id                  UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    connector_id        UUID         NOT NULL REFERENCES connectors(id) ON DELETE CASCADE,
    formcraft_field_id  UUID         NOT NULL REFERENCES elements(id) ON DELETE CASCADE,
    external_field_key  VARCHAR(255) NOT NULL,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT cfm_unique_per_connector_field UNIQUE (connector_id, formcraft_field_id)
);

CREATE INDEX IF NOT EXISTS idx_cfm_connector_id ON connector_field_mappings(connector_id);

-- =============================================================
-- 6. Row-Level Security
-- =============================================================
ALTER TABLE api_keys                 ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhooks                 ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhook_deliveries       ENABLE ROW LEVEL SECURITY;
ALTER TABLE connectors               ENABLE ROW LEVEL SECURITY;
ALTER TABLE connector_field_mappings ENABLE ROW LEVEL SECURITY;

-- Helper: drop any pre-existing policies (idempotent re-run)
DROP POLICY IF EXISTS api_keys_admin_all       ON api_keys;
DROP POLICY IF EXISTS webhooks_admin_all       ON webhooks;
DROP POLICY IF EXISTS wd_admin_select          ON webhook_deliveries;
DROP POLICY IF EXISTS wd_service_insert        ON webhook_deliveries;
DROP POLICY IF EXISTS wd_service_update        ON webhook_deliveries;
DROP POLICY IF EXISTS connectors_admin_all     ON connectors;
DROP POLICY IF EXISTS cfm_admin_all            ON connector_field_mappings;

-- All integration management is admin-only and strictly org-scoped.
CREATE POLICY api_keys_admin_all ON api_keys
    FOR ALL
    USING (
        org_id = (SELECT org_id FROM profiles WHERE id = auth.uid())
        AND EXISTS (SELECT 1 FROM profiles WHERE profiles.id = auth.uid() AND profiles.role = 'admin')
    )
    WITH CHECK (
        org_id = (SELECT org_id FROM profiles WHERE id = auth.uid())
        AND EXISTS (SELECT 1 FROM profiles WHERE profiles.id = auth.uid() AND profiles.role = 'admin')
    );

CREATE POLICY webhooks_admin_all ON webhooks
    FOR ALL
    USING (
        org_id = (SELECT org_id FROM profiles WHERE id = auth.uid())
        AND EXISTS (SELECT 1 FROM profiles WHERE profiles.id = auth.uid() AND profiles.role = 'admin')
    )
    WITH CHECK (
        org_id = (SELECT org_id FROM profiles WHERE id = auth.uid())
        AND EXISTS (SELECT 1 FROM profiles WHERE profiles.id = auth.uid() AND profiles.role = 'admin')
    );

-- webhook_deliveries: admins can SELECT for their org; INSERT/UPDATE only from service role
CREATE POLICY wd_admin_select ON webhook_deliveries
    FOR SELECT
    USING (
        org_id = (SELECT org_id FROM profiles WHERE id = auth.uid())
        AND EXISTS (SELECT 1 FROM profiles WHERE profiles.id = auth.uid() AND profiles.role = 'admin')
    );

CREATE POLICY connectors_admin_all ON connectors
    FOR ALL
    USING (
        org_id = (SELECT org_id FROM profiles WHERE id = auth.uid())
        AND EXISTS (SELECT 1 FROM profiles WHERE profiles.id = auth.uid() AND profiles.role = 'admin')
    )
    WITH CHECK (
        org_id = (SELECT org_id FROM profiles WHERE id = auth.uid())
        AND EXISTS (SELECT 1 FROM profiles WHERE profiles.id = auth.uid() AND profiles.role = 'admin')
    );

CREATE POLICY cfm_admin_all ON connector_field_mappings
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM connectors c
            JOIN profiles p ON p.id = auth.uid()
            WHERE c.id = connector_field_mappings.connector_id
              AND c.org_id = p.org_id
              AND p.role = 'admin'
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM connectors c
            JOIN profiles p ON p.id = auth.uid()
            WHERE c.id = connector_field_mappings.connector_id
              AND c.org_id = p.org_id
              AND p.role = 'admin'
        )
    );

COMMENT ON TABLE webhook_deliveries IS
    'Feature 049: Async webhook dispatch queue. Workers claim rows with FOR UPDATE SKIP LOCKED; retries scheduled at +1s, +5s, +30s. No external MQ.';
