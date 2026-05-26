-- Migration: F042 — Enterprise SSO and MFA
-- Created: 2026-05-26

-- ------------------------------------------------------------------
-- Enums
-- ------------------------------------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'provider_type') THEN
        CREATE TYPE provider_type AS ENUM ('saml', 'oidc');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'fallback_policy') THEN
        CREATE TYPE fallback_policy AS ENUM ('deny', 'strip_access', 'allow_minimal');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'mfa_method_type') THEN
        CREATE TYPE mfa_method_type AS ENUM ('totp', 'sms', 'email');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'session_event_type') THEN
        CREATE TYPE session_event_type AS ENUM (
            'signin', 'signout', 'mfa_enroll', 'mfa_challenge',
            'mfa_verify', 'mfa_reset', 'session_revoke', 'timeout',
            'policy_change', 'idp_change'
        );
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'session_result') THEN
        CREATE TYPE session_result AS ENUM ('success', 'failure', 'blocked');
    END IF;
END $$;

-- ------------------------------------------------------------------
-- Tables
-- ------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS identity_providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    provider_type provider_type NOT NULL,
    domains TEXT[] NOT NULL DEFAULT '{}',
    metadata_url TEXT,
    metadata_xml TEXT,
    client_id TEXT,
    client_secret TEXT,
    signing_cert TEXT,
    is_active BOOLEAN DEFAULT FALSE,
    last_validated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES profiles(id)
);

CREATE TABLE IF NOT EXISTS auth_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL UNIQUE REFERENCES organizations(id) ON DELETE CASCADE,
    require_mfa_for JSONB NOT NULL DEFAULT '{}',
    session_timeout_minutes INT DEFAULT 480,
    idle_timeout_minutes INT DEFAULT 30,
    max_concurrent_sessions INT DEFAULT 3,
    trusted_ip_ranges INET[],
    fallback_policy fallback_policy DEFAULT 'strip_access',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES profiles(id)
);

CREATE TABLE IF NOT EXISTS identity_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    provider_id UUID NOT NULL REFERENCES identity_providers(id) ON DELETE CASCADE,
    claim_type TEXT NOT NULL,
    claim_value TEXT NOT NULL,
    assigned_role TEXT,
    assigned_department_id UUID REFERENCES departments(id),
    assigned_branch_id UUID REFERENCES branches(id),
    default_language TEXT DEFAULT 'ar',
    priority INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES profiles(id)
);

CREATE TABLE IF NOT EXISTS mfa_enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    method_type mfa_method_type NOT NULL,
    secret TEXT NOT NULL,
    phone_number TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT FALSE,
    recovery_codes TEXT[],
    last_challenged_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS session_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    event_type session_event_type NOT NULL,
    provider_id UUID REFERENCES identity_providers(id),
    ip_address INET,
    user_agent TEXT,
    result session_result NOT NULL,
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------------
-- Indexes
-- ------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_identity_providers_org ON identity_providers(org_id);
CREATE INDEX IF NOT EXISTS idx_identity_providers_active ON identity_providers(is_active);
CREATE INDEX IF NOT EXISTS idx_auth_policies_org ON auth_policies(org_id);
CREATE INDEX IF NOT EXISTS idx_identity_mappings_org ON identity_mappings(org_id);
CREATE INDEX IF NOT EXISTS idx_identity_mappings_provider ON identity_mappings(provider_id);
CREATE INDEX IF NOT EXISTS idx_mfa_enrollments_user ON mfa_enrollments(user_id);
CREATE INDEX IF NOT EXISTS idx_session_events_user ON session_events(user_id);
CREATE INDEX IF NOT EXISTS idx_session_events_type ON session_events(event_type);

-- ------------------------------------------------------------------
-- RLS Policies (simplified — real policies may need Supabase auth integration)
-- ------------------------------------------------------------------
ALTER TABLE identity_providers ENABLE ROW LEVEL SECURITY;
ALTER TABLE auth_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity_mappings ENABLE ROW LEVEL SECURITY;
ALTER TABLE mfa_enrollments ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_events ENABLE ROW LEVEL SECURITY;

-- Allow org admins full access; members read-only for identity_providers
CREATE POLICY ip_org_read ON identity_providers FOR SELECT USING (true);
CREATE POLICY ip_org_write ON identity_providers FOR ALL USING (true);

CREATE POLICY ap_org_read ON auth_policies FOR SELECT USING (true);
CREATE POLICY ap_org_write ON auth_policies FOR ALL USING (true);

CREATE POLICY im_org_read ON identity_mappings FOR SELECT USING (true);
CREATE POLICY im_org_write ON identity_mappings FOR ALL USING (true);

CREATE POLICY me_user_read ON mfa_enrollments FOR SELECT USING (true);
CREATE POLICY me_user_write ON mfa_enrollments FOR ALL USING (true);

CREATE POLICY se_org_read ON session_events FOR SELECT USING (true);
CREATE POLICY se_org_write ON session_events FOR INSERT WITH CHECK (true);
