# Data Model: Operator Dashboard

**Date**: 2026-05-16

## Schema Changes

### New Table: `operator_pins`

| Column | Type | Nullable | Default | Constraint |
|--------|------|----------|---------|------------|
| id | UUID | NOT NULL | gen_random_uuid() | PRIMARY KEY |
| operator_id | UUID | NOT NULL | — | FK → auth.users(id) ON DELETE CASCADE |
| template_id | UUID | NOT NULL | — | FK → templates(id) ON DELETE CASCADE |
| org_id | UUID | NOT NULL | — | FK → organizations(id) ON DELETE CASCADE |
| created_at | TIMESTAMPTZ | NOT NULL | now() | — |

**Constraints**:
- UNIQUE (operator_id, template_id)
- INDEX on operator_id (query pattern: "all pins for this operator")

**RLS Policy**:
- Users can SELECT, INSERT, DELETE their own pins (operator_id = auth.uid())
- No UPDATE needed (pins are created or deleted, never modified)

**Migration file**: `016_operator_pins.sql`

### New Table: `notification_dismissals`

| Column | Type | Nullable | Default | Constraint |
|--------|------|----------|---------|------------|
| id | UUID | NOT NULL | gen_random_uuid() | PRIMARY KEY |
| operator_id | UUID | NOT NULL | — | FK → auth.users(id) ON DELETE CASCADE |
| template_id | UUID | NOT NULL | — | FK → templates(id) ON DELETE CASCADE |
| dismissed_version | INT | NOT NULL | — | The template version that was dismissed |
| org_id | UUID | NOT NULL | — | FK → organizations(id) ON DELETE CASCADE |
| created_at | TIMESTAMPTZ | NOT NULL | now() | — |

**Constraints**:
- UNIQUE (operator_id, template_id, dismissed_version)
- INDEX on operator_id

**RLS Policy**:
- Users can SELECT, INSERT their own dismissals (operator_id = auth.uid())

**Migration file**: `016_operator_pins.sql` (same migration)

### No Modified Tables

This feature does not modify existing tables. Recently used data is derived from `submissions` table queries. Draft data will be read from a future `drafts` table (created by Form Filler feature).

## Entity Relationships

```
operator_pins (new)
├── id (UUID PK)
├── operator_id (UUID FK → auth.users)  ─── who pinned
├── template_id (UUID FK → templates)   ─── what was pinned
├── org_id (UUID FK → organizations)    ─── org isolation
└── created_at (TIMESTAMPTZ)

notification_dismissals (new)
├── id (UUID PK)
├── operator_id (UUID FK → auth.users)
├── template_id (UUID FK → templates)
├── dismissed_version (INT)             ─── which version notification was dismissed
├── org_id (UUID FK → organizations)
└── created_at (TIMESTAMPTZ)

templates (existing, read-only)
├── id (UUID PK)
├── name, description, category, status, version, language, country
└── ...

submissions (existing, read-only — for "Recently Used" derivation)
├── id (UUID PK)
├── template_id (UUID FK → templates)
├── operator_id (UUID FK → auth.users)
├── created_at (TIMESTAMPTZ)
└── ...

Dashboard query joins:
  templates ←── operator_pins (pinned status)
  templates ←── submissions (recent usage, grouped by template_id)
  templates ←── notification_dismissals (filter out dismissed notifications)
```

## Validation Rules

| Rule | Enforced At | Error |
|------|-------------|-------|
| operator_id must be authenticated user | API auth middleware | 401 Unauthorized |
| template_id must exist and be published | API service layer | 404 Not Found |
| Duplicate pin prevention | DB unique constraint + API | 409 Conflict |
| Pin limit (20 per operator) | API service layer (count check) | 422 "Pin limit reached" |
| org_id must match operator's org | RLS policy | Row not visible / insert denied |

## Data Volume Impact

- **operator_pins**: Expected rows = operators × avg pins per operator ≈ 50 × 10 = 500 rows per org. Negligible.
- **notification_dismissals**: Expected rows = operators × dismissed notifications ≈ 50 × 20 = 1,000 rows per org. Negligible. Can be periodically cleaned up for dismissed versions older than current-2.
- No impact on existing table queries — new tables only.
- No new indexes on existing tables needed.
