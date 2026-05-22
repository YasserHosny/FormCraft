# API Contracts: New Element Types (Signature & Table)

**Date**: 2026-05-17

## Overview

No new API endpoints are introduced. The signature and table elements use existing element CRUD endpoints and submission endpoints. This document specifies the element `properties` and submission `data` schemas for the new types.

## Element Creation/Update (Existing Endpoints)

### `POST /api/templates/:id/pages/:page_id/elements`

Existing endpoint — new element type values accepted.

**Signature Element Request**:
```json
{
  "type": "signature",
  "key": "applicant_signature",
  "x_mm": 20,
  "y_mm": 180,
  "width_mm": 60,
  "height_mm": 25,
  "properties": {
    "label_ar": "توقيع مقدم الطلب",
    "label_en": "Applicant Signature",
    "required": true,
    "pen_color": "#000000",
    "background_color": "transparent"
  }
}
```

**Table Element Request**:
```json
{
  "type": "table",
  "key": "expense_table",
  "x_mm": 10,
  "y_mm": 80,
  "width_mm": 190,
  "height_mm": 100,
  "properties": {
    "label_ar": "جدول المصروفات",
    "label_en": "Expense Table",
    "required": true,
    "min_rows": 1,
    "max_rows": 20,
    "columns": [
      { "key": "description", "header_ar": "الوصف", "header_en": "Description", "type": "text", "width_mm": 80, "auto_sum": false },
      { "key": "amount", "header_ar": "المبلغ", "header_en": "Amount", "type": "number", "width_mm": 50, "auto_sum": true },
      { "key": "date", "header_ar": "التاريخ", "header_en": "Date", "type": "date", "width_mm": 60, "auto_sum": false }
    ],
    "show_header": true,
    "show_borders": true,
    "show_footer": true
  }
}
```

## Submission Data (Existing Endpoint)

### `POST /api/submissions`

Existing endpoint — new data shapes for signature and table values.

**Submission with Signature**:
```json
{
  "template_id": "uuid",
  "template_version": 1,
  "data": {
    "full_name": "Ahmed Mohamed",
    "applicant_signature": {
      "type": "inline",
      "data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg..."
    }
  }
}
```

**Submission with Table**:
```json
{
  "template_id": "uuid",
  "template_version": 1,
  "data": {
    "expense_table": [
      { "description": "Office supplies", "amount": 150.00, "date": "2026-05-01" },
      { "description": "Travel", "amount": 2500.00, "date": "2026-05-10" },
      { "description": "Software license", "amount": 500.00, "date": "2026-05-15" }
    ]
  }
}
```

## Signature Upload (Large Signatures)

### `POST /api/submissions/:id/signature-upload`

Upload signature to Supabase Storage when inline would exceed 100KB.

**Auth**: Operator, Branch Manager, Admin  
**Content-Type**: multipart/form-data  
**Form Fields**:
- `file`: PNG image
- `element_key`: string

**Response 201**:
```json
{
  "type": "storage",
  "path": "signatures/org_id/submission_id/applicant_signature.png"
}
```

**Errors**: 413 "Signature file too large (max 500KB)", 422 "Invalid image format"

## PDF Generation (Existing Endpoint)

### `POST /api/submissions/:id/pdf`

Existing endpoint — new renderers handle signature and table elements automatically.

**Signature rendering**: Renders `<img>` tag with base64 data (or fetches from Storage) at element's mm position.

**Table rendering**: Renders HTML `<table>` with `<thead>`, `<tbody>`, optional `<tfoot>` (auto-sum) at element's mm position with borders and column widths.

## Validation on Submission

| Element Type | Validation | Error |
|--------------|-----------|-------|
| Signature (required) | data field must be non-null with valid PNG base64 or storage path | 422 "Signature required" |
| Signature (optional) | if provided, must be valid format | 422 "Invalid signature format" |
| Table (required) | at least min_rows rows with all required columns filled | 422 "Minimum N rows required" |
| Table row | each cell validated against column type (number must be numeric, date must be ISO) | 422 per-cell errors |
