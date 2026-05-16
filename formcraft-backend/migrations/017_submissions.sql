-- Submissions table for Form Filler
-- Feature 016: form-filler

CREATE TABLE submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    template_version INT NOT NULL,
    operator_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    field_values JSONB NOT NULL DEFAULT '{}',
    reference_number TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (reference_number)
);

CREATE INDEX idx_submissions_operator ON submissions(operator_id, created_at DESC);
CREATE INDEX idx_submissions_template ON submissions(template_id);
CREATE INDEX idx_submissions_org ON submissions(org_id);
CREATE INDEX idx_submissions_ref ON submissions(reference_number);

ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Operators can view org submissions"
ON submissions FOR SELECT
USING (org_id IN (SELECT org_id FROM profiles WHERE id = auth.uid()));

CREATE POLICY "Operators can create own submissions"
ON submissions FOR INSERT
WITH CHECK (operator_id = auth.uid());

-- Reference number generation function
CREATE OR REPLACE FUNCTION generate_submission_ref(p_org_id UUID)
RETURNS TEXT AS $$
DECLARE
    seq_name TEXT;
    next_val INT;
    ref_text TEXT;
    month_year TEXT;
BEGIN
    month_year := to_char(now(), 'YYYY-MM');
    seq_name := 'submission_seq_' || replace(cast(p_org_id AS TEXT), '-', '_') || '_' || month_year;

    IF NOT EXISTS (SELECT 1 FROM pg_sequences WHERE sequencename = seq_name) THEN
        EXECUTE format('CREATE SEQUENCE %I START WITH 1 INCREMENT BY 1', seq_name);
    END IF;

    EXECUTE format('SELECT nextval(%L)', seq_name) INTO next_val;
    ref_text := 'FC-' || month_year || '-' || lpad(cast(next_val AS TEXT), 4, '0');

    RETURN ref_text;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;