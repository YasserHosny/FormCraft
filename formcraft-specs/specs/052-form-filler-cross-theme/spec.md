# Feature Specification: Form Filler Cross-Theme Implementation

**Feature Branch**: `052-form-filler-cross-theme`  
**Created**: 2026-05-31  
**Status**: Draft  
**Input**: Create unified specification for Form Filler feature supporting both classic desk and new theme with real data binding, comprehensive field support, validation, conditions, tafqeet, auto-fill, and draft management

## Overview

The Form Filler is the core operational tool for filling and submitting forms in FormCraft. This feature specification documents the complete implementation covering:

- **Classic Desk**: Full-featured implementation with auto-save intervals, offline support, cloning, and extended toolbar
- **New Theme**: Streamlined implementation with focus on modern UX and performance
- **Unified Data Model**: Both implementations use the same underlying services and data structures
- **Real Data Binding**: 100% real API data—zero hardcoded mock values or fallback arrays

## Clarifications

### Session 2026-05-31

- Q: Should both themes (classic and new) support identical features or can they differ? → A: Core features (load, validate, save, submit) must match. Advanced features (offline, cloning) can be theme-specific.
- Q: How many field types must be supported? → A: Minimum 7 types (text, number, date, select, checkbox, textarea, signature) with identical validation across themes.
- Q: Should tafqeet and auto-fill be mandatory or deferred? → A: Tafqeet is P2 (deferred). Auto-fill is P2 (deferred). Core features (template, validation, conditions, draft, submit) are P1.
- Q: What is the auto-save strategy? → A: Classic: 10-second intervals. New theme: On navigation away (ngOnDestroy). Both persist to same backend.

### Session 2026-06-01

- Q: Is the route guard already in place for `/ui/desk/fill/:templateId`? → A: Yes — confirmed in `ui-redesign.routes.ts`. `RoleGuard` with `['admin', 'branch_manager', 'operator']` already applied. No change needed.
- Q: What are the valid state transitions for a Draft? → A: `in_progress → submitted` (on SubmissionService.submit() success); `in_progress → deleted` (explicit operator action); `in_progress → expired` (client: `expires_at < now`; backend: 30-day inactivity). No locked or paused states.
- Q: What is the concurrency model for concurrent draft saves? → A: Last-write-wins. The backend auto-updates `updated_at` via Supabase. The client stores `draftUpdatedAt` on load; on each save response, if `response.updated_at > draftUpdatedAt` a warning toast is shown. Save always proceeds — no locking.
- Q: What is the retry policy on submission failure? → A: 3 attempts, exponential backoff: 1s / 2s / 4s (RxJS `retry({ count: 3, delay: (_, i) => timer(Math.pow(2, i-1) * 1000) })`). After exhaustion: persistent error banner with "Retry" and "Save as Draft" buttons.
- Q: How does the new-theme route coexist with the classic desk route? → A: Both routes are live simultaneously. Classic: `/desk/fill/:templateId`. New theme: `/ui/desk/fill/:templateId`. Completely separate components — no shared state, no redirect between them. F052 touches only the new-theme component.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Load Real Template Structure (Priority: P1)

As an operator navigating to `/desk/fill/{templateId}` or `/ui/desk/fill/{templateId}`, I see the actual published template structure (sections, fields, labels, types, ordering) loaded from the system, enabling me to fill the correct form for the task at hand.

**Why this priority**: Loading the correct template is the foundational requirement. Without real template data, the form filler cannot function.

**Independent Test**: Navigate to form filler URL with valid templateId. Verify template loads with correct sections, field count, and label text matching the template definition. Test with invalid templateId to verify error handling.

**Acceptance Scenarios**:

1. **Given** a published template with 3 sections and 15 fields, **When** the operator navigates to `/desk/fill/{templateId}`, **Then** all sections and fields render with correct labels (Arabic or English per language setting).
2. **Given** a template is deprecated or unpublished, **When** the operator navigates to its filler URL, **Then** the component displays an appropriate error or warning state.
3. **Given** the backend is unreachable, **When** the form filler loads, **Then** a user-friendly error message displays with a retry option.

---

### User Story 2 - Apply Field Validation (Priority: P1)

As an operator filling a form, I see real-time validation feedback for each field based on template-defined rules, preventing invalid submissions and guiding data entry.

**Why this priority**: Validation ensures data quality. Without it, operators could submit incomplete or malformed data.

**Independent Test**: Fill form with invalid data (missing required fields, wrong formats). Verify inline error messages appear per field. Attempt submit with validation errors—verify submission is blocked.

**Acceptance Scenarios**:

1. **Given** a template with required fields, **When** the operator tries to submit with empty required fields, **Then** each missing field displays an inline error message.
2. **Given** a number field with min/max constraints, **When** the operator enters an out-of-range value, **Then** a validation error appears after field blur.
3. **Given** a text field with email pattern validation, **When** the operator enters invalid email format, **Then** validation error displays immediately.
4. **Given** the operator fixes validation errors, **When** they correct the data, **Then** error messages disappear and submit button becomes enabled.

---

### User Story 3 - Evaluate Conditional Logic (Priority: P1)

As an operator, I see fields dynamically appear and disappear based on other field values, following rules defined in the template (e.g., show "Company Name" only when "Account Type" is "Corporate").

**Why this priority**: Conditional logic enables dynamic forms that adapt to user input, reducing clutter and guiding operators through relevant fields only.

**Independent Test**: Fill form with conditional fields. Change triggering field value. Verify conditional fields show/hide immediately. Test that hidden fields are excluded from form validation.

**Acceptance Scenarios**:

1. **Given** a template with conditional field "Company Name" visible only when "Account Type" equals "Corporate", **When** the operator selects "Individual", **Then** "Company Name" field is hidden from view.
2. **Given** the operator later selects "Corporate", **When** the change is made, **Then** "Company Name" field reappears immediately.
3. **Given** a field becomes required conditionally, **When** the condition is met, **Then** the required indicator appears and validation enforces the requirement.
4. **Given** a hidden field has validation errors, **When** the field is hidden by a condition, **Then** those errors are excluded from the error summary.

---

### User Story 4 - Save and Resume Drafts (Priority: P1)

As an operator, I can save in-progress forms as drafts and resume them later, protecting against accidental data loss and enabling partial completion workflows.

**Why this priority**: Draft management enables multi-step workflows and prevents data loss, critical for forms that take time to complete.

**Independent Test**: Start filling a form, save as draft, navigate away, return to form filler with draft ID. Verify all saved values are restored. Submit draft to create submission.

**Acceptance Scenarios**:

1. **Given** an operator filling a form, **When** they click "Save Draft" or navigate away, **Then** the current form values are saved to the backend.
2. **Given** a draft exists for a template, **When** the operator navigates to `/desk/fill/{templateId}?draft={draftId}`, **Then** the form populates with saved values.
3. **Given** a draft was saved with template version 1 and template is now version 2, **When** the operator loads the draft, **Then** a warning displays offering to reload with the latest template.
4. **Given** the operator modifies a loaded draft and submits, **When** the submission succeeds, **Then** the draft record is deleted or archived.

---

### User Story 5 - Submit Completed Forms (Priority: P1)

As an operator, I submit completed and validated forms, creating submission records that can be tracked, reviewed, and reported on.

**Why this priority**: Form submission is the primary operational outcome. Without successful submission, forms cannot be processed.

**Independent Test**: Complete form with all required fields. Click Submit. Verify submission record created with reference number. Check submission appears in history/activity.

**Acceptance Scenarios**:

1. **Given** a completed and validated form, **When** the operator clicks "Submit", **Then** the submission is sent to backend and a confirmation message displays with reference number.
2. **Given** the submission succeeds, **When** the response returns, **Then** the operator is redirected to dashboard or success page.
3. **Given** a submission fails due to backend error, **When** the error occurs, **Then** a user-friendly error message displays with retry option.
4. **Given** a submission requires approval workflow, **When** submitted, **Then** status reflects "Pending Review" and operator receives confirmation.

---

### User Story 6 - Select and Auto-Fill Customer Data (Priority: P2)

As an operator, I select a customer from a picker dialog, and form fields matching the customer profile automatically populate, speeding up form entry.

**Why this priority**: Auto-fill improves operational efficiency but operators can still manually enter customer data if needed.

**Independent Test**: Click customer picker. Search and select a customer. Verify matching form fields auto-populate with customer data. Verify fields can be manually overridden.

**Acceptance Scenarios**:

1. **Given** a form with customer-mappable fields (name, phone, email) and a selected customer with profile data, **When** customer is selected, **Then** matching fields auto-populate with actual customer values.
2. **Given** auto-filled fields, **When** the operator modifies a value, **Then** the field updates normally (not locked or read-only).
3. **Given** a customer with incomplete profile data, **When** selected, **Then** only available fields populate; missing data fields remain empty.

---

### User Story 7 - Convert Numbers to Arabic Words (Priority: P2)

As an operator entering numeric amounts in forms, I see the Arabic number-to-words representation (tafqeet) displayed, improving accuracy for financial and official documents.

**Why this priority**: Tafqeet enhances document accuracy but is not required for basic form filling.

**Independent Test**: Enter amount in tafqeet-enabled numeric field. Verify Arabic words display below field. Test with various amounts and verify accuracy.

**Acceptance Scenarios**:

1. **Given** a numeric field with tafqeet enabled, **When** the operator enters "1234", **Then** the field displays the Arabic equivalent "ألف ومائتان وأربعة وثلاثون".
2. **Given** the operator changes the number, **When** the change occurs, **Then** the tafqeet updates immediately.
3. **Given** a tafqeet-disabled numeric field, **When** the operator enters a number, **Then** no tafqeet is displayed.

---

### Edge Cases

- **Template not found**: System displays error message with option to return to template list.
- **Template unpublished after pinning**: Form filler rejects access or displays deprecation warning.
- **Draft template version mismatch**: System notifies operator with option to reload or continue with saved structure.
- **Session expires during form filling**: Auto-saved draft persists; operator re-authenticates and resumes from draft.
- **Backend validation failure on submit**: System displays validation error details and allows correction.
- **Customer has duplicate or missing data**: Auto-fill handles gracefully—fills available data, skips missing fields.
- **Field with very long options list**: Dropdown renders with search capability to find options.
- **Conditional logic with complex expressions**: System evaluates expressions accurately in real-time.
- **Unauthorized access to `/ui/desk/fill/:templateId`**: `RoleGuard` redirects non-operator roles before component loads.
- **Concurrent modification of a draft**: Last-write-wins; informational toast displayed, no data loss.
- **Draft loaded after expiry (`expires_at < now`)**: Snackbar shown, operator redirected to `/ui/desk`, form not loaded.
- **Submission retry exhausted (3 attempts)**: Persistent banner with "Retry" and "Save as Draft" buttons displayed; `submitting` reset to `false`.

## Requirements *(mandatory)*

### Functional Requirements

**Template Loading & Rendering**
- **FR-001**: Form filler MUST load real template structure via `FormFillerService.getTemplate(templateId)` at component initialization.
- **FR-002**: Template MUST include sections, fields, field types, labels, validation rules, and conditional logic—all fetched from backend.
- **FR-003**: Form MUST render dynamically from template structure using ReactiveForms with FormGroup built from template elements.
- **FR-004**: Field labels MUST display in current language (Arabic or English) from template's `label_ar` and `label_en` properties.

**Field Type Support**
- **FR-005**: Form filler MUST support 7 field types: text, number, date, select, checkbox, textarea, signature—all with identical implementation across classic and new themes.
- **FR-006**: Select fields MUST populate options from template's `options` array fetched from backend (never hardcoded).
- **FR-007**: All field values MUST bind to reactive form controls and sync bidirectionally with form data.

**Validation System**
- **FR-008**: Form filler MUST apply validation rules from template element definitions: `required`, `pattern`, `min`, `max`, `custom_rule`.
- **FR-009**: Validation rules MUST load from `ValidationService` based on field type and country-specific constraints.
- **FR-010**: Inline validation errors MUST display below each field when touched and invalid, showing specific error message (e.g., "Email format invalid").
- **FR-011**: Form submission MUST be blocked when any visible required field is invalid.
- **FR-012**: Error summary panel MUST list all current validation errors with field names and error descriptions.

**Conditional Logic**
- **FR-013**: Form filler MUST evaluate conditional visibility rules from `element.visible_when` and display/hide fields accordingly in real-time.
- **FR-014**: Form filler MUST evaluate conditional requirement rules from `element.required_when` and toggle required validators dynamically.
- **FR-015**: Hidden fields MUST be excluded from form validation and submission. Implementation: `ctrl.disable({ emitEvent: false })` for invisible fields; Angular's `formGroup.value` auto-excludes disabled controls.
- **FR-016**: Conditional logic MUST behave identically across classic desk and new theme implementations. Verified by classic desk regression test (T063).

**Draft Management**
- **FR-017**: Form filler MUST auto-save form state as a draft when operator navigates away, preventing data loss.
- **FR-018**: Draft MUST be saved to backend via `DraftService.saveDraft()` or `DraftService.updateDraft()` with all field values and metadata.
- **FR-019**: Form filler MUST load and populate draft data via `DraftService.getDraft(draftId)` when draft ID is provided.
- **FR-020**: If loaded draft's template version differs from current published version, system MUST open `VersionWarningComponent` dialog (not snackbar) with options to reload or continue.
- **FR-021**: Draft MUST persist customer reference, operator ID, timestamps, and completion metadata. The `completion_percent` field MUST be calculated via `calculateCompletion()` and passed to every `saveDraft()` / `updateDraft()` call.

**Form Submission**
- **FR-022**: Form filler MUST validate all visible required fields before allowing submission.
- **FR-023**: Submission MUST call `SubmissionService.submit(templateId, version, fieldValues)` with complete form data.
- **FR-024**: Backend MUST create submission record with reference number, timestamp, operator ID, template version, and field values.
- **FR-025**: Successful submission MUST display confirmation with `response.reference_number` (via `DESK.FILL.SUBMIT_SUCCESS` i18n key) and navigate to `/ui/desk` after 2 seconds.
- **FR-026**: Submission failures MUST trigger up to 3 retry attempts (exponential backoff: 1s / 2s / 4s). After exhaustion, a persistent error banner displays with "Retry" and "Save as Draft" options.

**Customer Auto-Fill**
- **FR-027**: Form filler MUST display customer picker dialog allowing operator to search and select customer.
- **FR-028**: Selected customer MUST trigger auto-fill via `CustomerService.getAutoPopulateData(customerId, templateId)`.
- **FR-029**: Auto-fill MUST populate form fields mapped to customer profile data via `AutoFillService.executeAutoFill()`.
- **FR-030**: Auto-filled fields MUST remain editable—operator can modify any value.

**Tafqeet Integration**
- **FR-031**: Numeric fields with `tafqeet_enabled === true` MUST compute Arabic number-to-words representation via `FillerTafqeetService.compute()`.
- **FR-032**: Tafqeet result MUST display below numeric field in real-time as operator enters/modifies value.

**Data Binding & Real Data**
- **FR-033**: All form data MUST come from real backend APIs—zero hardcoded mock data, no fallback arrays, no feature flags.
- **FR-034**: Template elements, field options, validation rules, and customer data MUST be fetched from database at runtime.
- **FR-035**: System MUST handle empty datasets gracefully without rendering broken UI. Specifically: (a) a template with zero sections renders a non-empty, translated error state message (not a blank page); (b) a select field with zero options renders an empty `<select>` or `<mat-select>` without throwing JavaScript exceptions; (c) a customer search with zero results renders an empty-state message, not an empty list silently.

**Internationalization & Accessibility**
- **FR-036**: Form labels, placeholders, error messages, and UI text MUST support both Arabic (RTL) and English (LTR) without layout breakage.
- **FR-037**: Field labels MUST display with required indicator (*) for mandatory fields.
- **FR-038**: Error messages MUST be clear, actionable, and match the current language setting.
- **FR-039**: ALL UI strings in both `.ts` and `.html` files MUST use `TranslateService` / `translate` pipe — zero hardcoded Arabic or English strings anywhere in the component.

**Cross-Theme Consistency**
- **FR-040**: Classic desk and new theme implementations MUST support identical core features: load, validate, save draft, submit.
- **FR-041**: Field rendering, validation behavior, and conditional logic MUST be identical across themes.
- **FR-042**: Theme-specific features (offline, cloning, extended toolbar) can differ but must not affect core form functionality.

**Authentication & Authorization**
- **FR-043**: Route `/ui/desk/fill/:templateId` MUST be protected by `RoleGuard` with roles `['admin', 'branch_manager', 'operator']`. (Already applied in `ui-redesign.routes.ts` — no code change required.)

**Draft State Management (Clarification 2026-06-01)**
- **FR-044**: Draft state machine: `in_progress → submitted` (on successful submission); `in_progress → deleted` (explicit operator action); `in_progress → expired` (client: `expires_at < now`; backend: 30-day inactivity).
- **FR-045**: On draft load, if `new Date(draft.expires_at) < new Date()` → show `DESK.FILL.DRAFT_EXPIRED` snackbar → navigate to `/ui/desk` → abort load.

**Concurrency (Clarification 2026-06-01)**
- **FR-046**: Last-write-wins concurrency: `draftUpdatedAt` stored on load; on save response if `response.updated_at > draftUpdatedAt` → show `DESK.FILL.DRAFT_CONCURRENT_MODIFIED` toast (informational only, save already applied). Always update `draftUpdatedAt = response.updated_at`.

**Submission Retry (Clarification 2026-06-01)**
- **FR-047**: Submission retry uses `retry({ count: 3, delay: (_, i) => timer(Math.pow(2, i-1) * 1000) })` from RxJS 7. After exhaustion: `showRetryBanner = true`, `submissionError = translate('DESK.FILL.SUBMIT_RETRY_EXHAUSTED')`, `submitting = false`.

### Key Entities

- **FillTemplate**: Complete template structure with pages, sections, and elements (fetched from backend)
- **TemplateElement**: Individual field definition with type, label, validation rules, visibility/required conditions
- **DraftResponse**: In-progress form with saved field values, template version, `updated_at` (for concurrency), `expires_at`, and `completion_percent`
- **Submission**: Completed form record with `reference_number`, status, and all field values
- **Customer**: Profile record used for auto-fill mapping to form fields

**Draft State Machine** (Clarification 2026-06-01):
```
in_progress → submitted   (SubmissionService.submit() success)
in_progress → deleted     (explicit operator action)
in_progress → expired     (client: expires_at < now; backend: 30-day inactivity)
```

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All template data is fetched from real backend APIs with zero hardcoded mock data in components.
- **SC-002**: Operators can complete a full form workflow (load → validate → save/resume → submit) entirely in either theme without fallback to other implementations.
- **SC-003**: Form validation errors display inline within 300ms of field blur event.
- **SC-004**: Conditional field visibility/requirement changes evaluate and render within 200ms of triggering value change.
- **SC-005**: Auto-fill from customer profile populates matching fields within 500ms of customer selection.
- **SC-006**: Tafqeet computes and displays within 200ms of numeric field value change.
- **SC-007**: Draft auto-save completes within 2 seconds without blocking user interaction.
- **SC-008**: Form submission succeeds or fails with clear feedback within 3 seconds of submit button click (excluding retry delay intervals).
- **SC-009**: 100% of core features (load, validate, save, submit) behave identically across classic and new theme implementations — verified by classic desk regression spec (T063).
- **SC-010**: All content displays correctly in both Arabic (RTL) and English (LTR) with no layout issues.
- **SC-011**: System handles edge cases gracefully (missing templates, empty data, backend errors) without crashes or broken UI.
- **SC-012**: Draft expiry check redirects operator to `/ui/desk` within one navigation cycle — no partial form render on expired drafts.
- **SC-013**: Submission retry exhaustion is reached within 7 seconds maximum (1s + 2s + 4s backoff) with persistent banner displayed immediately after final failure.
- **SC-014**: Zero hardcoded Arabic or English UI strings in `form-filler.component.ts` or `form-filler.component.html` — all text via `TranslateService` / `translate` pipe.

## Assumptions

- All required backend APIs exist and are used by the classic desk. No new backend endpoints required.
- Classic desk services (`FormFillerService`, `DraftService`, `SubmissionService`, `ValidationService`, `ConditionEngineService`, `AutoFillService`, `FillerTafqeetService`) can be imported directly into new theme standalone components.
- Template version compatibility is managed by backend—component displays warning for mismatches but does not enforce version constraints.
- All field options, validation rules, and conditional logic are stored in template definition—no separate configuration tables.
- Customer auto-fill mappings are determined by backend API response, not frontend configuration.
- Performance targets assume standard backend response times (< 1s for most APIs).
- Form filler implements Reactive Forms (`FormGroup`) for consistency with rest of application.
- Draft persistence uses same backend table structure for both implementations.
- `VersionWarningComponent` at `features/desk/components/version-warning/` is reused as-is — no new dialog component required.
- The new-theme route `/ui/desk/fill/:templateId` and classic route `/desk/fill/:templateId` coexist without redirect; F052 is exclusively frontend, new-theme component only.
