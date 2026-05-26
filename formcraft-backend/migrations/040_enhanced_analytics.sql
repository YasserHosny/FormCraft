-- Migration: F040 Enhanced Analytics Dashboard
-- Date: 2026-05-26

-- ============================================================
-- 1. field_analytics
-- ============================================================
CREATE TABLE IF NOT EXISTS field_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    template_version INT NOT NULL,
    field_key TEXT NOT NULL,
    error_count INT NOT NULL DEFAULT 0 CHECK (error_count >= 0),
    error_types JSONB NOT NULL DEFAULT '{}',
    empty_count INT NOT NULL DEFAULT 0 CHECK (empty_count >= 0),
    total_submissions INT NOT NULL DEFAULT 0 CHECK (total_submissions >= 0),
    avg_fill_time_ms INT CHECK (avg_fill_time_ms >= 0),
    computed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    retention_bucket TEXT NOT NULL DEFAULT 'hot' CHECK (retention_bucket IN ('hot', 'archive'))
);

CREATE INDEX IF NOT EXISTS idx_field_analytics_org_template ON field_analytics(org_id, template_id, template_version);
CREATE INDEX IF NOT EXISTS idx_field_analytics_period ON field_analytics(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_field_analytics_retention ON field_analytics(retention_bucket, computed_at);

ALTER TABLE field_analytics ENABLE ROW LEVEL SECURITY;

CREATE POLICY field_analytics_org_isolation ON field_analytics
    USING (org_id = auth.jwt() ->> 'org_id');

-- ============================================================
-- 2. operator_analytics
-- ============================================================
CREATE TABLE IF NOT EXISTS operator_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    operator_id UUID NOT NULL,
    period_type TEXT NOT NULL CHECK (period_type IN ('day', 'week', 'month')),
    period_start DATE NOT NULL,
    forms_filled INT NOT NULL DEFAULT 0 CHECK (forms_filled >= 0),
    avg_fill_time_ms INT CHECK (avg_fill_time_ms >= 0),
    error_rate DECIMAL(5,4) NOT NULL DEFAULT 0.0000 CHECK (error_rate >= 0 AND error_rate <= 1),
    busiest_hours JSONB NOT NULL DEFAULT '{}',
    computed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_operator_analytics_org_operator ON operator_analytics(org_id, operator_id, period_type, period_start);
CREATE INDEX IF NOT EXISTS idx_operator_analytics_period ON operator_analytics(period_type, period_start);

ALTER TABLE operator_analytics ENABLE ROW LEVEL SECURITY;

CREATE POLICY operator_analytics_org_isolation ON operator_analytics
    USING (org_id = auth.jwt() ->> 'org_id');

-- ============================================================
-- 3. compliance_scorecard_cache
-- ============================================================
CREATE TABLE IF NOT EXISTS compliance_scorecard_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    validator_coverage_pct DECIMAL(5,2) NOT NULL DEFAULT 0.00 CHECK (validator_coverage_pct >= 0 AND validator_coverage_pct <= 100),
    bilingual_label_pct DECIMAL(5,2) NOT NULL DEFAULT 0.00 CHECK (bilingual_label_pct >= 0 AND bilingual_label_pct <= 100),
    quality_score_avg DECIMAL(5,2) NOT NULL DEFAULT 0.00 CHECK (quality_score_avg >= 0 AND quality_score_avg <= 100),
    templates_needing_attention INT NOT NULL DEFAULT 0 CHECK (templates_needing_attention >= 0),
    customer_data_access_spike BOOLEAN NOT NULL DEFAULT FALSE,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    cache_expires_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_compliance_cache_org ON compliance_scorecard_cache(org_id, cache_expires_at);

ALTER TABLE compliance_scorecard_cache ENABLE ROW LEVEL SECURITY;

CREATE POLICY compliance_cache_admin_only ON compliance_scorecard_cache
    USING (
        org_id = auth.jwt() ->> 'org_id'
        AND auth.jwt() ->> 'role' = 'admin'
    );

-- ============================================================
-- 4. analytics_aggregation_log
-- ============================================================
CREATE TABLE IF NOT EXISTS analytics_aggregation_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    view_name TEXT NOT NULL,
    refresh_type TEXT NOT NULL CHECK (refresh_type IN ('full', 'incremental')),
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    duration_ms INT CHECK (duration_ms >= 0),
    row_count INT CHECK (row_count >= 0),
    status TEXT NOT NULL CHECK (status IN ('running', 'success', 'failed')),
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_agg_log_view_status ON analytics_aggregation_log(view_name, status, started_at DESC);

ALTER TABLE analytics_aggregation_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY analytics_log_admin_only ON analytics_aggregation_log
    USING (auth.jwt() ->> 'role' = 'admin');

-- ============================================================
-- 5. Materialized View: mv_template_usage_funnel
-- ============================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_template_usage_funnel AS
SELECT
    org_id,
    template_id,
    template_version,
    date_trunc('day', created_at) AS day,
    COUNT(*) FILTER (WHERE status = 'started') AS started_count,
    COUNT(*) FILTER (WHERE status = 'draft') AS draft_count,
    COUNT(*) FILTER (WHERE status = 'submitted') AS submitted_count,
    COUNT(*) FILTER (WHERE status = 'printed') AS printed_count
FROM submissions
GROUP BY org_id, template_id, template_version, day;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_funnel_unique ON mv_template_usage_funnel (org_id, template_id, template_version, day);
