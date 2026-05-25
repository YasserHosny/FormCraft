-- Migration: 035_external_form_portal.sql
-- Feature: F034 External Form Portal
-- Adds portal configuration, sessions, OTP verification, rate limit events, and public submission metadata tables.

-- ------------------------------------------------------
-- Portal Configurations
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS portal_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id),
    template_id UUID NOT NULL REFERENCES templates(id),
    public_slug TEXT NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    verification_required BOOLEAN NOT NULL DEFAULT FALSE,
    allowed_otp_modes TEXT[] NOT NULL DEFAULT '{}',
    captcha_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    captcha_provider TEXT,
    allow_pdf_download BOOLEAN NOT NULL DEFAULT FALSE,
    send_email_confirmation BOOLEAN NOT NULL DEFAULT FALSE,
    rate_limit_max INTEGER NOT NULL DEFAULT 10,
    rate_limit_window_minutes INTEGER NOT NULL DEFAULT 60,
    created_by UUID NOT NULL REFERENCES profiles(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_portal_config_org_slug
    ON portal_configurations(org_id, public_slug);

CREATE UNIQUE INDEX IF NOT EXISTS idx_portal_config_org_template
    ON portal_configurations(org_id, template_id);

CREATE INDEX IF NOT EXISTS idx_portal_config_enabled
    ON portal_configurations(org_id, enabled)
    WHERE enabled = TRUE;

-- ------------------------------------------------------
-- Portal Sessions
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS portal_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id),
    portal_configuration_id UUID NOT NULL REFERENCES portal_configurations(id),
    template_id UUID NOT NULL REFERENCES templates(id),
    template_version INTEGER NOT NULL,
    session_token_hash TEXT NOT NULL,
    browser_fingerprint_hash TEXT,
    ip_hash TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'started',
    otp_verified_at TIMESTAMPTZ,
    verified_contact_mode TEXT,
    verified_contact_hash TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_portal_session_status
        CHECK (status IN ('started', 'otp_verified', 'submitted', 'expired', 'locked'))
);

CREATE INDEX IF NOT EXISTS idx_portal_session_token_hash
    ON portal_sessions(session_token_hash);

CREATE INDEX IF NOT EXISTS idx_portal_session_expires
    ON portal_sessions(expires_at)
    WHERE status IN ('started', 'otp_verified');

-- ------------------------------------------------------
-- Portal OTP Verifications
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS portal_otp_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id),
    portal_session_id UUID NOT NULL REFERENCES portal_sessions(id) ON DELETE CASCADE,
    contact_mode TEXT NOT NULL,
    contact_hash TEXT NOT NULL,
    code_hash TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    attempt_count INTEGER NOT NULL DEFAULT 0,
    expires_at TIMESTAMPTZ NOT NULL,
    locked_until TIMESTAMPTZ,
    sent_at TIMESTAMPTZ,
    verified_at TIMESTAMPTZ,
    provider_error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_portal_otp_status
        CHECK (status IN ('pending', 'verified', 'failed', 'locked', 'expired', 'provider_failed'))
);

CREATE INDEX IF NOT EXISTS idx_portal_otp_session_latest
    ON portal_otp_verifications(portal_session_id, created_at DESC)
    WHERE status = 'pending';

-- ------------------------------------------------------
-- Portal Rate Limit Events
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS portal_rate_limit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id),
    portal_configuration_id UUID NOT NULL REFERENCES portal_configurations(id),
    portal_session_id UUID REFERENCES portal_sessions(id) ON DELETE SET NULL,
    key_type TEXT NOT NULL,
    key_hash TEXT NOT NULL,
    event_type TEXT NOT NULL,
    allowed BOOLEAN NOT NULL,
    window_start TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_portal_rate_key_type
        CHECK (key_type IN ('pre_otp', 'verified_contact')),
    CONSTRAINT chk_portal_rate_event_type
        CHECK (event_type IN ('load', 'otp_send', 'submit'))
);

CREATE INDEX IF NOT EXISTS idx_portal_rate_limit_lookup
    ON portal_rate_limit_events(org_id, portal_configuration_id, key_hash, event_type, window_start DESC);

-- ------------------------------------------------------
-- Public Submission Metadata
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS public_submission_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id),
    submission_id UUID NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    portal_configuration_id UUID NOT NULL REFERENCES portal_configurations(id),
    portal_session_id UUID NOT NULL REFERENCES portal_sessions(id),
    source TEXT NOT NULL DEFAULT 'public_portal',
    template_version INTEGER NOT NULL,
    verified_contact_mode TEXT,
    verified_contact_hash TEXT,
    submission_ip_hash TEXT NOT NULL,
    captcha_verified BOOLEAN NOT NULL DEFAULT FALSE,
    audit_field_summary JSONB NOT NULL DEFAULT '{}',
    pdf_download_token_hash TEXT,
    pdf_download_expires_at TIMESTAMPTZ,
    email_confirmation_status TEXT,
    email_confirmation_sent_at TIMESTAMPTZ,
    email_confirmation_failure_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_public_meta_source
        CHECK (source = 'public_portal'),
    CONSTRAINT chk_public_meta_email_status
        CHECK (email_confirmation_status IN ('not_requested', 'queued', 'sent', 'failed')),
    CONSTRAINT uq_public_meta_submission UNIQUE (submission_id)
);

CREATE INDEX IF NOT EXISTS idx_public_meta_session
    ON public_submission_metadata(portal_session_id);

CREATE INDEX IF NOT EXISTS idx_public_meta_config
    ON public_submission_metadata(portal_configuration_id);

-- ------------------------------------------------------
-- RLS Policies
-- ------------------------------------------------------
ALTER TABLE portal_configurations ENABLE ROW LEVEL SECURITY;
ALTER TABLE portal_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE portal_otp_verifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE portal_rate_limit_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public_submission_metadata ENABLE ROW LEVEL SECURITY;

-- portal_configurations: admins can manage; public read via anon for enabled configs is handled in service layer
CREATE POLICY portal_config_org_isolation ON portal_configurations
    USING (org_id = current_setting('app.current_org_id')::UUID);

-- portal_sessions: org-scoped service access
CREATE POLICY portal_session_org_isolation ON portal_sessions
    USING (org_id = current_setting('app.current_org_id')::UUID);

-- portal_otp_verifications: org-scoped service access
CREATE POLICY portal_otp_org_isolation ON portal_otp_verifications
    USING (org_id = current_setting('app.current_org_id')::UUID);

-- portal_rate_limit_events: org-scoped service access
CREATE POLICY portal_rate_org_isolation ON portal_rate_limit_events
    USING (org_id = current_setting('app.current_org_id')::UUID);

-- public_submission_metadata: org-scoped service access
CREATE POLICY public_meta_org_isolation ON public_submission_metadata
    USING (org_id = current_setting('app.current_org_id')::UUID);
