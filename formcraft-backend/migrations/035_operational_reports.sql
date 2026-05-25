-- Migration 035: Operational Report Engine
-- Feature: 033-operational-reports
-- Date: 2026-05-26

-- 1. Add field_type_tag to elements table
CREATE TYPE field_type_tag AS ENUM (
    'amount',
    'date',
    'customer_name',
    'customer_id',
    'reference_number',
    'beneficiary',
    'signatory'
);

ALTER TABLE elements
ADD COLUMN IF NOT EXISTS field_type_tag field_type_tag DEFAULT NULL;

COMMENT ON COLUMN elements.field_type_tag IS
  'Designer-assigned tag for report engine to identify summable/groupable fields. Independent of control_type.';

-- 2. Create report_templates table
CREATE TABLE IF NOT EXISTS report_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    name_ar TEXT,
    report_type TEXT NOT NULL CHECK (report_type IN (
        'transaction_register', 'daily_reconciliation', 'period_summary',
        'custom', 'beneficiary', 'void_reprint', 'signatory_usage'
    )),
    description TEXT,
    config JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_system BOOLEAN NOT NULL DEFAULT false,
    created_by UUID NOT NULL REFERENCES profiles(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_report_templates_org ON report_templates(org_id);
CREATE INDEX IF NOT EXISTS idx_report_templates_type ON report_templates(org_id, report_type);

ALTER TABLE report_templates ENABLE ROW LEVEL SECURITY;

CREATE POLICY report_templates_org_isolation ON report_templates
    FOR ALL
    USING (org_id = current_setting('app.current_org_id', true)::UUID)
    WITH CHECK (org_id = current_setting('app.current_org_id', true)::UUID);

-- 3. Create report_schedules table
CREATE TABLE IF NOT EXISTS report_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_template_id UUID NOT NULL REFERENCES report_templates(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    frequency TEXT NOT NULL CHECK (frequency IN ('daily', 'weekly', 'monthly')),
    schedule_time TIME NOT NULL,
    day_of_week SMALLINT CHECK (day_of_week BETWEEN 0 AND 6),
    day_of_month SMALLINT CHECK (day_of_month BETWEEN 1 AND 28),
    recipients JSONB NOT NULL DEFAULT '[]'::jsonb,
    export_format TEXT NOT NULL DEFAULT 'xlsx' CHECK (export_format IN ('xlsx', 'csv', 'pdf')),
    no_data_behavior TEXT NOT NULL DEFAULT 'send_empty' CHECK (no_data_behavior IN ('send_empty', 'skip_delivery')),
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_run_at TIMESTAMPTZ,
    next_run_at TIMESTAMPTZ,
    last_status TEXT NOT NULL DEFAULT 'pending' CHECK (last_status IN ('pending', 'success', 'failed')),
    last_error TEXT,
    created_by UUID NOT NULL REFERENCES profiles(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (
        (frequency = 'weekly' AND day_of_week IS NOT NULL) OR
        (frequency != 'weekly' AND day_of_week IS NULL)
    ),
    CHECK (
        (frequency = 'monthly' AND day_of_month IS NOT NULL) OR
        (frequency != 'monthly' AND day_of_month IS NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_report_schedules_next_run ON report_schedules(next_run_at)
    WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_report_schedules_org ON report_schedules(org_id);

ALTER TABLE report_schedules ENABLE ROW LEVEL SECURITY;

CREATE POLICY report_schedules_org_isolation ON report_schedules
    FOR ALL
    USING (org_id = current_setting('app.current_org_id', true)::UUID)
    WITH CHECK (org_id = current_setting('app.current_org_id', true)::UUID);

-- 4. Create report_archives table
CREATE TABLE IF NOT EXISTS report_archives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    report_template_id UUID REFERENCES report_templates(id) ON DELETE SET NULL,
    schedule_id UUID REFERENCES report_schedules(id) ON DELETE SET NULL,
    report_type TEXT NOT NULL CHECK (report_type IN (
        'transaction_register', 'daily_reconciliation', 'period_summary',
        'custom', 'beneficiary', 'void_reprint', 'signatory_usage'
    )),
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    export_format TEXT NOT NULL CHECK (export_format IN ('xlsx', 'csv', 'pdf')),
    filters_applied JSONB NOT NULL DEFAULT '{}'::jsonb,
    record_count INTEGER NOT NULL,
    generated_by UUID REFERENCES profiles(id),
    generation_method TEXT NOT NULL CHECK (generation_method IN ('manual', 'scheduled')),
    delivery_status TEXT NOT NULL DEFAULT 'generated' CHECK (delivery_status IN ('generated', 'delivered', 'delivery_failed')),
    delivery_recipients JSONB,
    delivery_error TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_report_archives_org_date ON report_archives(org_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_report_archives_expires ON report_archives(expires_at);

ALTER TABLE report_archives ENABLE ROW LEVEL SECURITY;

CREATE POLICY report_archives_org_isolation ON report_archives
    FOR ALL
    USING (org_id = current_setting('app.current_org_id', true)::UUID)
    WITH CHECK (org_id = current_setting('app.current_org_id', true)::UUID);

-- 5. Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_report_templates_updated_at ON report_templates;
CREATE TRIGGER update_report_templates_updated_at
    BEFORE UPDATE ON report_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_report_schedules_updated_at ON report_schedules;
CREATE TRIGGER update_report_schedules_updated_at
    BEFORE UPDATE ON report_schedules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 6. Add index on submissions for report performance
CREATE INDEX IF NOT EXISTS idx_submissions_org_created ON submissions(org_id, created_at DESC);

-- 7. Seed pre-built system report templates
INSERT INTO report_templates (org_id, name, name_ar, report_type, description, config, is_system, created_by)
SELECT 
    o.id,
    'Transaction Register',
    'سجل المعاملات',
    'transaction_register',
    'Complete transaction register with date range, template, operator, branch, department, status, and customer filters.',
    '{
        "display_columns": ["reference_number", "template_name", "operator", "customer", "date", "status"],
        "key_field_display": [],
        "default_sort": "created_at_desc"
    }'::jsonb,
    true,
    (SELECT id FROM profiles WHERE org_id = o.id LIMIT 1)
FROM organizations o
ON CONFLICT DO NOTHING;

INSERT INTO report_templates (org_id, name, name_ar, report_type, description, config, is_system, created_by)
SELECT 
    o.id,
    'Daily Reconciliation',
    'التسوية اليومية',
    'daily_reconciliation',
    'Per-operator, per-branch summary for a single day showing total submissions, total amounts for financial templates, and breakdown by template type.',
    '{
        "auto_generate_time": "17:00",
        "include_zero_operators": true,
        "amount_field_tags": ["amount"]
    }'::jsonb,
    true,
    (SELECT id FROM profiles WHERE org_id = o.id LIMIT 1)
FROM organizations o
ON CONFLICT DO NOTHING;

INSERT INTO report_templates (org_id, name, name_ar, report_type, description, config, is_system, created_by)
SELECT 
    o.id,
    'Period Summary',
    'ملخص الفترة',
    'period_summary',
    'Aggregate totals for configurable date ranges grouped by department, branch, template, or operator with period-over-period comparison.',
    '{
        "periods": ["week", "month", "quarter", "year"],
        "groupings": ["department", "branch", "template", "operator"],
        "show_comparison": true,
        "chart_type": "bar"
    }'::jsonb,
    true,
    (SELECT id FROM profiles WHERE org_id = o.id LIMIT 1)
FROM organizations o
ON CONFLICT DO NOTHING;

INSERT INTO report_templates (org_id, name, name_ar, report_type, description, config, is_system, created_by)
SELECT 
    o.id,
    'Beneficiary Report',
    'تقرير المستفيدين',
    'beneficiary',
    'All transactions grouped by beneficiary with totals for fraud monitoring and financial authorization tracking.',
    '{}'::jsonb,
    true,
    (SELECT id FROM profiles WHERE org_id = o.id LIMIT 1)
FROM organizations o
ON CONFLICT DO NOTHING;

INSERT INTO report_templates (org_id, name, name_ar, report_type, description, config, is_system, created_by)
SELECT 
    o.id,
    'Void & Reprint Register',
    'سجل الإلغاء وإعادة الطباعة',
    'void_reprint',
    'Tracks voided and reprinted submissions with warning indicators for operational audit.',
    '{}'::jsonb,
    true,
    (SELECT id FROM profiles WHERE org_id = o.id LIMIT 1)
FROM organizations o
ON CONFLICT DO NOTHING;

INSERT INTO report_templates (org_id, name, name_ar, report_type, description, config, is_system, created_by)
SELECT 
    o.id,
    'Signatory Usage Report',
    'تقرير استخدام الموقعين',
    'signatory_usage',
    'Signatory usage tracking with alerts for approaching authority limits.',
    '{}'::jsonb,
    true,
    (SELECT id FROM profiles WHERE org_id = o.id LIMIT 1)
FROM organizations o
ON CONFLICT DO NOTHING;
