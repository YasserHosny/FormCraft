-- Migration: Add retention and archival tables + archive schema
-- Feature: 044-data-retention-archival

-- ------------------------------------------------------------------
-- Archive schema
-- ------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS archive;

-- ------------------------------------------------------------------
-- retention_policies
-- ------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.retention_policies (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          uuid NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    name            jsonb NOT NULL,
    data_class      varchar(64) NOT NULL,
    scope_json      jsonb NOT NULL DEFAULT '{}',
    action          varchar(32) NOT NULL,
    period_days     integer NOT NULL,
    legal_basis     varchar(128),
    approval_required boolean NOT NULL DEFAULT true,
    effective_date  timestamptz NOT NULL DEFAULT now(),
    created_by      uuid NOT NULL REFERENCES public.profiles(id),
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_retention_policies_org_data_class_scope
    ON public.retention_policies (org_id, data_class, scope_json)
    WHERE approval_required = true;

CREATE INDEX IF NOT EXISTS idx_retention_policies_effective_date
    ON public.retention_policies (effective_date);

-- ------------------------------------------------------------------
-- retention_jobs
-- ------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.retention_jobs (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id           uuid NOT NULL REFERENCES public.retention_policies(id) ON DELETE CASCADE,
    status              varchar(32) NOT NULL DEFAULT 'pending',
    started_at          timestamptz,
    completed_at        timestamptz,
    batch_size          integer NOT NULL DEFAULT 1000,
    checkpoint_cursor   varchar(255),
    evaluated_count     integer NOT NULL DEFAULT 0,
    actioned_count      integer NOT NULL DEFAULT 0,
    error_count         integer NOT NULL DEFAULT 0,
    error_log           jsonb NOT NULL DEFAULT '[]',
    skipped_records     jsonb NOT NULL DEFAULT '[]',
    manifest_id         uuid,
    resumed_from_job_id uuid REFERENCES public.retention_jobs(id),
    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_retention_jobs_policy_status ON public.retention_jobs (policy_id, status);
CREATE INDEX IF NOT EXISTS idx_retention_jobs_status_created ON public.retention_jobs (status, created_at);

-- ------------------------------------------------------------------
-- legal_holds
-- ------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.legal_holds (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          uuid NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    hold_type       varchar(64) NOT NULL,
    scope_type      varchar(64) NOT NULL,
    scope_id        uuid NOT NULL,
    reason          text NOT NULL,
    expiry_date     timestamptz,
    created_by      uuid NOT NULL REFERENCES public.profiles(id),
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_legal_holds_org_scope
    ON public.legal_holds (org_id, scope_type, scope_id)
    WHERE expiry_date IS NULL OR expiry_date > now();

CREATE INDEX IF NOT EXISTS idx_legal_holds_hold_type ON public.legal_holds (hold_type);

-- ------------------------------------------------------------------
-- archive_manifests
-- ------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.archive_manifests (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id              uuid NOT NULL REFERENCES public.retention_jobs(id) ON DELETE CASCADE,
    record_count        integer NOT NULL,
    schema_location     varchar(255) NOT NULL,
    cold_storage_uri    text,
    sha256_hash         varchar(64) NOT NULL,
    integrity_status    varchar(32) NOT NULL DEFAULT 'verified',
    restore_conditions  jsonb NOT NULL DEFAULT '{}',
    created_at          timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_archive_manifests_job ON public.archive_manifests (job_id);
CREATE INDEX IF NOT EXISTS idx_archive_manifests_sha256 ON public.archive_manifests (sha256_hash);

-- ------------------------------------------------------------------
-- privacy_requests
-- ------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.privacy_requests (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id              uuid NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    request_type        varchar(64) NOT NULL,
    scope_type          varchar(64) NOT NULL,
    scope_id            uuid NOT NULL,
    status              varchar(32) NOT NULL DEFAULT 'pending',
    conflict_hold_id    uuid REFERENCES public.legal_holds(id),
    resolution          jsonb,
    created_by          uuid NOT NULL REFERENCES public.profiles(id),
    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_privacy_requests_org_status ON public.privacy_requests (org_id, status);
CREATE INDEX IF NOT EXISTS idx_privacy_requests_scope ON public.privacy_requests (scope_type, scope_id);

-- ------------------------------------------------------------------
-- Archive shadow tables
-- ------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS archive.form_submissions (
    LIKE public.form_submissions INCLUDING ALL,
    original_id     uuid NOT NULL,
    archived_at     timestamptz NOT NULL DEFAULT now(),
    manifest_id     uuid REFERENCES public.archive_manifests(id)
);

CREATE TABLE IF NOT EXISTS archive.customer_profiles (
    LIKE public.customer_profiles INCLUDING ALL,
    original_id     uuid NOT NULL,
    archived_at     timestamptz NOT NULL DEFAULT now(),
    manifest_id     uuid REFERENCES public.archive_manifests(id)
);

CREATE TABLE IF NOT EXISTS archive.generated_pdfs (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    original_id     uuid NOT NULL,
    metadata        jsonb NOT NULL DEFAULT '{}',
    archived_at     timestamptz NOT NULL DEFAULT now(),
    manifest_id     uuid REFERENCES public.archive_manifests(id),
    cold_storage_uri text
);

CREATE TABLE IF NOT EXISTS archive.export_files (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    original_id     uuid NOT NULL,
    metadata        jsonb NOT NULL DEFAULT '{}',
    archived_at     timestamptz NOT NULL DEFAULT now(),
    manifest_id     uuid REFERENCES public.archive_manifests(id),
    cold_storage_uri text
);

CREATE TABLE IF NOT EXISTS archive.portal_sessions (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    original_id     uuid NOT NULL,
    metadata        jsonb NOT NULL DEFAULT '{}',
    archived_at     timestamptz NOT NULL DEFAULT now(),
    manifest_id     uuid REFERENCES public.archive_manifests(id)
);

-- ------------------------------------------------------------------
-- RLS Policies
-- ------------------------------------------------------------------
ALTER TABLE public.retention_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.retention_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.legal_holds ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.archive_manifests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.privacy_requests ENABLE ROW LEVEL SECURITY;

CREATE POLICY retention_policies_org_isolation ON public.retention_policies
    FOR ALL USING (org_id = (auth.jwt() ->> 'org_id')::uuid);

CREATE POLICY retention_jobs_org_isolation ON public.retention_jobs
    FOR ALL USING (
        policy_id IN (
            SELECT id FROM public.retention_policies
            WHERE org_id = (auth.jwt() ->> 'org_id')::uuid
        )
    );

CREATE POLICY legal_holds_org_isolation ON public.legal_holds
    FOR ALL USING (org_id = (auth.jwt() ->> 'org_id')::uuid);

CREATE POLICY archive_manifests_org_isolation ON public.archive_manifests
    FOR ALL USING (
        job_id IN (
            SELECT j.id FROM public.retention_jobs j
            JOIN public.retention_policies p ON j.policy_id = p.id
            WHERE p.org_id = (auth.jwt() ->> 'org_id')::uuid
        )
    );

CREATE POLICY privacy_requests_org_isolation ON public.privacy_requests
    FOR ALL USING (org_id = (auth.jwt() ->> 'org_id')::uuid);
