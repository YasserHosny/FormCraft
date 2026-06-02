# Tasks: Spark Theme — Add Customer (F056)

**Branch**: `056-spark-add-customer`  
**Input**: Design documents from `formcraft-specs/specs/056-spark-add-customer/`  
**Constitution V**: TDD mandatory — test files written and failing **before** implementation begins  
**Frontend base**: `formcraft-frontend/src/app/features/ui-redesign/`

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no blocking dependency)
- **[US#]**: Maps to user story from spec.md

---

## Phase 1: Setup

**Purpose**: Create all new file shells so tests can import them immediately.

- [x] T001 Create empty `add-customer.component.ts` with `@Component` decorator and selector `fc-spark-add-customer` in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.ts`
- [x] T002 [P] Create empty `add-customer.component.html` with a single `<div>` placeholder in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.html`
- [x] T003 [P] Create empty `add-customer.component.scss` in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.scss`
- [x] T004 Create `add-customer.component.spec.ts` with `TestBed` scaffold importing `AddCustomerComponent` in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.spec.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Route wiring and i18n keys must exist before any user story can render or be tested end-to-end.

**⚠️ CRITICAL**: Complete before user story implementation phases.

- [x] T005 Replace the `SparkFeatureBridgeComponent` entry at path `desk/customers/new` with a `loadComponent` pointing to `AddCustomerComponent` in `formcraft-frontend/src/app/features/ui-redesign/ui-redesign.routes.ts`
- [x] T006 [P] Add `add_customer.*` English translation keys (title, all 7 field labels, all placeholder texts, button labels, all error messages, duplicate error) to `formcraft-frontend/src/assets/i18n/en.json`
- [x] T007 [P] Add `add_customer.*` Arabic translation keys matching the same key structure as en.json to `formcraft-frontend/src/assets/i18n/ar.json`

**Checkpoint**: Route resolves to `AddCustomerComponent` and translation keys are available in both languages.

---

## Phase 3: User Story 1 — Create a New Customer (Priority: P1) 🎯 MVP

**Goal**: Operator can open the native Spark form, fill required fields, and save a new customer record.

**Independent Test**: Navigate to `/ui/desk/customers/new`, fill Arabic Name + Identifier Type + Identifier, click Save → customer created, redirected to `/desk/customers/:id`.

### Tests for User Story 1 (TDD — write FIRST, must FAIL before implementation)

- [x] T008 [US1] Write failing test: component renders a `<form>` element (no placeholder text) in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.spec.ts`
- [x] T009 [US1] Write failing test: Save button is present and clicking it with empty form triggers `name_ar` required error in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.spec.ts`
- [x] T010 [US1] Write failing test: clicking Cancel calls `router.navigate(['/ui/desk/customers'])` in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.spec.ts`
- [x] T011 [US1] Write failing test: successful `CustomerService.create()` call triggers `router.navigate(['/desk/customers', id])` in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.spec.ts`

### Implementation for User Story 1

- [x] T011a [US1] Create `notWhitespace` `ValidatorFn` that returns `{ whitespace: true }` when the trimmed value is empty, export from `formcraft-frontend/src/app/shared/validators/not-whitespace.validator.ts`
- [x] T012 [US1] Implement `FormGroup` with 7 `FormControl` fields, required validators on `name_ar`/`identifier_type`/`identifier`, `Validators.email` on `contact_email`, `notWhitespace` custom validator on `name_ar` in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.ts`
- [x] T013 [US1] Implement `save()` method: guard on `form.invalid`, call `CustomerService.create()`, navigate to `/desk/customers/:id` on success; declare `saving = false` property and set `true` before call / `false` in both success and error callbacks in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.ts`
- [x] T014 [US1] Implement `cancel()` method navigating to `/ui/desk/customers` in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.ts`
- [x] T015 [US1] Build HTML template: page header with back arrow, full-width `mat-form-field` for Arabic Name and English Name, two-column row for Identifier Type dropdown + Identifier, two-column row for Phone + Email, full-width textarea for Address, Cancel + Save button row in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.html`
- [x] T016 [US1] Apply RTL attributes: `dir="auto"` on `name_ar` input and `address` textarea; `dir="ltr"` on `name_en`, `identifier`, `contact_phone`, `contact_email` inputs in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.html`
- [x] T017 [US1] Wire all `mat-error` elements for required-field validation (name_ar, identifier_type, identifier) and email format error (contact_email) using translation keys in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.html`
- [x] T018 [US1] Populate the Identifier Type dropdown with all 5 options (national_id, iqama, commercial_register, passport, other) defaulting to `national_id` in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.ts`

**Checkpoint**: US1 acceptance scenarios 1–4 pass. Form renders, saves, cancels, and validates required fields.

---

## Phase 4: User Story 2 — Duplicate Customer Detection (Priority: P2)

**Goal**: HTTP 409 response shows an inline error beneath the Identifier field; form stays open with all data preserved.

**Independent Test**: Submit a form with an identifier that already exists → inline error appears under the Identifier field, no navigation occurs.

### Tests for User Story 2 (TDD — write FIRST, must FAIL before implementation)

- [x] T019 [US2] Write failing test: when `CustomerService.create()` returns HTTP 409, the `identifier` `FormControl` has error key `duplicate` and the form remains open in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.spec.ts`

### Implementation for User Story 2

- [x] T020 [US2] In `save()` error callback, detect `err.status === 409` and call `this.form.get('identifier')!.setErrors({ duplicate: true })` to inject the error without closing the form in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.ts`
- [x] T021 [US2] Add `<mat-error *ngIf="form.get('identifier')?.hasError('duplicate')">` element beneath the Identifier `mat-form-field` using the translation key `add_customer.error_duplicate` in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.html`
- [x] T022 [US2] Clear the `duplicate` error from `identifier` `FormControl` on each `valueChanges` emission so the error disappears as soon as the operator edits the field in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.ts`

**Checkpoint**: US2 acceptance scenario passes. Duplicate identifier shows inline error, form data preserved.

---

## Phase 5: User Story 3 — Optional Fields Flexibility (Priority: P3)

**Goal**: Form submits successfully with only the three required fields; optional fields are excluded (sent as `undefined`, not empty string) from the payload.

**Independent Test**: Submit with only Arabic Name + Identifier Type + Identifier → customer created without validation errors on Phone, Email, English Name, or Address.

### Tests for User Story 3 (TDD — write FIRST, must FAIL before implementation)

- [x] T023 [US3] Write failing test: `buildPayload()` returns an object containing only `name_ar`, `identifier_type`, `identifier`, and `custom_fields: {}` when all optional fields are empty in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.spec.ts`

### Implementation for User Story 3

- [x] T024 [US3] Extract a `buildPayload()` helper in `AddCustomerComponent` that constructs `CustomerCreate` from form values, omitting keys whose values are falsy (empty string / null) except for the three required fields and `custom_fields: {}` in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.ts`
- [x] T025 [US3] Update `save()` to call `this.buildPayload()` instead of spreading form value directly in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.ts`

**Checkpoint**: US3 acceptance scenarios 1 and 2 pass. Minimum-data and full-data submissions both work correctly.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Loading state, styling, network-error handling, and final RTL validation.

- [x] T026 Bind `[disabled]="saving"` on the Save button and render `<mat-spinner diameter="18">` inside it when `saving` is true in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.html` (the `saving` flag itself is declared and managed in T013)
- [x] T027 [P] Handle non-409 API errors in `save()`: display `err.error?.detail` or fallback message via `MatSnackBar` without closing the form in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.ts`
- [x] T028 [P] Add SCSS: two-column grid (`.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }`) and full-width field overrides in `formcraft-frontend/src/app/features/ui-redesign/desk/add-customer.component.scss`
- [x] T029 Run quickstart.md validation: navigate to `/ui/desk/customers/new` in Spark theme, verify all 6 checkpoints pass including Arabic RTL layout (SC-001: flow under 60s, FR-010: Spark sidebar and header visible, FR-011: all labels in Arabic when language switched) per `formcraft-specs/specs/056-spark-add-customer/quickstart.md`
- [x] T030 [P] Update checklist `formcraft-specs/specs/056-spark-add-customer/checklists/requirements.md` to mark all items verified

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — **blocks all user story phases**
- **Phase 3 (US1)**: Depends on Phase 2 — core MVP, blocks nothing else
- **Phase 4 (US2)**: Depends on Phase 3 (needs `save()` method to extend)
- **Phase 5 (US3)**: Depends on Phase 3 (needs form + `save()` to refactor)
- **Phase 6 (Polish)**: Depends on Phase 3 (builds on existing `save()`); T027/T028 also depend on Phase 3

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 — the core, independent MVP
- **US2 (P2)**: Depends on US1 `save()` method (extends the error callback)
- **US3 (P3)**: Depends on US1 form setup (refactors the payload construction)

### Within Each Phase

- TDD tasks (T008–T011, T019, T023) MUST be written and confirmed **failing** before T012+ implementation begins
- T012 (FormGroup) MUST complete before T013/T014 (methods using `form`)
- T015 (template) MUST complete before T016/T017 (template additions)
- T020 MUST complete before T021/T022 (duplicate error in template depends on TS method)
- T024 MUST complete before T025 (buildPayload extracted before save() updated)

---

## Parallel Opportunities

```
Phase 1:   T001 → T002+T003 [parallel] → T004
Phase 2:   T005 → T006+T007 [parallel]
Phase 3:   T008 → T009+T010+T011 [parallel] → T012 → T013+T014 [parallel] → T015 → T016+T017+T018 [parallel]
Phase 4:   T019 → T020 → T021+T022 [parallel]
Phase 5:   T023 → T024 → T025
Phase 6:   T026 → T027+T028 [parallel] → T029+T030 [parallel]
```

---

## Implementation Strategy

### MVP First (US1 only — ~18 tasks)

1. Complete Phase 1 + Phase 2 (setup + route + i18n)
2. Complete Phase 3 (US1 tests + implementation)
3. **Stop and validate**: Run `ng test`, check all US1 scenarios manually
4. Feature is shippable at this point — operator can create customers in Spark theme

### Incremental Delivery

1. Phase 1 + 2 → Foundation ready
2. Phase 3 → MVP: basic create flow works
3. Phase 4 → Duplicate detection added
4. Phase 5 → Optional fields payload cleanup
5. Phase 6 → Polish: loading state, error handling, styling

---

## Summary

| Metric | Count |
|--------|-------|
| Total tasks | 30 |
| Phase 1 (Setup) | 4 |
| Phase 2 (Foundational) | 3 |
| Phase 3 (US1 — MVP) | 11 |
| Phase 4 (US2) | 4 |
| Phase 5 (US3) | 3 |
| Phase 6 (Polish) | 5 |
| Tasks with [P] parallel marker | 14 |
| TDD test tasks | 5 (T008–T011, T019, T023) |

**MVP scope**: Phases 1–3 (18 tasks) deliver a shippable Add Customer form in Spark theme.
