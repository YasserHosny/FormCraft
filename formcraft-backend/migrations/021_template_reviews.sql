-- Feature 018: Template Versioning & Cloning
-- Create template_reviews table

CREATE TABLE template_reviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
  reviewer_id UUID NOT NULL REFERENCES auth.users(id),
  action TEXT NOT NULL CHECK (action IN ('approved', 'rejected')),
  comment TEXT,
  org_id UUID NOT NULL REFERENCES organizations(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT rejected_requires_comment CHECK (
    action != 'rejected' OR comment IS NOT NULL
  )
);

CREATE INDEX idx_template_reviews_template ON template_reviews(template_id, created_at DESC);

ALTER TABLE template_reviews ENABLE ROW LEVEL SECURITY;

CREATE POLICY template_reviews_org_isolation ON template_reviews
  USING (org_id IN (SELECT org_id FROM profiles WHERE id = auth.uid()));

COMMENT ON TABLE template_reviews IS
  'Review actions (approve/reject) on templates during the review workflow.';