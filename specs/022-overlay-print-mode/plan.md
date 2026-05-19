# Implementation Plan: Overlay Print Mode

**Date**: 2026-05-17  
**Feature Branch**: `022-overlay-print-mode`  
**Depends on**: Feature 016 (PDF generation), Feature 020 (new element types need include_in_overlay defaults)

## Architecture Overview

Overlay Print Mode modifies the existing PDF generation pipeline to support rendering only data-bearing elements with printer calibration offsets. It adds two new tables, one new column on elements, and modifies the `build_html()` function.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Design Studio                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ PrintSettingsPanel (print_mode selector)                  │   │
│  │ Element Properties (include_in_overlay toggle)           │   │
│  └──────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                     Admin Panel                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ PrinterProfileManager (CRUD, calibration page)           │   │
│  └──────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                     Form Desk                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ PrintDialog (printer profile selector)                    │   │
│  └──────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                     Backend (PDF Pipeline)                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ build_html(template, overlay_mode, x_offset, y_offset)   │   │
│  │  ├── filter: include_in_overlay elements only            │   │
│  │  ├── offset: shift all positions by profile values       │   │
│  │  └── style: suppress backgrounds/borders in overlay      │   │
│  └──────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                     Database                                      │
│  template_print_settings (1:1 with templates)                    │
│  printer_profiles (per org)                                      │
│  elements.include_in_overlay (boolean)                           │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

- **Backend**: Python 3.12, FastAPI, WeasyPrint (PDF generation)
- **Frontend**: Angular 17, Angular Material
- **PDF calibration**: Pure HTML/CSS with mm units (WeasyPrint handles precision)

## Implementation Phases

### Phase 1: Database Migration & Models

Create template_print_settings, printer_profiles tables. Add include_in_overlay to elements.

### Phase 2: Backend — Printer Profile CRUD

Service and routes for printer profile management, including calibration page generation.

### Phase 3: Backend — Overlay PDF Generation

Modify `build_html()` to accept overlay_mode, x_offset_mm, y_offset_mm. Filter elements, apply offset, suppress decorative styling.

### Phase 4: Backend — Print Settings & PDF Endpoint Extension

Template print settings CRUD. Extend PDF generation endpoint with printer_profile_id and mode override.

### Phase 5: Frontend — Admin Printer Profiles

Printer profile management page: CRUD, set default, generate calibration page.

### Phase 6: Frontend — Design Studio Print Settings

Print mode selector in template settings. include_in_overlay toggle per element. Overlay preview.

### Phase 7: Frontend — Form Desk Print Dialog

Printer profile selector in print dialog. "Both" mode produces download with two files.

## Technical Constraints

1. **Modify build_html() signature** — add optional parameters, maintain backwards compatibility (defaults to non-overlay)
2. **Precision** — offsets stored as NUMERIC(5,1) for 0.1mm granularity
3. **Single default per org** — enforced by partial unique index
4. **Soft delete printer profiles** — preserve references in audit logs
5. **Audit metadata** — every PDF generation logs print_mode and profile used

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| WeasyPrint mm precision variance | Misalignment | Test with physical prints; document ±0.1mm expected variance |
| Offset exceeds page bounds | Elements invisible | Validate offset range (-50 to +50mm); warn in UI |
| "Both" mode doubles PDF generation time | Slow UX | Parallelize the two build_html() calls |
| Calibration requires physical printer | Can't test digitally | Provide reference PDF for visual verification without printing |
