# Tasks: Form Filler Cross-Theme Implementation (F053)

**Input**: Design documents from `formcraft-specs/specs/053-form-filler-cross-theme/`
**Branch**: `053-form-filler-cross-theme` | **Generated**: 2026-06-01
**User Stories**: 7 (US1–US5 are P1, US6–US7 are P2)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1–US7)
- All paths are relative to the repository root

---

## Phase 1: Setup (Foundational Prerequisites)

**Purpose**: Fix shared data contracts and backend endpoints that ALL user stories depend on. No user story work can begin until this phase is complete.

**⚠️ CRITICAL**: These tasks unblock all downstream phases.

- [ ] T001 Extend `TemplateElement` interface in `formcraft-frontend/src/app/features/desk/services/form-filler.service.ts` — add `options?: Array<{ value: string; label_ar: string; label_en: string }>`, `visible_when?: { conditions: Array<{ field: string; operator: string; value: unknown }>; logic: 'AND' } | null`, `required_when?: (same shape) | null`, `tafqeet_enabled?: boolean` (see data-model.md for full shape)
- [ ] T002 Verify `formcraft-backend/app/api/routes/drafts.py` exposes `GET /desk/drafts` returning all drafts for the authenticated user (operator_id = auth.uid()); add the route + `DraftService.list_drafts()` in `formcraft-backend/app/services/draft_service.py` if missing
- [ ] T003 Add `listDrafts(): Observable<DraftResponse[]>` method to `formcraft-frontend/src/app/features/desk/services/draft.service.ts` calling `GET {apiUrl}` (no params; backend filters by auth.uid())
- [ ] T004 [P] Verify `formcraft-frontend/src/app/features/desk/services/submission.service.ts` `submit()` return type matches `SubmissionResponse` contract (id, reference_number, template_id, template_version, created_at) from `formcraft-specs/specs/053-form-filler-cross-theme/contracts/api-contracts.md`; update the interface if the shape differs

**Checkpoint**: `TemplateElement` has all required fields, `DraftService.listDrafts()` exists, `SubmissionResponse` contract matches — all components can now compile.

---

## Phase 2: User Story 1 — Load Real Template Structure (Priority: P1) 🎯 MVP

**Goal**: Both theme implementations load and render the actual published template structure from the backend with correct i18n labels, loading skeleton, and error state.

**Independent Test**: Navigate to `/desk/fill/{templateId}` and `/ui/desk/fill/{templateId}` with a 3-section, 15-field published template. Verify all sections and field labels render matching the template definition in both Arabic and English. Navigate with an invalid templateId and verify an error state with retry button appears (no mock data).

- [ ] T005 [US1] Fix `buildFormFromTemplate()` in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` — replace hardcoded section title `صفحة ${sectionNumber}` with `this.translate.instant('desk.page_number', { n: pageIndex + 1 })`; replace hardcoded `templateCode` initialiser; use `element.label_ar` / `element.label_en` per `this.currentLanguage` for all field `label` values
- [ ] T006 [US1] Verify `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.html` shows a loading skeleton (mat-progress-bar or shimmer) while `loading === true` and renders an error card with a "Retry" button calling `ngOnInit()` when `error !== null`; add these states if missing
- [ ] T007 [P] [US1] Verify `formcraft-frontend/src/app/features/desk/fill/fill.component.ts` (classic desk) calls `FormFillerService.getTemplate(templateId)` as sole source of form structure (FR-001/002); confirm no hardcoded section arrays or field arrays remain; confirm `is_deprecated` triggers a deprecation banner (FR-004 variant)
- [ ] T008 [P] [US1] Add missing i18n keys to `formcraft-frontend/src/assets/i18n/ar.json` and `formcraft-frontend/src/assets/i18n/en.json`: `desk.page_number` (e.g. `"صفحة {{n}}"` / `"Page {{n}}"`), `desk.template_load_error`, `desk.template_deprecated`, `desk.retry`

---

## Phase 3: User Story 2 — Apply Field Validation (Priority: P1)

**Goal**: Both theme implementations render all 7 field types with inline validation errors (touch-triggered), an error summary panel on failed submit, and country-specific validators applied via `ValidationService`.

**Independent Test**: Open a template with all 7 field types including required fields, a number field (min=0, max=1000), and an email-pattern field. Enter invalid data, blur each field, and verify specific inline errors appear. Attempt submit — verify submission blocked and error summary lists all failing fields. Correct each field and verify errors disappear and submit becomes enabled.

- [ ] T009 [US2] Add complete field-type renderer to `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.html` — implement `@switch (element.type)` with cases for `text` (mat-input), `number` (mat-input type="number"), `date` (mat-datepicker), `select` (mat-select with `*ngFor` over `element.options`), `checkbox` (mat-checkbox), `textarea` (mat-input textarea), `signature` (fc-signature-pad); bind each to `formGroup.get(element.key)`
- [ ] T010 [US2] Import `SignaturePadComponent` into standalone `imports` array of `FormFillerComponent` in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`; handle `(confirmed)` output → `formGroup.get(element.key)?.setValue(base64String)`; handle `(cleared)` output → `formGroup.get(element.key)?.setValue(null)`
- [ ] T011 [US2] Update `buildFormFromTemplate()` in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` to call `this.validationService.getValidatorFn(element)` and spread the returned validators into the `FormControl` alongside `Validators.required` when `element.required === true` (already partially done — verify country-specific validators are included)
- [ ] T012 [US2] Add error summary panel to `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.html` — render a `mat-card` with class `error-summary` above the submit button only when `submitted === true && formGroup.invalid`; list each invalid visible control's label and error message; add `submitted = false` property and set to `true` on submit click
- [ ] T013 [P] [US2] Add `error-summary` and `signature-pad-wrapper` styles to `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.scss` — red border, error icon, RTL-aware layout; ensure mat-error messages display below each field in both RTL and LTR
- [ ] T014 [P] [US2] Add missing validation i18n keys to `formcraft-frontend/src/assets/i18n/ar.json` and `en.json`: `desk.form_filler.validation_error_summary`, `desk.form_filler.field_required`, `desk.form_filler.field_invalid`, `desk.form_filler.submit_blocked`
- [ ] T015 [P] [US2] Verify `formcraft-frontend/src/app/features/desk/fill/fill.component.ts` (classic desk) renders all 7 field types including signature via `SignaturePadComponent`; confirm `ValidationService.getValidatorFn()` is called for every element; confirm error summary panel exists (FR-012)

---

## Phase 4: User Story 3 — Evaluate Conditional Logic (Priority: P1)

**Goal**: Both theme implementations wire `ConditionEngineService` so fields show/hide and become required/optional in real-time based on form values; hidden fields are excluded from validation and submission payload.

**Independent Test**: Open a template with a conditional field (`company_name` visible only when `account_type === 'Corporate'`). Select "Individual" — verify `company_name` disappears. Select "Corporate" — verify it reappears within 200ms. Attempt submit with `company_name` empty while hidden — verify submission is not blocked by hidden field.

- [ ] T016 [US3] Call `this.conditionEngineService.initialize(flatElements, this.formGroup)` at the end of `buildFormFromTemplate()` in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` — `flatElements` is the flattened array of all `TemplateElement` objects across all pages
- [ ] T017 [US3] Subscribe to `this.conditionEngineService.visibilityChanged$` in `ngOnInit()` of `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` — update `this.visibleKeys: Set<string>`; add `visibleKeys = new Set<string>()` property; call `this.conditionEngineService.destroy()` in `ngOnDestroy()`
- [ ] T018 [US3] Subscribe to `this.conditionEngineService.requiredChanged$` in `ngOnInit()` of `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` — update `this.requiredKeys: Set<string>`; add `requiredKeys = new Set<string>()` property; dynamically update `Validators.required` on the `FormControl` when requiredKeys changes
- [ ] T019 [US3] Update `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.html` field renderer to show/hide each field using `*ngIf="visibleKeys.has(element.key)"` (or equivalent `@if` block); fields not in `visibleKeys` must not render
- [ ] T020 [US3] Update `submitForm()` in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` to build the submission payload using only keys in `this.visibleKeys` — `const payload = Object.fromEntries(Object.entries(this.formGroup.value).filter(([k]) => this.visibleKeys.has(k)))`
- [ ] T021 [P] [US3] Verify `formcraft-frontend/src/app/features/desk/fill/fill.component.ts` (classic desk) has identical `visibleKeys` filtering in its submit handler (FR-016/017); add filter if missing

---

## Phase 5: User Story 4 — Save and Resume Drafts (Priority: P1)

**Goal**: Operators can save in-progress forms as drafts, discover them via the "My Drafts" panel, resume with all values restored, and receive a version mismatch warning when template has changed.

**Independent Test**: Start filling a form in new-theme, save as draft (or navigate away), re-open the desk dashboard, find the draft in "My Drafts" panel, click to resume — verify all saved field values are restored. Repeat with a draft saved at an older template version — verify the version mismatch warning dialog appears.

- [ ] T022 [US4] Add `ngOnDestroy` auto-save to `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` — in `ngOnDestroy()`, if `this.formGroup.dirty && !this.submitted`, call `this.saveDraft()` synchronously (use `take(1)` subscribe); add `submitted = false` property set to `true` on successful submission
- [ ] T023 [US4] Add template version mismatch check to `loadDraft()` in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` — after patching form values, compare `draft.template_version !== this.template?.version`; if mismatch, open `MatDialog` with `VersionWarningComponent` (import from `formcraft-frontend/src/app/features/desk/components/version-warning/version-warning.component.ts`); pass `{ currentVersion: template.version, draftVersion: draft.template_version }` as dialog data
- [ ] T024 [US4] Replace hardcoded snackbar strings in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` — `'تم حفظ المسودة بنجاح'` → `this.translate.instant('desk.form_filler.draft_saved')`, `'فشل حفظ المسودة'` → `this.translate.instant('desk.form_filler.draft_save_failed')`, `'تم إرسال النموذج بنجاح'` → `this.translate.instant('desk.form_filler.submit_success')`
- [ ] T025 [US4] Update `formcraft-frontend/src/app/features/desk/components/draft-list/draft-list.component.ts` — inject `DraftService`; call `draftService.listDrafts()` on init instead of using an `@Input() drafts` array; `openDraft(draft)` must navigate to `/ui/desk/fill/${draft.template_id}?draftId=${draft.id}` for new-theme context (keep classic route for backward compatibility)
- [ ] T026 [US4] Wire `DraftListComponent` into `formcraft-frontend/src/app/features/ui-redesign/desk/dashboard.component.ts` — import `DraftListComponent` in standalone imports; add `<fc-draft-list>` to `formcraft-frontend/src/app/features/ui-redesign/desk/dashboard.component.html` in the appropriate panel area
- [ ] T027 [P] [US4] Add missing draft i18n keys to `formcraft-frontend/src/assets/i18n/ar.json` and `en.json`: `desk.form_filler.draft_saved`, `desk.form_filler.draft_save_failed`, `desk.form_filler.draft_version_mismatch`, `desk.my_drafts`, `desk.draft_untitled`, `desk.empty_drafts`
- [ ] T028 [P] [US4] Verify `formcraft-frontend/src/app/features/desk/fill/fill.component.ts` (classic desk) has 10-second auto-save interval (FR-019); confirm version mismatch dialog uses `VersionWarningComponent`; confirm draft is archived/deleted after successful submission

---

## Phase 6: User Story 5 — Submit Completed Forms (Priority: P1)

**Goal**: Operators submit valid forms and land on a dedicated `SubmissionConfirmedComponent` showing the reference number; failed submissions preserve form data with a retry option.

**Independent Test**: Complete a form in new-theme and submit. Verify the browser navigates to `/ui/desk/submission-confirmed` with the reference number visible prominently. Click "Back to Desk" and verify navigation to `/ui/desk`. Submit with a simulated backend failure — verify error banner appears with retry button and form data is preserved.

- [ ] T029 [US5] Create `formcraft-frontend/src/app/features/ui-redesign/desk/submission-confirmed.component.ts` as a standalone component — reads `router.getCurrentNavigation()?.extras.state as SubmissionConfirmedState`; if state is null, immediately navigate to `/ui/desk`; displays `referenceNumber`, `templateName`, `submittedAt` from state; exports `SubmissionConfirmedState` interface `{ referenceNumber: string; templateName: string; submittedAt: string }`
- [ ] T030 [US5] Create `formcraft-frontend/src/app/features/ui-redesign/desk/submission-confirmed.component.html` — large mat-card with a success icon, reference number in bold prominent text, template name, formatted submission timestamp, and a mat-button "Back to Desk" navigating to `/ui/desk`; use translate pipe for all labels
- [ ] T031 [US5] Add route `/ui/desk/submission-confirmed` to `formcraft-frontend/src/app/features/ui-redesign/ui-redesign.routes.ts` with `canActivate: [RoleGuard]`, `data: { roles: ['admin', 'branch_manager', 'operator'] }`, `loadComponent` pointing to `SubmissionConfirmedComponent`
- [ ] T032 [US5] Update `submitForm()` in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` — on success, set `this.submitted = true`, then `this.router.navigate(['/ui/desk/submission-confirmed'], { state: { referenceNumber: response.reference_number, templateName: this.template?.name, submittedAt: new Date().toISOString() } })`; remove the existing 2-second setTimeout and `/ui/desk` navigation
- [ ] T033 [P] [US5] Update `submitForm()` failure handler in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` — display persistent error banner (not just a snackbar) with a "Retry" button calling `submitForm()` again; ensure form group remains unmodified so the operator can retry without re-entering data
- [ ] T034 [P] [US5] Add submission confirmation i18n keys to `formcraft-frontend/src/assets/i18n/ar.json` and `en.json`: `desk.submission_confirmed.title`, `desk.submission_confirmed.reference_label`, `desk.submission_confirmed.submitted_at`, `desk.submission_confirmed.back_to_desk`, `desk.form_filler.submit_failed`, `desk.form_filler.retry`
- [ ] T035 [P] [US5] Verify `formcraft-frontend/src/app/features/desk/fill/fill.component.ts` (classic desk) submission success shows reference number via snackbar or confirmation UI; submission failure preserves form data with retry option (FR-025)

---

## Phase 7: User Story 6 — Customer Auto-Fill (Priority: P2)

**Goal**: Operators search for and select a customer from a picker dialog; mapped form fields auto-populate with real customer data from the backend.

**Independent Test**: Click the customer picker button in the new-theme form filler header. Search for a customer by name. Select a customer with a complete profile mapped to the current template. Verify mapped fields populate instantly. Modify one auto-filled field and verify it remains editable.

- [ ] T036 [US6] Add `CustomerService` (or verify it exists) in `formcraft-frontend/src/app/features/desk/services/` — if absent, create `customer.service.ts` with `searchCustomers(query: string): Observable<Customer[]>` calling `GET /desk/customers/search?q={query}` and `getAutoFillData(customerId: string, templateId: string): Observable<AutoFillMapping>` calling `GET /desk/customers/{customerId}/auto-fill?template_id={templateId}`; define `Customer` and `AutoFillMapping` interfaces per `formcraft-specs/specs/053-form-filler-cross-theme/contracts/api-contracts.md`
- [ ] T037 [US6] Create a `CustomerPickerDialogComponent` in `formcraft-frontend/src/app/features/desk/components/customer-picker/customer-picker-dialog.component.ts` as a standalone `MatDialogRef`-based component — contains a `MatInput` search field with 300ms debounce calling `CustomerService.searchCustomers(query)`; renders results list; on row click emits the selected `Customer` via `dialogRef.close(customer)`
- [ ] T038 [US6] Update `openCustomerPicker()` in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` — open `CustomerPickerDialogComponent` via `MatDialog.open()`; subscribe to `afterClosed()` result; if a customer is returned, call `this.customerService.getAutoFillData(customer.id, this.templateId).subscribe(mapping => this.autoFillService.executeAutoFill(mapping.mappings, this.formGroup))`
- [ ] T039 [P] [US6] Add customer picker i18n keys to `formcraft-frontend/src/assets/i18n/ar.json` and `en.json`: `desk.customer_picker.title`, `desk.customer_picker.search_placeholder`, `desk.customer_picker.no_results`, `desk.customer_picker.select`
- [ ] T040 [P] [US6] Verify `formcraft-frontend/src/app/features/desk/fill/fill.component.ts` (classic desk) customer picker already calls `CustomerService.getAutoFillData()` and `AutoFillService.executeAutoFill()` (FR-026–029)

---

## Phase 8: User Story 7 — Tafqeet: Arabic Number-to-Words (Priority: P2)

**Goal**: Numeric fields with `tafqeet_enabled === true` display the Arabic word form below the field, updating on every keystroke.

**Independent Test**: Open a template with a `tafqeet_enabled` numeric field. Enter "12345" — verify the Arabic text `اثنا عشر ألفاً وثلاثمائة وخمسة وأربعون` appears below the field within 200ms. Clear the field — verify the tafqeet text disappears. Enter a value in a non-tafqeet field — verify no Arabic words appear.

- [ ] T041 [US7] Add `tafqeetValues = new Map<string, string>()` property to `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`; in `buildFormFromTemplate()`, for each element where `element.tafqeet_enabled === true`, subscribe to `this.formGroup.get(element.key)!.valueChanges.pipe(takeUntil(this.destroy$))` and on each value call `this.tafqeetService.compute(value)` — store the result in `tafqeetValues.set(element.key, result)` (clear on null/empty value)
- [ ] T042 [US7] Add tafqeet display markup to the field renderer in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.html` — below the number input for `tafqeet_enabled` elements, add `<span class="tafqeet-text" *ngIf="tafqeetValues.get(element.key)" dir="rtl">{{ tafqeetValues.get(element.key) }}</span>`
- [ ] T043 [P] [US7] Add `.tafqeet-text` style to `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.scss` — Arabic font, subtle colour, RTL-forced direction, margin-top 4px
- [ ] T044 [P] [US7] Verify `formcraft-frontend/src/app/features/desk/fill/fill.component.ts` (classic desk) wires `FillerTafqeetService` for all `tafqeet_enabled` elements; confirm tafqeet text renders below numeric fields and clears on empty value (FR-030/031)

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: i18n completeness, RTL/LTR layout verification, SC criteria pass, and final constitution check.

- [ ] T045 Audit all i18n key usages in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` — ensure zero remaining hardcoded Arabic strings; verify all keys added in T005, T008, T014, T024, T027, T034, T039 exist in both `ar.json` and `en.json`; run `ng build` and confirm no missing translation warnings
- [ ] T046 [P] Verify RTL layout for new-theme `FormFillerComponent` — switch language to Arabic via app language toggle; confirm all field labels, error messages, section titles, signature pad, and error summary panel align correctly in RTL; check `dir="auto"` is applied to text inputs
- [ ] T047 [P] Verify `formcraft-frontend/src/app/features/ui-redesign/desk/submission-confirmed.component.ts` handles null router state gracefully (SC-015 edge case) — navigate directly to `/ui/desk/submission-confirmed` without state; confirm immediate redirect to `/ui/desk` without error
- [ ] T048 [P] Verify `SignaturePadComponent` serialises to non-empty base64 PNG on confirm and returns null on clear — confirm `formGroup.get(signatureKey).value` is null when cleared and a non-empty string after confirm; confirm required validation blocks submission when signature is empty (SC-012)
- [ ] T049 [P] Run full FR checklist verification: confirm FR-001 to FR-038 are satisfied by the final state of both `fill.component.ts` (classic) and `form-filler.component.ts` (new-theme); document any remaining gaps as follow-up items

---

## Dependencies

```
T001 → T005, T009, T011, T016, T041   (TemplateElement interface unblocks all field rendering)
T002 → T003                            (backend list route unblocks frontend listDrafts)
T003 → T025, T026                      (listDrafts() unblocks My Drafts panel)
T004 → T032                            (SubmissionResponse shape unblocks submit navigation)
T005, T008 → T006                      (i18n keys needed for loading/error states)
T009 → T010                            (field renderer must exist before signature import)
T011 → T012                            (validators wired before error summary)
T016 → T017, T018, T019               (initialize() must be called before subscriptions)
T017, T018, T019 → T020               (visibility/required sets needed for payload filter)
T022 → T023                            (ngOnDestroy order: save before destroy)
T029 → T030, T031, T032               (component must exist before route and navigation)
T036 → T037, T038                      (CustomerService must exist before picker)
T041 → T042                            (tafqeetValues map populated before template renders it)
```

## Parallel Execution Opportunities

**US1 + US2 setup** (after Phase 1 complete): T005, T007, T008 can run in parallel  
**US2 field types + styles**: T009 (template) || T013 (styles) || T014 (i18n)  
**US3 subscriptions**: T017, T018 can run in parallel after T016  
**US4 misc**: T027 (i18n), T028 (classic desk verify) can run parallel with T022, T023, T025  
**US5 misc**: T033, T034, T035 can run parallel after T032  
**US6 misc**: T039, T040 can run parallel with T037  
**US7 misc**: T043, T044 can run parallel with T041  
**Phase 9 all**: T045–T049 can run in parallel after all user stories complete

## Implementation Strategy

**MVP Scope (US1 only — T001, T005, T006, T007, T008)**:
Delivers a new-theme form filler that loads real templates with correct i18n labels and proper error handling. Classic desk loading verified. No validation, conditions, or submission — just template rendering.

**P1 Core (US1–US5 — T001–T035)**:
Complete functional form filler in both themes: load, validate, conditional logic, draft management, and submission with confirmation screen. Satisfies all SC-001–SC-011 criteria.

**P2 Extensions (US6–US7 — T036–T044)**:
Customer auto-fill and tafqeet for numeric fields.

**Total tasks**: 49 (T001–T049)
**P1 tasks**: 35 (T001–T035)
**P2 tasks**: 9 (T036–T044)
**Polish tasks**: 5 (T045–T049)
