-- Add status column to submissions table
-- Feature 017: submission-history

ALTER TABLE submissions
ADD COLUMN status TEXT NOT NULL DEFAULT 'printed'
CHECK (status IN ('printed', 'submitted'));

COMMENT ON COLUMN submissions.status IS
  'Whether the form was printed or submitted digitally.';