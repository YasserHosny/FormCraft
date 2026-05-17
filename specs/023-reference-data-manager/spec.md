# Feature Specification: Reference Data Manager

**Feature Branch**: `023-reference-data-manager`  
**Created**: 2026-05-17  
**Status**: Draft  
**Input**: DS-11 — Reference Data Lists & Field Binding; Roadmap 1.12

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create & Manage Reference Lists (Priority: P1)

An admin creates a reference data list (e.g., "Egyptian Governorates", "Vehicle Types", "Banks List") with a bilingual name, description, and a typed column schema. Each column in the schema has a key, label (ar/en), data type (text, number, date, dropdown), and required flag. The admin can later edit the schema or archive the list.

**Why this priority**: Reference lists are the foundation all other features depend on — field binding, auto-fill, and searchable dropdowns all require lists to exist first.

**Independent Test**: Create list "Egyptian Banks" with columns [code (text, required), name_ar (text, required), name_en (text, required), swift (text)] → verify list appears in management grid → edit description → archive → verify not available for new bindings.

**Acceptance Scenarios**:

1. **Given** an admin opens the Reference Data page, **When** they click "Create List", **Then** a form appears with fields for name_ar, name_en, description, and a column schema builder
2. **Given** the admin defines 3 columns and clicks Save, **When** the list is created, **Then** it appears in the management grid with 0 entries and the defined column count
3. **Given** an admin clicks "Edit" on a list, **When** they add a new optional column and save, **Then** existing entries remain unaffected and new entries can populate the new column
4. **Given** an admin archives a list, **When** a designer opens field binding configuration, **Then** the archived list does not appear in the list picker dropdown
5. **Given** a list is in use (bound to at least one element), **When** an admin attempts to delete it, **Then** the system prevents deletion with "This list is bound to N fields — archive instead"

---

### User Story 2 - Manage Reference Entries (Priority: P1)

Admins add, edit, deactivate, and reactivate entries within a reference list. Each entry stores values matching the list's column schema. Inactive entries remain in the database (for historical submissions) but do not appear in form dropdowns.

**Why this priority**: Without entries, lists are empty shells. Entry management is the primary daily workflow for reference data maintainers.

**Independent Test**: Open list "Egyptian Banks" → add entry {code: "NBE", name_ar: "البنك الأهلي", name_en: "National Bank of Egypt", swift: "NBEGEGCX"} → verify appears in entry grid → deactivate → verify does not appear in form dropdown → reactivate → verify appears again.

**Acceptance Scenarios**:

1. **Given** an admin opens a reference list, **When** they click "Add Entry", **Then** a form appears with one field per column (respecting types: text input, number input, date picker, nested dropdown)
2. **Given** an admin submits an entry with valid data, **When** saved, **Then** the entry appears in the list grid sorted by creation date (newest first)
3. **Given** an admin toggles an entry to "Inactive", **When** the entry is deactivated, **Then** it remains visible in admin grid (greyed out) but is excluded from Form Desk dropdowns
4. **Given** an admin edits an entry value, **When** saved, **Then** the audit trail records the old value, new value, actor, and timestamp
5. **Given** a column is marked required, **When** an admin submits an entry with that column empty, **Then** validation prevents save with a field-level error message

---

### User Story 3 - CSV Bulk Import (Priority: P2)

Admins can upload a CSV file to populate or update entries in bulk. The system validates each row against the column schema before committing. A preview step shows valid/invalid row counts and specific errors per row.

**Why this priority**: Banks and government agencies manage hundreds of reference entries (branches, codes, regions). Manual entry-by-entry input is impractical for initial data load.

**Independent Test**: Create list with 3 columns → upload CSV with 50 rows (2 invalid: missing required field, wrong type) → preview shows 48 valid, 2 invalid with error details → confirm import → verify 48 entries created.

**Acceptance Scenarios**:

1. **Given** an admin clicks "Import CSV", **When** they upload a CSV file, **Then** the system parses the file and shows a preview with column mapping (auto-matched by header name)
2. **Given** the CSV has headers that don't match column keys, **When** in preview mode, **Then** the admin can manually map CSV columns to list columns via dropdowns
3. **Given** the preview shows 2 invalid rows, **When** the admin clicks "Import Valid Only", **Then** only the 48 valid rows are created and a downloadable error report lists the 2 failures
4. **Given** a CSV row has a value matching an existing entry's unique column, **When** import mode is "Update Existing", **Then** the matching entry is updated rather than duplicated
5. **Given** the CSV exceeds 5,000 rows, **When** upload begins, **Then** the system processes in background and notifies the admin on completion

---

### User Story 4 - Field Binding to Reference List (Priority: P1)

A designer configures a dropdown element in Design Studio to be "bound" to a reference list. They select which column displays in the dropdown and which column provides the stored value. They can also configure auto-fill mappings: when the user selects an entry, other fields on the form are auto-populated from the same entry's columns.

**Why this priority**: This is the primary consumption mechanism — without binding, reference lists have no connection to forms. Auto-fill is the highest-value UX improvement for operators filling repetitive forms.

**Independent Test**: Create list "Banks" with columns [code, name_ar, swift] → add 3 entries → in Design Studio, create dropdown element → bind to "Banks" list → set display=name_ar, value=code → add auto-fill: swift_field ← swift column → preview form → select bank → verify dropdown shows Arabic names, stores code, and auto-fills swift field.

**Acceptance Scenarios**:

1. **Given** a designer selects a dropdown element's properties, **When** they choose "Bind to Reference List", **Then** a picker shows all active (non-archived) reference lists for the org
2. **Given** a list is selected, **When** configuring binding, **Then** the designer can select display_column (shown in dropdown) and value_column (stored in submission)
3. **Given** a designer adds an auto-fill mapping, **When** they select a target element + source column, **Then** the mapping is saved and displayed in a summary table
4. **Given** an operator opens a bound form in Form Desk, **When** they click the dropdown, **Then** they see all active entries' display_column values, sorted alphabetically
5. **Given** the operator selects an entry with auto-fill mappings, **When** the selection is confirmed, **Then** mapped fields are immediately populated with the entry's column values
6. **Given** a reference list has 50+ entries, **When** the operator focuses the dropdown, **Then** a searchable type-ahead input appears instead of a plain select

---

### User Story 5 - Searchable Dropdown for Large Lists (Priority: P2)

When a reference list bound to a dropdown has more than a configurable threshold (default: 20) entries, the form renders a searchable type-ahead input instead of a native select. The search filters entries by display column value (case-insensitive, Arabic-aware).

**Why this priority**: Egypt has 27 governorates, hundreds of bank branches. A native select with 200+ items is unusable. Searchable input is essential for operator productivity.

**Independent Test**: Bind dropdown to list with 100 entries → open form → type first 2 characters of an entry name → verify filtered results appear → select one → verify value stored and auto-fill triggered.

**Acceptance Scenarios**:

1. **Given** a bound dropdown has 25 active entries (above threshold 20), **When** the form renders, **Then** a type-ahead search input is shown instead of a native select element
2. **Given** the operator types "الأه" in the search, **When** debounce completes (300ms), **Then** only entries with display values containing "الأه" are shown
3. **Given** no entries match the search text, **When** the dropdown shows results, **Then** a "No results" message appears in Arabic/English (per locale)
4. **Given** the designer sets the threshold to 50 for a specific field, **When** the list has 30 entries, **Then** a regular select is rendered (30 < 50)
5. **Given** the operator clears the search and selects nothing, **When** they move focus away, **Then** any previously auto-filled fields are cleared if the binding is configured with "clear_on_deselect: true"

---

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Admin can create reference lists with bilingual name, description, and typed column schema | P1 |
| FR-02 | Column schema supports types: text, number, date, dropdown (with inline options) | P1 |
| FR-03 | Admin can edit list metadata and add new optional columns to existing lists | P1 |
| FR-04 | Admin can archive a list (hides from binding picker, entries preserved) | P1 |
| FR-05 | System prevents deletion of lists bound to existing form elements | P1 |
| FR-06 | Admin can add, edit, deactivate, and reactivate individual entries | P1 |
| FR-07 | Inactive entries are excluded from Form Desk dropdowns but preserved for historical data | P1 |
| FR-08 | Admin can import entries from CSV with preview, validation, and column mapping | P2 |
| FR-09 | CSV import supports "Insert New" and "Update Existing" modes | P2 |
| FR-10 | Designer can bind a dropdown element to a reference list, selecting display and value columns | P1 |
| FR-11 | Designer can configure auto-fill mappings: target element ← source column | P1 |
| FR-12 | Form renders searchable type-ahead for bound dropdowns exceeding entry threshold | P2 |
| FR-13 | All entry changes (create, update, deactivate) are recorded in the audit trail | P1 |

## Non-Functional Requirements

| ID | Requirement | Metric |
|----|-------------|--------|
| NFR-01 | Searchable dropdown filters entries within 300ms of debounced input | < 300ms client-side filter |
| NFR-02 | CSV import of 5,000 rows completes within 30 seconds | < 30s for 5K rows |
| NFR-03 | Form Desk dropdown endpoint (`/entries/dropdown`) and single entry endpoint (`/entries/:id`) cached with 5-min TTL to reduce DB load | Cache hit > 90% during form filling sessions |
| NFR-04 | All reference data is scoped by org_id with RLS enforcement | Zero cross-org data leakage |

## Edge Cases

| # | Case | Handling |
|---|------|----------|
| 1 | Admin removes a column from list schema while entries exist | Soft-remove: column marked hidden, existing entry values preserved in JSONB |
| 2 | Entry deactivated after operator already loaded the form | On submit, validate value still active; if not, show inline warning "Selected value is no longer active — please re-select" |
| 3 | CSV contains duplicate entries (same unique key) in single upload | Report as validation error, skip duplicates within batch |
| 4 | Reference list has 0 active entries when form loads | Show disabled dropdown with placeholder "No entries available" |
| 5 | Auto-fill target field is hidden by visibility condition | Skip auto-fill for hidden fields; apply if field becomes visible later |
| 6 | Two dropdowns on same form bound to same list | Each operates independently; selections do not conflict |
| 7 | Designer changes binding after submissions exist | Existing submissions retain stored value_column value; new submissions use new binding |

## Success Criteria

- Admin can create list, define schema, add 10+ entries, and bind to form element within 5 minutes
- Operator can select from a 100-entry bound dropdown using search in under 3 seconds
- CSV import of 1,000 government branch entries completes without errors on valid data
- Auto-fill correctly populates 3+ fields from a single dropdown selection
- Historical submissions retain valid data even after entry deactivation or binding changes
