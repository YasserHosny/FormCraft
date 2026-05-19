# API Contracts: Advanced Form Validation & Conditional Logic

**Date**: 2026-05-17

## Overview

No new API endpoints. Conditional logic columns are part of the existing element CRUD endpoints. The ConditionEngine operates at form submission validation time. This document specifies the extended element schema and submission behavior.

## Element Create/Update (Existing Endpoints)

### `POST /api/templates/:id/pages/:page_id/elements`
### `PATCH /api/templates/:id/pages/:page_id/elements/:element_id`

Extended element payload with new optional fields:

```json
{
  "type": "text",
  "key": "spouse_name",
  "x_mm": 20,
  "y_mm": 100,
  "width_mm": 80,
  "height_mm": 10,
  "properties": {
    "label_ar": "اسم الزوج/ة",
    "label_en": "Spouse Name",
    "required": false
  },
  "visible_when": {
    "conditions": [
      { "field": "marital_status", "operator": "equals", "value": "married" }
    ],
    "logic": "AND"
  },
  "required_when": {
    "conditions": [
      { "field": "marital_status", "operator": "equals", "value": "married" }
    ],
    "logic": "AND"
  },
  "computed_value": null,
  "default_value": null,
  "placeholder_text": { "ar": "أدخل اسم الزوج/ة", "en": "Enter spouse name" }
}
```

**Computed value example**:
```json
{
  "type": "number",
  "key": "total",
  "properties": { "label_ar": "الإجمالي", "label_en": "Total", "required": false },
  "computed_value": "subtotal * (1 + tax_rate / 100)",
  "visible_when": null,
  "required_when": null,
  "default_value": null,
  "placeholder_text": null
}
```

**Validation on save** (422 errors):
- `visible_when.conditions[].field` must exist as element key in same template
- `required_when.conditions[].field` must exist as element key in same template
- `computed_value` expression must parse without syntax errors
- `computed_value` field references must exist as element keys in same template
- Circular dependency check across all elements' conditions and computed values

## Element Response (Extended)

`GET /api/templates/:id` response includes new fields on each element:

```json
{
  "elements": [
    {
      "id": "uuid",
      "key": "spouse_name",
      "type": "text",
      "x_mm": 20,
      "y_mm": 100,
      "width_mm": 80,
      "height_mm": 10,
      "properties": { "label_ar": "اسم الزوج/ة", "label_en": "Spouse Name", "required": false },
      "visible_when": { "conditions": [...], "logic": "AND" },
      "required_when": { "conditions": [...], "logic": "AND" },
      "computed_value": null,
      "default_value": null,
      "placeholder_text": { "ar": "أدخل اسم الزوج/ة", "en": "Enter spouse name" }
    }
  ]
}
```

## Submission Behavior (Modified)

### `POST /api/submissions`

On submission, the backend ConditionEngine:

1. Loads all elements for the template version
2. Evaluates `visible_when` for each element using submitted data
3. Strips values for elements where `visible_when` evaluates to false (hidden)
4. Evaluates `required_when` for visible elements
5. Validates that required fields (static required OR required_when=true) have non-empty values
6. Stores only visible field values in submission data

**Error response for conditional required violation**:
```json
{
  "detail": "Validation failed",
  "errors": [
    { "field": "guarantor_phone", "message": "Required when loan amount exceeds 50,000" }
  ]
}
```

## Dependency Validation Endpoint

### `POST /api/templates/:id/validate-dependencies`

Validate all element dependencies for circular references (called by frontend on condition save).

**Auth**: Designer, Admin  
**Request**: (no body — validates current template state)

**Response 200** (no issues):
```json
{
  "valid": true,
  "dependency_count": 8,
  "max_depth": 3
}
```

**Response 422** (circular dependency):
```json
{
  "valid": false,
  "detail": "Circular dependency detected",
  "cycle": ["spouse_name", "marital_status", "spouse_name"]
}
```

## Draft Save Behavior

### `POST /api/drafts` / `PATCH /api/drafts/:id`

Drafts store ALL field values including hidden fields. No stripping occurs on draft save. This preserves data if the user changes a condition trigger back to its previous value.
