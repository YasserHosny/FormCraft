-- Create feedback_submissions table
CREATE TABLE feedback_submissions (
    id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    page_url     TEXT        NOT NULL,
    text_content TEXT        NOT NULL CHECK (char_length(text_content) BETWEEN 1 AND 2000),
    image_url    TEXT,
    audio_url    TEXT,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status       TEXT        NOT NULL DEFAULT 'new'
                             CHECK (status IN ('new', 'reviewed', 'resolved'))
);

-- Indexes
CREATE INDEX idx_feedback_user_time ON feedback_submissions (user_id, submitted_at DESC);
CREATE INDEX idx_feedback_time      ON feedback_submissions (submitted_at DESC);
CREATE INDEX idx_feedback_status    ON feedback_submissions (status);

-- RLS
ALTER TABLE feedback_submissions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can insert own feedback"
    ON feedback_submissions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Admins can read all feedback"
    ON feedback_submissions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
              AND profiles.role = 'admin'
        )
    );

CREATE POLICY "Admins can update feedback status"
    ON feedback_submissions FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
              AND profiles.role = 'admin'
        )
    )
    WITH CHECK (true);