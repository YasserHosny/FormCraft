# Data Model: New Element Types (Signature & Table)

**Date**: 2026-05-17

## Schema Changes

### Modified: `elements` table — type CHECK constraint expansion

**Migration file**: `023_new_element_types.sql`

```sql
-- Expand element type CHECK to include signature and table
ALTER TABLE elements
DROP CONSTRAINT IF EXISTS elements_type_check;

ALTER TABLE elements
ADD CONSTRAINT elements_type_check
CHECK (type IN (
  'text', 'number', 'date', 'checkbox', 'radio', 'dropdown',
  'textarea', 'image', 'label', 'barcode', 'qr_code',
  'signature', 'table'
));
```

### Element `properties` JSONB Structures

#### Signature Element Properties

```json
{
  "type": "signature",
  "properties": {
    "label_ar": "التوقيع",
    "label_en": "Signature",
    "required": true,
    "width_mm": 60,
    "height_mm": 25,
    "pen_color": "#000000",
    "background_color": "transparent"
  }
}
```

#### Table Element Properties

```json
{
  "type": "table",
  "properties": {
    "label_ar": "جدول المصروفات",
    "label_en": "Expense Table",
    "required": true,
    "min_rows": 1,
    "max_rows": 20,
    "columns": [
      {
        "key": "description",
        "header_ar": "الوصف",
        "header_en": "Description",
        "type": "text",
        "width_mm": 50,
        "auto_sum": false
      },
      {
        "key": "amount",
        "header_ar": "المبلغ",
        "header_en": "Amount",
        "type": "number",
        "width_mm": 30,
        "auto_sum": true
      },
      {
        "key": "date",
        "header_ar": "التاريخ",
        "header_en": "Date",
        "type": "date",
        "width_mm": 30,
        "auto_sum": false
      }
    ],
    "show_header": true,
    "show_borders": true,
    "show_footer": true
  }
}
```

### Submission Data Storage

#### Signature Value in Submission

```json
{
  "signature_field": {
    "type": "inline",
    "data": "data:image/png;base64,iVBORw0KGgo..."
  }
}
```

Or for large signatures (>100KB):
```json
{
  "signature_field": {
    "type": "storage",
    "path": "signatures/org_id/submission_id/signature_field.png"
  }
}
```

#### Table Value in Submission

```json
{
  "expense_table": [
    { "description": "Office supplies", "amount": 150.00, "date": "2026-05-01" },
    { "description": "Travel", "amount": 2500.00, "date": "2026-05-10" }
  ]
}
```

## Entity Relationships

```
elements (MODIFIED — type CHECK expanded)
├── type: 'signature' | 'table' (new values)
├── properties (JSONB) — signature: {label, required, width_mm, height_mm, pen_color, background_color}
│                       — table: {label, required, min_rows, max_rows, columns[], show_header, show_borders, show_footer}
└── formatting (JSONB) — unchanged

submissions.data (JSONB)
├── [signature_element_key]: { type: "inline"|"storage", data|path }
└── [table_element_key]: [ { col_key: value, ... }, ... ]
```

## Validation Rules

| Rule | Enforced At | Error |
|------|-------------|-------|
| Signature dimensions > 0 mm | API (Pydantic) | 422 "Invalid dimensions" |
| Table must have ≥1 column | API (Pydantic) | 422 "At least one column required" |
| Table column keys must be unique | API (Pydantic) | 422 "Duplicate column key" |
| Table column type must be text/number/date | API (Pydantic) | 422 "Invalid column type" |
| min_rows ≥ 0, max_rows ≥ min_rows | API (Pydantic) | 422 "Invalid row constraints" |
| Signature required: data must be non-null on submit | Form Filler + API | 422 "Signature required" |
| Table required: at least min_rows non-empty rows on submit | Form Filler + API | 422 "Minimum N rows required" |
| Signature PNG must be valid base64 image | API service | 422 "Invalid signature data" |

## Data Volume Impact

- No new tables created — only CHECK constraint expansion
- Signature data: 20-50KB per signature in submission JSONB (inline) or Supabase Storage
- Table data: ~100-500 bytes per row in submission JSONB
- Storage bucket `signatures/` created for overflow (rare)
- No additional indexes needed
