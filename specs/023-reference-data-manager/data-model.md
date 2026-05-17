# Data Model: Reference Data Manager

**Date**: 2026-05-17

## Schema Changes

### New Table: `reference_lists`

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | NO | PK, default gen_random_uuid() |
| name_ar | TEXT | NO | Arabic display name |
| name_en | TEXT | NO | English display name |
| description | TEXT | YES | Optional description of list purpose |
| schema | JSONB | NO | Column definitions array |
| is_archived | BOOLEAN | NO | Default false. Archived lists hidden from binding picker |
| org_id | UUID | NO | FK → organizations(id), RLS scope |
| created_by | UUID | NO | FK → auth.users(id) |
| created_at | TIMESTAMPTZ | NO | Default now() |
| updated_at | TIMESTAMPTZ | NO | Default now() |

**Schema JSONB structure**:
```json
[
  {
    "key": "code",
    "label_ar": "الكود",
    "label_en": "Code",
    "type": "text",
    "required": true,
    "is_unique_key": true,
    "is_hidden": false,
    "options": null
  },
  {
    "key": "name_ar",
    "label_ar": "الاسم بالعربي",
    "label_en": "Arabic Name",
    "type": "text",
    "required": true,
    "is_unique_key": false,
    "is_hidden": false,
    "options": null
  },
  {
    "key": "category",
    "label_ar": "التصنيف",
    "label_en": "Category",
    "type": "dropdown",
    "required": false,
    "is_unique_key": false,
    "is_hidden": false,
    "options": ["public", "private", "investment"]
  }
]

**Column removal policy**: Columns are never physically removed from the schema array. When an admin "removes" a column, `is_hidden` is set to `true`. Hidden columns are excluded from entry forms and display grids but their existing values are preserved in entry JSONB.
```

### New Table: `reference_entries`

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | NO | PK, default gen_random_uuid() |
| list_id | UUID | NO | FK → reference_lists(id) ON DELETE CASCADE |
| values | JSONB | NO | Entry values keyed by column key |
| is_active | BOOLEAN | NO | Default true. Inactive entries excluded from Form Desk |
| org_id | UUID | NO | FK → organizations(id), RLS scope |
| created_by | UUID | NO | FK → auth.users(id) |
| created_at | TIMESTAMPTZ | NO | Default now() |
| updated_at | TIMESTAMPTZ | NO | Default now() |

**Values JSONB structure** (matches schema keys):
```json
{
  "code": "NBE",
  "name_ar": "البنك الأهلي المصري",
  "name_en": "National Bank of Egypt",
  "swift": "NBEGEGCX",
  "category": "public"
}
```

### Modified: Element `formatting` JSONB (no DDL change)

When an element of type `dropdown` is bound to a reference list, its `formatting` column includes:
```json
{
  "ref_binding": {
    "list_id": "uuid-of-reference-list",
    "display_column": "name_ar",
    "value_column": "code",
    "search_threshold": 20,
    "clear_on_deselect": false,
    "auto_fill": [
      {
        "target_element_key": "bank_swift",
        "source_column": "swift"
      },
      {
        "target_element_key": "bank_name_en",
        "source_column": "name_en"
      }
    ]
  }
}
```

## Migration

**Migration file**: `026_reference_data.sql`

```sql
-- Reference Lists table
CREATE TABLE reference_lists (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name_ar TEXT NOT NULL,
  name_en TEXT NOT NULL,
  description TEXT,
  schema JSONB NOT NULL DEFAULT '[]'::JSONB,
  is_archived BOOLEAN NOT NULL DEFAULT false,
  org_id UUID NOT NULL REFERENCES organizations(id),
  created_by UUID NOT NULL REFERENCES auth.users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_reference_lists_org ON reference_lists(org_id);
CREATE INDEX idx_reference_lists_org_active ON reference_lists(org_id)
  WHERE is_archived = false;

ALTER TABLE reference_lists ENABLE ROW LEVEL SECURITY;

CREATE POLICY reference_lists_org_isolation ON reference_lists
  USING (org_id = current_setting('app.current_org_id')::UUID);

-- Reference Entries table
CREATE TABLE reference_entries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  list_id UUID NOT NULL REFERENCES reference_lists(id) ON DELETE CASCADE,
  values JSONB NOT NULL DEFAULT '{}'::JSONB,
  is_active BOOLEAN NOT NULL DEFAULT true,
  org_id UUID NOT NULL REFERENCES organizations(id),
  created_by UUID NOT NULL REFERENCES auth.users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_reference_entries_list ON reference_entries(list_id);
CREATE INDEX idx_reference_entries_list_active ON reference_entries(list_id)
  WHERE is_active = true;
CREATE INDEX idx_reference_entries_org ON reference_entries(org_id);

ALTER TABLE reference_entries ENABLE ROW LEVEL SECURITY;

CREATE POLICY reference_entries_org_isolation ON reference_entries
  USING (org_id = current_setting('app.current_org_id')::UUID);

-- Comments
COMMENT ON TABLE reference_lists IS
  'Centrally managed reference data lists with typed column schemas.';
COMMENT ON COLUMN reference_lists.schema IS
  'JSONB array of column definitions: [{key, label_ar, label_en, type, required, is_unique_key, options}]';
COMMENT ON TABLE reference_entries IS
  'Individual entries within a reference list. Values keyed by column key from parent list schema.';
COMMENT ON COLUMN reference_entries.is_active IS
  'Inactive entries preserved for historical submissions but excluded from form dropdowns.';
```

## Entity Relationships

```
reference_lists
├── id (UUID PK)
├── name_ar (TEXT)
├── name_en (TEXT)
├── description (TEXT)
├── schema (JSONB) — column definitions
├── is_archived (BOOLEAN)
├── org_id (UUID FK → organizations)
├── created_by (UUID FK → auth.users)
├── created_at (TIMESTAMPTZ)
└── updated_at (TIMESTAMPTZ)
     │
     │ 1:N
     ▼
reference_entries
├── id (UUID PK)
├── list_id (UUID FK → reference_lists)
├── values (JSONB) — keyed by schema column keys
├── is_active (BOOLEAN)
├── org_id (UUID FK → organizations)
├── created_by (UUID FK → auth.users)
├── created_at (TIMESTAMPTZ)
└── updated_at (TIMESTAMPTZ)

Binding (no FK, stored in element.formatting.ref_binding.list_id):
  elements.formatting.ref_binding.list_id ──references──> reference_lists.id
  elements.formatting.ref_binding.auto_fill[].target_element_key ──references──> elements.key (same template)
```

## Validation Rules

| Rule | Enforced At | Error |
|------|-------------|-------|
| List name_ar and name_en required, non-empty | API + DB NOT NULL | 422 "Name required" |
| Schema must have ≥1 column | API (Pydantic) | 422 "At least one column required" |
| Column keys must be unique within schema | API (Pydantic) | 422 "Duplicate column key" |
| Column type must be one of: text, number, date, dropdown | API (Pydantic) | 422 "Invalid column type" |
| Dropdown column type requires non-empty options array | API (Pydantic) | 422 "Options required for dropdown type" |
| Entry values must match schema: required columns present, types coerced | API (dynamic validation) | 422 per-field errors |
| Cannot delete list bound to existing elements | API service | 409 "List is bound to N elements" |
| reference_lists scoped by org_id | RLS | Row not visible |
| reference_entries scoped by org_id | RLS | Row not visible |
| Unique key column: no duplicate values within active entries of same list | API service | 409 "Duplicate value for unique key" |

## Data Volume Impact

- reference_lists: Low volume (10-50 per org typically)
- reference_entries: Medium volume (10-5,000 per list). JSONB values indexed for GIN if search needed later
- Partial index `idx_reference_entries_list_active` keeps Form Desk queries fast (only active entries)
- No impact on existing tables (binding stored in element formatting JSONB, no DDL change)
- Cache invalidation on entry changes prevents stale Form Desk data
