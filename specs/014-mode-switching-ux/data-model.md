# Data Model: Mode Switching UX

**Date**: 2026-05-16

## Schema Changes

### Modified Table: `profiles`

| Column | Type | Change | Default | Constraint |
|--------|------|--------|---------|------------|
| preferred_mode | TEXT | ADD | NULL | CHECK (preferred_mode IN ('studio', 'desk', 'admin')) |

**Migration file**: `015_add_preferred_mode.sql`

```sql
ALTER TABLE profiles
ADD COLUMN preferred_mode TEXT
CHECK (preferred_mode IN ('studio', 'desk', 'admin'))
DEFAULT NULL;

COMMENT ON COLUMN profiles.preferred_mode IS
  'Last-used product mode. NULL means use role default.';
```

### No New Tables

This feature does not require new tables. The mode configuration is defined in frontend code (not database-driven) because:
- Mode definitions are static (3 modes, fixed set)
- Mode-role mapping is fixed (derived from role hierarchy)
- No admin UI to configure modes dynamically

## Entity Relationships

```
profiles (existing)
├── id (UUID PK)
├── email (TEXT)
├── role (TEXT) ──────────────┐
├── language (TEXT)           │
├── display_name (TEXT)       │  role determines which modes are visible
├── preferred_mode (TEXT) ◄───┘  must be a mode the role permits (or NULL)
└── ...other existing columns
```

## Validation Rules

| Rule | Enforced At | Error |
|------|-------------|-------|
| preferred_mode must be one of: studio, desk, admin, NULL | DB CHECK constraint + API schema | 422 Validation Error |
| preferred_mode must be accessible by user's role | API service layer | 422 "Role '{role}' does not have access to mode '{mode}'" |
| Role changes may invalidate preferred_mode | API service (on role update) | Auto-set preferred_mode to NULL if no longer valid |

## State Transitions

```
preferred_mode lifecycle:
  NULL (new user) ──[first mode switch]──> "desk" | "studio" | "admin"
  "studio" ──[click Form Desk tab]──> "desk"
  "desk" ──[click Admin tab]──> "admin"
  "admin" ──[role downgraded to operator]──> NULL (auto-reset)
```

## Data Volume Impact

- No new rows, no new tables
- One nullable TEXT column added to profiles
- Zero performance impact on existing queries
- No index needed (never queried by preferred_mode)
