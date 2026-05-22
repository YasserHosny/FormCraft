# Feature Specification: Submission History & Reprint

**Feature Branch**: `017-submission-history`  
**Created**: 2026-05-16  
**Status**: Draft  
**Input**: Form Desk Submission History (FD-05) — searchable history of all forms submitted by the operator with reprint, clone-as-new, and export capabilities

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Submission History List with Search (Priority: P1)

When an operator navigates to `/desk/history`, they see a paginated table of all their past submissions. They can search by reference number, template name, or date range. Each row shows the reference number, template name, date, and status.

**Why this priority**: Operators and customers need to look up past forms by reference number ("I printed a cheque earlier with ref FC-2026-05-0042 — can I see it?"). This is the minimum lookup capability.

**Independent Test**: Print a form → navigate to `/desk/history` → verify the new submission appears → search by reference number → verify it's found.

**Acceptance Scenarios**:

1. **Given** an operator navigates to `/desk/history`, **When** the page loads, **Then** a table shows all their submissions sorted by date (newest first)
2. **Given** 100 submissions exist, **When** the operator views the history, **Then** results are paginated (25 per page) with page controls
3. **Given** the operator types "FC-2026-05-0042" in the search bar, **When** search fires, **Then** only submissions matching that reference number are shown
4. **Given** the operator searches by template name "KYC", **When** search fires, **Then** submissions for templates containing "KYC" appear
5. **Given** the operator sets a date range filter (from: May 1, to: May 15), **When** the filter applies, **Then** only submissions within that range appear
6. **Given** the operator filters by template "KYC Form", **When** the filter applies, **Then** only KYC Form submissions appear

---

### User Story 2 - Submission Detail View (Priority: P1)

Clicking a submission row opens a read-only detail view showing all filled field values, the template version used, operator name, timestamp, and reference number. The operator can download the PDF from this view.

**Why this priority**: Operators need to see what was actually submitted — for customer inquiries, compliance checks, or dispute resolution. The read-only view is essential for accountability.

**Independent Test**: Click a submission row → verify all field values display in read-only mode → click "Download PDF" → verify PDF generates with the original data.

**Acceptance Scenarios**:

1. **Given** the operator clicks a submission row, **When** the detail view opens, **Then** all field_values are displayed with their labels in read-only mode
2. **Given** the detail view is open, **When** checking the metadata, **Then** reference_number, template name, version, date, and operator name are visible
3. **Given** the detail view is open, **When** the operator clicks "Download PDF", **Then** a PDF is generated using the stored field_values and the original template version

---

### User Story 3 - Reprint with Watermark (Priority: P1)

Operators can reprint any past submission. Reprinted PDFs use the original template version and field data but are stamped with a "REPRINT" watermark and the reprint timestamp.

**Why this priority**: Customers lose printed forms or need additional copies. Banks require reprints to be clearly marked to prevent fraud (duplicate form usage). This is a daily operational need.

**Independent Test**: Open a submission detail → click "Reprint" → verify PDF opens with "REPRINT" watermark and today's date → verify audit log records FORM_REPRINTED event.

**Acceptance Scenarios**:

1. **Given** the operator clicks "Reprint" on a submission, **When** the PDF generates, **Then** it contains the original field_values at the original template version
2. **Given** a reprint PDF is generated, **When** examining the output, **Then** a "REPRINT" watermark appears diagonally across each page
3. **Given** a reprint PDF is generated, **When** examining the footer, **Then** reprint timestamp and "Originally printed: {date}" are shown
4. **Given** a reprint is performed, **When** checking the audit log, **Then** a FORM_REPRINTED event exists with submission_id, operator_id, and timestamp

---

### User Story 4 - Clone as New Submission (Priority: P2)

Operators can clone a past submission's data into a new form filling session. This pre-fills the Form Filler with the old data, allowing quick modifications for similar entries (e.g., same form type but different customer).

**Why this priority**: High value for repetitive workflows (same form, minor changes) but not essential for day-1 operations.

**Independent Test**: Click "Clone as New" on a submission → verify Form Filler opens pre-filled with old values → modify one field → print → verify new submission created with new reference number.

**Acceptance Scenarios**:

1. **Given** the operator clicks "Clone as New" on a submission, **When** the Form Filler opens, **Then** all field values from the original submission are pre-loaded into the form controls
2. **Given** the cloned form is printed, **When** the submission is created, **Then** it has a new reference number (not the original's)
3. **Given** the template has been updated since the original submission, **When** cloning, **Then** the Form Filler loads the latest published version and maps old field values by element key (missing keys left empty, extra keys ignored)

---

### User Story 5 - Export Submission Data (Priority: P3)

Operators can export a single submission's data as JSON or CSV for integration with other systems.

**Why this priority**: Nice-to-have for interoperability but not required for core operations. Most value comes when bulk export is needed (Phase 2).

**Independent Test**: Click "Export" on a submission → select CSV → verify file downloads with field keys as headers and values as row.

**Acceptance Scenarios**:

1. **Given** the operator clicks "Export" → "JSON", **When** the download completes, **Then** the file contains the submission's field_values as a JSON object with reference_number and metadata
2. **Given** the operator clicks "Export" → "CSV", **When** the download completes, **Then** the file has element keys as column headers and values as the single data row

---

### Edge Cases

- What happens when the template version used in a submission has since been deleted? The submission still renders with stored field_values; the PDF regeneration uses a "frozen" snapshot. If the template no longer exists, show a warning but still allow JSON export.
- What happens when an operator searches for a submission that belongs to another operator in the same org? Visibility is role-based: operators see only their own submissions by default. Admin and branch_manager roles see all org submissions. A query param `scope=org` is available for privileged roles to expand visibility; for operators, this param is ignored and the API always filters by operator_id.
- What happens on reprint if the PDF renderer has changed since original print? Reprints always use the current renderer version — minor cosmetic differences are acceptable; field positions are determined by the stored template version's element coordinates.
- What happens when cloning a submission where a required field's element was removed in the new template version? The clone skips that field and leaves the new required field empty for the operator to fill.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a paginated table of submissions with columns: reference_number, template_name, date, status, key_field_summary (first 3 field values)
- **FR-002**: System MUST provide search by reference number (exact match) and template name (partial match)
- **FR-003**: System MUST provide filters for: date range, template name, status (submitted/printed/reprinted)
- **FR-004**: System MUST sort submissions by date descending (default) with option to sort by template name or reference number
- **FR-005**: System MUST show a detail view with all field_values in read-only form layout, plus metadata (ref, template, version, date, operator)
- **FR-006**: System MUST generate PDF from stored field_values and the original template version on "Download PDF" or "Reprint"
- **FR-007**: System MUST stamp reprinted PDFs with "REPRINT" diagonal watermark and reprint timestamp
- **FR-008**: System MUST log a FORM_REPRINTED audit event on every reprint
- **FR-009**: System MUST allow "Clone as New" which opens Form Filler pre-filled with submission's field_values
- **FR-010**: System MUST generate a new reference number for cloned submissions (not reuse original)
- **FR-011**: System MUST support single-submission export as JSON or CSV
- **FR-012**: System MUST display all text in the user's selected language (Arabic/English)
- **FR-013**: System MUST paginate at 25 items per page with configurable options (25/50/100)

### Non-Functional Requirements

- **NFR-001**: History page MUST load within 1 second for up to 1000 submissions
- **NFR-002**: Search MUST return results within 500ms
- **NFR-003**: Reprint PDF generation MUST complete within 3 seconds
- **NFR-004**: Export file generation MUST complete within 2 seconds for single submission

### Key Entities

- **Submission** (existing from feature 016): id, template_id, template_version, operator_id, org_id, field_values, reference_number, created_at
- **Reprint Record**: An audit trail entry for each reprint — links to submission, captures timestamp, operator who reprinted
- **Key Field Summary**: The first 3 non-empty field values from a submission, displayed in the history table for quick identification

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Operator finds a specific submission by reference number in under 5 seconds
- **SC-002**: 100% of reprints include "REPRINT" watermark and are logged in audit trail
- **SC-003**: History page loads within 1 second for operators with up to 1000 past submissions
- **SC-004**: Clone-as-new correctly maps all compatible field values to the current template version
- **SC-005**: All history UI text displays correctly in both Arabic (RTL) and English (LTR)
- **SC-006**: Every reprint is distinguishable from an original print (watermark + metadata)
