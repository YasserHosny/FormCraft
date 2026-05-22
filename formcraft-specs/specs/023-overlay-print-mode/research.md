# Research: Overlay Print Mode

**Date**: 2026-05-17

## Research Questions

No NEEDS CLARIFICATION items. Research focused on overlay rendering strategy, offset application, print mode storage, and calibration page design.

## Findings

### 1. Overlay Rendering Strategy

**Current PDF pipeline**: `build_html(template)` iterates all pages → all elements → calls `get_renderer(type).render(element, data)` → produces full HTML → WeasyPrint converts to PDF.

**Overlay modification**: Add `overlay_mode` parameter to `build_html()`:
- When `overlay_mode=True`: filter elements to only those with `include_in_overlay=True`
- When `overlay_mode=True`: suppress page background-color, form borders, decorative elements
- When `overlay_mode=True`: apply offset (x_offset_mm, y_offset_mm) to each element's position

**Decision**: Modify `build_html()` signature to accept `overlay_mode: bool = False`, `x_offset_mm: float = 0`, `y_offset_mm: float = 0`. The element loop checks `include_in_overlay` flag. Each renderer's `_base_style()` adds the offset to left/top values.

### 2. Print Mode Storage

**Options**:
1. Add print_mode column to templates table
2. Separate template_print_settings table

**Decision**: Separate `template_print_settings` table with 1:1 relationship to templates. Rationale: keeps the templates table clean; print settings may grow (paper size, margins, etc.) in future features.

### 3. include_in_overlay Element Flag

**Decision**: Add `include_in_overlay` BOOLEAN column to `elements` table. Defaults:
- Data-bearing types (text, number, date, checkbox, radio, dropdown, textarea, signature, table): default TRUE
- Decorative types (image, label, barcode, qr_code): default FALSE

Designers can override the default for any element.

### 4. Printer Profile Architecture

Store printer profiles in a `printer_profiles` table with:
- name, description
- x_offset_mm (NUMERIC, precision 1 decimal)
- y_offset_mm (NUMERIC, precision 1 decimal)
- is_default (BOOLEAN, unique per org via partial unique index)
- is_active (BOOLEAN, for soft delete)
- org_id (RLS)

### 5. Calibration Page Design

Generate a special PDF (not template-based) with:
- Page size: A4 (210mm × 297mm)
- Crosshair markers (+) at known positions: (10,10), (50,50), (100,100), (150,150), (190,280)
- Grid lines every 10mm (light grey, 0.1pt)
- Position labels in mm next to each marker
- Instructions text at top: "Print this page and measure marker positions with a ruler"

The admin compares printed marker positions to expected positions. Difference = offset to enter in profile.

### 6. Audit Trail for Print Mode

**Decision**: When a PDF is generated, the audit log (`SUBMISSION_PDF_GENERATED` action) metadata includes:
```json
{
  "print_mode": "overlay",
  "printer_profile_id": "uuid-or-null",
  "x_offset_mm": 1.5,
  "y_offset_mm": -0.5
}
```

This enables reprints with the same settings and provides traceability for compliance.

### 7. "Both" Mode Implementation

When print_mode="both", the PDF generation endpoint returns a response with two PDF URLs/streams:
- `full_pdf_url`: standard full-render PDF
- `overlay_pdf_url`: overlay-only PDF with offset applied

Implementation: call `build_html()` twice (once with overlay_mode=False, once with overlay_mode=True) and render both through WeasyPrint. The two generations are independent and can be parallelized.
