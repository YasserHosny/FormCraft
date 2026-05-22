# Implementation Plan: New Element Types (Signature & Table)

**Date**: 2026-05-17  
**Feature Branch**: `020-new-element-types`  
**Depends on**: Feature 016 (Form Filler element rendering), Feature 015 (Design Studio canvas)

## Architecture Overview

This feature extends the existing element type system with two new types: Signature and Table. It follows the established pattern of ElementType enum → properties schema → backend HTML renderer → frontend form component.

```
┌──────────────────────────────────────────────────────────────────┐
│                     Design Studio                                  │
│  ┌───────────────────────┐  ┌──────────────────────────────────┐ │
│  │ Signature Placeholder │  │ Table Config Panel               │ │
│  │ (dotted box + label)  │  │ (columns, rows, auto-sum)       │ │
│  └───────────────────────┘  └──────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────┤
│                     Form Desk (Operator)                           │
│  ┌───────────────────────┐  ┌──────────────────────────────────┐ │
│  │ SignaturePadComponent  │  │ TableInputComponent              │ │
│  │ (canvas draw/clear)   │  │ (dynamic rows, auto-sum footer) │ │
│  └───────────────────────┘  └──────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────┤
│                     Backend (PDF Rendering)                        │
│  ┌───────────────────────┐  ┌──────────────────────────────────┐ │
│  │ SignatureHTMLRenderer  │  │ TableHTMLRenderer                │ │
│  │ (<img> at mm pos)     │  │ (<table> with borders/headers)  │ │
│  └───────────────────────┘  └──────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────┤
│                     Database                                       │
│  elements.type CHECK expanded: + 'signature', 'table'            │
│  elements.properties JSONB: type-specific configuration          │
│  submissions.data JSONB: signature PNG / table row array         │
└──────────────────────────────────────────────────────────────────┘
```

## Technology Stack

- **Backend**: Python 3.12, FastAPI, WeasyPrint (PDF), Supabase Storage (signature overflow)
- **Frontend**: Angular 17, `signature_pad` (npm, ~14KB), Angular Material (mat-table for table input)
- **PDF**: HTML `<img>` for signatures, HTML `<table>` for tables — both via WeasyPrint

## Implementation Phases

### Phase 1: Database Migration & Enum Expansion

Expand ElementType CHECK constraint. Update Python enum. No new tables.

### Phase 2: Backend — Signature Renderer & Validation

Create `SignatureHTMLRenderer` extending `ElementHTMLRenderer` ABC. Add signature validation to submission service. Add signature upload endpoint for oversized signatures.

### Phase 3: Backend — Table Renderer & Validation

Create `TableHTMLRenderer` extending `ElementHTMLRenderer` ABC. Add table row/cell validation to submission service. Handle page overflow for tall tables.

### Phase 4: Frontend — Signature in Design Studio

Canvas placeholder component for Design Studio. Properties panel for dimensions, label, pen color.

### Phase 5: Frontend — Signature in Form Desk

`SignaturePadComponent` wrapping `signature_pad` library. Draw/clear/confirm actions. Storage logic for data URL vs upload.

### Phase 6: Frontend — Table in Design Studio

Table configuration panel: column definition CRUD, row limits, auto-sum toggle, preview rendering.

### Phase 7: Frontend — Table in Form Desk

`TableInputComponent` with dynamic rows, add/remove row buttons, auto-sum footer, per-cell validation.

### Phase 8: Integration & PDF Verification

End-to-end test: create template → add both element types → fill form → submit → generate PDF → verify rendering.

## Technical Constraints

1. **Follow existing renderer pattern** — new renderers registered in `html_builder.py` renderer registry
2. **One npm dependency added** — `signature_pad` (MIT, lightweight)
3. **No new database tables** — only CHECK constraint expansion
4. **Signature transparency** — PNG with transparent background for overlay print mode compatibility
5. **Table height is approximate** — actual rendered height depends on row count; PDF renderer handles overflow

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| signature_pad touch latency on older devices | Poor UX on tablets | Test on target hardware; consider reducing canvas resolution |
| Table overflow complex in PDF | Visual defects | Rely on WeasyPrint's native table pagination; test with max_rows |
| Large signatures bloat submission JSONB | DB performance | 100KB threshold → Supabase Storage for oversize |
| Table auto-sum floating point errors | Incorrect totals | Round to 2 decimal places in display and sum calculation |
