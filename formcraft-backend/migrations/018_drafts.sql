-- Drafts table for Form Filler
-- Feature 016: form-filler

CREATE TABLE drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    template_version INT NOT NULL,
    operator_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    field_values JSONB NOT NULL DEFAULT '{}',
    completion_percent INT NOT NULL DEFAULT 0,
    name TEXT,
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (now() + INTERVAL '7 days'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_drafts_operator ON drafts(operator_id, updated_at DESC);

ALTER TABLE drafts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Operators can manage own drafts"
ON drafts FOR ALL
USING (operator_id = auth.uid())
WITH CHECK (operator_id = auth.uid());