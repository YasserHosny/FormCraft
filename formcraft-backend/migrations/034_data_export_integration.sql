-- Migration 034: Data Export & Integration
-- Feature: 032-data-export-integration
-- Date: 2026-05-25

CREATE TABLE IF NOT EXISTS export_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_by UUID NOT NULL REFERENCES profiles(id),
    dataset TEXT NOT NULL DEFAULT 'submissions' CHECK (dataset IN ('submissions')),
    filters JSONB NOT NULL DEFAULT '{}'::jsonb,
    format TEXT NOT NULL CHECK (format IN ('csv', 'xlsx', 'json')),
    scope TEXT NOT NULL CHECK (scope IN ('flattened', 'structured')),
    frequency TEXT NOT NULL CHECK (frequency IN ('daily', 'weekly')),
    email_recipients TEXT[] NOT NULL,
    no_data_behavior TEXT NOT NULL DEFAULT 'send_empty_file' CHECK (no_data_behavior IN ('send_empty_file', 'send_notice')),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'disabled')),
    next_run_at TIMESTAMPTZ NOT NULL,
    last_run_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (cardinality(email_recipients) > 0)
);

CREATE TABLE IF NOT EXISTS export_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    requested_by UUID NOT NULL REFERENCES profiles(id),
    schedule_id UUID REFERENCES export_schedules(id) ON DELETE SET NULL,
    dataset TEXT NOT NULL DEFAULT 'submissions' CHECK (dataset IN ('submissions')),
    filters JSONB NOT NULL DEFAULT '{}'::jsonb,
    format TEXT NOT NULL CHECK (format IN ('csv', 'xlsx', 'json')),
    scope TEXT NOT NULL CHECK (scope IN ('flattened', 'structured')),
    matching_count INTEGER NOT NULL DEFAULT 0 CHECK (matching_count >= 0),
    status TEXT NOT NULL CHECK (status IN ('previewed', 'completed', 'rejected', 'failed')),
    rejection_reason TEXT,
    file_name TEXT,
    file_size_bytes BIGINT CHECK (file_size_bytes IS NULL OR file_size_bytes >= 0),
    completed_at TIMESTAMPTZ,
    created_by UUID NOT NULL REFERENCES profiles(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS export_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    schedule_id UUID NOT NULL REFERENCES export_schedules(id) ON DELETE CASCADE,
    export_request_id UUID REFERENCES export_requests(id) ON DELETE SET NULL,
    email_recipients TEXT[] NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'sent', 'failed')),
    attempt_count INTEGER NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    failure_reason TEXT,
    sent_at TIMESTAMPTZ,
    created_by UUID REFERENCES profiles(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS integration_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    key_hash TEXT NOT NULL,
    key_prefix TEXT NOT NULL,
    scopes TEXT[] NOT NULL,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'revoked', 'expired')),
    expires_at TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ,
    revoked_by UUID REFERENCES profiles(id),
    created_by UUID NOT NULL REFERENCES profiles(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (cardinality(scopes) > 0)
);

CREATE TABLE IF NOT EXISTS webhook_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    event_type TEXT NOT NULL CHECK (event_type IN ('form_submitted', 'form_printed', 'template_published', 'batch_completed')),
    target_url TEXT NOT NULL,
    signing_secret_hash TEXT NOT NULL,
    signing_secret_prefix TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'disabled')),
    created_by UUID NOT NULL REFERENCES profiles(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS webhook_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    subscription_id UUID NOT NULL REFERENCES webhook_subscriptions(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL CHECK (event_type IN ('form_submitted', 'form_printed', 'template_published', 'batch_completed')),
    event_id UUID NOT NULL,
    payload_preview JSONB NOT NULL,
    signature_header TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'delivered', 'failed')),
    attempt_count INTEGER NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    next_retry_at TIMESTAMPTZ,
    last_response_code INTEGER,
    last_response_body_preview TEXT,
    delivered_at TIMESTAMPTZ,
    created_by UUID REFERENCES profiles(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_export_requests_org_created ON export_requests(org_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_export_requests_schedule ON export_requests(schedule_id);
CREATE INDEX IF NOT EXISTS idx_export_schedules_org_status_next_run ON export_schedules(org_id, status, next_run_at);
CREATE INDEX IF NOT EXISTS idx_export_deliveries_schedule ON export_deliveries(schedule_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_export_deliveries_org_created ON export_deliveries(org_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_integration_credentials_org_status ON integration_credentials(org_id, status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_integration_credentials_key_hash ON integration_credentials(key_hash);
CREATE INDEX IF NOT EXISTS idx_webhook_subscriptions_org_event_status ON webhook_subscriptions(org_id, event_type, status);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_subscription_created ON webhook_deliveries(subscription_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_org_status ON webhook_deliveries(org_id, status, next_retry_at);

ALTER TABLE export_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE export_schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE export_deliveries ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhook_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhook_deliveries ENABLE ROW LEVEL SECURITY;

CREATE POLICY export_requests_org_isolation ON export_requests
    FOR ALL
    USING (org_id = current_setting('app.current_org_id', true)::UUID)
    WITH CHECK (org_id = current_setting('app.current_org_id', true)::UUID);

CREATE POLICY export_schedules_org_isolation ON export_schedules
    FOR ALL
    USING (org_id = current_setting('app.current_org_id', true)::UUID)
    WITH CHECK (org_id = current_setting('app.current_org_id', true)::UUID);

CREATE POLICY export_deliveries_org_isolation ON export_deliveries
    FOR ALL
    USING (org_id = current_setting('app.current_org_id', true)::UUID)
    WITH CHECK (org_id = current_setting('app.current_org_id', true)::UUID);

CREATE POLICY integration_credentials_org_isolation ON integration_credentials
    FOR ALL
    USING (org_id = current_setting('app.current_org_id', true)::UUID)
    WITH CHECK (org_id = current_setting('app.current_org_id', true)::UUID);

CREATE POLICY webhook_subscriptions_org_isolation ON webhook_subscriptions
    FOR ALL
    USING (org_id = current_setting('app.current_org_id', true)::UUID)
    WITH CHECK (org_id = current_setting('app.current_org_id', true)::UUID);

CREATE POLICY webhook_deliveries_org_isolation ON webhook_deliveries
    FOR ALL
    USING (org_id = current_setting('app.current_org_id', true)::UUID)
    WITH CHECK (org_id = current_setting('app.current_org_id', true)::UUID);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_export_requests_updated_at ON export_requests;
CREATE TRIGGER update_export_requests_updated_at
    BEFORE UPDATE ON export_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_export_schedules_updated_at ON export_schedules;
CREATE TRIGGER update_export_schedules_updated_at
    BEFORE UPDATE ON export_schedules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_export_deliveries_updated_at ON export_deliveries;
CREATE TRIGGER update_export_deliveries_updated_at
    BEFORE UPDATE ON export_deliveries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_integration_credentials_updated_at ON integration_credentials;
CREATE TRIGGER update_integration_credentials_updated_at
    BEFORE UPDATE ON integration_credentials
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_webhook_subscriptions_updated_at ON webhook_subscriptions;
CREATE TRIGGER update_webhook_subscriptions_updated_at
    BEFORE UPDATE ON webhook_subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_webhook_deliveries_updated_at ON webhook_deliveries;
CREATE TRIGGER update_webhook_deliveries_updated_at
    BEFORE UPDATE ON webhook_deliveries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
