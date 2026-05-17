# Tasks: New Element Types (Signature & Table)

**Input**: Design documents from `/specs/020-new-element-types/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Depends on**: Feature 016 (Form Filler element rendering), Feature 015 (Design Studio canvas)

## Phase 1: Database Migration & Enum Expansion

**Purpose**: Expand element type to include signature and table

- [X] T001 [P] Create migration `formcraft-backend/migrations/023_new_element_types.sql` — DROP existing elements_type_check constraint, ADD new CHECK including 'signature' and 'table' values
- [X] T002 [P] Update `formcraft-backend/app/models/enums.py` — add SIGNATURE = "signature" and TABLE = "table" to ElementType enum
- [X] T003 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/ar.json` — element_types.signature, element_types.table, signature.*, table.* keys
- [X] T004 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/en.json` — same keys in English

---

## Phase 2: Backend — Signature Renderer & Validation

**Purpose**: PDF rendering and submission validation for signature elements

- [X] T005 Create `formcraft-backend/app/services/pdf/element_renderers/signature_renderer.py` — SignatureHTMLRenderer extending ElementHTMLRenderer ABC; render() produces `<img>` tag with base64 data at absolute mm position; for storage type, fetch from Supabase Storage and inline
- [X] T006 Register SignatureHTMLRenderer in renderer registry (`formcraft-backend/app/services/pdf/html_builder.py`) — map ElementType.SIGNATURE → SignatureHTMLRenderer
- [X] T007 Add signature validation to submission service — validate: required check (non-null), format check (valid PNG base64 or storage path), size check (<500KB)
- [X] T008 Add signature upload endpoint `POST /api/submissions/:id/signature-upload` to submissions route — multipart upload to Supabase Storage `signatures/` bucket, return storage path

**Checkpoint**: Signature elements render in PDF. Submission validates signature data.

---

## Phase 3: Backend — Table Renderer & Validation

**Purpose**: PDF rendering and submission validation for table elements

- [X] T009 Create `formcraft-backend/app/services/pdf/element_renderers/table_renderer.py` — TableHTMLRenderer extending ElementHTMLRenderer ABC; render() produces HTML `<table>` with `<thead>` (headers from properties.columns), `<tbody>` (data rows), optional `<tfoot>` (auto-sum); CSS: borders, column widths in mm, page-break-inside: avoid on rows
- [X] T010 Register TableHTMLRenderer in renderer registry — map ElementType.TABLE → TableHTMLRenderer
- [X] T011 Add table validation to submission service — validate: min_rows check, per-cell type validation (number must be numeric, date must be ISO format), required column enforcement

**Checkpoint**: Table elements render in PDF with headers, borders, data, and auto-sum footer. Submission validates row data.

---

## Phase 4: Frontend — Signature in Design Studio

**Purpose**: Designer can add and configure signature elements on canvas

- [X] T012 Add Signature to element palette in Design Studio — draggable "Signature" item in element toolbox
- [X] T013 Create SignaturePlaceholderComponent `formcraft-frontend/src/app/features/designer/components/signature-placeholder/` — renders dotted border box at element dimensions with "Signature" label
- [X] T014 Create signature properties panel in Design Studio — form fields: label_ar, label_en, required, width_mm, height_mm, pen_color

**Checkpoint**: Designer can drag signature element to canvas, configure dimensions and properties.

---

## Phase 5: Frontend — Signature in Form Desk

**Purpose**: Operator can draw and submit signatures

- [X] T015 Install `signature_pad` npm dependency — SKIPPED: custom canvas implementation used instead (no external dependency needed)
- [X] T016 Create SignaturePadComponent `formcraft-frontend/src/app/features/desk/components/signature-pad/` — wraps signature_pad canvas, exposes value as PNG data URL, actions: draw, clear, confirm; respects pen_color from element properties
- [X] T017 Integrate SignaturePadComponent into form filler element switch — when element.type === 'signature', render SignaturePadComponent instead of default input
- [X] T018 Add signature storage logic — if PNG data URL > 100KB, upload via /signature-upload endpoint; otherwise store inline in submission data

**Checkpoint**: Operator can draw signature on touch/mouse, clear, confirm. Data stored correctly.

---

## Phase 6: Frontend — Table in Design Studio

**Purpose**: Designer can add and configure table elements

- [X] T019 Add Table to element palette in Design Studio — draggable "Table" item in element toolbox
- [X] T020 Create TableConfigPanel `formcraft-frontend/src/app/features/designer/components/table-config/` — column definition CRUD (add/remove/reorder columns, set header_ar, header_en, type, width_mm, auto_sum), row limits (min_rows, max_rows), display options (show_header, show_borders, show_footer)
- [X] T021 Create TablePreviewComponent — render table preview on canvas with configured columns and sample row

**Checkpoint**: Designer can configure table columns, row limits, and auto-sum settings.

---

## Phase 7: Frontend — Table in Form Desk

**Purpose**: Operator can fill table data dynamically

- [X] T022 Create TableInputComponent `formcraft-frontend/src/app/features/desk/components/table-input/` — dynamic FormArray of row FormGroups, each with controls per column; renders as mat-table with editable cells
- [X] T023 Add row management — "Add Row" button (disabled at max_rows), "Remove Row" button per row (disabled at min_rows), row reordering
- [X] T024 Add auto-sum footer — reactive computation: for columns with auto_sum=true, sum all numeric values (treat empty as 0), display in footer row, update on any cell change
- [X] T025 Integrate TableInputComponent into form filler element switch — when element.type === 'table', render TableInputComponent

**Checkpoint**: Operator can add/remove rows, fill cells, see live auto-sum. Validation per cell.

---

## Phase 8: Integration & PDF Verification

**Purpose**: End-to-end verification

- [X] T026 Test signature flow: create template → add signature element → fill in Form Desk → submit → generate PDF → verify signature renders at correct position with correct dimensions
- [X] T027 Test table flow: create template → add table with 3 columns + auto-sum → fill 5 rows → submit → generate PDF → verify table renders with headers, borders, data, footer
- [X] T028 Test edge cases: signature on mobile touch, table at max_rows, table overflow page height, empty optional signature

**Checkpoint**: Both element types work end-to-end through Design Studio → Form Desk → PDF generation.