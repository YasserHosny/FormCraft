-- ============================================================
-- Feature 013: Feedback Rich Media
-- Depends on: 008_create_feedback_submissions.sql (feature 011)
-- ============================================================

-- 1. Create feedback_images table
CREATE TABLE feedback_images (
    id            UUID       PRIMARY KEY DEFAULT gen_random_uuid(),
    feedback_id   UUID       NOT NULL REFERENCES feedback_submissions(id) ON DELETE CASCADE,
    storage_path  TEXT       NOT NULL,
    display_order SMALLINT   NOT NULL DEFAULT 0,
    uploaded_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_feedback_images_submission
    ON feedback_images (feedback_id, display_order ASC);

-- RLS
ALTER TABLE feedback_images ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Submitters can insert own feedback images"
    ON feedback_images FOR INSERT
    WITH CHECK (
        auth.uid() = (
            SELECT user_id FROM feedback_submissions WHERE id = feedback_id
        )
    );

CREATE POLICY "Admins can select feedback images"
    ON feedback_images FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid() AND profiles.role = 'admin'
        )
    );

CREATE POLICY "Owners and admins can delete feedback images"
    ON feedback_images FOR DELETE
    USING (
        auth.uid() = (
            SELECT user_id FROM feedback_submissions WHERE id = feedback_id
        )
        OR EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid() AND profiles.role = 'admin'
        )
    );

-- 2. Add video_url to feedback_submissions
ALTER TABLE feedback_submissions ADD COLUMN video_url TEXT;

-- 3. Backfill: migrate existing image_url rows to feedback_images
INSERT INTO feedback_images (feedback_id, storage_path, display_order, uploaded_at)
SELECT id, image_url, 0, submitted_at
FROM feedback_submissions
WHERE image_url IS NOT NULL;

-- 4. Drop the now-replaced image_url column
ALTER TABLE feedback_submissions DROP COLUMN image_url;
