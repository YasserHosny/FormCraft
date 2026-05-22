# Tasks: Feedback Dashboard Search & Labels

**Input**: Design documents from `formcraft-specs/specs/12-feedback-dashboard-search/`  
**Branch**: `012-feedback-dashboard-search` | **Date**: 2026-05-07  
**Prerequisites**: plan.md ✅ · spec.md ✅ · data-model.md ✅ · contracts/api.md ✅ · research.md ✅ · quickstart.md ✅  
**Depends on**: Feature 011 (`001-customer-feedback`) fully applied

**Tests**: Included — TDD approach consistent with feature 011 pattern.

**Organization**: Tasks grouped by user story (P1 Search/Filter → P2 Labels) so each story is independently implementable, testable, and deployable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[Story]**: User story label (US1 / US2)

## Path Conventions

- Backend: `formcraft-backend/`
- Frontend: `formcraft-frontend/src/app/`

---

## Phase 1: Setup

**Purpose**: Create migration, empty file skeletons, and extend existing modules so subsequent phases have a stable base.

- [x] T001 Write migration `formcraft-backend/supabase/migrations/009_create_feedback_labels.sql` — full SQL from data-model.md (`feedback_labels` table, `feedback_submission_labels` join table, indexes, RLS policies)
- [x] T002 [P] Create backend file skeletons: `formcraft-backend/app/schemas/label.py` (empty), `formcraft-backend/tests/unit/feedback/test_label_service.py` (empty), `formcraft-backend/tests/integration/feedback/test_admin_label_route.py` (empty)
- [x] T003 [P] Create frontend file skeletons: `formcraft-frontend/src/app/features/feedback/services/feedback-filter-state.service.ts` (empty), `formcraft-frontend/src/app/features/feedback/components/label-manager/label-manager.component.ts` (empty), `label-manager.component.html` (empty), `label-manager.component.scss` (empty)

**Checkpoint**: Migration and empty modules in place — ready to write schemas and tests

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Pydantic schemas, extended service skeleton, and Angular service stubs. Shared by both user stories — must be complete before any story implementation begins.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Write all Pydantic models in `formcraft-backend/app/schemas/label.py`: `LabelColour` (str enum: red, orange, yellow, green, teal, blue, purple, pink, grey, brown), `LabelCreateRequest`, `LabelUpdateRequest`, `LabelResponse`, `SubmissionLabelAssignRequest` (label_ids: list[UUID], max 5); extend `FeedbackAdminItem` in `formcraft-backend/app/schemas/feedback.py` to include `labels: list[LabelResponse]`
- [x] T005 [P] Add empty method stubs to `formcraft-backend/app/services/feedback/service.py`: `create_label()`, `update_label()`, `delete_label()`, `assign_labels()`; add `search` and `label_ids` parameters to existing `list_feedback()` signature (no implementation yet)
- [x] T006 [P] Add HTTP method stubs to `formcraft-frontend/src/app/features/feedback/services/feedback.service.ts`: `getLabels()`, `createLabel()`, `updateLabel()`, `deleteLabel()`, `assignLabels()`; extend `listFeedback()` signature to accept `search` and `labelIds` params (return `EMPTY` observables for new methods)

**Checkpoint**: Schemas compile, service stubs importable — user story implementation can begin

---

## Phase 3: User Story 1 — Search and Filter Feedback (Priority: P1) 🎯 MVP

**Goal**: Admins can use a debounced keyword search and multi-facet filters (status, submitter, date range) to narrow the feedback list. Filter state persists within the session.

**Independent Test**: Submit 5 entries with distinct text and statuses → type a keyword → verify only matching entries shown → apply status filter → verify intersection → navigate away and back → verify filter state preserved.

### Backend Tests — Write First, Must FAIL Before Implementation

- [x] T007 [P] [US1] Write unit tests for extended `list_feedback()` in `formcraft-backend/tests/unit/feedback/test_label_service.py`: keyword match returns correct rows, no match returns empty, partial ILIKE match, multiple facet filters return intersection, `label_ids` filter deferred to US2 tests
- [x] T008 [P] [US1] Write integration tests in `formcraft-backend/tests/integration/feedback/test_admin_label_route.py`: `GET /api/admin/feedback?search=keyword` → 200 matching results only, `GET /api/admin/feedback?search=no-match` → 200 empty data array, `GET /api/admin/feedback?status=new&search=keyword` → 200 intersection, `GET /api/admin/feedback` by non-admin → 403

### Backend Implementation — US1

- [x] T009 [US1] Implement `search` (ILIKE on `text_content`) and `status`/`user_id`/`date_from`/`date_to` filter params in `list_feedback()` in `formcraft-backend/app/services/feedback/service.py` — dynamic WHERE clause; JOIN `feedback_submission_labels` and `feedback_labels` for `labels` field on each row (empty array if none)
- [x] T010 [US1] Implement `list_submitters()` in `formcraft-backend/app/services/feedback/service.py` — SELECT DISTINCT `user_id` from `feedback_submissions`, JOIN `profiles` for `display_name` (fallback to email), return list ordered alphabetically by display_name
- [x] T011 [US1] Add `GET /api/admin/feedback/submitters` and extend `GET /api/admin/feedback` in `formcraft-backend/app/api/routes/admin.py` to accept `search: str | None` and `label_ids: list[UUID] | None` query params and pass to service; add `submitter_id` as the filter query param name (replacing ambiguous `user_id`) consistent with contracts/api.md

### Frontend Implementation — US1

- [x] T012 [US1] Implement `FeedbackFilterStateService` in `formcraft-frontend/src/app/features/feedback/services/feedback-filter-state.service.ts` — singleton Angular service with `BehaviorSubject<FeedbackFilterState>` holding `{ search, status, submitterId, dateFrom, dateTo, labelIds }`; expose `setFilter()`, `clearAll()`, `getSnapshot()` methods; state lives for the Angular session only (no storage)
- [x] T013 [US1] Wire HTTP calls in `formcraft-frontend/src/app/features/feedback/services/feedback.service.ts`: extend `listFeedback()` to pass `search` and `labelIds` params; add `getSubmitters()` calling `GET /api/admin/feedback/submitters` to return the autocomplete data source
- [x] T014 [US1] Add search bar to `formcraft-frontend/src/app/features/feedback/components/feedback-admin/feedback-admin.component.html` — Angular Material `mat-form-field` with debounce via RxJS `debounceTime(400)` + `distinctUntilChanged()` piped through `FeedbackFilterStateService`; bind to `feedback-admin.component.ts`
- [x] T015 [US1] Add filter controls to `feedback-admin.component.html` and `feedback-admin.component.ts`: status chip group (new/reviewed/resolved/all), submitter autocomplete (`mat-autocomplete` populated from `getSubmitters()` — display_name shown, submitter_id sent as filter param), date range pickers (`mat-datepicker`); each control calls `FeedbackFilterStateService.setFilter()`
- [x] T016 [US1] Add "Clear filters" button and empty-state to `feedback-admin.component.html`: (a) "Clear filters" button visible only when any filter or search is active, calls `FeedbackFilterStateService.clearAll()`; (b) empty-state block shown when `data.length === 0` and any filter is active — displays "No results found" message and an inline "Clear filters" link; subscribe to filter state in `feedback-admin.component.ts` to re-fetch list on every change
- [x] T017 [US1] Add US1 i18n keys to `formcraft-frontend/src/assets/i18n/ar.json` and `en.json`: search placeholder, filter by status, filter by submitter, filter by date, from date, to date, clear filters, no results found, showing N results

**Checkpoint**: Search and filtering fully functional — debounce fires, all facets work, state persists within session, admin can locate submissions by keyword → **MVP deliverable**

---

## Phase 4: User Story 2 — Categorize Feedback with Labels (Priority: P2)

**Goal**: Admins can create, edit, and delete named semantic-colour labels from an inline modal on the dashboard. They assign up to 5 labels per submission via a chip-autocomplete. Label filter uses OR logic; assignments reflect instantly without page reload.

**Independent Test**: Create label "Bug Report" (red) → assign to a submission → verify chip appears on row → filter by that label → verify only tagged submission shown → delete label → verify chip removed from all rows.

### Backend Tests — Write First, Must FAIL Before Implementation

- [x] T019 [P] [US2] Write unit tests for label service methods in `formcraft-backend/tests/unit/feedback/test_label_service.py`: `create_label` success, duplicate name → 409, invalid colour → 422; `update_label` success, 404, name conflict → 409; `delete_label` success, 404, cascade removes submission associations; `assign_labels` 3 labels success, 6 labels → 400, 0 labels clears all, invalid label_id → 404; concurrency: two sequential `assign_labels()` calls on the same submission — verify second call's label set is final state (last-write-wins)
- [x] T020 [P] [US2] Write integration tests in `formcraft-backend/tests/integration/feedback/test_admin_label_route.py`: `GET /api/admin/labels` → 200 list, 403 non-admin; `POST /api/admin/labels` → 201, 409 duplicate, 400 invalid colour, 403; `PATCH /api/admin/labels/{id}` → 200, 404, 409, 403; `DELETE /api/admin/labels/{id}` → 204, 404, 403; `PUT /api/admin/feedback/{id}/labels` → 200 valid, 400 > 5 labels, 404 bad label_id, 403; `GET /api/admin/feedback?label_ids=uuid1,uuid2` → 200 OR logic (both tagged submissions returned, non-tagged excluded)

### Backend Implementation — US2

- [x] T021 [US2] Implement `create_label(admin_id, payload)` in `formcraft-backend/app/services/feedback/service.py` — insert row, raise 409 on UNIQUE violation
- [x] T022 [US2] Implement `update_label(id, payload)` in `formcraft-backend/app/services/feedback/service.py` — PATCH row, raise 404 if not found, raise 409 on name conflict
- [x] T023 [US2] Implement `delete_label(id)` in `formcraft-backend/app/services/feedback/service.py` — DELETE row (CASCADE handles `feedback_submission_labels`), raise 404 if not found
- [x] T024 [US2] Implement `assign_labels(feedback_id, label_ids)` in `formcraft-backend/app/services/feedback/service.py` — enforce ≤ 5 limit (raise 400 if exceeded), DELETE existing rows for `feedback_id`, INSERT new set; raise 404 if any `label_id` not found
- [x] T025 [US2] Add `label_ids` OR filter to `list_feedback()` in `formcraft-backend/app/services/feedback/service.py` — `WHERE fsl.label_id = ANY(label_ids)` when param present. **Note**: depends on T009 (list_feedback base implementation) — must not be implemented in parallel with T009
- [x] T026 [US2] Add label CRUD + assignment routes to `formcraft-backend/app/api/routes/admin.py`: `GET /api/admin/labels`, `POST /api/admin/labels`, `PATCH /api/admin/labels/{id}`, `DELETE /api/admin/labels/{id}`, `PUT /api/admin/feedback/{id}/labels` — all behind `require_role(Role.ADMIN)`

### Frontend Implementation — US2

- [x] T027 [P] [US2] Implement `getLabels()`, `createLabel()`, `updateLabel()`, `deleteLabel()`, `assignLabels()` HTTP calls in `formcraft-frontend/src/app/features/feedback/services/feedback.service.ts`
- [x] T028 [US2] Build `LabelManagerComponent` in `formcraft-frontend/src/app/features/feedback/components/label-manager/label-manager.component.ts` and `.html`: MatDialog modal showing list of existing labels (name chip with colour swatch, inline edit, delete with confirmation); "New label" form with name input (max 50 chars) + 10-colour swatch picker (not free-input) + Save button; optimistic update on create/edit/delete (roll back on API error)
- [x] T029 [US2] Add "Manage Labels" button to `feedback-admin.component.html` — opens `LabelManagerComponent` as `MatDialog`; refresh label list in filter controls after dialog closes
- [x] T030 [US2] Add labels column to `feedback-admin.component.html` — display label chips (name + colour) on each submission row; in expanded row show chip-autocomplete (`mat-autocomplete`) backed by `getLabels()`; selecting a label from autocomplete calls `assignLabels()` via `PUT /api/admin/feedback/{id}/labels`; clicking a chip removes it (same PUT with updated list); show validation message when 6th label attempted
- [x] T031 [US2] Add label multi-select to the filter controls in `feedback-admin.component.ts` — list of label chips (toggle on/off); selected label IDs stored in `FeedbackFilterStateService` as `labelIds`; triggers re-fetch with OR logic
- [x] T032 [US2] Add US2 i18n keys to `formcraft-frontend/src/assets/i18n/ar.json` and `en.json`: manage labels, new label, label name, label colour, create label, edit label, delete label, delete label confirm, max labels reached (5 maximum), no labels yet, filter by label

**Checkpoint**: Labels fully functional end-to-end — create, assign (up to 5), filter (OR), edit, delete with cascade; all reflected instantly without page reload

---

## Phase 5: Polish & Cross-Cutting Concerns

- [x] T033 [P] Run full backend test suite and fix failures: `pytest formcraft-backend/tests/unit/feedback/test_label_service.py formcraft-backend/tests/integration/feedback/test_admin_label_route.py -v`
- [x] T034 [P] Run `ruff check .` on all new/modified backend Python files and fix violations
- [x] T035 [P] Verify label chips render correctly at 360px viewport width in `feedback-admin.component.scss` — chips should wrap or truncate gracefully, not overflow
- [ ] T036 Manual E2E validation per `quickstart.md` using a **10,000-row seed dataset** (SC-001): apply migration → seed test data → verify search returns within 2 seconds → create 3 labels → assign labels to submissions → filter by label (verify OR) → search keyword (verify debounce) → apply multi-facet filter (verify AND across facets) → navigate away and back (verify filter state) → edit label (verify instant reflection) → delete label (verify cascade removal from all rows)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    └── Phase 2 (Foundational)   ← BLOCKS both user stories
            ├── Phase 3 (US1 — Search/Filter)   🎯 MVP
            │       └── Phase 4 (US2 — Labels)
            └── Phase 5 (Polish) ← after all desired stories complete
```

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2 — no story dependencies
- **US2 (P2)**: Starts after Phase 2 — extends filter controls and dashboard built in US1; `FeedbackFilterStateService` (US1) must exist before `labelIds` can be stored in it; **T025 depends on T009** (label_ids OR filter extends the base list_feedback() built in T009 — these must not run in parallel)

### Within Each User Story

1. Write tests first → confirm they FAIL
2. Schemas in Phase 2 before service implementation
3. Service methods before route handlers
4. Backend complete before wiring Angular HTTP calls
5. Angular service wired before building component interactions
6. i18n keys added as last step per story

---

## Parallel Opportunities

### Phase 1
```
T002 (backend skeletons) ‖ T003 (frontend skeletons)
```

### Phase 2
```
T005 (service stubs) ‖ T006 (Angular service stubs)
```

### Phase 3 (US1)
```
# Tests (write in parallel):
T007 (unit tests) ‖ T008 (integration tests)

# Frontend (after backend complete):
T014 (search bar) ‖ T015 (filter controls) — T016 depends on both
```

### Phase 4 (US2)
```
# Tests (write in parallel):
T019 (unit tests) ‖ T020 (integration tests)

# Backend (after tests written, sequential where noted):
T021 ‖ T022 ‖ T023  (independent service methods)
T025 — sequential after T009 (extends list_feedback base)

# Frontend (after backend complete):
T027 (HTTP wiring) ‖ T028 (LabelManagerComponent)
```

### Phase 5
```
T033 (pytest) ‖ T034 (ruff) ‖ T035 (responsive check)
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Phase 1: Setup (T001–T003)
2. Phase 2: Foundational (T004–T006)
3. Phase 3: US1 — Search & Filter (T007–T017)
4. **STOP and VALIDATE**: Keyword search debounces correctly; all filter facets work (incl. submitter autocomplete populated from API); filter state persists on navigation; empty-state shows when no results
5. Ship/demo MVP

### Incremental Delivery

| Milestone | Phases | Deliverable |
|-----------|--------|-------------|
| MVP | 1 + 2 + 3 | Debounced search + status/submitter/date filters |
| v1 | + 4 | Label creation, assignment, filter (OR), instant reflection |
| Release | + 5 | Hardened, responsive, E2E validated |

### Parallel Team Strategy

With two developers after Phase 2 completes:
- **Dev A**: Phase 3 backend (T007–T011) while **Dev B**: Phase 3 frontend (T012–T017)
- Phase 4 can be split the same way; note T025 must follow T009 (not parallel)

---

## Summary

| Phase | Tasks | Notes |
|-------|-------|-------|
| Phase 1 — Setup | T001–T003 | 3 tasks |
| Phase 2 — Foundational | T004–T006 | 3 tasks |
| Phase 3 — US1 Search/Filter | T007–T017 | 11 tasks (incl. 2 test files) |
| Phase 4 — US2 Labels | T019–T032 | 14 tasks (incl. 2 test files) |
| Phase 5 — Polish | T033–T036 | 4 tasks |
| **Total** | **T001–T036** | **36 tasks** |

- [P] parallelizable: 16 tasks
- Tests: 4 test-writing tasks (T007, T008, T019, T020)
- MVP scope: T001–T017 (17 tasks)
- T025 depends on T009 — must be sequential even if US2 starts after Phase 2
