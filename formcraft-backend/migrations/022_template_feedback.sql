-- Template feedback table (operator → designer feedback on template elements)
-- Feature 019: Template Feedback

CREATE TABLE IF NOT EXISTS template_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    page_number INTEGER,
    element_key TEXT,
    category TEXT NOT NULL CHECK (category IN ('layout', 'readability', 'logical', 'other')),
    comment TEXT NOT NULL,
    screenshot_path TEXT,
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'acknowledged', 'resolved')),
    created_by UUID NOT NULL REFERENCES profiles(id),
    resolved_by UUID REFERENCES profiles(id),
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_template_feedback_template ON template_feedback(template_id);
CREATE INDEX IF NOT EXISTS idx_template_feedback_status ON template_feedback(status);
CREATE INDEX IF NOT EXISTS idx_template_feedback_created_by ON template_feedback(created_by);

-- RLS policies
ALTER TABLE template_feedback ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Operators can submit template feedback"
    ON template_feedback FOR INSERT
    WITH CHECK (auth.uid() = created_by AND (auth.jwt()->>'role') IN ('operator', 'admin', 'designer'));

CREATE POLICY "Users can view feedback on templates they can access"
    ON template_feedback FOR SELECT
    USING (true);

CREATE POLICY "Designers and admins can update feedback status"
    ON template_feedback FOR UPDATE
    USING ((auth.jwt()->>'role') IN ('designer', 'admin'));

-- Audit log trigger
CREATE OR REPLACE FUNCTION log_template_feedback_event() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_logs (action, resource_type, resource_id, actor_id, details)
    VALUES(
        CASE
            WHEN TG_OP = 'INSERT' THEN 'TEMPLATE_FEEDBACK_CREATED'
            WHEN TG_OP = 'UPDATE' THEN 'TEMPLATE_FEEDBACK_UPDATED'
        END,
        'template_feedback',
        COALESCE(NEW.id, OLD.id),
        COALESCE(NEW.created_by, OLD.created_by),
        jsonb_build_object(
            'template_id', COALESCE(NEW.template_id, OLD.template_id),
            'category', COALESCE(NEW.category, OLD.category),
            'status', COALESCE(NEW.status, OLD.status)
        )
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS template_feedback_audit ON template_feedback;
CREATE TRIGGER template_feedback_audit
    AFTER INSERT OR UPDATE ON template_feedback
    FOR EACH ROW EXECUTE FUNCTION log_template_feedback_event();