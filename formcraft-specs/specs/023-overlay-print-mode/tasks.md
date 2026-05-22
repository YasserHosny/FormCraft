# Tasks: Overlay Print Mode

**Input**: Design documents from `/specs/022-overlay-print-mode/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Depends on**: Feature 016 (PDF generation pipeline), Feature 020 (new element types)

## Phase 1: Database Migration & Models

**Purpose**: Create tables and add include_in_overlay column

- [X] T001 [P] Create migration `formcraft-backend/migrations/025_overlay_print_mode.sql` — CREATE TABLE template_print_settings (id, template_id UNIQUE FK, print_mode CHECK, org_id FK, timestamps) with RLS; CREATE TABLE printer_profiles (id, name, description, x_offset_mm NUMERIC(5,1), y_offset_mm NUMERIC(5,1), is_default, is_active, org_id FK, created_by FK, timestamps) with RLS and partial unique index on is_default per org; ALTER TABLE elements ADD COLUMN include_in_overlay BOOLEAN NOT NULL DEFAULT true
- [X] T002 [P] Create `formcraft-backend/app/models/print_settings.py` — SQLAlchemy models: TemplatePrintSettings, PrinterProfile
- [X] T003 [P] Create `formcraft-backend/app/schemas/print_settings.py` — Pydantic schemas: PrintSettingsResponse, PrintSettingsUpdate, PrinterProfileCreate, PrinterProfileUpdate, PrinterProfileResponse, PdfGenerationRequest (extended)
- [X] T004 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/ar.json` — print_settings.*, printer_profiles.*, overlay.* keys
- [X] T005 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/en.json` — same keys in English

---

## Phase 2: Backend �� Printer Profile Service & Routes

**Purpose**: CRUD for printer profiles including calibration page

- [X] T006 Create `formcraft-backend/app/services/printer_profile_service.py` — methods: create_profile(), list_profiles(), update_profile(), delete_profile() (soft), set_default() (unset previous), generate_calibration_page() (returns PDF bytes with crosshair markers at known positions)
- [X] T007 Create `formcraft-backend/app/api/routes/printer_profiles.py` — routes: POST /printer-profiles, GET /printer-profiles, PATCH /:id, DELETE /:id, POST /:id/set-default, POST /:id/calibration-page
- [X] T008 Register printer profiles router in `formcraft-backend/app/main.py`

**Checkpoint**: Admin can CRUD printer profiles and generate calibration test pages.

---

## Phase 3: Backend — Overlay PDF Generation

**Purpose**: Modify PDF pipeline to support overlay mode with offset

- [X] T009 Modify `formcraft-backend/app/services/pdf/html_builder.py` build_html() — add parameters: overlay_mode (bool, default False), x_offset_mm (float, default 0), y_offset_mm (float, default 0); when overlay_mode=True: filter elements to include_in_overlay=True only, suppress page background/borders
- [X] T010 Modify `formcraft-backend/app/services/pdf/element_renderers/base.py` _base_style() — accept optional x_offset and y_offset parameters; add offset to left and top mm values
- [X] T011 Update all element renderers to pass offset through _base_style() — SignatureHTMLRenderer, TableHTMLRenderer, and existing renderers
- [X] T012 Modify `formcraft-backend/app/services/pdf/renderer.py` render_pdf() — accept overlay_mode and offset params, pass to build_html()

**Checkpoint**: build_html() produces overlay HTML (filtered elements, offset positions, no decorative styling).

---

## Phase 4: Backend — Print Settings & PDF Endpoint

**Purpose**: Template print settings and extended PDF generation

- [X] T013 Create print settings service — get_settings(), upsert_settings() for template_print_settings
- [X] T014 Add print settings routes to templates router — GET /templates/:id/print-settings, PUT /templates/:id/print-settings
- [X] T015 Extend PDF generation endpoint `POST /submissions/:id/pdf` — accept printer_profile_id and print_mode_override in request; resolve profile offset; generate overlay/full/both based on template settings; log print_mode + profile in audit metadata
- [X] T016 Handle "both" mode — generate full PDF + overlay PDF in parallel; return both URLs in response

**Checkpoint**: PDF endpoint respects template print_mode, applies printer offset, logs mode in audit trail.

---

## Phase 5: Frontend — Admin Printer Profiles

**Purpose**: Admin UI for managing printer profiles

- [X] T017 Create PrinterProfilesComponent `formcraft-frontend/src/app/features/admin/printer-profiles/` — mat-table listing profiles with name, offset values, default badge, actions (edit, delete, set default, calibration page)
- [X] T018 Create PrinterProfileFormDialog — reactive form for name, description, x_offset_mm, y_offset_mm, is_default
- [X] T019 Add calibration page download button — calls /calibration-page endpoint, triggers PDF download
- [X] T020 Create PrinterProfileService — Angular HttpClient service wrapping all profile endpoints
- [X] T021 Register route `/admin/printer-profiles` in admin routing module

**Checkpoint**: Admin can manage printer profiles and download calibration pages.

---

## Phase 6: Frontend — Design Studio Print Settings

**Purpose**: Print mode configuration and overlay toggle per element

- [X] T022 Create PrintSettingsPanel in Design Studio — mat-radio-group for print_mode (full/overlay/both); shown in template settings sidebar
- [X] T023 Add include_in_overlay toggle to element properties panel — mat-slide-toggle; default based on element type (true for data types, false for decorative)
- [X] T024 Add overlay preview mode in Design Studio — toggle button: when active, canvas dims excluded elements and highlights included ones

**Checkpoint**: Designer can set template print mode and control which elements appear in overlay.

---

## Phase 7: Frontend — Form Desk Print Dialog

**Purpose**: Operator selects printer profile when generating PDF

- [X] T025 Modify print dialog in Form Desk — add printer profile dropdown (lists active profiles, shows default with badge); pass selected profile_id to PDF generation request
- [X] T026 Handle "both" mode response — when response has full_pdf_url + overlay_pdf_url, show download buttons for each or trigger both downloads
- [X] T027 Add print mode indicator — show "Overlay Mode" or "Full Mode" badge in print dialog based on template setting

**Checkpoint**: Operator can select printer profile before printing. "Both" mode produces two downloadable PDFs.

---

## Phase 8: Integration Testing

**Purpose**: End-to-end verification of overlay pipeline

- [X] T028 Test overlay generation — template with 5 elements (3 include_in_overlay=true, 2 false) → generate overlay → verify only 3 elements rendered
- [X] T029 Test offset application — set profile offset (2.0, -1.0) → generate overlay → verify element positions shifted correctly in output HTML/PDF
- [X] T030 Test "both" mode — generate → verify two distinct PDFs returned (one full, one overlay)
- [X] T031 Test audit trail — generate overlay PDF → verify audit log contains print_mode and printer_profile_id in metadata

**Checkpoint**: Complete overlay print pipeline working with calibration, filtering, and audit trail.
