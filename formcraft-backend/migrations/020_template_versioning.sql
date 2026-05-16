-- Feature 018: Template Versioning & Cloning
-- Add lineage columns, expand status CHECK, add indexes

-- Step 1: Drop existing CHECK constraint on status
ALTER TABLE templates
DROP CONSTRAINT IF EXISTS templates_status_check;

-- Step 2: Add expanded status CHECK
ALTER TABLE templates
ADD CONSTRAINT templates_status_check
CHECK (status IN ('draft', 'submitted_for_review', 'approved', 'rejected', 'published', 'archived', 'deprecated'));

-- Step 3: Add lineage tracking columns
ALTER TABLE templates
ADD COLUMN IF NOT EXISTS lineage_id UUID,
ADD COLUMN IF NOT EXISTS parent_version_id UUID REFERENCES templates(id);

-- Step 4: Backfill lineage_id for existing templates
UPDATE templates SET lineage_id = id WHERE lineage_id IS NULL;

-- Step 5: Make lineage_id NOT NULL after backfill
ALTER TABLE templates
ALTER COLUMN lineage_id SET NOT NULL;

-- Step 6: Add index for version history queries
CREATE INDEX IF NOT EXISTS idx_templates_lineage ON templates(lineage_id, version DESC);

-- Step 7: Add index for Form Desk latest-version lookup
CREATE INDEX IF NOT EXISTS idx_templates_lineage_published ON templates(lineage_id, version DESC)
WHERE status = 'published';

COMMENT ON COLUMN templates.lineage_id IS
  'Groups all versions of the same template. Root templates have lineage_id = id.';
COMMENT ON COLUMN templates.parent_version_id IS
  'The template row this version was cloned/versioned from. NULL for root templates and independent clones.';