# Data Model: Form Filler

**Date**: 2026-05-16

## Schema Changes

### New Table: `submissions`

| Column | Type | Nullable | Default | Constraint |
|--------|------|----------|---------|------------|
| id | UUID | NOT NULL | gen_random_uuid() | PRIMARY KEY |
| template_id | UUID | NOT NULL | — | FK → templates(id) |
| template_version | INT | NOT NULL | — | Snapshot of template.version at fill time |
| operator_id | UUID | NOT NULL | — | FK → auth.users(id) |
| org_id | UUID | NOT NULL | — | FK → organizations(id) |
| field_values | JSONB | NOT NULL | '{}' | `{ "element_key": value }` map |
| reference_number | TEXT | NOT NULL | — | UNIQUE, format FC-YYYY-MM-NNNN |
| created_at | TIMESTAMPTZ | NOT NULL | now() | — |

**Indexes**:
- `idx_submissions_operator` on (operator_id, created_at DESC) — for "Recently Used" queries
- `idx_submissions_template` on (template_id) — for version notification derivation
- `idx_submissions_org` on (org_id) — for RLS performance
- `idx_submissions_ref` on (reference_number) — for reference number lookup

**RLS**:
- SELECT: org_id matches user's org (operators can see all org submissions for history/reprint)
- INSERT: operator_id = auth.uid()

**Migration file**: `017_submissions.sql`

### New Table: `drafts`

| Column | Type | Nullable | Default | Constraint |
|--------|------|----------|---------|------------|
| id | UUID | NOT NULL | gen_random_uuid() | PRIMARY KEY |
| template_id | UUID | NOT NULL | — | FK → templates(id) |
| template_version | INT | NOT NULL | — | Version at time of draft creation |
| operator_id | UUID | NOT NULL | — | FK ��� auth.users(id) ON DELETE CASCADE |
| org_id | UUID | NOT NULL | — | FK → organizations(id) |
| field_values | JSONB | NOT NULL | '{}' | Partial field values |
| completion_percent | INT | NOT NULL | 0 | Filled required fields / total required × 100 |
| name | TEXT | YES | NULL | Optional human-friendly name |
| expires_at | TIMESTAMPTZ | NOT NULL | now() + 7 days | Org-configurable expiry |
| created_at | TIMESTAMPTZ | NOT NULL | now() | — |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | Updated on every save |

**Indexes**:
- `idx_drafts_operator` on (operator_id, updated_at DESC) — for dashboard listing

**RLS**:
- ALL: operator_id = auth.uid() (operators can only see/manage their own drafts)

**Migration file**: `018_drafts.sql`

### New Function: `generate_submission_ref(org_id UUID)`

Creates per-org monthly sequences and returns formatted reference numbers (`FC-YYYY-MM-NNNN`). Uses PostgreSQL sequences for atomicity under concurrent inserts.

**Migration file**: `017_submissions.sql` (same file)

### No Modified Tables

The existing `templates`, `pages`, and `elements` tables are read-only in this feature. The PDF renderer is modified in code but not in schema.

## Entity Relationships

```
submissions (new)
├── id (UUID PK)
├── template_id (UUID FK → templates) ─── which form was filled
├── template_version (INT)             ─── exact version snapshot
├── operator_id (UUID FK → auth.users) ─── who filled it
├── org_id (UUID FK → organizations)   ─── org isolation
├── field_values (JSONB)               ─── { "key": "value" } map
├── reference_number (TEXT UNIQUE)     ─── FC-2026-05-0042
└── created_at (TIMESTAMPTZ)

drafts (new)
├── id (UUID PK)
├── template_id (UUID FK → templates)
├── template_version (INT)
├── operator_id (UUID FK → auth.users)
├── org_id (UUID FK → organizations)
├── field_values (JSONB)               ─── partial values
├── completion_percent (INT)           ─── 0-100
├── name (TEXT nullable)
├── expires_at (TIMESTAMPTZ)
├── created_at (TIMESTAMPTZ)
└── updated_at (TIMESTAMPTZ)

templates (existing, read-only)
├── pages[] → elements[]              ─── defines form structure
└── version (INT)                     ─── compared against draft.template_version

Relationships:
  submissions.template_id → templates.id (many submissions per template)
  submissions.operator_id → auth.users.id (many submissions per operator)
  drafts.template_id → templates.id (many drafts per template)
  drafts.operator_id → auth.users.id (many drafts per operator, but typically 1-3 active)
```

## Validation Rules

| Rule | Enforced At | Error |
|------|-------------|-------|
| template_id must reference a published template | API service layer | 404 "Template not found or not published" |
| field_values keys must match template element keys | API service layer | 422 "Unknown field key: X" |
| required fields must have non-empty values (on submit) | API + client | 422 "Required field missing: X" |
| validation patterns must pass (on submit) | API + client | 422 "Validation failed for field: X" |
| draft operator_id must be auth.uid() | RLS | Row not visible |
| reference_number must be unique | DB unique constraint | 500 (retry with new sequence value) |
| draft.expires_at must be in the future (on resume) | API service | 410 "Draft expired" |

## Data Volume Impact

- **submissions**: High volume — expected 50-200 per operator per day in bank environments. Index on (operator_id, created_at) supports efficient recent-template queries. Monthly partitioning could be added later if volume warrants.
- **drafts**: Low volume — typically 1-5 active drafts per operator. Expired drafts can be cleaned up via scheduled job.
- **field_values JSONB**: Typically 10-50 key-value pairs per submission. Average size: 1-5 KB. No performance concern.
- **Sequences**: One sequence created per (org, year, month). Lightweight metadata objects.

## State Transitions

```
Draft lifecycle:
  (none) ──[Save Draft / Auto-save]──> ACTIVE draft
  ACTIVE ──[Resume + fill + Print]──> DELETED (draft consumed → submission created)
  ACTIVE ──[Auto-save timer]──> ACTIVE (updated_at refreshed)
  ACTIVE ──[Operator deletes]──> DELETED
  ACTIVE ──[expires_at passes]──> EXPIRED (cannot resume)

Submission lifecycle:
  (form filled + Print clicked) ──> CREATED (immutable)
  Submissions are append-only — never updated or deleted.
```
