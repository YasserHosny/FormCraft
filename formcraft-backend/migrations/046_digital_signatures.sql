-- Migration: F046 Digital Signatures
-- Created: 2026-05-26

-- ============================================================
-- Signature Workflows
-- ============================================================
CREATE TABLE IF NOT EXISTS signature_workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    template_id UUID REFERENCES templates(id) ON DELETE SET NULL,
    approval_step_id UUID REFERENCES template_reviews(id) ON DELETE SET NULL,
    created_by UUID NOT NULL REFERENCES profiles(id),
    name TEXT NOT NULL,
    is_ordered BOOLEAN NOT NULL DEFAULT FALSE,
    expiration_days INTEGER NOT NULL DEFAULT 7 CHECK (expiration_days BETWEEN 1 AND 30),
    decline_policy TEXT NOT NULL DEFAULT 'stop' CHECK (decline_policy IN ('stop', 'continue_next', 'route_to_admin')),
    require_all_signers BOOLEAN NOT NULL DEFAULT TRUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT exactly_one_target CHECK (
        (template_id IS NOT NULL AND approval_step_id IS NULL)
        OR (template_id IS NULL AND approval_step_id IS NOT NULL)
    )
);

CREATE UNIQUE INDEX idx_signature_workflows_active_template
    ON signature_workflows(org_id, template_id)
    WHERE is_active = TRUE AND template_id IS NOT NULL;

CREATE UNIQUE INDEX idx_signature_workflows_active_approval
    ON signature_workflows(org_id, approval_step_id)
    WHERE is_active = TRUE AND approval_step_id IS NOT NULL;

-- ============================================================
-- Signature Requests
-- ============================================================
CREATE TABLE IF NOT EXISTS signature_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES signature_workflows(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    submission_id UUID REFERENCES form_submissions(id) ON DELETE SET NULL,
    approval_id UUID REFERENCES template_reviews(id) ON DELETE SET NULL,
    created_by UUID NOT NULL REFERENCES profiles(id),
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'in_progress', 'signed', 'declined', 'expired', 'canceled', 'sealed', 'failed')),
    current_signer_index INTEGER NOT NULL DEFAULT 0,
    expires_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    sealed_pdf_path TEXT,
    document_hash TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT exactly_one_request_target CHECK (
        (submission_id IS NOT NULL AND approval_id IS NULL)
        OR (submission_id IS NULL AND approval_id IS NOT NULL)
    ),
    CONSTRAINT expires_after_created CHECK (expires_at > created_at)
);

CREATE INDEX idx_signature_requests_org_status ON signature_requests(org_id, status);
CREATE INDEX idx_signature_requests_submission ON signature_requests(submission_id);

-- ============================================================
-- Signature Recipients
-- ============================================================
CREATE TABLE IF NOT EXISTS signature_recipients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL REFERENCES signature_requests(id) ON DELETE CASCADE,
    signer_type TEXT NOT NULL CHECK (signer_type IN ('internal', 'external')),
    profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    email TEXT,
    name TEXT NOT NULL,
    phone TEXT,
    order_index INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'invited', 'viewed', 'verified', 'signed', 'declined', 'expired', 'canceled')),
    decline_reason TEXT,
    signed_at TIMESTAMPTZ,
    signature_token TEXT,
    token_expires_at TIMESTAMPTZ,
    otp_code_hash TEXT,
    otp_expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT internal_has_profile CHECK (
        signer_type != 'internal' OR profile_id IS NOT NULL
    ),
    CONSTRAINT external_has_email CHECK (
        signer_type != 'external' OR email IS NOT NULL
    )
);

CREATE UNIQUE INDEX idx_signature_recipients_ordered
    ON signature_recipients(request_id, order_index)
    WHERE order_index > 0;

CREATE INDEX idx_signature_recipients_token ON signature_recipients(signature_token);
CREATE INDEX idx_signature_recipients_request ON signature_recipients(request_id);

-- ============================================================
-- Signature Events
-- ============================================================
CREATE TABLE IF NOT EXISTS signature_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL REFERENCES signature_requests(id) ON DELETE CASCADE,
    recipient_id UUID REFERENCES signature_recipients(id) ON DELETE SET NULL,
    actor_type TEXT NOT NULL CHECK (actor_type IN ('system', 'operator', 'admin', 'signer')),
    actor_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    event_type TEXT NOT NULL CHECK (event_type IN ('created', 'invited', 'viewed', 'verified', 'signed', 'declined', 'resend', 'canceled', 'expired', 'sealed', 'failed', 'hash_verified')),
    event_data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_signature_events_request ON signature_events(request_id);
CREATE INDEX idx_signature_events_created ON signature_events(created_at);

-- ============================================================
-- Signed Evidence Packages
-- ============================================================
CREATE TABLE IF NOT EXISTS signed_evidence_packages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL UNIQUE REFERENCES signature_requests(id) ON DELETE CASCADE,
    document_hash TEXT NOT NULL,
    hash_algorithm TEXT NOT NULL DEFAULT 'sha256',
    original_pdf_path TEXT,
    sealed_pdf_path TEXT NOT NULL,
    signer_snapshot JSONB NOT NULL,
    event_summary JSONB NOT NULL,
    integrity_status TEXT NOT NULL DEFAULT 'valid' CHECK (integrity_status IN ('valid', 'invalid', 'unknown')),
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- RLS Policies
-- ============================================================

ALTER TABLE signature_workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE signature_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE signature_recipients ENABLE ROW LEVEL SECURITY;
ALTER TABLE signature_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE signed_evidence_packages ENABLE ROW LEVEL SECURITY;

-- signature_workflows: org members with admin/designer role
CREATE POLICY signature_workflows_org_select ON signature_workflows
    FOR SELECT USING (auth.uid() IN (
        SELECT p.id FROM profiles p
        JOIN org_members om ON om.profile_id = p.id
        WHERE om.org_id = signature_workflows.org_id AND om.role IN ('admin', 'designer')
    ));

CREATE POLICY signature_workflows_org_modify ON signature_workflows
    FOR ALL USING (auth.uid() IN (
        SELECT p.id FROM profiles p
        JOIN org_members om ON om.profile_id = p.id
        WHERE om.org_id = signature_workflows.org_id AND om.role IN ('admin', 'designer')
    ));

-- signature_requests: org members; internal signers can see their own
CREATE POLICY signature_requests_org_select ON signature_requests
    FOR SELECT USING (
        auth.uid() IN (
            SELECT p.id FROM profiles p
            JOIN org_members om ON om.profile_id = p.id
            WHERE om.org_id = signature_requests.org_id
        )
        OR auth.uid() IN (
            SELECT r.profile_id FROM signature_recipients r
            WHERE r.request_id = signature_requests.id AND r.signer_type = 'internal'
        )
    );

CREATE POLICY signature_requests_org_modify ON signature_requests
    FOR ALL USING (auth.uid() IN (
        SELECT p.id FROM profiles p
        JOIN org_members om ON om.profile_id = p.id
        WHERE om.org_id = signature_requests.org_id AND om.role IN ('admin', 'designer', 'operator')
    ));

-- signature_recipients: external signers via token hash match is handled at app level
-- org members can see all recipients for their requests
CREATE POLICY signature_recipients_org_select ON signature_recipients
    FOR SELECT USING (auth.uid() IN (
        SELECT p.id FROM profiles p
        JOIN org_members om ON om.profile_id = p.id
        JOIN signature_requests sr ON sr.org_id = om.org_id
        WHERE sr.id = signature_recipients.request_id
    ));

CREATE POLICY signature_recipients_org_modify ON signature_recipients
    FOR ALL USING (auth.uid() IN (
        SELECT p.id FROM profiles p
        JOIN org_members om ON om.profile_id = p.id
        JOIN signature_requests sr ON sr.org_id = om.org_id
        WHERE sr.id = signature_recipients.request_id AND om.role IN ('admin', 'designer', 'operator')
    ));

-- signature_events: org members and signers for their own requests
CREATE POLICY signature_events_org_select ON signature_events
    FOR SELECT USING (
        auth.uid() IN (
            SELECT p.id FROM profiles p
            JOIN org_members om ON om.profile_id = p.id
            JOIN signature_requests sr ON sr.org_id = om.org_id
            WHERE sr.id = signature_events.request_id
        )
        OR auth.uid() IN (
            SELECT r.profile_id FROM signature_recipients r
            WHERE r.request_id = signature_events.request_id AND r.signer_type = 'internal'
        )
    );

-- signed_evidence_packages: org members with appropriate roles
CREATE POLICY signed_evidence_org_select ON signed_evidence_packages
    FOR SELECT USING (auth.uid() IN (
        SELECT p.id FROM profiles p
        JOIN org_members om ON om.profile_id = p.id
        JOIN signature_requests sr ON sr.org_id = om.org_id
        WHERE sr.id = signed_evidence_packages.request_id
    ));

-- ============================================================
-- Audit logging trigger for signature_events
-- ============================================================
CREATE OR REPLACE FUNCTION log_signature_event_audit()
RETURNS TRIGGER AS $$
BEGIN
    -- Note: actual audit log writes should happen at application level
    -- for richer context (actor info, IP, user agent).
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER signature_events_audit_trigger
    AFTER INSERT ON signature_events
    FOR EACH ROW
    EXECUTE FUNCTION log_signature_event_audit();
