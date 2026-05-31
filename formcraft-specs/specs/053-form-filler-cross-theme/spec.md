# Feature Specification: Form Filler Cross-Theme Implementation

**Feature Branch**: `053-form-filler-cross-theme`  
**Created**: 2026-05-31  
**Status**: Draft  
**Input**: Unified specification for the Form Filler (/desk/fill/{templateId} and /ui/desk/fill/{templateId}) covering both the classic desk and new theme implementations, with real data binding, comprehensive field support, validation, conditional logic, tafqeet, customer auto-fill, and draft management

## Overview

The Form Filler is the core operational tool for filling and submitting forms in FormCraft. This specification covers both implementations end-to-end:

- **Classic Desk** (`/desk/fill/{templateId}`): Full-featured implementation — auto-save intervals, offline sync, submission cloning, extended toolbar, feedback dialog, print dialog
- **New Theme** (`/ui/desk/fill/{templateId}`): Streamlined standalone component — modern UX, completion progress bar, side-panel section navigation
- **Unified Data Model**: Both implementations use the same services, data structures, and backend APIs
- **Real Data Only**: Zero hardcoded mock values. All data — template structure, options, validation rules, customer data — is fetched from backend at runtime

## Clarifications

### Session 2026-05-31

- **Theme parity**: Core features (load template, validate, save draft, submit) must be identical across both themes. Advanced features (offline, cloning, print queue) are classic-only.
- **Field types**: Minimum 7 types supported: text, number, date, select, checkbox, textarea, signature — same behaviour in both themes.
- **Tafqeet & auto-fill priority**: P2 (defer after core). Core features (template rendering, validation, conditions, draft, submit) are P1.
- **Auto-save strategy**: Classic — periodic 10-second interval plus `ngOnDestroy`. New theme — `ngOnDestroy` only. Both persist to the same `drafts` table.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Load Real Template Structure (Priority: P1)

As an operator navigating to the form filler URL, I see the actual published template structure — sections, fields, labels, types, ordering — loaded from the system so I can fill the correct form for the task at hand.

**Why this priority**: Template loading is the foundational requirement. Without real template data the form cannot function.

**Independent Test**: Navigate to `/desk/fill/{templateId}` and `/ui/desk/fill/{templateId}` with a valid published template. Verify sections, field count, and label text match the template definition. Repeat with an invalid/unpublished template and verify graceful error handling.

**Acceptance Scenarios**:

1. **Given** a published template with 3 sections and 15 fields, **When** the operator opens the form filler, **Then** all 3 sections and 15 fields render with correct labels in the current language (Arabic or English).
2. **Given** a deprecated template, **When** the form filler loads, **Then** a deprecation warning banner is shown and the operator can still fill the form.
3. **Given** the backend is unreachable, **When** the form filler loads, **Then** a user-friendly error state displays with a retry option — no mock data shown.

---

### User Story 2 — Apply Field Validation (Priority: P1)

As an operator filling a form, I receive real-time validation feedback for each field based on rules defined in the template, preventing invalid submissions and guiding correct data entry.

**Why this priority**: Validation ensures data quality and prevents backend rejection of malformed submissions.

**Independent Test**: Fill a form with invalid data (blank required fields, wrong format, out-of-range numbers). Attempt to submit and verify each failing field shows a specific inline error. Fix each error and confirm it disappears.

**Acceptance Scenarios**:

1. **Given** required fields are left blank, **When** the operator attempts to submit, **Then** each blank required field shows an inline error and submission is blocked.
2. **Given** a number field with min=0 max=1000, **When** the operator enters -5, **Then** a validation error appears after the field loses focus.
3. **Given** an email-pattern field, **When** the operator enters "not-an-email", **Then** a validation error appears immediately.
4. **Given** the operator corrects all errors, **When** the form becomes valid, **Then** all error messages disappear and the submit button is enabled.

---

### User Story 3 — Evaluate Conditional Logic (Priority: P1)

As an operator, form fields dynamically appear and disappear in real-time based on other field values, following rules embedded in the template (e.g., show "Company Name" only when "Account Type" is "Corporate").

**Why this priority**: Conditional logic reduces visual clutter, ensures relevance of collected data, and must behave identically to the classic desk for operational trust.

**Independent Test**: Open a template with conditional fields. Change the triggering field and verify dependent fields appear/disappear instantly. Verify hidden fields are excluded from validation and submission payload.

**Acceptance Scenarios**:

1. **Given** "Company Name" is `visible_when: account_type == 'Corporate'`, **When** the operator selects "Individual", **Then** "Company Name" is immediately hidden.
2. **Given** the operator changes to "Corporate", **Then** "Company Name" appears immediately.
3. **Given** a field is `required_when: employment_status == 'Employed'`, **When** that condition is met, **Then** the required indicator (*) appears and validation enforces the field.
4. **Given** a conditionally hidden field has a validation error, **When** the field is hidden, **Then** its error is removed from the error summary and does not block submission.

---

### User Story 4 — Save and Resume Drafts (Priority: P1)

As an operator, I can save in-progress forms as drafts and resume them later, protecting against accidental data loss and supporting multi-step completion workflows.

**Why this priority**: Drafts prevent loss of partial work. Many forms take significant time to complete and operators are frequently interrupted.

**Independent Test**: Start filling a form, save as draft, close/navigate away, reopen with the draft ID. Verify all saved values are restored exactly. Submit the resumed draft and confirm submission created.

**Acceptance Scenarios**:

1. **Given** an operator partially fills a form and clicks "Save Draft" or navigates away, **When** the action occurs, **Then** all current field values are persisted to the backend draft record.
2. **Given** a saved draft, **When** the operator reopens it via `/desk/fill/{templateId}?draft={draftId}`, **Then** all previously entered values are restored in the form.
3. **Given** a draft was saved at template version 1 and the template is now version 2, **When** the draft is loaded, **Then** a version mismatch warning displays, offering the option to reload with the latest template structure.
4. **Given** the operator submits a resumed draft, **When** submission succeeds, **Then** the draft record is archived/deleted.

---

### User Story 5 — Submit Completed Forms (Priority: P1)

As an operator, I submit a completed validated form and receive a reference number confirming the submission was created and is ready for processing.

**Why this priority**: Submission is the primary business outcome of the form filler. Without it, no form reaches the approval/processing pipeline.

**Independent Test**: Complete a form in both classic and new theme. Submit in each. Verify a submission record exists in the database with reference number, operator ID, template version, and all field values.

**Acceptance Scenarios**:

1. **Given** all required fields are filled and valid, **When** the operator clicks "Submit", **Then** the submission is sent to the backend and a success confirmation with reference number is shown.
2. **Given** successful submission, **When** the page redirects, **Then** the operator returns to the desk dashboard or a submission-confirmed screen.
3. **Given** a backend submission failure (e.g., network error), **When** the error occurs, **Then** a user-friendly error message displays with a retry option and the form data is preserved.
4. **Given** a template with an approval workflow, **When** submitted, **Then** the submission status shows "Pending Review" and the operator is notified.

---

### User Story 6 — Customer Auto-Fill (Priority: P2)

As an operator, I search for and select a customer from the customer picker, and form fields mapped to the customer profile auto-populate, reducing manual entry time and transcription errors.

**Why this priority**: Auto-fill improves operational speed. Core functionality works without it.

**Independent Test**: Click the customer picker in the form header. Search and select a customer with a complete profile. Verify mapped fields (name, phone, email, ID) populate with actual customer data. Modify one auto-filled value and verify it is editable.

**Acceptance Scenarios**:

1. **Given** a customer with profile data and a template with mapped fields, **When** the customer is selected, **Then** all mapped fields populate with the customer's actual data.
2. **Given** auto-filled fields, **When** the operator edits a value, **Then** the field updates normally (not locked or overridden).
3. **Given** a customer with an incomplete profile, **When** selected, **Then** only available fields populate — fields with no mapping remain empty.
4. **Given** no customer is selected, **When** the form loads, **Then** all fields start empty, no placeholder customer data is shown.

---

### User Story 7 — Tafqeet: Arabic Number-to-Words (Priority: P2)

As an operator entering numeric amounts in fields with tafqeet enabled, I see the Arabic written representation of the number displayed in real-time, reducing errors in financial and official documents.

**Why this priority**: Tafqeet adds accuracy for specific document types. Core form filling works without it.

**Independent Test**: Enter values in a tafqeet-enabled numeric field. Verify the Arabic word form appears beneath the field and updates as the operator types. Verify non-tafqeet fields show no Arabic words.

**Acceptance Scenarios**:

1. **Given** a tafqeet-enabled field, **When** the operator enters "12345", **Then** the Arabic text "اثنا عشر ألفاً وثلاثمائة وخمسة وأربعون" displays below the field.
2. **Given** the operator clears the value, **When** the field becomes empty, **Then** the tafqeet text also clears.
3. **Given** a field without tafqeet, **When** the operator enters a number, **Then** no Arabic word text appears.

---

### Edge Cases

- **Template not found or forbidden**: Form filler shows error state with a "Return to templates" link. No mock template is loaded.
- **Template unpublished mid-session**: If still loaded in memory, submission is rejected by backend; filler shows error and advises checking template status.
- **Draft version mismatch**: Warning shown, operator chooses: continue with saved structure or reload latest version.
- **Session expiry during filling**: Auto-save persists draft before expiry; operator re-authenticates and finds the draft waiting.
- **Backend submit validation failure**: Backend-side errors returned and displayed as field-level or form-level messages.
- **Empty options list on a select field**: Select renders with only the placeholder option; a warning note is shown if the list is empty.
- **All conditional fields hidden**: Form renders the visible non-conditional fields only; submit is permitted if all visible required fields pass validation.
- **Concurrent edit of same draft**: Last write wins; no collaborative editing.

## Requirements *(mandatory)*

### Functional Requirements

#### Template Loading & Rendering
- **FR-001**: Form filler MUST call `FormFillerService.getTemplate(templateId)` at initialization and use the returned `FillTemplate` as the sole source of form structure.
- **FR-002**: Template pages and their elements MUST map directly to rendered sections and fields — no hardcoded sections, no placeholders.
- **FR-003**: Field labels MUST use `element.label_ar` when current language is Arabic and `element.label_en` when English.
- **FR-004**: A loading skeleton MUST display while the template fetch is in progress. An error state with retry MUST display on failure.

#### Field Types
- **FR-005**: Both implementations MUST render: `text`, `number`, `date`, `select`, `checkbox`, `textarea`, `signature`.
- **FR-006**: Select field `options` MUST be populated from `element.options` (fetched as part of the template) — never hardcoded.
- **FR-007**: All field values MUST be bound to Angular reactive `FormControl` instances keyed by `element.key`.

#### Validation
- **FR-008**: Validators MUST be applied from `element.required`, `element.validation.pattern`, `element.validation.min`, `element.validation.max`, and `element.validation.custom_rule`.
- **FR-009**: Country-specific validators MUST be loaded via `ValidationService.getValidatorFn(element)`.
- **FR-010**: Validation errors MUST appear inline below each field only after the field has been touched.
- **FR-011**: Submission MUST be blocked while any visible required field is invalid.
- **FR-012**: An error summary panel MUST list all current validation errors with field names.

#### Conditional Logic
- **FR-013**: `ConditionEngineService` MUST be initialized with all template elements and the form group.
- **FR-014**: Field visibility MUST update in real-time from `conditionEngine.visibilityChanged$` observable.
- **FR-015**: Field requirement MUST update in real-time from `conditionEngine.requiredChanged$` observable.
- **FR-016**: Hidden fields MUST be removed from validation and excluded from submission payload.
- **FR-017**: Conditional logic behaviour MUST be identical between the classic desk and new theme.

#### Draft Management
- **FR-018**: On navigation away, form filler MUST call `DraftService.saveDraft()` or `updateDraft()` with current `formGroup.value`, `templateId`, and `template.version`.
- **FR-019**: Classic desk MUST additionally auto-save on a 10-second interval.
- **FR-020**: When `draftId` is present in query params, form filler MUST call `DraftService.getDraft(draftId)` and patch the form with returned `field_values`.
- **FR-021**: If `draft.template_version !== template.version`, a mismatch warning MUST be shown offering to reload or continue.

#### Form Submission
- **FR-022**: Submission MUST call `SubmissionService.submit(templateId, version, visibleFieldValues)`.
- **FR-023**: Only values for currently visible fields MUST be included in the submission payload.
- **FR-024**: On success, a snackbar or confirmation screen MUST display the backend-returned `reference_number`.
- **FR-025**: On backend failure, a user-friendly error MUST display; form data MUST be preserved for retry.

#### Customer Auto-Fill (P2)
- **FR-026**: A customer picker dialog MUST allow search by name, phone, or national ID.
- **FR-027**: On customer selection, form filler MUST call `CustomerService.getAutoPopulateData(customerId, templateId)`.
- **FR-028**: `AutoFillService.executeAutoFill(mappings, formGroup)` MUST populate matched form controls.
- **FR-029**: Auto-filled fields MUST remain fully editable.

#### Tafqeet (P2)
- **FR-030**: Fields with `element.tafqeet_enabled === true` MUST subscribe to `valueChanges` and call `FillerTafqeetService.compute(value)`.
- **FR-031**: The computed Arabic word-form MUST render below the numeric field and update on every value change.

#### Real Data Guarantee
- **FR-032**: Zero hardcoded mock data, placeholder arrays, or fallback values are permitted in either implementation.
- **FR-033**: All field options, validation rules, conditions, and customer mappings MUST be derived from backend API responses at runtime.
- **FR-034**: Empty datasets (no options, no customers, no drafts) MUST render graceful empty states — not broken UI.

#### Internationalisation & Layout
- **FR-035**: All labels, placeholders, error messages, and UI text MUST support Arabic (RTL) and English (LTR).
- **FR-036**: Required field indicators (*) MUST display for fields where `element.required === true` or where `requiredKeys` set includes the field key.

#### Cross-Theme Consistency
- **FR-037**: Implementations MUST share the same service calls, data models, and validation behaviour.
- **FR-038**: Theme-specific extras (offline, cloning, feedback, print-next) are permitted but MUST NOT affect core form behaviour.

### Key Entities

| Entity | Description |
|---|---|
| `FillTemplate` | Complete template with pages, elements, version, country — loaded from backend |
| `TemplateElement` | Single field: type, label_ar, label_en, required, validation, visible_when, required_when, tafqeet_enabled |
| `Draft` | In-progress form: id, template_id, template_version, field_values (JSON), created_at, updated_at |
| `Submission` | Completed form: id, reference_number, status, template_id, version, field_values |
| `Customer` | Profile used for auto-fill: name, phone, email, national_id, and mapped field values |
| `AutoFillMapping` | Map of template field keys → customer values, returned by CustomerService |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of template structure (sections, fields, labels, options) is loaded from backend APIs — zero hardcoded values in either implementation.
- **SC-002**: Operators complete a full form workflow (load → fill → validate → draft → submit) in both classic desk and new theme without any mock data appearing.
- **SC-003**: Inline validation errors appear within 300ms of a field losing focus.
- **SC-004**: Conditional field visibility/requirement changes render within 200ms of the triggering value change.
- **SC-005**: Customer auto-fill populates matched fields within 500ms of customer selection.
- **SC-006**: Tafqeet text updates within 200ms of each keystroke in a tafqeet-enabled field.
- **SC-007**: Draft auto-save completes in the background within 2 seconds without blocking UI interaction.
- **SC-008**: Form submission returns confirmation or error within 3 seconds of the submit action.
- **SC-009**: Conditional logic behaviour is identical between classic desk and new theme across all tested templates.
- **SC-010**: All UI text, labels, and errors display correctly in both Arabic (RTL) and English (LTR) with no layout breakage.
- **SC-011**: All edge cases (missing template, empty options, draft mismatch, submission failure) produce appropriate UI states with no crashes.

## Assumptions

- All backend APIs used by the classic desk already exist and are stable; no new endpoints are required for this feature.
- `ValidationService`, `ConditionEngineService`, `AutoFillService`, and `FillerTafqeetService` are `providedIn: 'root'` and importable directly into new-theme standalone components.
- Template options lists, validation rules, and conditional expressions are stored in the template definition returned by `FormFillerService.getTemplate()`.
- Customer auto-fill mappings are fully determined by the backend response — no frontend mapping configuration is needed.
- Draft table schema is identical for both implementations; no schema changes are needed.
- Both implementations use Angular Reactive Forms (`FormGroup` / `FormControl`).
- Performance targets assume standard backend latency (< 1s for template and draft fetches).
