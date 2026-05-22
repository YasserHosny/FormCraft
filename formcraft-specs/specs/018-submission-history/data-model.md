# Data Model: Submission History & Reprint

**Date**: 2026-05-16

## Schema Changes

### No New Tables

This feature reads from the existing `submissions` table (created in feature 016). Reprints are tracked via audit log entries (existing audit infrastructure), not a separate table.

### Modified Table: `submissions`

| Column | Type | Change | Notes |
|--------|------|--------|-------|
| status | TEXT | ADD | Values: 'printed', 'submitted'. Default: 'printed'. Tracks whether form was printed or submitted digitally. |

**Migration file**: `019_submissions_status.sql`

```sql
ALTER TABLE submissions
ADD COLUMN status TEXT NOT NULL DEFAULT 'printed'
CHECK (status IN ('printed', 'submitted'));

COMMENT ON COLUMN submissions.status IS
  'Whether the form was printed or submitted digitally.';
```

**Coordination note**: Feature 016 creates the `submissions` table without this column. This migration (019) adds it retroactively with a default of `'printed'`, so all existing submissions from 016 are automatically correct. Feature 016's `POST /api/submissions` endpoint should be updated to accept an optional `status` field (defaulting to `'printed'`) once this migration is applied.

### No New Indexes Required

Existing indexes on submissions are sufficient:
- `idx_submissions_operator` (operator_id, created_at DESC) — history listing
- `idx_submissions_ref` (reference_number) — reference number lookup
- `idx_submissions_org` (org_id) — RLS performance

Search by template name uses a JOIN to templates table (already indexed by id).

## Entity Relationships

```
submissions (existing, minor update)
├── id (UUID PK)
├── template_id (UUID FK → templates)
├── template_version (INT)
├── operator_id (UUID FK → auth.users)
├── org_id (UUID FK → organizations)
├── field_values (JSONB)
├── reference_number (TEXT UNIQUE)
├── status (TEXT) ← NEW: 'printed' | 'submitted'
└── created_at (TIMESTAMPTZ)

audit_log (existing, used for reprint tracking)
├── id (UUID PK)
├── user_id (UUID)
├── action (TEXT) ← 'FORM_REPRINTED', 'SUBMISSION_EXPORTED'
├── resource_type (TEXT) ← 'submission'
├── resource_id (TEXT) ← submission.id
├── metadata (JSONB) ← { reference_number, template_name }
├── ip_address (TEXT)
└── created_at (TIMESTAMPTZ)

For reprints:
  submissions ──[audit_log]──> reprint events
  (no separate reprint table — audit log is the record)

For clone-as-new:
  submissions.field_values ──[loaded into Form Filler]──> new submission
  (creates a new submission with new reference_number)
```

## Validation Rules

| Rule | Enforced At | Error |
|------|-------------|-------|
| operator can only see own org submissions | RLS | Row not visible |
| submission_id must exist for detail/reprint/export | API service | 404 |
| reprint requires valid submission_id | API service | 404 |
| export format must be 'json' or 'csv' | API schema validation | 422 |

## Data Volume Impact

- Single column addition (status TEXT) — negligible migration impact
- No new tables, no new indexes
- Reprint watermark logic is in-memory (PDF rendering) — no storage impact
- Audit log grows by 1 row per reprint — negligible (< 100 reprints/day/org)
