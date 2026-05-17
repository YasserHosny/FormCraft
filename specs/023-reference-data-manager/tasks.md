# Tasks: Reference Data Manager

**Input**: Design documents from `/specs/023-reference-data-manager/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Depends on**: Feature 016 (Form Filler dropdown rendering), Feature 021 (ConditionEngine for visibility checks during auto-fill)

## Phase 1: Database Migration & Backend Models

**Purpose**: Create tables, SQLAlchemy models, and Pydantic schemas for reference data

- [X] T001 [P] Create migration `formcraft-backend/migrations/026_reference_data.sql` — CREATE TABLE reference_lists (id, name_ar, name_en, description, schema JSONB, is_archived, org_id, created_by, created_at, updated_at) with RLS and indexes; CREATE TABLE reference_entries (id, list_id FK, values JSONB, is_active, org_id, created_by, created_at, updated_at) with RLS and indexes
- [X] T002 [P] Create `formcraft-backend/app/models/reference.py` — SQLAlchemy models for ReferenceList and ReferenceEntry with relationships
- [X] T003 [P] Create `formcraft-backend/app/schemas/reference.py` — Pydantic schemas: ColumnSchema (key, label_ar, label_en, type, required, is_unique_key, is_hidden, options), ReferenceListCreate, ReferenceListUpdate, ReferenceListResponse, ReferenceEntryCreate, ReferenceEntryUpdate, ReferenceEntryResponse, DropdownItem, ImportPreviewResponse, ImportConfirmRequest
- [X] T004 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/ar.json` — reference_data.*, import.*, binding.* keys
- [X] T005 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/en.json` — same keys in English

---

## Phase 2: Backend List & Entry CRUD Service

**Purpose**: Full business logic for list management, entry CRUD, schema validation, audit logging

- [X] T006 Create `formcraft-backend/app/services/reference_service.py` — ReferenceService class with methods: create_list(), get_list(), list_lists(), update_list(), archive_list(), unarchive_list(), delete_list() (with binding protection check), create_entry(), update_entry(), deactivate_entry(), activate_entry(), get_entries()
- [X] T007 Add dynamic entry validation in ReferenceService — validate entry values against list schema: required checks, type coercion (text→str, number→float, date→ISO date, dropdown→enum membership), unique key conflict detection
- [X] T008 Add audit logging to ReferenceService — log REFERENCE_LIST_CREATED, REFERENCE_LIST_UPDATED, REFERENCE_LIST_ARCHIVED, REFERENCE_ENTRY_CREATED, REFERENCE_ENTRY_UPDATED (with old/new diff), REFERENCE_ENTRY_DEACTIVATED, REFERENCE_ENTRY_REACTIVATED
- [X] T009 Create `formcraft-backend/app/api/routes/reference.py` — register all CRUD routes: POST/GET/PATCH /reference-lists, POST /:id/archive, POST /:id/unarchive, DELETE /:id, GET/POST /:id/entries, PATCH/POST /:id/entries/:eid (deactivate/activate)
- [X] T010 Register reference router in `formcraft-backend/app/main.py` — add router with prefix /api/reference-lists

**Checkpoint**: Admin can create lists, define schemas, add/edit/deactivate entries via API. Audit trail records all changes.

---

## Phase 3: CSV Import Pipeline

**Purpose**: Upload, parse, validate, preview, and bulk insert reference entries from CSV

- [X] T011 Create `formcraft-backend/app/services/reference_import_service.py` — methods: parse_csv(file), auto_map_columns(headers, schema), validate_rows(rows, schema, mode), bulk_insert(list_id, rows), bulk_update(list_id, rows, unique_key_column)
- [X] T012 Add import preview endpoint to reference routes — POST /:id/import/preview (multipart upload, returns valid/invalid counts, errors, column_mapping, preview_token stored in-memory with 15-min TTL); if mode="update" and list schema has no column with is_unique_key=true, return 422 "Update mode requires a unique key column"
- [X] T013 Add import confirm endpoint to reference routes — POST /:id/import/confirm (validates preview_token, inserts/updates valid rows in 100-row transaction chunks, returns imported_count, audit log REFERENCE_ENTRIES_IMPORTED with count)

**Checkpoint**: Admin can upload CSV, see validation preview, confirm import. 5K rows complete in <30s.

---

## Phase 4: Form Desk Integration API

**Purpose**: Optimized dropdown endpoint for Form Desk consumption with caching

- [X] T014 Add dropdown endpoint GET /api/reference-lists/:id/entries/dropdown — accepts display_column, value_column, q (optional search), returns [{display, value, entry_id}], active entries only, sorted alphabetically by display
- [X] T015 Add single entry endpoint GET /api/reference-lists/:id/entries/:entry_id — returns full entry values for auto-fill after selection
- [X] T016 Create `formcraft-backend/app/services/reference_cache.py` — in-memory LRU cache (maxsize=200) keyed by (org_id, list_id), 5-min TTL, invalidated on entry create/update/deactivate/import

**Checkpoint**: Form Desk can fetch dropdown data and individual entries for auto-fill. Cached responses for repeated form loads.

---

## Phase 5: Frontend Admin - List Management

**Purpose**: Angular admin UI for creating and managing reference lists

- [X] T017 Create Angular module `formcraft-frontend/src/app/features/admin/reference-data/reference-data.module.ts` — lazy-loaded module with routing
- [X] T018 Create list grid component `reference-data-list.component.ts` — mat-table displaying lists with columns: name (ar/en), column count, entry count, status (active/archived), actions (edit, archive, delete)
- [X] T019 Create list form dialog `reference-data-form-dialog.component.ts` — reactive form for name_ar, name_en, description + dynamic column schema builder (add/remove columns, set type, required, unique key)
- [X] T020 Create `reference-data.service.ts` — Angular HttpClient service wrapping all backend list and entry API endpoints
- [X] T021 Register route in admin routing module — `/admin/reference-data` path, lazy-loaded

**Checkpoint**: Admin can view list grid, create/edit lists with schema builder, archive/delete lists via UI.

---

## Phase 6: Frontend Admin - Entry Management

**Purpose**: Entry grid with CRUD and active/inactive toggle

- [X] T022 Create entries component `reference-entries.component.ts` — navigated from list grid row click, mat-table with dynamic columns from list schema, is_active toggle, add/edit/delete actions
- [X] T023 Create entry form dialog `reference-entry-form-dialog.component.ts` — reactive form generated from list schema columns (text input, number input, date picker, mat-select for dropdown type)
- [X] T024 Add active/inactive filter toggle to entries component — default shows all with inactive rows greyed out, filter toggle for "active only"

**Checkpoint**: Admin can view entries in dynamic grid, add/edit entries, toggle active status.

---

## Phase 7: Frontend Admin - CSV Import Wizard

**Purpose**: Multi-step import UI with upload, mapping, preview, and confirm

- [X] T025 Create import wizard component `reference-import.component.ts` — Angular Material stepper: Step 1 (file upload + mode select), Step 2 (column mapping review/override), Step 3 (validation preview with error table), Step 4 (confirm/cancel)
- [X] T026 Add CSV file upload handling — accept .csv files up to 10MB, send to preview endpoint, display mapping results
- [X] T027 Add error display in preview step — mat-table showing invalid rows with row number, column, and error message; download errors as CSV option

**Checkpoint**: Admin can upload CSV, review column mapping, see validation errors, confirm import of valid rows.

---

## Phase 8: Design Studio - Binding Configuration

**Purpose**: Allow designers to bind dropdown elements to reference lists with auto-fill mappings

- [X] T028 Create ref-binding panel component `ref-binding-panel.component.ts` — shown in element properties when element type is 'dropdown'; contains list picker (mat-select of active lists), display_column picker, value_column picker, search_threshold input, clear_on_deselect toggle
- [X] T029 Add auto-fill mapping editor to ref-binding panel — repeatable row: target element selector (mat-select of other elements on same page by key) + source column selector (from bound list schema)
- [X] T030 Save binding config to element.formatting.ref_binding — on panel save, update element's formatting JSONB via existing element update API
- [X] T031 Add binding indicator to Design Studio canvas — dropdown elements with ref_binding show a small "linked" icon badge

**Checkpoint**: Designer can bind dropdown to reference list, configure display/value columns, add auto-fill mappings.

---

## Phase 9: Form Desk - Bound Dropdown & Auto-Fill

**Purpose**: Render bound dropdowns with search and execute auto-fill on selection

- [X] T032 Create BoundDropdownComponent `bound-dropdown.component.ts` — detects ref_binding in element config; if entries ≤ threshold, render mat-select; if > threshold, render mat-autocomplete with debounced filter (300ms)
- [X] T033 Implement dropdown data loading — on component init, call /dropdown endpoint; cache results in service; for >500 entries, use server-side search via `q` param on each debounced input
- [X] T034 Create AutoFillService `auto-fill.service.ts` — on entry selection, read auto_fill[] mappings, fetch full entry from /entries/:id, for each mapping find target FormControl by element key, set value if element is visible (check ConditionEngine), emit valueChanges
- [X] T035 Integrate BoundDropdownComponent into form filler template — in form-filler component, detect ref_binding on dropdown elements and render BoundDropdownComponent instead of plain mat-select
- [X] T036 Handle edge cases — entry deactivated after form load (validate on submit, show warning), clear_on_deselect behavior, auto-fill with hidden target fields

**Checkpoint**: Operator sees searchable dropdown for bound fields, selecting an entry auto-fills mapped fields. Large lists use type-ahead search.

---

## Phase 10: Integration Testing & Polish

**Purpose**: End-to-end validation of the full reference data flow

- [X] T037 Add entry validation on form submission — verify selected entry is still active at submit time; if deactivated, show inline warning "Selected value is no longer active"
- [X] T038 Add empty-state handling — bound dropdown with 0 active entries shows disabled select with "No entries available" placeholder
- [X] T039 Test full flow: create list → add entries → bind to form element → fill form → auto-fill fires → submit → verify stored value matches value_column

**Checkpoint**: Complete reference data pipeline working end-to-end with proper error handling and edge cases covered.
