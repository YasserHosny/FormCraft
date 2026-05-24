-- Migration 030: Approval Workflow
-- Feature: 028-approval-workflow
-- Date: 2026-05-24

-- Add element_comments column to template_reviews for element-level feedback
ALTER TABLE template_reviews
ADD COLUMN IF NOT EXISTS element_comments JSONB DEFAULT NULL;

-- Create department_default_reviewers table for default reviewer assignments
CREATE TABLE IF NOT EXISTS department_default_reviewers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    department_id UUID NOT NULL REFERENCES departments(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (department_id)
);

-- Enable RLS on department_default_reviewers
ALTER TABLE department_default_reviewers ENABLE ROW LEVEL SECURITY;

-- RLS policy: users can only see records from their org
CREATE POLICY department_default_reviewers_org_isolation ON department_default_reviewers
    FOR ALL
    USING (org_id = current_setting('app.current_org_id', true)::UUID)
    WITH CHECK (org_id = current_setting('app.current_org_id', true)::UUID);

-- Composite index for review queue performance
CREATE INDEX IF NOT EXISTS idx_templates_org_status ON templates(org_id, status);

-- Index for review queue date filtering
CREATE INDEX IF NOT EXISTS idx_template_reviews_org_created ON template_reviews(org_id, created_at);
