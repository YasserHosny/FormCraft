-- Migration: 036_batch_operations.sql
-- Feature: F036 Batch Operations & Print Queue
-- Date: 2026-05-26

-- ------------------------------------------------------
-- 1. Extend form_submissions for batch tracking
-- ------------------------------------------------------
ALTER TABLE form_submissions
ADD COLUMN IF NOT EXISTS batch_job_id UUID REFERENCES batch_jobs(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS batch_generated BOOLEAN NOT NULL DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_form_submissions_batch_job_id ON form_submissions(batch_job_id);

-- ------------------------------------------------------
-- 2. Batch Jobs
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS batch_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    template_id UUID NOT NULL REFERENCES templates(id),
    template_version INTEGER NOT NULL,
    created_by UUID NOT NULL REFERENCES profiles(id),
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued', 'running', 'completed', 'failed', 'cancelled')),
    data_source_type TEXT NOT NULL
        CHECK (data_source_type IN ('csv', 'xlsx', 'clipboard')),
    data_source_id UUID REFERENCES batch_data_sources(id) ON DELETE SET NULL,
    column_mapping JSONB NOT NULL DEFAULT '{}'::jsonb,
    row_count INTEGER NOT NULL DEFAULT 0,
    success_count INTEGER NOT NULL DEFAULT 0,
    fail_count INTEGER NOT NULL DEFAULT 0,
    progress INTEGER NOT NULL DEFAULT 0,
    duplicate_strategy TEXT NOT NULL DEFAULT 'warn'
        CHECK (duplicate_strategy IN ('warn', 'skip', 'include')),
    duplicate_count INTEGER NOT NULL DEFAULT 0,
    download_format TEXT NOT NULL DEFAULT 'zip'
        CHECK (download_format IN ('zip', 'merged_pdf', 'printer_queue')),
    printer_profile_id UUID REFERENCES printer_profiles(id),
    scheduled_job_id UUID REFERENCES batch_schedules(id) ON DELETE SET NULL,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    cancelled_by UUID REFERENCES profiles(id),
    error_summary TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_batch_job_progress CHECK (progress <= row_count)
);

CREATE INDEX IF NOT EXISTS idx_batch_jobs_org_status ON batch_jobs(org_id, status, updated_at);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_template ON batch_jobs(template_id);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_created_by ON batch_jobs(created_by);

ALTER TABLE batch_jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY batch_jobs_org_isolation ON batch_jobs
    FOR ALL
    USING (org_id = current_setting('app.current_org_id', true)::UUID)
    WITH CHECK (org_id = current_setting('app.current_org_id', true)::UUID);

-- ------------------------------------------------------
-- 3. Batch Data Sources
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS batch_data_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    mime_type TEXT NOT NULL
        CHECK (mime_type IN ('text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')),
    file_size_bytes INTEGER NOT NULL
        CHECK (file_size_bytes <= 10485760), -- 10 MB
    encoding TEXT,
    column_headers JSONB NOT NULL DEFAULT '[]'::jsonb,
    checksum TEXT NOT NULL,
    created_by UUID NOT NULL REFERENCES profiles(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_batch_data_sources_org ON batch_data_sources(org_id, created_at);

ALTER TABLE batch_data_sources ENABLE ROW LEVEL SECURITY;

CREATE POLICY batch_data_sources_org_isolation ON batch_data_sources
    FOR ALL
    USING (org_id = current_setting('app.current_org_id', true)::UUID)
    WITH CHECK (org_id = current_setting('app.current_org_id', true)::UUID);

-- ------------------------------------------------------
-- 4. Batch Schedules
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS batch_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    template_id UUID NOT NULL REFERENCES templates(id),
    created_by UUID NOT NULL REFERENCES profiles(id),
    name TEXT NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    data_source_type TEXT NOT NULL DEFAULT 'api'
        CHECK (data_source_type IN ('api')),
    api_endpoint TEXT NOT NULL,
    api_auth_type TEXT NOT NULL
        CHECK (api_auth_type IN ('api_key', 'bearer_token')),
    api_auth_credential TEXT NOT NULL,
    api_headers JSONB NOT NULL DEFAULT '{}'::jsonb,
    cron_expression TEXT NOT NULL,
    notification_recipients JSONB NOT NULL DEFAULT '[]'::jsonb,
    column_mapping JSONB NOT NULL DEFAULT '{}'::jsonb,
    download_format TEXT NOT NULL DEFAULT 'zip'
        CHECK (download_format IN ('zip', 'merged_pdf', 'printer_queue')),
    printer_profile_id UUID REFERENCES printer_profiles(id),
    max_rows_per_run INTEGER NOT NULL DEFAULT 1000,
    last_run_at TIMESTAMPTZ,
    last_run_status TEXT
        CHECK (last_run_status IN ('success', 'failed', 'cancelled')),
    last_run_job_id UUID REFERENCES batch_jobs(id) ON DELETE SET NULL,
    next_run_at TIMESTAMPTZ,
    failure_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_batch_schedules_org_enabled ON batch_schedules(org_id, enabled);
CREATE INDEX IF NOT EXISTS idx_batch_schedules_next_run ON batch_schedules(next_run_at) WHERE enabled = TRUE;

ALTER TABLE batch_schedules ENABLE ROW LEVEL SECURITY;

CREATE POLICY batch_schedules_org_isolation ON batch_schedules
    FOR ALL
    USING (org_id = current_setting('app.current_org_id', true)::UUID)
    WITH CHECK (org_id = current_setting('app.current_org_id', true)::UUID);

-- ------------------------------------------------------
-- 5. Batch Errors
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS batch_errors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    batch_job_id UUID NOT NULL REFERENCES batch_jobs(id) ON DELETE CASCADE,
    row_number INTEGER NOT NULL CHECK (row_number >= 1),
    field_key TEXT,
    error_type TEXT NOT NULL
        CHECK (error_type IN ('validation', 'generation', 'mapping', 'duplicate', 'template_changed')),
    error_message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_batch_errors_job ON batch_errors(batch_job_id, row_number);
CREATE INDEX IF NOT EXISTS idx_batch_errors_type ON batch_errors(batch_job_id, error_type);

ALTER TABLE batch_errors ENABLE ROW LEVEL SECURITY;

CREATE POLICY batch_errors_org_isolation ON batch_errors
    FOR ALL
    USING (org_id = current_setting('app.current_org_id', true)::UUID)
    WITH CHECK (org_id = current_setting('app.current_org_id', true)::UUID);

-- ------------------------------------------------------
-- 6. Comments
-- ------------------------------------------------------
COMMENT ON TABLE batch_jobs IS 'On-demand and scheduled batch form generation jobs.';
COMMENT ON TABLE batch_data_sources IS 'Uploaded CSV/XLSX/clipboard data sources for batch jobs.';
COMMENT ON TABLE batch_schedules IS 'Recurring batch job schedules with API data sources.';
COMMENT ON TABLE batch_errors IS 'Per-row, per-field errors for batch jobs.';
