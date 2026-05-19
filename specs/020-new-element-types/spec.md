# Feature Specification: New Element Types (Signature & Table)

**Feature Branch**: `020-new-element-types`  
**Created**: 2026-05-17  
**Status**: Draft  
**Input**: DS-12 — Signature Element & Table Element; Roadmap 1.9

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Signature Element in Design Studio (Priority: P1)

A designer adds a signature element to a form template. The element has configurable dimensions (width/height in mm), a label, and a required flag. In Form Desk, the operator (or the form signee) draws their signature using a touch/mouse pad. The signature is stored as a PNG data URL or uploaded to Supabase Storage.

**Why this priority**: Signature fields are mandatory for legal/financial forms in Egyptian banking. Without electronic signatures, forms must be printed, signed, and re-scanned — defeating the purpose of digital form filling.

**Independent Test**: Add signature element to template → set required=true → open in Form Desk → draw signature → submit → verify signature PNG stored in submission data → generate PDF → verify signature rendered at correct position.

**Acceptance Scenarios**:

1. **Given** a designer drags a "Signature" element to the canvas, **When** placed, **Then** a placeholder box appears with dotted border and "Signature" label at the configured dimensions
2. **Given** a designer sets the signature element as required, **When** an operator submits the form without signing, **Then** validation prevents submission with "Signature required"
3. **Given** an operator clicks the signature field in Form Desk, **When** a signature pad opens, **Then** they can draw with mouse/touch, clear, and confirm
4. **Given** the operator confirms their signature, **When** the pad closes, **Then** the signature preview appears in the field and the data is stored as a transparent PNG
5. **Given** a submitted form with a signature, **When** a PDF is generated, **Then** the signature PNG is rendered at the exact mm position specified in the template

---

### User Story 2 - Table Element in Design Studio (Priority: P1)

A designer adds a table element to a form template. The table has configurable columns (header, type, width) and rows can be added dynamically by the operator during form filling. Each cell stores a value matching the column type. Optional auto-sum footer calculates column totals for numeric columns.

**Why this priority**: Financial forms (invoices, balance sheets, transaction lists) require tabular data input. Currently this requires multiple separate fields with manual alignment — a table element provides structured multi-row data capture.

**Independent Test**: Add table element → define columns [Description (text), Amount (number), Date (date)] → set min_rows=1, max_rows=20 → open in Form Desk → add 3 rows → fill data → verify auto-sum shows total for Amount column → submit → generate PDF → verify table rendered with borders and alignment.

**Acceptance Scenarios**:

1. **Given** a designer drags a "Table" element to the canvas, **When** placed, **Then** a table configuration panel opens with column definition (header_ar, header_en, type, width_mm)
2. **Given** the designer adds 3 columns and sets min_rows=1, max_rows=10, **When** saved, **Then** the canvas shows a table preview with headers and one empty row
3. **Given** the designer enables "Auto-sum footer" for the Amount column, **When** the setting is saved, **Then** a footer row indicator appears in the preview
4. **Given** an operator opens the form in Form Desk, **When** they view the table, **Then** min_rows empty rows are shown with an "Add Row" button (if below max_rows)
5. **Given** the operator fills 3 rows with amounts 100, 200, 300, **When** the auto-sum column is configured, **Then** the footer shows 600
6. **Given** the operator attempts to add an 11th row (max_rows=10), **When** they click "Add Row", **Then** the button is disabled with tooltip "Maximum rows reached"
7. **Given** a submitted form with table data, **When** a PDF is generated, **Then** the table is rendered with borders, column headers, data rows, and auto-sum footer at the configured position

---

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Designer can add Signature element type to template canvas | P1 |
| FR-02 | Signature element has configurable dimensions (width_mm, height_mm), label, and required flag | P1 |
| FR-03 | Operator can draw signature with mouse/touch in Form Desk using signature pad | P1 |
| FR-04 | Signature stored as transparent PNG (data URL for small, Supabase Storage for >100KB) | P1 |
| FR-05 | Signature rendered in PDF at exact mm position with correct dimensions | P1 |
| FR-06 | Designer can add Table element type to template canvas | P1 |
| FR-07 | Table has configurable columns: header_ar, header_en, type (text, number, date), width_mm | P1 |
| FR-08 | Table has min_rows (default 1) and max_rows (default 20) configuration | P1 |
| FR-09 | Operator can add/remove rows dynamically within min/max bounds | P1 |
| FR-10 | Table supports auto-sum footer for numeric columns (configurable per column) | P1 |
| FR-11 | Table data stored as JSONB array of row objects in submission | P1 |
| FR-12 | Table rendered in PDF with borders, headers, data rows, and optional footer | P1 |
| FR-13 | ElementType enum expanded to include 'signature' and 'table' | P1 |

## Non-Functional Requirements

| ID | Requirement | Metric |
|----|-------------|--------|
| NFR-01 | Signature pad renders within 200ms of click | < 200ms open time |
| NFR-02 | Table with 20 rows renders without lag on mobile | < 100ms per row add |
| NFR-03 | Signature PNG file size < 50KB for typical signatures | Median < 50KB |
| NFR-04 | PDF table rendering handles page overflow (split across pages if needed) | Tables > page height split cleanly |

## Edge Cases

| # | Case | Handling |
|---|------|----------|
| 1 | Operator starts signature then navigates away | Signature pad state preserved in form draft; on return, show "Resume or Clear" |
| 2 | Signature exceeds element dimensions | Scale signature to fit within configured width_mm × height_mm, maintaining aspect ratio |
| 3 | Table has 0 columns defined | Validation prevents save — at least 1 column required |
| 4 | Operator deletes all rows (below min_rows) | Prevent deletion of last row if at min_rows; disable remove button |
| 5 | Table auto-sum with empty numeric cells | Treat empty/null as 0 for sum calculation |
| 6 | PDF page overflow for tall table | Split table at row boundary; repeat headers on continuation page |
| 7 | Signature field on a form that will be printed (overlay mode) | Signature element include_in_overlay should default to true |

## Success Criteria

- Designer can add signature and table elements in under 60 seconds each
- Operator can sign a form on mobile device with finger in under 5 seconds
- Table with 10 rows and 5 columns renders correctly in PDF with proper alignment
- Auto-sum calculates correctly with mixed empty/filled numeric cells
