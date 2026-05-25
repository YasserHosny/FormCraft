-- Migration 033: Template Governance
-- Feature: 031-template-governance
-- Date: 2026-05-25

-- Create template_review_comments table
CREATE TABLE IF NOT EXISTS template_review_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    template_version INTEGER NOT NULL,
    review_id UUID REFERENCES template_reviews(id) ON DELETE SET NULL,
    reviewer_id UUID NOT NULL REFERENCES profiles(id),
    created_by UUID NOT NULL REFERENCES profiles(id),
    element_id UUID REFERENCES elements(id) ON DELETE SET NULL,
    element_key TEXT,
    page_id UUID REFERENCES pages(id) ON DELETE SET NULL,
    x_mm NUMERIC(10,3),
    y_mm NUMERIC(10,3),
    comment_text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved')),
    designer_reply TEXT,
    resolved_by UUID REFERENCES profiles(id),
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create validator_change_events table
CREATE TABLE IF NOT EXISTS validator_change_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    validator_key TEXT NOT NULL,
    country TEXT,
    field_type TEXT,
    old_rule JSONB NOT NULL,
    new_rule JSONB NOT NULL,
    affected_template_count INTEGER NOT NULL DEFAULT 0,
    change_summary TEXT NOT NULL,
    effective_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_by UUID REFERENCES profiles(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for template_review_comments
CREATE INDEX IF NOT EXISTS idx_template_review_comments_template ON template_review_comments(template_id);
CREATE INDEX IF NOT EXISTS idx_template_review_comments_org ON template_review_comments(org_id);
CREATE INDEX IF NOT EXISTS idx_template_review_comments_status ON template_review_comments(status);
CREATE INDEX IF NOT EXISTS idx_template_review_comments_reviewer ON template_review_comments(reviewer_id);

-- Indexes for validator_change_events
CREATE INDEX IF NOT EXISTS idx_validator_change_events_org ON validator_change_events(org_id);
CREATE INDEX IF NOT EXISTS idx_validator_change_events_key ON validator_change_events(validator_key);
CREATE INDEX IF NOT EXISTS idx_validator_change_events_date ON validator_change_events(effective_date);

-- Enable RLS
ALTER TABLE template_review_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE validator_change_events ENABLE ROW LEVEL SECURITY;

-- RLS policies for template_review_comments
CREATE POLICY template_review_comments_org_isolation ON template_review_comments
    FOR ALL
    USING (org_id = current_setting('app.current_org_id', true)::UUID)
    WITH CHECK (org_id = current_setting('app.current_org_id', true)::UUID);

-- RLS policies for validator_change_events
CREATE POLICY validator_change_events_org_isolation ON validator_change_events
    FOR ALL
    USING (
        org_id = current_setting('app.current_org_id', true)::UUID
        OR org_id IS NULL
    )
    WITH CHECK (org_id = current_setting('app.current_org_id', true)::UUID);

-- Auto-update updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_template_review_comments_updated_at ON template_review_comments;
CREATE TRIGGER update_template_review_comments_updated_at
    BEFORE UPDATE ON template_review_comments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_validator_change_events_updated_at ON validator_change_events;
CREATE TRIGGER update_validator_change_events_updated_at
    BEFORE UPDATE ON validator_change_events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
