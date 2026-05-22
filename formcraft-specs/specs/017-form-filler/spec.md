# Feature Specification: Form Filler

**Feature Branch**: `016-form-filler`  
**Created**: 2026-05-16  
**Status**: Draft  
**Input**: Form Desk Form Filler (FD-02) — the daily workhorse for operators filling published templates with live validation, tafqeet auto-computation, and keyboard-optimized flow layout

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Flow Layout Form Filling (Priority: P1)

When an operator selects a published template from the dashboard, the Form Filler opens at `/desk/fill/:templateId` and renders all fields in Flow Layout mode — fields stacked vertically by page, grouped logically, optimized for keyboard-driven data entry. Tab moves between fields in sort_order sequence.

**Why this priority**: This is the absolute minimum — operators must be able to fill fields and see them rendered. Without this, no form can be completed on the platform.

**Independent Test**: Select any published template with text/number/date fields → verify Form Filler renders all fields as Angular Material form controls → Tab between fields → type values → verify data captures correctly.

**Acceptance Scenarios**:

1. **Given** an operator navigates to `/desk/fill/:templateId`, **When** the page loads, **Then** all elements from the template's pages are rendered as interactive form controls in Flow Layout (vertical stack)
2. **Given** a template has 3 pages with 5 elements each, **When** the form loads, **Then** all 15 fields render in sort_order within each page, with page dividers
3. **Given** the operator presses Tab after filling a field, **When** focus moves, **Then** the next field in sort_order receives focus
4. **Given** a field has `direction: "rtl"`, **When** it renders, **Then** the input is right-aligned with RTL text direction
5. **Given** the operator fills all fields, **When** they review the form, **Then** all values are held in component state ready for submission

---

### User Story 2 - Live Field Validation (Priority: P1)

As the operator fills fields, real-time validation fires on blur. Required fields show errors when left empty. Fields with validation rules (regex, min/max, country-specific validators) display inline bilingual error messages. A form-level summary shows remaining errors.

**Why this priority**: Equal to P1 because forms without validation produce garbage data. The entire platform's value is accuracy — validation is non-negotiable from day one.

**Independent Test**: Fill a national ID field with 13 digits (invalid — should be 14) → verify inline error appears. Leave a required field empty and tab away → verify required error shows. Fix all errors → verify error summary disappears and submit becomes enabled.

**Acceptance Scenarios**:

1. **Given** a required field is left empty, **When** the field loses focus (blur), **Then** an inline error "هذا الحقل مطلوب" / "This field is required" appears below the field
2. **Given** a field has validation rule `{ "pattern": "^\\d{14}$" }`, **When** the operator types "12345" and blurs, **Then** an inline error appears with the validation message
3. **Given** the template's country is "EG" and a field key matches a registered validator (e.g., `national_id`), **When** the operator types an invalid value, **Then** the country-specific validator fires and shows its error message
4. **Given** 3 fields have validation errors, **When** the operator views the form, **Then** a top banner shows "3 errors remaining" (translated)
5. **Given** all required fields are filled and all validations pass, **When** the operator checks the form state, **Then** the error banner disappears and the "Print" button becomes enabled

---

### User Story 3 - Tafqeet Auto-Computation (Priority: P1)

When a tafqeet element is linked to a currency/number source field, the tafqeet field auto-computes the Arabic amount-in-words as the operator types. The tafqeet field is read-only and updates live.

**Why this priority**: Banks require amount-in-words on every cheque. Without live tafqeet, operators must manually compute and type Arabic number words — error-prone and slow.

**Independent Test**: Open a template with a currency field linked to a tafqeet field → type "1500.25" → verify tafqeet field instantly shows "ألف وخمسمائة جنيه مصري وخمسة وعشرون قرشاً".

**Acceptance Scenarios**:

1. **Given** a tafqeet element has `formatting.sourceElementKey` pointing to a currency field, **When** the operator types "1500.25" in the source field, **Then** the tafqeet field shows the Arabic words equivalent
2. **Given** the source field is empty, **When** the form loads, **Then** the tafqeet field shows placeholder text or remains empty
3. **Given** the operator clears the source field value, **When** the value becomes empty, **Then** the tafqeet field clears
4. **Given** tafqeet is configured for "both" languages, **When** the amount is entered, **Then** both Arabic and English text renders

---

### User Story 4 - Form Toolbar & Actions (Priority: P1)

The Form Filler toolbar provides actions: Save Draft (Ctrl+S), Preview PDF, Print, Print & Next, Clear All, and Cancel. The Print button is disabled until validation passes.

**Why this priority**: Without at minimum Print and Cancel, the form has no output. Save Draft enables interruption recovery. These are the minimum viable actions.

**Independent Test**: Fill a form completely → click Print → verify PDF generation triggers. Click Cancel → verify navigation back to dashboard. Press Ctrl+S → verify draft saved.

**Acceptance Scenarios**:

1. **Given** all validations pass, **When** the operator clicks "Print", **Then** the PDF is generated with filled values and the browser print dialog opens
2. **Given** validation errors exist, **When** the operator views the toolbar, **Then** the "Print" button is disabled with a tooltip explaining errors remain
3. **Given** the operator clicks "Save Draft", **When** the action completes, **Then** form data is persisted as a draft and a success toast appears
4. **Given** the operator presses Ctrl+S, **When** the keyboard shortcut fires, **Then** the Save Draft action triggers
5. **Given** the operator clicks "Cancel", **When** the dialog confirms, **Then** navigation returns to `/desk` without saving
6. **Given** the operator clicks "Clear All", **When** they confirm, **Then** all field values reset to empty/defaults
7. **Given** the operator clicks "Print & Next", **When** the print completes, **Then** the form resets for the next entry (same template, empty fields)

---

### User Story 5 - Draft Save & Resume (Priority: P2)

Operators can save partially filled forms as drafts. Drafts are persisted server-side, appear on the dashboard, and can be resumed with all previously entered data restored. Drafts auto-expire after a configurable period.

**Why this priority**: Prevents data loss on interruption but the system is usable without it (operators can refill). Critical for complex forms that take 10+ minutes.

**Independent Test**: Fill 5 out of 10 fields → Save Draft → navigate away → return via dashboard "Resume" → verify all 5 values restored.

**Acceptance Scenarios**:

1. **Given** the operator has filled 5 of 10 required fields, **When** they click "Save Draft", **Then** a draft record is created with all current field values
2. **Given** a draft exists for template X, **When** the operator navigates to `/desk/fill/:templateId?draft=:draftId`, **Then** all previously saved values are restored into the form controls
3. **Given** a draft was saved against template v2 but template is now v3, **When** resuming, **Then** a warning shows "Template updated since draft was saved" with options to continue with old version data or discard
4. **Given** a draft is older than the org's expiry period (default 7 days), **When** the operator tries to resume, **Then** the draft is marked expired and cannot be resumed
5. **Given** an auto-save fires (every 60 seconds while form is open), **When** the timer triggers, **Then** the draft is silently updated without disrupting the operator

---

### User Story 6 - Submission & Audit Trail (Priority: P1)

When the operator prints a form, a submission record is created with a unique reference number, linked to the template version, operator, and all field values. This enables history lookup and reprint.

**Why this priority**: Without a submission record, there's no proof a form was filled and no way to find it later. The audit trail is a constitution requirement.

**Independent Test**: Print a form → verify a reference number is generated (FC-YYYY-MM-NNNN format) → verify the submission appears in history → verify audit log entry created.

**Acceptance Scenarios**:

1. **Given** the operator prints a valid form, **When** the print succeeds, **Then** a submission record is created with a unique reference number
2. **Given** the submission is created, **When** checking its data, **Then** it includes: template_id, template_version, operator_id, org_id, field_values (JSONB), created_at, reference_number
3. **Given** the reference number format is `FC-{YYYY}-{MM}-{sequence}`, **When** a submission is created, **Then** the sequence auto-increments per month per org
4. **Given** a successful print, **When** the audit log is checked, **Then** a FORM_SUBMITTED event exists with operator, template, reference_number, and IP

---

### Edge Cases

- What happens when a template has zero fillable fields (only static/tafqeet elements)? The form shows a message "This template has no fillable fields" and enables Print immediately.
- What happens when the operator navigates away with unsaved changes? A browser beforeunload prompt warns "You have unsaved changes."
- What happens when the network drops during draft save? Toast shows "Save failed — will retry" and auto-retries on reconnection.
- What happens when two operators fill the same template simultaneously? No conflict — each creates their own independent submission. Drafts are per-operator.
- What happens with very long forms (50+ fields)? Flow Layout is scrollable; a sticky error summary banner remains visible at the top.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST render all template elements as interactive Angular Material form controls in Flow Layout (vertical stack by sort_order)
- **FR-002**: System MUST support all existing element types: text, number, date, currency, dropdown, radio, checkbox, image, QR, barcode, tafqeet
- **FR-003**: System MUST validate fields on blur with inline bilingual error messages (Arabic + English based on user language)
- **FR-004**: System MUST enforce required field validation — block print until all required fields are filled
- **FR-005**: System MUST apply country-specific validators (from ValidatorRegistry) when the element key matches a registered validator
- **FR-006**: System MUST auto-compute tafqeet fields in real-time when their linked source field value changes
- **FR-007**: System MUST display a form-level error summary banner showing the count of remaining validation errors
- **FR-008**: System MUST provide toolbar with: Save Draft, Preview PDF, Print, Print & Next, Clear All, Cancel
- **FR-009**: System MUST support keyboard shortcuts: Ctrl+S (save draft), Ctrl+P (print), Ctrl+Enter (print & next)
- **FR-010**: System MUST generate a PDF with filled values on Print action using the existing PDF render endpoint
- **FR-011**: System MUST create a submission record on successful print with unique reference number and full audit trail
- **FR-012**: System MUST persist drafts server-side with field_values, completion percentage, and expiry tracking
- **FR-013**: System MUST auto-save drafts every 60 seconds while the form is open (silent, non-blocking)
- **FR-014**: System MUST restore draft data when navigating to `/desk/fill/:templateId?draft=:draftId`
- **FR-015**: System MUST warn on template version mismatch between draft and current published version
- **FR-016**: System MUST display bilingual labels for all fields (label_ar when language=ar, label_en when language=en)
- **FR-017**: System MUST support Tab navigation between fields in sort_order sequence across all pages

### Non-Functional Requirements

- **NFR-001**: Form Filler MUST load and render all fields within 1 second for templates with up to 50 elements
- **NFR-002**: Tafqeet computation MUST update within 200ms of keystroke
- **NFR-003**: Validation MUST execute within 100ms on blur (no perceptible delay)
- **NFR-004**: Draft save (auto-save and manual) MUST be non-blocking — operator typing is never interrupted
- **NFR-005**: PDF generation MUST complete within 3 seconds for A4 single-page forms

### Key Entities

- **Submission**: A completed form filling event — template_id, template_version, operator_id, org_id, field_values (JSONB), reference_number, created_at
- **Draft**: A partially filled form — template_id, template_version, operator_id, org_id, field_values (JSONB), completion_percent, created_at, updated_at, expires_at
- **Field Value Map**: A JSONB object keyed by element.key containing the operator's entered values — `{ "national_id": "12345678901234", "amount": 1500.25 }`
- **Reference Number**: Unique identifier for submissions — format `FC-{YYYY}-{MM}-{org_sequence}`, auto-incremented per org per month

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Operator can complete a 10-field form in under 2 minutes using Flow Layout with Tab navigation
- **SC-002**: 100% of validation errors caught before print (zero invalid PDFs generated)
- **SC-003**: Tafqeet updates appear within 200ms — no visible lag as operator types amount
- **SC-004**: Draft save succeeds within 500ms; auto-save never blocks typing
- **SC-005**: Every submission has a unique reference number and complete audit log entry
- **SC-006**: Form loads within 1 second for templates with up to 50 elements
- **SC-007**: All form labels and error messages display correctly in both Arabic (RTL) and English (LTR)
