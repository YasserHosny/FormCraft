# Tasks: Form Filler

**Input**: Design documents from `/specs/016-form-filler/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Depends on**: Feature 014 (mode-switching-ux), Feature 015 (operator-dashboard) — `/desk/fill/:templateId` route placeholder must exist

## Phase 1: Setup (Backend Schema + i18n)

**Purpose**: Database migrations and localization keys

- [x] T001 [P] Create migration `formcraft-backend/migrations/017_submissions.sql` — CREATE TABLE submissions (id, template_id, template_version, operator_id, org_id, field_values JSONB, reference_number TEXT UNIQUE, created_at) with indexes, RLS policies, and generate_submission_ref() function
- [x] T002 [P] Create migration `formcraft-backend/migrations/018_drafts.sql` — CREATE TABLE drafts (id, template_id, template_version, operator_id, org_id, field_values JSONB, completion_percent INT, name TEXT, expires_at, created_at, updated_at) with index, RLS policy
- [x] T003 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/ar.json` — filler.* keys (title, toolbar actions, error messages, draft messages, print success)
- [x] T004 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/en.json` — same filler.* keys in English

---

## Phase 2: Backend (Submission + Draft + Validator APIs)

**Purpose**: Submission creation, draft CRUD, validator exposure, PDF extension

- [x] T005 Create `formcraft-backend/app/schemas/submission.py` — Pydantic schemas: CreateSubmissionRequest (template_id, template_version, field_values), SubmissionResponse (id, reference_number, template_id, template_version, operator_id, created_at), CreateDraftRequest, UpdateDraftRequest, DraftResponse, ValidatorResponse
- [x] T006 Create `formcraft-backend/app/models/submission.py` — Submission and Draft Pydantic models
- [x] T007 Create `formcraft-backend/app/services/submission_service.py` — SubmissionService with: create_submission(data, operator_id, org_id) — validates field_values server-side, generates reference_number via generate_submission_ref(), creates audit log entry
- [x] T008 Create `formcraft-backend/app/services/draft_service.py` — DraftService with: create_draft(data, operator_id, org_id), update_draft(draft_id, data), get_draft(draft_id), delete_draft(draft_id), compute_completion_percent(field_values, template_elements). Include AuditLogger calls for DRAFT_SAVED, DRAFT_UPDATED, DRAFT_DELETED events on each mutation.
- [x] T009 Create `formcraft-backend/app/api/routes/submissions.py` — Router: POST /api/submissions (create submission + audit log), GET /api/submissions (list with pagination for history)
- [x] T010 Create `formcraft-backend/app/api/routes/drafts.py` — Router: POST /api/desk/drafts, PATCH /api/desk/drafts/:draftId, GET /api/desk/drafts/:draftId, DELETE /api/desk/drafts/:draftId
- [x] T011 Create `formcraft-backend/app/api/routes/validators_route.py` — Router: GET /api/validators/:country — returns all registered validator patterns for the given country
- [x] T012 Update `formcraft-backend/app/api/routes/pdf.py` — extend POST /api/pdf/render/:templateId to accept optional `field_values` body; pass to render_template_pdf()
- [x] T013 Update `formcraft-backend/app/services/pdf/renderer.py` — extend render_template_pdf(template, field_values=None); pass field_values to element renderers via context dict
- [x] T014 Register new routers in `formcraft-backend/app/main.py` — add submissions, drafts, validators routers

**Checkpoint**: All APIs functional. Submission creates with reference number. Drafts CRUD works. Validators exposed. PDF renders with filled data.

---

## Phase 3: User Story 1 — Flow Layout Form Rendering (Priority: P1)

**Goal**: Form Filler renders all template elements as interactive form controls in Flow Layout

### Implementation

- [x] T015 Create `formcraft-frontend/src/app/features/desk/fill/fill.module.ts` — FormFillerModule with declarations and imports (ReactiveFormsModule, Material modules)
- [x] T016 Create `formcraft-frontend/src/app/features/desk/services/form-filler.service.ts` — FormFillerService: getTemplate(templateId) calls GET /api/desk/fill/:templateId; returns template with pages and elements
- [x] T017 Create `formcraft-frontend/src/app/features/desk/fill/fill.component.ts` — main container: loads template, constructs FormGroup dynamically (one FormControl per element using element.key as control name), manages form state
- [x] T018 Create `formcraft-frontend/src/app/features/desk/components/field-renderer/field-renderer.component.ts` — FieldRendererComponent with [ngSwitch] on element.type: text→mat-input, number→mat-input[type=number], date→mat-datepicker, currency→mat-input with mask, dropdown→mat-select with options from formatting.options, radio→mat-radio-group, checkbox→mat-checkbox, tafqeet→read-only display, image→file upload input, QR/barcode→read-only auto-generated from linked field value (same pattern as tafqeet)
- [x] T019 Create `formcraft-frontend/src/app/features/desk/fill/fill.component.html` — Flow Layout template: iterate pages with dividers, iterate elements per page in sort_order, render <fc-field-renderer> per element with FormControl binding
- [x] T020 Create `formcraft-frontend/src/app/features/desk/fill/fill.component.scss` — Flow Layout styles: vertical stack, full-width fields, page dividers, responsive padding, RTL support via [dir]
- [x] T021 Update `formcraft-frontend/src/app/app-routing.module.ts` — wire `/desk/fill/:templateId` to FormFillerModule (lazy loaded)

**Checkpoint**: Navigate to `/desk/fill/:templateId` → all fields render as interactive controls in vertical stack. Tab moves between fields.

---

## Phase 4: User Story 2 — Live Validation (Priority: P1)

**Goal**: Validation fires on blur with inline bilingual errors; error summary banner; print disabled until valid

### Implementation

- [x] T022 Create `formcraft-frontend/src/app/features/desk/services/validation.service.ts` — ValidationService: loadValidators(country) calls GET /api/validators/:country; getValidatorFn(element) returns Angular ValidatorFn based on element.validation JSONB + country validators
- [x] T023 Update fill.component.ts (T017) — on FormGroup construction, attach validators to each FormControl: Validators.required (if element.required), pattern validator from element.validation.pattern, country validator from ValidationService
- [x] T024 Update field-renderer.component — display mat-error below each field on blur (touched + invalid), show bilingual error message (required vs pattern vs country-specific)
- [x] T025 Create `formcraft-frontend/src/app/features/desk/components/error-summary/error-summary.component.ts` — ErrorSummaryComponent: input FormGroup, computes error count, displays sticky banner "N errors remaining" (translated), hidden when form is valid

**Checkpoint**: Fill invalid data → see inline errors on blur. Error summary shows count. Fix errors → summary disappears.

---

## Phase 5: User Story 3 — Tafqeet Auto-Computation (Priority: P1)

**Goal**: Tafqeet fields auto-compute Arabic amount-in-words as operator types in source field

### Implementation

- [x] T026 Create `formcraft-frontend/src/app/features/desk/services/tafqeet.service.ts` — TafqeetService: compute(amount, currency, language) calls POST /api/tafqeet/preview with 200ms debounce; returns Observable<string>
- [x] T027 Update fill.component.ts — for each tafqeet element, subscribe to its sourceElementKey FormControl's valueChanges; on change, call TafqeetService.compute(); pipe result to tafqeet FormControl (read-only)
- [x] T028 Update field-renderer.component — tafqeet type case renders as read-only mat-input with computed text, styled distinctly (italic, background highlight)

**Checkpoint**: Type amount in currency field → tafqeet field updates with Arabic words within 200ms.

---

## Phase 6: User Story 4 — Toolbar & Print Action (Priority: P1)

**Goal**: Toolbar with Print, Cancel, Clear All. Print generates PDF with filled data and creates submission.

### Implementation

- [x] T029 Create `formcraft-frontend/src/app/features/desk/components/form-toolbar/form-toolbar.component.ts` — FormToolbarComponent: inputs (formValid, isDirty); outputs (print, printNext, saveDraft, clearAll, cancel); Print/PrintNext disabled when !formValid
- [x] T030 Create `formcraft-frontend/src/app/features/desk/services/submission.service.ts` — SubmissionService: submit(templateId, templateVersion, fieldValues) calls POST /api/submissions; returns reference_number
- [x] T031 Update fill.component.ts — wire toolbar outputs: Print → call PDF render with field_values → open browser print dialog → on success call SubmissionService.submit() → show success toast with reference_number; Cancel → confirm dialog → navigate to /desk; Clear All → confirm → reset FormGroup; Print & Next → Print + reset form for next entry
- [x] T032 Add keyboard shortcuts — Ctrl+S → save draft; Ctrl+P → print (if valid); Ctrl+Enter → print & next
- [x] T033 Add beforeunload guard — warn on navigation if form isDirty and not saved

**Checkpoint**: Fill form → Print → PDF opens → submission created with reference number → toast shows. Cancel returns to dashboard.

---

## Phase 7: User Story 5 — Draft Save & Resume (Priority: P2)

**Goal**: Save partial form as draft; resume with data restored; auto-save every 60s

### Implementation

- [x] T034 Create `formcraft-frontend/src/app/features/desk/services/draft.service.ts` — DraftService: saveDraft(templateId, version, fieldValues, name), updateDraft(draftId, fieldValues), getDraft(draftId), deleteDraft(draftId)
- [x] T035 Update fill.component.ts — on "Save Draft" click: call DraftService.saveDraft() → show toast; on route with ?draft=draftId: load draft via DraftService.getDraft() → populate FormGroup with saved field_values
- [x] T036 Add auto-save timer — setInterval(60000) fires DraftService.updateDraft() if form isDirty since last save; non-blocking (fire-and-forget with error toast on failure)
- [x] T037 Create `formcraft-frontend/src/app/features/desk/components/version-warning/version-warning.component.ts` — dialog shown when draft.template_version < current template.version; options: "Continue with saved data" or "Start fresh"
- [x] T038 Update fill.component — on draft resume: compare draft.template_version with loaded template.version; if mismatch, show version-warning dialog before populating form
- [x] T039 Handle draft-to-submission transition — on successful Print, if a draft was loaded, delete it via DraftService.deleteDraft()

**Checkpoint**: Save draft → leave → return via ?draft=id → data restored. Auto-save fires silently. Version mismatch warns user.

---

## Phase 8: User Story 6 — Submission & Audit Trail (Priority: P1)

**Goal**: Every print creates an immutable submission with reference number and audit log

### Implementation

- [x] T040 Update `formcraft-backend/app/services/submission_service.py` — ensure create_submission: (1) re-validates field_values against template elements, (2) calls generate_submission_ref(org_id), (3) inserts submission row, (4) logs FORM_SUBMITTED audit event via AuditLogger
- [x] T041 Add server-side validation in submission_service — iterate template elements, check required fields present, validate patterns match, validate country-specific rules; return 422 with detailed errors array on failure
- [x] T042 Verify audit log entry contains: operator_id, template_id, template_version, reference_number, IP address, timestamp

**Checkpoint**: Print a form → submission row exists with reference_number → audit log entry exists with full metadata.

---

## Phase 9: Polish & Edge Cases

**Purpose**: Handle edge cases, RTL, accessibility, error recovery

- [x] T043 Handle template with zero fillable fields — show "No fillable fields" message, enable Print immediately (generates PDF with static content only)
- [x] T044 RTL styling for all form filler components — labels align right, error messages right-aligned, toolbar buttons mirrored
- [x] T045 Loading state — show skeleton while template loads; show spinner on Print/Save actions
- [x] T046 Network error handling — toast on API failure for draft save/submit; retry button for critical failures
- [x] T047 Long form scrollability — sticky error summary banner and sticky toolbar; smooth scroll to first error on print attempt when validation fails
- [x] T048 Compute completion_percent correctly — filled required fields / total required fields × 100; update on every draft save

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — all tasks parallel
- **Phase 2 (Backend)**: Depends on Phase 1 (migrations must exist)
- **Phase 3 (Rendering)**: Depends on Phase 2 (API must exist to load template)
- **Phase 4 (Validation)**: Depends on Phase 3 (form controls must exist to attach validators)
- **Phase 5 (Tafqeet)**: Depends on Phase 3 (field valueChanges subscriptions need FormGroup)
- **Phase 6 (Toolbar)**: Depends on Phase 3 (form state needed for print/save)
- **Phase 7 (Drafts)**: Depends on Phase 6 (save action infrastructure)
- **Phase 8 (Submission)**: Depends on Phase 6 (print action triggers submission)
- **Phase 9 (Polish)**: Depends on all previous phases

### Parallel Opportunities

```
Phase 1: T001 || T002 || T003 || T004 (all parallel)
Phase 2: T005 || T006 → T007 || T008 → T009 || T010 || T011 → T012 + T013 → T014
Phase 3: T015 → T016 → T017 → T018 → T019 → T020 → T021
Phase 4-5-6: Can overlap once Phase 3 is done:
  T022-T025 (validation) || T026-T028 (tafqeet) || T029-T033 (toolbar)
Phase 7: After Phase 6
Phase 8: After Phase 6 (can parallel with Phase 7)
```

### Critical Path

```
T001/T002 → T005/T006 → T007/T008 → T009/T010 → T014 (backend complete)
T003/T004 → T015 → T016 → T017 → T018 → T019 → T021 (form renders)
T019 → T022 → T023 → T024 (validation works)
T019 → T026 → T027 (tafqeet works)
T017 → T029 → T030 → T031 (print works)
T031 → T040 → T041 → T042 (audit works)
```

## Notes

- Total tasks: 48
- Estimated effort: 6-8 days for single developer
- All frontend paths relative to `formcraft-frontend/`
- All backend paths relative to `formcraft-backend/`
- Commit after each phase completion
- This is the largest single feature — consider splitting into 2 PRs: (1) Phases 1-6 as core, (2) Phases 7-9 as enhancement
- The existing tafqeet API is already production-ready — no changes needed to the converter itself
- PDF renderer extension (T012-T013) is backward-compatible — existing calls without field_values continue to work
