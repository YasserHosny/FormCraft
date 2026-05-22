# Feature Specification: Overlay Print Mode

**Feature Branch**: `022-overlay-print-mode`  
**Created**: 2026-05-17  
**Status**: Draft  
**Input**: DS-14 — Overlay Print Mode & Printer Calibration; Roadmap 1.11

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure Print Mode per Template (Priority: P1)

A designer configures whether a template should generate PDFs in "full" mode (complete form with backgrounds, labels, and data), "overlay" mode (only data-bearing elements, positioned to align with a pre-printed form), or "both" (generate both versions). This setting is stored per template.

**Why this priority**: Egyptian banks use pre-printed government forms. Operators fill data digitally and print ONLY the data onto the pre-printed form sheet in the printer. Without overlay mode, forms must be filled by hand or printed completely (wasting the pre-printed stock).

**Independent Test**: Create template → set print_mode to "overlay" → add 5 elements (3 data fields, 1 label, 1 logo) → mark 3 data fields as include_in_overlay=true → generate overlay PDF → verify only 3 data fields appear (no label, no logo, no background).

**Acceptance Scenarios**:

1. **Given** a designer opens template print settings, **When** they select "Overlay" mode, **Then** the setting is saved and a preview shows which elements will appear in overlay
2. **Given** a template is set to "Full" mode, **When** a PDF is generated, **Then** all elements render (backgrounds, labels, data, images) — current behavior unchanged
3. **Given** a template is set to "Overlay" mode, **When** a PDF is generated, **Then** only elements with include_in_overlay=true render, with no background/border styling
4. **Given** a template is set to "Both" mode, **When** a PDF is generated, **Then** two PDF files are produced: one full, one overlay
5. **Given** the designer toggles include_in_overlay on an element, **When** saved, **Then** the overlay preview updates to show/hide that element

---

### User Story 2 - Printer Profile Calibration (Priority: P1)

An admin creates printer profiles with X/Y offset calibration values (in mm). When generating overlay PDFs, the system applies the printer's offset to shift all elements, compensating for printer feed alignment. Different printers (or trays) may have different offsets.

**Why this priority**: Every printer has slight mechanical variance in paper feed position (0.5-3mm). Without calibration, overlay data lands in the wrong position on pre-printed forms. The calibration page lets admins measure and correct this offset per printer.

**Independent Test**: Create printer profile "HP LaserJet Tray 2" with x_offset=1.5mm, y_offset=-0.5mm → generate overlay PDF using this profile → verify all element positions shifted by (1.5, -0.5)mm from their template positions.

**Acceptance Scenarios**:

1. **Given** an admin opens printer management, **When** they click "Add Printer Profile", **Then** a form appears with: name, x_offset_mm, y_offset_mm, description, is_default flag
2. **Given** an admin saves a printer profile with offsets (2.0, -1.0), **When** an overlay PDF is generated using this profile, **Then** every element position is shifted: rendered_x = template_x + 2.0, rendered_y = template_y + (-1.0)
3. **Given** multiple printer profiles exist, **When** an operator prints from Form Desk, **Then** they can select which printer profile to use (or the default is applied automatically)
4. **Given** no printer profile is selected, **When** an overlay PDF is generated, **Then** zero offset is applied (elements at exact template positions)

---

### User Story 3 - Calibration Test Page (Priority: P2)

An admin can print a calibration test page — a PDF with measurement markers at known positions. By comparing the printed markers against a reference grid, the admin can determine the X/Y offset for their printer and update the profile accordingly.

**Why this priority**: Without a standardized calibration mechanism, admins must guess offsets through trial-and-error. A calibration page makes the process deterministic and repeatable.

**Independent Test**: Generate calibration page → print on target printer → measure marker displacement with ruler → enter measured offset into printer profile → regenerate calibration page → verify markers now align.

**Acceptance Scenarios**:

1. **Given** an admin clicks "Print Calibration Page" for a printer profile, **When** the page generates, **Then** a PDF is produced with crosshair markers at positions (10mm, 10mm), (100mm, 100mm), (190mm, 280mm) with grid lines every 10mm
2. **Given** the admin measures that markers are offset by 1.5mm right and 0.5mm down, **When** they enter x_offset=-1.5, y_offset=-0.5 in the profile, **Then** subsequent overlay PDFs compensate for this variance
3. **Given** a calibration page is generated, **When** it's printed on a correctly calibrated printer, **Then** all markers should align with a reference measurement template

---

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Template print settings store print_mode: 'full', 'overlay', 'both' | P1 |
| FR-02 | Each element has include_in_overlay boolean (default: true for data-bearing elements, false for decorative) | P1 |
| FR-03 | Overlay PDF renders only elements where include_in_overlay=true | P1 |
| FR-04 | Overlay PDF has no background colors, borders, or decorative elements | P1 |
| FR-05 | Admin can create printer profiles with name, x_offset_mm, y_offset_mm | P1 |
| FR-06 | Overlay PDF applies printer profile offset to all element positions | P1 |
| FR-07 | Operator can select printer profile when generating overlay PDF from Form Desk | P1 |
| FR-08 | "Both" mode generates two separate PDFs (full + overlay) | P1 |
| FR-09 | Admin can generate calibration test page PDF with measurement markers | P2 |
| FR-10 | Printer profile has is_default flag (one default per org) | P1 |
| FR-11 | Overlay mode stored in audit log metadata for reprint traceability | P1 |

## Non-Functional Requirements

| ID | Requirement | Metric |
|----|-------------|--------|
| NFR-01 | Overlay PDF generation adds < 200ms overhead vs full PDF | < 200ms additional |
| NFR-02 | Offset precision to 0.1mm (one decimal place) | 0.1mm granularity |
| NFR-03 | Printer profiles scoped by org_id with RLS | Zero cross-org data leakage |
| NFR-04 | Calibration page positions accurate to 0.1mm in generated PDF | ±0.1mm WeasyPrint precision |

## Edge Cases

| # | Case | Handling |
|---|------|----------|
| 1 | All elements have include_in_overlay=false | Generate empty (blank) PDF — valid for testing |
| 2 | Offset pushes element outside page boundaries | Clip to page bounds; warn admin in profile settings |
| 3 | Template set to "overlay" but no printer profile exists | Generate overlay with zero offset (no error) |
| 4 | Operator requests reprint — which mode was original? | Audit log stores print_mode in metadata; reprint uses same mode |
| 5 | Signature element in overlay mode | Signatures typically include_in_overlay=true (they're data) |
| 6 | Table element in overlay mode | Tables render without decorative borders in overlay; only cell data |
| 7 | Admin deletes a printer profile that was used for past prints | Profile soft-deleted (is_active=false); past audit logs retain profile_id reference |

## Success Criteria

- Overlay PDF of a 5-element form generates in under 1 second
- Printed overlay aligns within 0.5mm of target position after calibration
- Admin can calibrate a new printer in under 5 minutes using calibration page
- "Both" mode correctly produces two distinct PDFs in a single operation
