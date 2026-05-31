# Tasks: Form Filler Cross-Theme (F052)

**Branch**: `052-form-filler-cross-theme`  
**Input**: Design documents from `formcraft-specs/specs/052-form-filler-cross-theme/`  
**Prerequisites**: plan.md ✅ spec.md ✅ research.md ✅ data-model.md ✅ contracts/ ✅

**Implementation note**: The `FormFillerComponent` skeleton in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` already has services injected, condition engine wired, auto-save on destroy, and version mismatch detection (as a snackbar). These tasks complete the remaining 10 gaps identified in research.md, organized by user story. TDD is mandatory (Constitution V) — failing tests are written before each implementation task.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks in same phase)
- **[Story]**: User story label (US1–US7)
- Exact file paths included in every task description

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add i18n translation keys and extend the test spec file — both blocking ALL subsequent tasks.

- [ ] T001 Add ALL `DESK.FILL.*` translation keys to `formcraft-frontend/src/assets/i18n/ar.json` (keys: DRAFT_SAVED, DRAFT_SAVE_FAILED, DRAFT_LOAD_FAILED, SUBMIT_SUCCESS, SUBMIT_FAILED, SUBMIT_RETRY_EXHAUSTED, DRAFT_CONCURRENT_MODIFIED, DRAFT_EXPIRED, REQUIRED_FIELDS_MISSING, TEMPLATE_VERSION_MISMATCH, TEMPLATE_LOAD_FAILED, NO_TEMPLATE_ID, PAGE_LABEL, RETRY, SAVE_AS_DRAFT, SUBMITTING, DRAFT_SAVING, AUTO_SAVED — see data-model.md for Arabic values; AUTO_SAVED = `"تم الحفظ تلقائياً"`)
- [ ] T002 Add ALL `DESK.FILL.*` translation keys to `formcraft-frontend/src/assets/i18n/en.json` (English values corresponding to T001 keys; AUTO_SAVED = `"Auto-saved"`, DRAFT_LOAD_FAILED = `"Failed to load draft"`, TEMPLATE_LOAD_FAILED = `"Failed to load template"`, NO_TEMPLATE_ID = `"No template specified"`)

**Checkpoint**: I18n infrastructure ready — all component tasks can now use `translate('DESK.FILL.*')`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Cross-cutting component state additions that every user story's tests depend on.

- [ ] T003 Add `draftUpdatedAt: string | null = null` and `submitting = false` and `savingDraft = false` and `retryCount = 0` state fields to `FormFillerComponent` in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T004 Add `TranslateModule` and `TranslateService` import/injection to `FormFillerComponent` in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` (add `TranslateModule` to `imports` array, inject `private translate: TranslateService` in constructor)
- [ ] T005 Add `retry` and `timer` imports from `rxjs` to `FormFillerComponent` in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T006 [P] Add `MatDialogModule` to `FormFillerComponent` imports array and inject `MatDialog` in constructor in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` (needed for VersionWarningComponent dialog in US4)

**Checkpoint**: State fields and dependencies ready — user story phases can proceed.

---

## Phase 3: User Story 1 — Load Real Template Structure (P1) 🎯 MVP

**Goal**: Template name, version, and section labels display real data with no hardcoded strings.

**Independent Test**: Navigate to `/ui/desk/fill/{validTemplateId}`. Verify the page title matches the template's actual name, the version badge shows the real version number, and section headings are i18n-resolved. Navigate to `/ui/desk/fill/{invalidTemplateId}` — verify error state with translated message.

### Tests for User Story 1

> **Write these tests FIRST — ensure they FAIL before implementing T010–T013**

- [ ] T007 [US1] Write failing spec: template name and version are bound from API response (not hardcoded defaults) — extend `form-filler.component.spec.ts` in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.spec.ts`
- [ ] T008 [US1] Write failing spec: section title uses `translate('DESK.FILL.PAGE_LABEL', { number })` not hardcoded Arabic string — extend `form-filler.component.spec.ts`
- [ ] T009 [US1] Write failing spec: `getTemplate()` subscription is cleaned up on destroy (no active subscription after ngOnDestroy) — extend `form-filler.component.spec.ts`

### Implementation for User Story 1

- [ ] T010 [US1] Remove hardcoded default values `templateName = 'طلب فتح حساب جاري للأفراد'` and `templateCode = 'AC-001 · v4.2'` — replace with `templateName = ''` and `templateCode = ''` in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T011 [US1] Replace hardcoded `صفحة ${sectionNumber}` in `sections[].title` and `sideSections[].label` with `this.translate.instant('DESK.FILL.PAGE_LABEL', { number: sectionNumber })` in `buildFormFromTemplate()` in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T012 [US1] Add `takeUntil(this.destroy$)` pipe to `this.formFillerService.getTemplate().subscribe(...)` call inside `ngOnInit()` in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T013 [US1] Replace hardcoded `'Failed to load template'` and `'No template ID provided'` error strings with `this.translate.instant('DESK.FILL.TEMPLATE_LOAD_FAILED')` and `this.translate.instant('DESK.FILL.NO_TEMPLATE_ID')` in `ngOnInit()` error handler in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` (keys are already included in T001/T002)

**Checkpoint**: Template loads with real data, section labels are i18n-resolved, memory leak fixed.

---

## Phase 4: User Story 2 — Apply Field Validation (P1)

**Goal**: Inline validation errors display per-field; submission is blocked when any visible required field is invalid; hidden fields are excluded from validation.

**Independent Test**: Load a template with required fields and a conditional field. Leave required field empty → click Submit → verify inline error appears, submission does NOT proceed. Fill required field → verify error clears and submission is allowed. Trigger condition to hide a required field → verify that hidden field's error does not block submission.

### Tests for User Story 2

> **Write these tests FIRST — ensure they FAIL before implementing T018–T022**

- [ ] T014 [US2] Write failing spec: `submitForm()` is blocked when a VISIBLE required field is empty — extend `form-filler.component.spec.ts`
- [ ] T015 [US2] Write failing spec: `submitForm()` is NOT blocked by a HIDDEN required field (i.e., field not in `visibleFields`) — extend `form-filler.component.spec.ts`
- [ ] T016 [US2] Write failing spec: `syncHiddenControls()` disables controls not in visible set and enables those in visible set — extend `form-filler.component.spec.ts`

### Implementation for User Story 2

- [ ] T017 [US2] Implement `private syncHiddenControls(visibleKeys: Set<string>): void` method in `FormFillerComponent` — for each control key: call `ctrl.disable({ emitEvent: false })` if not in visibleKeys, `ctrl.enable({ emitEvent: false })` if in visibleKeys — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T018 [US2] Call `this.syncHiddenControls(visibleKeys)` inside the `visibilityChanged$` subscription callback (after `this.visibleFields = visibleKeys`) in `buildFormFromTemplate()` in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T019 [US2] Implement `private isFormValid(): boolean` that returns `Array.from(this.visibleFields).every(key => !this.formGroup.get(key)?.invalid)` in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T020 [US2] Replace `!this.formGroup.valid` check in `submitForm()` with `!this.isFormValid()` so only visible fields gate submission in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T021 [US2] Replace hardcoded snackbar string `'يرجى ملء جميع الحقول المطلوبة'` in `submitForm()` with `this.translate.instant('DESK.FILL.REQUIRED_FIELDS_MISSING')` in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`

**Checkpoint**: Validation only considers visible fields; hidden fields are disabled and excluded.

---

## Phase 5: User Story 3 — Evaluate Conditional Logic (P1)

**Goal**: Conditional fields show/hide within 200ms of trigger field change; hidden fields are excluded from validation and submission payload.

**Independent Test**: Load template with field B visible only when field A equals "yes". Set A="no" → verify B is hidden and disabled. Set A="yes" → verify B appears and is enabled. Submit with B hidden → verify B's value is absent from submission payload.

### Tests for User Story 3

> **Write these tests FIRST — ensure they FAIL before implementing T025–T026**

- [ ] T022 [US3] Write failing spec: field is disabled (via `disable()`) when removed from `visibleFields` — extend `form-filler.component.spec.ts`
- [ ] T023 [US3] Write failing spec: `formGroup.value` (submission payload) excludes disabled field value — extend `form-filler.component.spec.ts`
- [ ] T024 [US3] Write failing spec: `ConditionEngineService.initialize()` is called with all template elements after `formGroup` is built — extend `form-filler.component.spec.ts`

### Implementation for User Story 3

- [ ] T025 [US3] Verify that `syncHiddenControls()` (from T017) is already called in the `visibilityChanged$` subscription — confirm `formGroup.value` automatically excludes disabled controls, ensuring submission payload excludes hidden fields — no new code if T017/T018 already done — verify in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T026 [P] [US3] Update `form-filler.component.html` to bind `[hidden]` or `*ngIf` on each field using `visibleFields.has(field.key)` so the HTML reflects field visibility (user sees fields appear/disappear) — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.html`

**Checkpoint**: Conditional logic wired end-to-end: engine evaluates → visibility set updated → controls disabled → submission payload clean.

---

## Phase 6: User Story 4 — Save and Resume Drafts (P1)

**Goal**: Drafts save/resume correctly; expired drafts are rejected; concurrent modification is warned; version mismatch shows proper dialog; all messages are i18n-translated.

**Independent Test**: (a) Save draft, navigate away, return with `?draftId=` — values restored. (b) Load an expired draft — redirect to dashboard with toast. (c) Save draft from two tabs simultaneously — second save shows concurrent-modification toast. (d) Load draft with older template version — dialog appears with "Reload" option.

### Tests for User Story 4

> **Write these tests FIRST — ensure they FAIL before implementing T030–T037**

- [ ] T027 [US4] Write failing spec: `loadDraft()` redirects to `/ui/desk` and shows toast when `draft.expires_at` is in the past — extend `form-filler.component.spec.ts`
- [ ] T028 [US4] Write failing spec: after `saveDraft()` succeeds, `draftUpdatedAt` equals `response.updated_at` — extend `form-filler.component.spec.ts`
- [ ] T029 [US4] Write failing spec: when `response.updated_at` is newer than pre-save `draftUpdatedAt`, concurrent-modification toast is shown — extend `form-filler.component.spec.ts`

### Implementation for User Story 4

- [ ] T030 [US4] Add draft expiry check at top of `loadDraft()`: if `new Date(draft.expires_at) < new Date()` → show `translate('DESK.FILL.DRAFT_EXPIRED')` snackbar → `this.router.navigate(['/ui/desk'])` → return — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T031 [US4] Store `this.draftUpdatedAt = draft.updated_at` after successful draft load in `loadDraft()` in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T032 [US4] In `saveDraft()` `updateDraft()` success handler: if `response.updated_at > this.draftUpdatedAt!` — show `translate('DESK.FILL.DRAFT_CONCURRENT_MODIFIED')` snackbar; always update `this.draftUpdatedAt = response.updated_at` — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T033 [US4] In `saveDraft()` `saveDraft()` (new draft) success handler: store `this.draftUpdatedAt = response.updated_at` — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T034 [US4] Replace hardcoded snackbar strings in `saveDraft()` (`'تم حفظ المسودة بنجاح'`, `'فشل حفظ المسودة'`) with `this.translate.instant('DESK.FILL.DRAFT_SAVED')` and `this.translate.instant('DESK.FILL.DRAFT_SAVE_FAILED')` — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T035 [US4] Replace template version mismatch snackbar in `loadDraft()` with `VersionWarningComponent` dialog: `this.dialog.open(VersionWarningComponent, { data: { savedVersion: draft.template_version, currentVersion: this.template.version } as VersionWarningData })` — on `afterClosed()` if result === 'reload': reload template — import `VersionWarningComponent` and `VersionWarningData` from `'../../../features/desk/components/version-warning/version-warning.component'` in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T036 [US4] Add error snackbar to `loadDraft()` error handler: show `translate('DESK.FILL.DRAFT_LOAD_FAILED')` — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` (key already included in T001/T002)
- [ ] T036b [US4] Implement `private calculateCompletion(): number` that returns `Math.round((filledVisibleCount / totalVisibleRequired) * 100)` and call it before each `DraftService.saveDraft()` and `DraftService.updateDraft()` invocation, passing the result as `completion_percent` — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` (satisfies FR-021: draft MUST persist completion metadata)

**Checkpoint**: Full draft lifecycle works: create, resume, version-mismatch dialog, expiry redirect, concurrent-write warning, completion percentage tracked.

---

## Phase 7: User Story 5 — Submit Completed Forms (P1)

**Goal**: Submission succeeds or fails with translated feedback; failures retry up to 3 times with exponential backoff; exhausted retries show persistent banner with "Retry" and "Save as Draft" options; success shows reference number.

**Independent Test**: Submit valid form → confirm `SubmissionResponse.reference_number` appears in success message and operator navigates to `/ui/desk`. Mock 3 consecutive failures → confirm auto-retries occur (1s, 2s, 4s) → confirm persistent error banner appears with both "Retry" and "Save as Draft" buttons. Click "Save as Draft" from error banner → confirm draft save is triggered.

### Tests for User Story 5

> **Write these tests FIRST — ensure they FAIL before implementing T040–T044**

- [ ] T037 [US5] Write failing spec: `submitForm()` retries up to 3 times on failure before calling error handler — extend `form-filler.component.spec.ts`
- [ ] T038 [US5] Write failing spec: success snackbar message includes `reference_number` from response — extend `form-filler.component.spec.ts`
- [ ] T039 [US5] Write failing spec: after retry exhaustion, `submitting` is false and persistent error banner state is set — extend `form-filler.component.spec.ts`

### Implementation for User Story 5

- [ ] T040 [US5] Add `submissionError: string | null = null` and `showRetryBanner = false` state fields to `FormFillerComponent` in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T041 [US5] Rewrite `submitForm()` to use RxJS retry with exponential backoff: `this.submissionService.submit(...).pipe(retry({ count: 3, delay: (_, i) => timer(Math.pow(2, i - 1) * 1000) }), takeUntil(this.destroy$)).subscribe({ next: onSuccess, error: onExhausted })` — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T042 [US5] In `submitForm()` success handler: replace hardcoded string with `this.translate.instant('DESK.FILL.SUBMIT_SUCCESS', { ref: response.reference_number })` — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T043 [US5] In `submitForm()` error handler (after retry exhaustion): set `this.submitting = false`, `this.showRetryBanner = true`, `this.submissionError = this.translate.instant('DESK.FILL.SUBMIT_RETRY_EXHAUSTED')` — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T044 [US5] Add `retrySubmit()` method that calls `submitForm()` and `dismissBanner()` that resets `showRetryBanner = false` and `submissionError = null` — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T045 [US5] Add persistent error banner to `form-filler.component.html` controlled by `showRetryBanner` with "Retry" button (calls `retrySubmit()`) and "Save as Draft" button (calls `saveDraft(); dismissBanner()`) — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.html`
- [ ] T046 [US5] Replace hardcoded submit failure snackbar string `'فشل إرسال النموذج'` with `translate('DESK.FILL.SUBMIT_FAILED')` (keep existing snackbar for non-exhaustion single-attempt failure path if retained) — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`

**Checkpoint**: Full submission flow: validation → retry → success with reference → exhaustion banner.

---

## Phase 8: User Story 6 — Customer Auto-Fill (P2)

**Goal**: Operator selects customer from picker → mapped fields auto-populate. (P2 — implement after P1 stories complete.)

**Independent Test**: Click customer picker button → search results appear with real customer data → select customer → fields mapped by `AutoFillService` populate correctly → fields remain editable.

### Tests for User Story 6

> **Write these tests FIRST — ensure they FAIL before implementing T050–T052**

- [ ] T047 [P] [US6] Write failing spec: `openCustomerPicker()` sets `showCustomerPicker = true` — extend `form-filler.component.spec.ts`
- [ ] T048 [P] [US6] Write failing spec: customer selection calls `AutoFillService.executeAutoFill()` and patches form values — extend `form-filler.component.spec.ts`

### Implementation for User Story 6

- [ ] T049 [US6] Implement customer search in customer picker: call `CustomerService.searchCustomers(query)` and populate `customerResults` (create `searchCustomers()` method) — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T050 [US6] Implement `selectCustomer(customerId: string)` method: call `AutoFillService.executeAutoFill(customerId, this.templateId, this.formGroup)` → patch form with result → close picker — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T051 [US6] Wire customer picker UI in `form-filler.component.html`: show search input, results list, and empty state — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.html`

**Checkpoint**: Customer picker functional with real data — auto-fill populates matched fields.

---

## Phase 9: User Story 7 — Tafqeet (P2)

**Goal**: Numeric fields with `tafqeet_enabled === true` show Arabic number-to-words below field in real time. (P2 — deferred.)

**Independent Test**: Enter "1234" in tafqeet-enabled field → verify Arabic words `"ألف ومائتان وأربعة وثلاثون"` display below field within 200ms. Change value → words update immediately.

### Tests for User Story 7

> **Write these tests FIRST — ensure they FAIL before implementing T054–T055**

- [ ] T052 [P] [US7] Write failing spec: for tafqeet-enabled number field, `FillerTafqeetService.compute(value)` result displays below the field — extend `form-filler.component.spec.ts`

### Implementation for User Story 7

- [ ] T053 [US7] Add `tafqeetValues: Record<string, string> = {}` state field to `FormFillerComponent` — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T054 [US7] In `buildFormFromTemplate()`, subscribe to `formGroup.get(key)?.valueChanges` for each element with `tafqeet_enabled === true`: call `this.tafqeetValues[key] = this.tafqeetService.compute(value)` — pipe with `debounceTime(100)` and `takeUntil(this.destroy$)` — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
- [ ] T055 [US7] Add tafqeet display element below each tafqeet-enabled numeric field in `form-filler.component.html` bound to `tafqeetValues[field.key]` — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.html`

**Checkpoint**: Tafqeet displays in real-time for enabled numeric fields.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: RTL/LTR compliance, error summary, cleanup. All P1 stories must be complete first.

- [ ] T056 [P] Add `dir="auto"` attribute to ALL input elements in the `[ngSwitch]` block in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.html`: text `<input>`, number `<input>`, date `<input>`, `<textarea>`, `<select>` (or `<mat-select>`), and the label/visible text of checkbox fields — covers all 6 field types (Constitution Principle I: RTL-Native)
- [ ] T057 [P] Add error summary panel to `form-filler.component.html`: display list of all visible invalid field names and their error messages when form has been submitted at least once — bind to `formGroup.controls` filtered by `visibleFields` — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.html`
- [ ] T058 Audit BOTH files for hardcoded UI strings — zero hardcoded Arabic or English strings allowed anywhere: (a) `form-filler.component.ts`: all snackbar/dialog messages use `translate('DESK.FILL.*')`; (b) `form-filler.component.html`: replace any hardcoded Arabic text (e.g., `محفوظ تلقائياً` on line 36 auto-save indicator) with `{{ 'DESK.FILL.AUTO_SAVED' | translate }}` — audit `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` and `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.html`
- [ ] T059 [P] Manual RTL test: load form in Arabic locale — verify section labels, field labels, and error messages all render RTL without layout breakage — `formcraft-frontend/src/app/features/ui-redesign/desk/`
- [ ] T060 [P] Manual LTR test: switch to English locale — verify all UI mirrors correctly (flex direction, icon positions, text alignment) — `formcraft-frontend/src/app/features/ui-redesign/desk/`
- [ ] T061 Run `ng test --include=form-filler.component.spec.ts` — all tests PASS — `formcraft-frontend/`
- [ ] T062 [P] Run `ng build --configuration production` — no TypeScript errors or compilation warnings — `formcraft-frontend/`
- [ ] T063 [P] Run classic desk form filler regression spec to confirm F052 service-layer changes introduce zero regressions — `ng test --include=**/desk/form-filler.component.spec.ts` (classic path) — `formcraft-frontend/` (satisfies FR-016: conditional logic and core features must be identical across themes — SC-009: 100% core feature parity)
- [ ] T064 [P] Add performance smoke assertions to `form-filler.component.spec.ts`: (a) stub `visibilityChanged$` emit and assert `syncHiddenControls` completes synchronously (< 200ms budget — SC-004); (b) stub field blur and assert validation error is set within the same microtask (< 300ms budget — SC-003); (c) confirm `debounceTime` on tafqeet valueChanges is ≤ 100ms — in `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.spec.ts`

---

## Dependencies (Story Completion Order)

```
Phase 1 (T001–T002)
  └── Phase 2 (T003–T006)
        ├── Phase 3: US1 (T007–T013) ← MVP
        │     └── Phase 4: US2 (T014–T021)
        │           └── Phase 5: US3 (T022–T026) ← depends on US2 syncHiddenControls
        ├── Phase 6: US4 (T027–T036) ← independent of US2/US3
        ├── Phase 7: US5 (T037–T046) ← independent of US2/US3
        ├── Phase 8: US6 (T047–T051) ← P2, after all P1
        ├── Phase 9: US7 (T052–T055) ← P2, after all P1
        └── Final Phase (T056–T064) ← after all user stories
```

## Parallel Execution Examples

**After Phase 2 complete**, these story phases can run in parallel on different files:

| Agent A | Agent B | Agent C |
|---------|---------|---------|
| Phase 3: US1 (T007–T013) | Phase 6: US4 (T027–T036) | Phase 7: US5 (T037–T046) |

**Within Phase 7** (US5): T040–T044 are in `form-filler.component.ts`; T045 is in `.html` — can run in parallel.

## Implementation Strategy

**Suggested MVP Scope (Phase 1–3 only)**:
- Add i18n keys
- Fix hardcoded default values
- Fix section label i18n
- Add `takeUntil` on template load

This gives a releasable increment: template loads cleanly with real data, no memory leaks, no hardcoded strings.

**Full P1 Scope** (Phases 1–7): Completes all spec FR requirements for production readiness.

**P2 Scope** (Phases 8–9): Auto-fill and tafqeet — implement after P1 is verified.

---

## Task Summary

| Phase | Story | Tasks | Status |
|-------|-------|-------|--------|
| Phase 1: Setup | — | T001–T002 | Not started |
| Phase 2: Foundational | — | T003–T006 | Not started |
| Phase 3 | US1 Load Template | T007–T013 | Not started |
| Phase 4 | US2 Validation | T014–T021 | Not started |
| Phase 5 | US3 Conditional Logic | T022–T026 | Not started |
| Phase 6 | US4 Draft Management | T027–T036 | Not started |
| Phase 7 | US5 Submit Forms | T037–T046 | Not started |
| Phase 8 | US6 Customer Auto-Fill | T047–T051 | Not started (P2) |
| Phase 9 | US7 Tafqeet | T052–T055 | Not started (P2) |
| Final | Polish | T056–T064 | Not started |

**Total tasks**: 66 (added T036b, T063, T064; renumbered none — T036b inserted in-phase)
**P1 tasks** (Phases 1–7 + Final): 59  
**P2 tasks** (Phases 8–9): 7  
**[P] parallelizable tasks**: 23  
**Test tasks (TDD-first)**: 17  
**Implementation tasks**: 49
