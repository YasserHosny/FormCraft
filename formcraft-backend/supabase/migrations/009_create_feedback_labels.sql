-- Colour palette enum values (used in CHECK constraint)
-- red, orange, yellow, green, teal, blue, purple, pink, grey, brown

CREATE TABLE feedback_labels (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT        NOT NULL UNIQUE CHECK (char_length(name) BETWEEN 1 AND 50),
    colour      TEXT        CHECK (colour IN (
                                'red','orange','yellow','green','teal',
                                'blue','purple','pink','grey','brown'
                            )),
    created_by  UUID        NOT NULL REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_feedback_labels_created_at ON feedback_labels (created_at DESC);

CREATE TABLE feedback_submission_labels (
    feedback_id  UUID NOT NULL REFERENCES feedback_submissions(id) ON DELETE CASCADE,
    label_id     UUID NOT NULL REFERENCES feedback_labels(id) ON DELETE CASCADE,
    assigned_by  UUID NOT NULL REFERENCES auth.users(id) ON DELETE SET NULL,
    assigned_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (feedback_id, label_id)
);

CREATE INDEX idx_fsl_feedback_id ON feedback_submission_labels (feedback_id);
CREATE INDEX idx_fsl_label_id    ON feedback_submission_labels (label_id);

-- RLS
ALTER TABLE feedback_labels ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback_submission_labels ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Admins can manage labels"
    ON feedback_labels FOR ALL
    USING (
        EXISTS (SELECT 1 FROM profiles WHERE profiles.id = auth.uid() AND profiles.role = 'admin')
    )
    WITH CHECK (
        EXISTS (SELECT 1 FROM profiles WHERE profiles.id = auth.uid() AND profiles.role = 'admin')
    );

CREATE POLICY "Admins can manage submission labels"
    ON feedback_submission_labels FOR ALL
    USING (
        EXISTS (SELECT 1 FROM profiles WHERE profiles.id = auth.uid() AND profiles.role = 'admin')
    )
    WITH CHECK (
        EXISTS (SELECT 1 FROM profiles WHERE profiles.id = auth.uid() AND profiles.role = 'admin')
    );