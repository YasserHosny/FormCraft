-- ============================================================
-- Feature 014: Feedback Threading & Replies
-- Depends on: 008_create_feedback_submissions.sql (feature 011)
-- ============================================================

-- 1. Add denormalised columns to feedback_submissions
ALTER TABLE feedback_submissions
    ADD COLUMN reply_count          INT     NOT NULL DEFAULT 0,
    ADD COLUMN has_unread_user_reply BOOLEAN NOT NULL DEFAULT FALSE;

-- 2. Create feedback_replies table
CREATE TABLE feedback_replies (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    feedback_id   UUID        NOT NULL REFERENCES feedback_submissions(id) ON DELETE CASCADE,
    author_id     UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    author_role   TEXT        NOT NULL CHECK (author_role IN ('admin', 'user')),
    text_content  TEXT        NOT NULL CHECK (char_length(text_content) BETWEEN 1 AND 2000),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_feedback_replies_thread
    ON feedback_replies (feedback_id, created_at DESC);

-- RLS
ALTER TABLE feedback_replies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authors can insert own replies"
    ON feedback_replies FOR INSERT
    WITH CHECK (auth.uid() = author_id);

CREATE POLICY "Submitters and admins can select replies"
    ON feedback_replies FOR SELECT
    USING (
        auth.uid() = (
            SELECT user_id FROM feedback_submissions WHERE id = feedback_id
        )
        OR EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid() AND profiles.role = 'admin'
        )
    );

-- 3. Create feedback_notifications table
CREATE TABLE feedback_notifications (
    id                 UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_user_id  UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    feedback_id        UUID        NOT NULL REFERENCES feedback_submissions(id) ON DELETE CASCADE,
    reply_id           UUID        NOT NULL REFERENCES feedback_replies(id) ON DELETE CASCADE,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    delivered_at       TIMESTAMPTZ,
    read_at            TIMESTAMPTZ
);

CREATE INDEX idx_notifications_undelivered
    ON feedback_notifications (recipient_user_id, delivered_at)
    WHERE delivered_at IS NULL;

CREATE INDEX idx_notifications_user_time
    ON feedback_notifications (recipient_user_id, created_at DESC);

-- RLS
ALTER TABLE feedback_notifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Admins can insert notifications"
    ON feedback_notifications FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid() AND profiles.role = 'admin'
        )
    );

CREATE POLICY "Recipients and admins can select notifications"
    ON feedback_notifications FOR SELECT
    USING (
        auth.uid() = recipient_user_id
        OR EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid() AND profiles.role = 'admin'
        )
    );

CREATE POLICY "Recipients can update own notifications"
    ON feedback_notifications FOR UPDATE
    USING (auth.uid() = recipient_user_id)
    WITH CHECK (auth.uid() = recipient_user_id);
