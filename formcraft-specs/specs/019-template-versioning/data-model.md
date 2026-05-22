# Data Model: Template Versioning & Cloning

**Date**: 2026-05-16

## Schema Changes

### Modified Table: `templates`

| Column | Type | Change | Notes |
|--------|------|--------|-------|
| status | TEXT | MODIFY CHECK | Expand to: 'draft', 'submitted_for_review', 'approved', 'published', 'archived', 'deprecated' |
| lineage_id | UUID | ADD | Groups all versions of the same template family. Defaults to own ID for root templates. |
| parent_version_id | UUID | ADD | Points to the template row this version was created from. NULL for root/cloned templates. |

**Migration file**: `020_template_versioning.sql`

```sql
-- Step 1: Drop existing CHECK constraint on status
ALTER TABLE templates
DROP CONSTRAINT IF EXISTS templates_status_check;

-- Step 2: Add expanded status CHECK
ALTER TABLE templates
ADD CONSTRAINT templates_status_check
CHECK (status IN ('draft', 'submitted_for_review', 'approved', 'rejected', 'published', 'archived', 'deprecated'));

-- Step 3: Add lineage tracking columns
ALTER TABLE templates
ADD COLUMN lineage_id UUID,
ADD COLUMN parent_version_id UUID REFERENCES templates(id);

-- Step 4: Backfill lineage_id for existing templates
UPDATE templates SET lineage_id = id WHERE lineage_id IS NULL;

-- Step 5: Make lineage_id NOT NULL after backfill
ALTER TABLE templates
ALTER COLUMN lineage_id SET NOT NULL;

-- Step 6: Add index for version history queries
CREATE INDEX idx_templates_lineage ON templates(lineage_id, version DESC);

-- Step 7: Add index for Form Desk latest-version lookup
CREATE INDEX idx_templates_lineage_published ON templates(lineage_id, version DESC)
WHERE status = 'published';

COMMENT ON COLUMN templates.lineage_id IS
  'Groups all versions of the same template. Root templates have lineage_id = id.';
COMMENT ON COLUMN templates.parent_version_id IS
  'The template row this version was cloned/versioned from. NULL for root templates and independent clones.';
```

### New Table: `template_reviews`

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | NO | PK, default gen_random_uuid() |
| template_id | UUID | NO | FK → templates(id) |
| reviewer_id | UUID | NO | FK → auth.users(id) |
| action | TEXT | NO | 'approved' or 'rejected' |
| comment | TEXT | YES | Required for rejection, optional for approval |
| org_id | UUID | NO | FK → organizations(id), for RLS |
| created_at | TIMESTAMPTZ | NO | Default now() |

**Migration file**: `021_template_reviews.sql`

```sql
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

-- RLS policy: users can only see reviews for their org
ALTER TABLE template_reviews ENABLE ROW LEVEL SECURITY;

CREATE POLICY template_reviews_org_isolation ON template_reviews
  USING (org_id = current_setting('app.current_org_id')::UUID);

COMMENT ON TABLE template_reviews IS
  'Review actions (approve/reject) on templates during the review workflow.';
```

## Entity Relationships

```
templates (modified)
├── id (UUID PK)
├── name (TEXT)
├── description (TEXT)
├── category (TEXT)
├── status (TEXT) ← EXPANDED: draft|submitted_for_review|approved|rejected|published|archived|deprecated
├── version (INT)
├── lineage_id (UUID) ← NEW: links all versions in a family
├── parent_version_id (UUID FK → templates) ← NEW: direct parent
├── language (TEXT)
├── country (TEXT)
├── created_by (UUID FK → auth.users)
├── org_id (UUID FK → organizations)
├── created_at (TIMESTAMPTZ)
└── updated_at (TIMESTAMPTZ)

template_reviews (NEW)
├── id (UUID PK)
├── template_id (UUID FK → templates)
├── reviewer_id (UUID FK → auth.users)
├── action (TEXT: 'approved'|'rejected')
├── comment (TEXT, required if rejected)
├── org_id (UUID FK → organizations)
└── created_at (TIMESTAMPTZ)

Lineage graph:
  templates(lineage_id=L) ──[version 1]──> templates(lineage_id=L, version=2, parent_version_id=v1.id)
                                                     └──> templates(lineage_id=L, version=3, parent_version_id=v2.id)

Clone creates independent tree:
  templates(id=A) ──[clone]──> templates(id=B, lineage_id=B, parent_version_id=NULL)

For version diff:
  templates(lineage_id=L, version=1).elements
  vs.
  templates(lineage_id=L, version=2).elements
  → matched by element.key → diff computed on-demand
```

## Validation Rules

| Rule | Enforced At | Error |
|------|-------------|-------|
| Status transitions must follow allowed map | API service | 422 "Invalid status transition" |
| Only published templates can be versioned | API service | 400 "Only published templates can be versioned" |
| Rejection requires non-empty comment | DB CHECK + API | 422 "Rejection comment required" |
| Published templates cannot be edited | API service (edit endpoints) | 403 "Published templates are immutable" |
| Only admin/branch_manager can approve/publish | API service (role check) | 403 "Insufficient role" |
| Only designer/admin can submit for review | API service (role check) | 403 "Insufficient role" |
| lineage_id cannot be changed after creation | API service | 400 "Lineage cannot be modified" |
| template_reviews scoped by org_id | RLS | Row not visible |

## Data Volume Impact

- 2 new columns on templates (UUID × 2) — negligible per row
- template_reviews: ~2-5 reviews per template version lifecycle — small table
- Partial index `idx_templates_lineage_published` keeps Form Desk queries fast
- No denormalization; diff computed on-demand
- Backfill migration touches all existing template rows once (SET lineage_id = id)
