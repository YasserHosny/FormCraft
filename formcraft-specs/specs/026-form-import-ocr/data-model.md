# Data Model: Form Import & OCR Detection

**Date**: 2026-05-23
**Feature**: 026-form-import-ocr

## Entities

### FormDetection

Stores the results of a single OCR import operation for one template page.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique detection batch identifier |
| template_id | UUID | FK → templates(id), NOT NULL, ON DELETE CASCADE | Parent template |
| page_index | INT | NOT NULL, DEFAULT 0, CHECK >= 0 | Zero-indexed page number within template |
| detected_fields | JSONB | NOT NULL, DEFAULT '[]' | Array of DetectedField objects |
| page_dimensions | JSONB | nullable | Page dimensions in mm: `{width, height}` |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Import timestamp |

**Indexes**:
- `idx_form_detections_template_id` on `template_id` — fast lookup by template
- `idx_form_detections_created_at` on `created_at` — cleanup/ordering queries

**RLS Policies**:
- Admins: full CRUD on all detections
- Designers: full CRUD on detections for templates they created

### DetectedField (JSONB structure within detected_fields array)

| Field | Type | Description |
|-------|------|-------------|
| text | string | Recognized text content from OCR |
| bbox | object | Bounding box in mm: `{x, y, width, height}` |
| confidence | float (0.0-1.0) | OCR confidence score |
| suggested_type | enum | One of: `date`, `currency`, `text`, `number`, `signature`, `checkbox`, `unknown` |
| status | enum | Review status: `pending`, `accepted`, `rejected` |

### Relationships

```
templates (1) ──── (N) form_detections
    │                       │
    │                       └── detected_fields [JSONB array]
    │                              └── DetectedField objects
    │
    └── pages (1) ──── (N) elements
                              ↑
                    Created from accepted detections
```

### State Transitions

```
DetectedField.status:

  [OCR Import] → pending
                    │
                    ├── [Accept] → accepted → element created in elements table
                    │
                    └── [Reject] → rejected → no element created
```

### Existing Entities Modified

**pages** — No schema changes. The `background_asset` field (already exists) is populated with the uploaded form image URL during import.

**elements** — No schema changes. New elements are created via existing `add_element` API when detections are accepted. Element data (type, position, dimensions) comes from the detection's bbox and suggested_type.

## Migration

Migration file: `028_form_detections.sql` (based on existing `formcraft-specs/migrations/008_form_detections.sql`)

The migration creates:
1. `form_detections` table with columns above
2. Indexes for template_id and created_at
3. RLS policies for admin and designer access
4. Grants for authenticated users
