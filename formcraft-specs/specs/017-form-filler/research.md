# Research: Form Filler

**Date**: 2026-05-16

## Research Questions

No NEEDS CLARIFICATION items in the spec. Research focused on technical approach validation against existing codebase.

## Findings

### 1. Existing Template Data Structure

The template → pages → elements hierarchy already exists. Each element has:
- `type` (ElementType enum: text, number, date, currency, dropdown, radio, checkbox, image, QR, barcode, tafqeet)
- `key` (string, unique per template — used as the field_values JSONB key)
- `label_ar`, `label_en` (bilingual labels)
- `validation` (JSONB — stores pattern rules, min/max, etc.)
- `formatting` (JSONB — stores tafqeet sourceElementKey, currency settings, dropdown options)
- `required` (boolean)
- `direction` (rtl/ltr/auto)
- `sort_order` (int — determines Tab order in Flow Layout)
- `x_mm`, `y_mm`, `width_mm`, `height_mm` (positioning for PDF/Print Layout — not used in Flow Layout)

This is everything needed to dynamically render form controls. No schema changes to templates/pages/elements.

### 2. Existing Validator Infrastructure

`ValidatorRegistry` maps (country, field_type) → validator. Validators use regex patterns:
- Egypt: national_id (14 digits), phone (+20 patterns), tax_id
- Saudi: national_id (10 digits), IBAN (SA prefix + 22 chars)
- UAE: emirates_id, IBAN (AE prefix)

For client-side integration, we need to:
1. Expose validator patterns via a new `GET /api/validators/:country` endpoint (returns regex patterns)
2. Or hardcode known patterns in the Angular app (less flexible but simpler)

**Decision**: Add a `GET /api/validators/:country` endpoint that returns patterns. This keeps the frontend in sync with backend validators without duplication.

### 3. Existing PDF Renderer

`render_template_pdf(template)` already:
- Iterates all pages/elements
- Positions each element at (x_mm, y_mm) with (width_mm, height_mm)
- Renders via ElementRenderer subclass per type
- Handles Arabic text reshaping/bidi
- Outputs WeasyPrint PDF

Currently renders empty/placeholder content. Extension point: each renderer's `render(element, context)` can check `context.get('field_values', {}).get(element['key'])` for a filled value.

### 4. Existing Tafqeet Service

`POST /api/tafqeet/preview` accepts `{ amount, currency, language }` and returns `{ text_ar, text_en }`. The converter handles:
- Integer and decimal parts
- Currency names (EGP, SAR, AED) with masculine/feminine agreement
- Zero handling, overflow handling
- Both Arabic and English output

This endpoint is already production-ready. The Form Filler just needs to call it on source field value changes.

### 5. Dropdown Options Source

Elements with `type: "dropdown"` store their options in `formatting.options` JSONB array. Each option has `{ value, label_ar, label_en }`. The Form Filler reads these to populate mat-select options.

No API call needed for dropdown options — they're part of the element data that comes with the template.

## Alternatives Considered

| Option | Rejected Because |
|--------|-----------------|
| Client-side tafqeet library | 500+ lines of Arabic number-word logic; too fragile to duplicate; API is fast enough (< 50ms) |
| FormArray instead of FormGroup | FormGroup with element.key as control names is more natural for field_values JSONB mapping |
| Dynamic component loading per field type | ngSwitch on 11 types is simpler; ComponentFactoryResolver is deprecated in Angular 17 |
| Local-only draft save (localStorage) | Violates Constitution V (data sovereignty); doesn't work cross-device |
| UUID-based reference numbers | Banks need human-readable reference numbers for phone/counter communication |
| Client-side PDF generation (jsPDF) | Would duplicate the entire WeasyPrint pipeline; Arabic text rendering in jsPDF is unreliable |
