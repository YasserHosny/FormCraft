# Tasks: New Theme Desk Live Data Integration

**Input**: Design documents from `formcraft-specs/specs/050-new-theme-desk-data/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Constitution V mandates TDD. Integration tests included per user story.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup

**Purpose**: Prepare the codebase for live data integration

- [ ] T001 Delete mock data file at formcraft-frontend/src/app/features/ui-redesign/shared/mock-data.ts and remove all imports referencing it across ui-redesign components
- [ ] T002 Verify all existing desk services compile and are injectable by running `ng build` from formcraft-frontend/

**Checkpoint**: Mock data removed, existing services verified available

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared component changes that multiple user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 Add loading and empty state support to formcraft-frontend/src/app/features/ui-redesign/desk/dashboard.component.ts — add `loading`, `error`, and `isEmpty` state properties with corresponding template blocks in dashboard.component.html (skeleton loaders while fetching, error message on failure, empty state per section)
- [ ] T004 Add loading and error state support to formcraft-frontend/src/app/features/ui-redesign/desk/customers.component.ts — add `loading` and `error` properties with corresponding template blocks in customers.component.html

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 — Dashboard Shows Real KPIs (Priority: P1) 🎯 MVP

**Goal**: Replace hardcoded KPI numbers with real counts fetched from backend on page load

**Independent Test**: Log in, navigate to /ui/desk, verify KPI cards show actual counts matching backend data. Verify zero state displays "0" not mock numbers.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T005 [P] [US1] Integration test: dashboard KPIs display real counts in formcraft-frontend/src/app/features/ui-redesign/desk/dashboard.component.spec.ts — mock DeskService.getDashboard() and HistoryService.getSubmissions(), verify KPI values render in template, verify zero state renders "0", verify error state shows error message

### Implementation for User Story 1

- [ ] T006 [US1] Inject DeskService and HistoryService into formcraft-frontend/src/app/features/ui-redesign/desk/dashboard.component.ts constructor
- [ ] T007 [US1] In dashboard.component.ts ngOnInit, call DeskService.getDashboard() and store the response — extract drafts count, pinned count, and templates total for KPI cards
- [ ] T008 [US1] In dashboard.component.ts ngOnInit, call HistoryService.getSubmissions() with date_from set to today's date (ISO format) and limit=1 to get total today's submissions count from the response.total field
- [ ] T009 [US1] In dashboard.component.html, replace all hardcoded KPI values (e.g., "٢٣", "٧", "١٢٨") with bound properties: todaySubmissions, pendingDrafts, activeTemplates — format numbers with Angular's number pipe or custom Arabic numeral display
- [ ] T010 [US1] In dashboard.component.html, wrap KPI section with loading/error states from T003

**Checkpoint**: KPI cards show real numbers from backend. Zero state works. Error state works.

---

## Phase 4: User Story 2 — Recent Activity From Real Submissions (Priority: P1)

**Goal**: Replace hardcoded activities array with real submission history, limited to 10 most recent

**Independent Test**: Submit forms via classic desk, navigate to /ui/desk, verify activity table shows those submissions with correct form name, status, reference, timestamp.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T011 [P] [US2] Integration test: recent activity table displays real submissions in formcraft-frontend/src/app/features/ui-redesign/desk/dashboard.component.spec.ts — mock HistoryService.getSubmissions() with 3 items, verify table renders 3 rows with correct template_name, status, reference_number; verify empty state when 0 items

### Implementation for User Story 2

- [ ] T012 [US2] In dashboard.component.ts, use HistoryService.getSubmissions({ limit: 10, sort_by: 'created_at', sort_dir: 'desc' }) to fetch recent activity and store as `activities: SubmissionListItem[]`
- [ ] T013 [US2] Remove the hardcoded `activities` array from dashboard.component.ts
- [ ] T014 [US2] In dashboard.component.html, update the activity table to bind from the `activities` property — map SubmissionListItem fields (template_name → form name, status → status chip, reference_number → ref, created_at → time via date pipe, key_summary → customer display)
- [ ] T015 [US2] In dashboard.component.html, add "View All" link navigating to /ui/desk/history (or /desk/history via ClassicRedirect) after the activity table
- [ ] T016 [US2] In dashboard.component.html, add empty state for activity section when activities array is empty

**Checkpoint**: Activity table shows real submissions. Empty state works. "View All" link navigates to history.

---

## Phase 5: User Story 3 — Drafts Panel From Real Drafts (Priority: P1)

**Goal**: Replace hardcoded drafts array with real drafts from DeskService dashboard response

**Independent Test**: Save a draft via classic desk, navigate to /ui/desk, verify draft appears in panel with correct form name and timestamp. Click draft to resume.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T017 [P] [US3] Integration test: drafts panel displays real drafts in formcraft-frontend/src/app/features/ui-redesign/desk/dashboard.component.spec.ts — mock DeskService.getDashboard() with 2 drafts, verify panel renders 2 items with name, completion_percent, updated_at; verify empty state when 0 drafts; verify click calls router.navigate with correct draftId

### Implementation for User Story 3

- [ ] T018 [US3] In dashboard.component.ts, extract drafts from the DashboardData response (already fetched in T007) and store as `drafts: DraftResponse[]` (reuse DraftResponse type from DraftService)
- [ ] T019 [US3] Remove the hardcoded `drafts` array from dashboard.component.ts
- [ ] T020 [US3] In dashboard.component.html, update drafts panel to bind from `drafts` property — map DraftResponse fields (name or template_id → form name, completion_percent → progress bar, updated_at → time via date pipe)
- [ ] T021 [US3] In dashboard.component.ts, add `resumeDraft(draft: DraftResponse)` method that navigates to /ui/desk/fill/{draft.template_id} with queryParam draftId={draft.id}
- [ ] T022 [US3] In dashboard.component.html, add empty state for drafts panel when drafts array is empty

**Checkpoint**: Drafts panel shows real drafts. Click navigates to form filler. Empty state works.

---

## Phase 6: User Story 4 — Pinned Templates (Priority: P2)

**Goal**: Replace hardcoded pinnedForms array with real pinned templates from DeskService, capped at 6

**Independent Test**: Pin a template via classic desk, navigate to /ui/desk, verify pinned template appears. Click to navigate to form filler.

### Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T023 [P] [US4] Integration test: pinned templates section displays real pins in formcraft-frontend/src/app/features/ui-redesign/desk/dashboard.component.spec.ts — mock DeskService.getDashboard() with 8 pinned (2 unpublished), verify only 6 published render, verify click calls router.navigate to /ui/desk/fill/{id}, verify empty state

### Implementation for User Story 4

- [ ] T024 [US4] In dashboard.component.ts, extract pinned templates from DashboardData response (already fetched in T007), filter to `is_published === true`, and slice to max 6 — store as `pinnedTemplates: PinnedTemplate[]`
- [ ] T025 [US4] Remove the hardcoded `pinnedForms` array and its `PinnedForm` interface from dashboard.component.ts
- [ ] T026 [US4] In dashboard.component.html, update pinned forms grid to bind from `pinnedTemplates` — map PinnedTemplate fields (template_name → name, template_id → code/link, category → icon selection, pinned_at → last used indicator)
- [ ] T027 [US4] In dashboard.component.ts, add `fillTemplate(templateId: string)` method that navigates to /ui/desk/fill/{templateId}
- [ ] T028 [US4] In dashboard.component.html, add empty state for pinned section when pinnedTemplates array is empty — show message suggesting to pin templates from the template list

**Checkpoint**: Pinned templates show real data. Unpublished templates excluded. Click navigates to filler. Max 6 displayed.

---

## Phase 7: User Story 5 — Form Filler With Real Template Structure (Priority: P1)

**Goal**: Replace hardcoded form sections/fields with real template structure, wire validation, conditional logic, auto-fill, tafqeet, draft save, and submission

**Independent Test**: Navigate to /ui/desk/fill/{templateId}, verify real sections and fields render. Fill fields, verify validation. Test conditional visibility. Submit and verify submission created.

### Tests for User Story 5

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T029 [P] [US5] Integration test: form filler renders real template and submits in formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.spec.ts — mock FormFillerService.getTemplate() with a 2-page template, verify fields render dynamically, verify required field validation blocks submit, verify SubmissionService.submit() called on valid submit, verify DraftService.saveDraft() called on navigation away

### Implementation for User Story 5

- [ ] T030 [US5] Inject FormFillerService, ConditionEngineService, AutoFillService, FillerTafqeetService, ValidationService, SubmissionService, DraftService, CustomerService, and LanguageService into formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts constructor
- [ ] T031 [US5] In form-filler.component.ts ngOnInit, call FormFillerService.getTemplate(templateId) and store the FillTemplate response — extract pages and elements for rendering
- [ ] T032 [US5] In form-filler.component.ts, build an Angular Reactive FormGroup from the template elements — create FormControls for each element keyed by element.key, applying required validators from element.required and element.validation
- [ ] T033 [US5] Remove all hardcoded `sections`, `sideSections`, `alerts`, `shortcuts`, `recentCustomers`, and `customerResults` arrays from form-filler.component.ts
- [ ] T034 [US5] In form-filler.component.html, replace hardcoded sections with dynamic rendering — iterate over template pages and their elements, render appropriate field components based on element.type (text, number, date, select, checkbox, signature, etc.), display label_ar or label_en based on current language
- [ ] T035 [US5] In form-filler.component.ts, initialize ConditionEngineService with the template elements and form group — subscribe to visibilityChanged$ and requiredChanged$ to dynamically show/hide fields and toggle required validators
- [ ] T036 [US5] In form-filler.component.ts, wire tafqeet for numeric fields — identify elements with tafqeet formatting, subscribe to their FormControl valueChanges, call FillerTafqeetService.compute() and display the result
- [ ] T037 [US5] In form-filler.component.ts, wire customer auto-fill — when a customer is selected, call CustomerService.getAutoPopulateData(customerId, templateId) then pass mappings to AutoFillService.executeAutoFill()
- [ ] T038 [US5] In form-filler.component.ts, implement saveDraft() — call DraftService.saveDraft() or updateDraft() with current form values and templateId/version, store returned draftId for subsequent updates
- [ ] T039 [US5] In form-filler.component.ts, implement submitForm() — validate all visible required fields, call SubmissionService.submit() with templateId, version, and field values, show success snackbar and navigate back to dashboard
- [ ] T040 [US5] In form-filler.component.ts, implement auto-save on navigation — add a CanDeactivate guard or use ngOnDestroy to call saveDraft() when the operator navigates away with unsaved changes
- [ ] T041 [US5] In form-filler.component.ts ngOnInit, check for draftId query parameter — if present, call DraftService.getDraft(draftId) and populate the form with saved field_values
- [ ] T042 [US5] In form-filler.component.ts, after loading a draft via getDraft(), compare draft.template_version against the current published template version from getTemplate() — if mismatched, show a snackbar or dialog warning the operator that the template has been updated, offering to reload with the latest version or continue with the saved structure
- [ ] T043 [US5] In form-filler.component.html, add validation error messages — display inline errors below each field when touched and invalid, show error summary panel listing all current validation errors
- [ ] T044 [US5] In form-filler.component.html, update the side navigation to render real sections from template pages with completion counts based on filled/total fields per page
- [ ] T045 [US5] Add loading state to form-filler.component.html — show skeleton while template structure loads, error state if template fetch fails

**Checkpoint**: Form filler renders real template. Validation, conditions, tafqeet, auto-fill work. Draft save/resume works. Submit creates submission. Draft version mismatch detected.

---

## Phase 8: User Story 6 — Customers Page With Real Data (Priority: P2)

**Goal**: Replace mock CUSTOMERS data with real customer profiles from CustomerService with search and pagination

**Independent Test**: Navigate to /ui/desk/customers, verify real customer list appears. Search by name and verify filter works. Click customer to view detail.

### Tests for User Story 6

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T046 [P] [US6] Integration test: customers page displays real data in formcraft-frontend/src/app/features/ui-redesign/desk/customers.component.spec.ts — mock CustomerService.list() with paginated response, verify list renders customer names and IDs, verify search calls list() with search param after debounce, verify empty state when no results

### Implementation for User Story 6

- [ ] T047 [US6] Inject CustomerService into formcraft-frontend/src/app/features/ui-redesign/desk/customers.component.ts constructor
- [ ] T048 [US6] In customers.component.ts ngOnInit, call CustomerService.list() with default pagination (page 1, page_size 25) and store response — extract items for display and total for pagination
- [ ] T049 [US6] Remove the `customers = CUSTOMERS` mock assignment and the CUSTOMERS import from customers.component.ts
- [ ] T050 [US6] In customers.component.html, update customer list to bind from real Customer model fields — map name, national_id (or equivalent), phone, email, is_active status
- [ ] T051 [US6] In customers.component.ts, add search functionality — add a search input bound to a subject, debounce 300ms, call CustomerService.list({ search: query }) on each emission
- [ ] T052 [US6] In customers.component.ts, add pagination — handle page change events, call CustomerService.list() with updated page parameter
- [ ] T053 [US6] In customers.component.html, add empty state when no customers match search, and loading state while data is being fetched

**Checkpoint**: Customer list shows real data. Search filters in real-time. Pagination works. Empty/loading states render correctly.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup and cross-story validation

- [ ] T054 [P] Verify all i18n — ensure no hardcoded Arabic strings remain in dashboard, form-filler, or customers components; add any missing translation keys to formcraft-frontend/src/assets/i18n/ar.json and en.json
- [ ] T055 [P] Verify RTL/LTR rendering — test all three components in both Arabic and English mode, fix any layout regressions
- [ ] T056 Remove any remaining mock-data references — grep for 'mock-data', 'CUSTOMERS', 'pinnedForms', 'ActivityItem', 'DraftItem' across the ui-redesign directory and remove dead code
- [ ] T057 Run quickstart.md validation — follow all verification steps in formcraft-specs/specs/050-new-theme-desk-data/quickstart.md and confirm each passes
- [ ] T058 Verify dashboard loads within 3 seconds — measure from navigation to full render with network throttling to "Fast 3G" to confirm SC-003

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user stories
- **Phases 3–6 (US1–US4)**: All depend on Phase 2. US1–US3 share the DeskService.getDashboard() call (T007), so implement US1 first, then US2–US4 can proceed in parallel since they consume different parts of the same response.
- **Phase 7 (US5)**: Depends on Phase 2 only — can proceed in parallel with US1–US4 (different component)
- **Phase 8 (US6)**: Depends on Phase 2 only — can proceed in parallel with all other stories (different component)
- **Phase 9 (Polish)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (KPIs)**: Depends on Phase 2 only — MVP starting point
- **US2 (Activity)**: Depends on T007 from US1 (shared dashboard data fetch) — implement after US1 or refactor to share the call
- **US3 (Drafts)**: Depends on T007 from US1 (shared dashboard data fetch) — implement after US1 or refactor to share the call
- **US4 (Pinned Templates)**: Depends on T007 from US1 (shared dashboard data fetch) — implement after US1
- **US5 (Form Filler)**: Independent of dashboard stories — can start after Phase 2
- **US6 (Customers)**: Independent of all other stories — can start after Phase 2

### Within Each User Story

- Write test (FAIL) → Remove mock data → Wire service → Update template bindings → Add states → Verify test (PASS)

### Parallel Opportunities

- US5 (Form Filler) and US6 (Customers) can run fully in parallel with dashboard stories (US1–US4) since they modify different files
- Within US5, tasks T030–T032 (inject, fetch, build form) are sequential; T035–T037 (conditions, tafqeet, auto-fill) can run in parallel after T034
- Polish tasks T054 and T055 can run in parallel
- All test tasks (T005, T011, T017, T023, T029, T046) marked [P] can be written in parallel before implementation begins

---

## Parallel Example: After Phase 2

```
# Developer A: Dashboard stories (sequential due to shared data fetch)
T005 (test) → T006 → T007 → T008 → T009 → T010 (US1 KPIs)
T011 (test) → T012 → T013 → T014 → T015 → T016 (US2 Activity)
T017 (test) → T018 → T019 → T020 → T021 → T022 (US3 Drafts)
T023 (test) → T024 → T025 → T026 → T027 → T028 (US4 Pinned)

# Developer B: Form Filler (independent)
T029 (test) → T030 → T031 → T032 → T033 → T034 → T035/T036/T037 → T038 → T039 → T040 → T041 → T042 → T043 → T044 → T045

# Developer C: Customers (independent)
T046 (test) → T047 → T048 → T049 → T050 → T051 → T052 → T053
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T002)
2. Complete Phase 2: Foundational (T003–T004)
3. Complete Phase 3: User Story 1 — KPIs (T005–T010)
4. **STOP and VALIDATE**: Dashboard shows real KPI numbers, test passes
5. Demo if ready — operators see real counts

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 (KPIs) → Real numbers on dashboard (MVP!)
3. US2 (Activity) + US3 (Drafts) → Dashboard fully live
4. US4 (Pinned Templates) → Quick-access templates working
5. US5 (Form Filler) → Complete form workflow in new theme
6. US6 (Customers) → Customer management in new theme
7. Polish → i18n verified, RTL tested, performance confirmed

---

## Notes

- All services are `providedIn: 'root'` — no module imports needed for standalone components
- US1–US4 share a single DeskService.getDashboard() call — consolidate in T007 and distribute data to each section
- Form filler (US5) is the largest story with 17 tasks (incl. test) — consider splitting implementation across sessions
- Mock data deletion (T001) may cause compile errors until services are wired — T002 verifies build still passes after cleanup
- Commit after each task or logical group
- Each user story starts with a failing test (Constitution V compliance)
