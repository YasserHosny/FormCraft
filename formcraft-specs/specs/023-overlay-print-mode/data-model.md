# Data Model: Overlay Print Mode

**Date**: 2026-05-17

## Schema Changes

### New Table: `template_print_settings`

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | NO | PK, default gen_random_uuid() |
| template_id | UUID | NO | FK → templates(id), UNIQUE |
| print_mode | TEXT | NO | 'full', 'overlay', 'both'. Default 'full' |
| org_id | UUID | NO | FK → organizations(id), RLS scope |
| created_at | TIMESTAMPTZ | NO | Default now() |
| updated_at | TIMESTAMPTZ | NO | Default now() |

### New Table: `printer_profiles`

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | NO | PK, default gen_random_uuid() |
| name | TEXT | NO | Display name (e.g., "HP LaserJet Tray 2") |
| description | TEXT | YES | Optional description |
| x_offset_mm | NUMERIC(5,1) | NO | Horizontal offset in mm. Default 0.0 |
| y_offset_mm | NUMERIC(5,1) | NO | Vertical offset in mm. Default 0.0 |
| is_default | BOOLEAN | NO | Default false. One default per org (partial unique index) |
| is_active | BOOLEAN | NO | Default true. False = soft-deleted |
| org_id | UUID | NO | FK → organizations(id), RLS scope |
| created_by | UUID | NO | FK → auth.users(id) |
| created_at | TIMESTAMPTZ | NO | Default now() |
| updated_at | TIMESTAMPTZ | NO | Default now() |

### Modified Table: `elements`

| Column | Type | Change | Notes |
|--------|------|--------|-------|
| include_in_overlay | BOOLEAN | ADD | Default varies by type: true for data-bearing, false for decorative |

**Migration file**: `025_overlay_print_mode.sql`

```sql
-- Template print settings
CREATE TABLE template_print_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
  print_mode TEXT NOT NULL DEFAULT 'full' CHECK (print_mode IN ('full', 'overlay', 'both')),
  org_id UUID NOT NULL REFERENCES organizations(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (template_id)
);

ALTER TABLE template_print_settings ENABLE ROW LEVEL SECURITY;
CREATE POLICY template_print_settings_org_isolation ON template_print_settings
  USING (org_id = current_setting('app.current_org_id')::UUID);

-- Printer profiles
CREATE TABLE printer_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  x_offset_mm NUMERIC(5,1) NOT NULL DEFAULT 0.0,
  y_offset_mm NUMERIC(5,1) NOT NULL DEFAULT 0.0,
  is_default BOOLEAN NOT NULL DEFAULT false,
  is_active BOOLEAN NOT NULL DEFAULT true,
  org_id UUID NOT NULL REFERENCES organizations(id),
  created_by UUID NOT NULL REFERENCES auth.users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Only one default printer per org
CREATE UNIQUE INDEX idx_printer_profiles_default_per_org
  ON printer_profiles(org_id) WHERE is_default = true AND is_active = true;

CREATE INDEX idx_printer_profiles_org ON printer_profiles(org_id);

ALTER TABLE printer_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY printer_profiles_org_isolation ON printer_profiles
  USING (org_id = current_setting('app.current_org_id')::UUID);

-- Add include_in_overlay to elements
ALTER TABLE elements
ADD COLUMN include_in_overlay BOOLEAN NOT NULL DEFAULT true;

COMMENT ON TABLE template_print_settings IS
  'Per-template print mode configuration: full, overlay, or both.';
COMMENT ON TABLE printer_profiles IS
  'Printer calibration profiles with X/Y offset for overlay print alignment.';
COMMENT ON COLUMN printer_profiles.x_offset_mm IS
  'Horizontal offset applied to all element positions in overlay mode. Positive = shift right.';
COMMENT ON COLUMN printer_profiles.y_offset_mm IS
  'Vertical offset applied to all element positions in overlay mode. Positive = shift down.';
COMMENT ON COLUMN elements.include_in_overlay IS
  'Whether this element appears in overlay PDF mode. Default true for data elements, false for decorative.';
```

## Entity Relationships

```
template_print_settings (NEW)
├── id (UUID PK)
├── template_id (UUID FK → templates, UNIQUE)
├── print_mode (TEXT: full|overlay|both)
├── org_id (UUID FK → organizations)
├── created_at (TIMESTAMPTZ)
└── updated_at (TIMESTAMPTZ)

printer_profiles (NEW)
├── id (UUID PK)
├── name (TEXT)
├── description (TEXT, nullable)
├── x_offset_mm (NUMERIC(5,1))
├── y_offset_mm (NUMERIC(5,1))
├── is_default (BOOLEAN)
├── is_active (BOOLEAN)
├── org_id (UUID FK → organizations)
├── created_by (UUID FK → auth.users)
├── created_at (TIMESTAMPTZ)
└── updated_at (TIMESTAMPTZ)

elements (MODIFIED)
└── include_in_overlay (BOOLEAN, default true)

Relationships:
  template_print_settings.template_id → templates.id (1:1)
  printer_profiles.org_id → organizations.id (N:1)
  
PDF generation uses:
  template_print_settings.print_mode → determines rendering path
  elements[].include_in_overlay → filters elements in overlay mode
  printer_profiles.x_offset_mm/y_offset_mm → shifts positions
```

## Validation Rules

| Rule | Enforced At | Error |
|------|-------------|-------|
| print_mode must be full/overlay/both | DB CHECK + API | 422 "Invalid print mode" |
| x_offset_mm range: -50.0 to +50.0 | API (Pydantic) | 422 "Offset out of range" |
| y_offset_mm range: -50.0 to +50.0 | API (Pydantic) | 422 "Offset out of range" |
| Only one is_default=true per org | DB partial unique index | 409 "Default profile already exists" |
| Printer profile name non-empty | API + DB NOT NULL | 422 "Name required" |
| template_print_settings unique per template | DB UNIQUE | 409 "Settings already exist" |
| All tables scoped by org_id | RLS | Row not visible |

## Data Volume Impact

- template_print_settings: 1 row per template — negligible
- printer_profiles: 1-5 per org — negligible
- include_in_overlay: 1 boolean per element row — negligible storage
- No impact on query performance (boolean filter in overlay generation is in-memory)
