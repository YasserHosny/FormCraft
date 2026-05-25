# Tasks: Desk Search & Quick Fill

**Feature**: F037 - Desk Search & Quick Fill  
**Branch**: `037-desk-search-quickfill-implementation`  
**Date**: 2026-05-26

## Dependencies & Order

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1: Global Search) → Phase 4 (US2: Quick Fill) → Phase 5 (Polish)
```

User Story 1 (Global Search) and User Story 2 (Quick Fill) share the foundational database layer but are otherwise independently testable once Phase 2 is complete.

---

## Phase 1: Setup

- [ ] T001 [P] Create feature branch `037-desk-search-quickfill-implementation` from main
- [ ] T002 Create backend directory structure: `formcraft-backend/app/services/search_service.py`, `formcraft-backend/app/services/quickfill_service.py`, `formcraft-backend/app/api/routes/search.py`, `formcraft-backend/app/api/routes/quickfill.py`
- [ ] T003 Create frontend directory structure: `formcraft-frontend/src/app/shared/components/global-search/`, `formcraft-frontend/src/app/shared/components/quickfill-dialog/`, `formcraft-frontend/src/app/core/services/search.service.ts`, `formcraft-frontend/src/app/core/services/quickfill.service.ts`
- [ ] T004 Create migration file `formcraft-backend/migrations/037_desk_search_quickfill.sql`
- [ ] T005 Create backend test files: `formcraft-backend/tests/unit/test_search_service.py`, `formcraft-backend/tests/unit/test_quickfill_service.py`

---

## Phase 2: Foundational — Database & Shared Services

**Goal**: Establish the database schema, indexes, and shared services required by both user stories.

**Independent Test Criteria**: Database migrations apply cleanly; pg_trgm and unaccent extensions are active; materialized view refreshes successfully.

- [ ] T006 Enable PostgreSQL extensions `pg_trgm` and `unaccent` in migration `037_desk_search_quickfill.sql`
- [ ] T007 Create `quickfill_mappings` table with default seed data in `037_desk_search_quickfill.sql`
- [ ] T008 Create `mv_global_search` materialized view with `tsvector`, `name_trigram`, and RLS columns in `037_desk_search_quickfill.sql`
- [ ] T009 Create GIN and trigram indexes on `mv_global_search` in `037_desk_search_quickfill.sql`
- [ ] T010 Add `customer_id` nullable FK to `form_submissions` in `037_desk_search_quickfill.sql`
- [ ] T011 Write failing unit tests for `search_service.py` (exact match, fuzzy match, mixed-script) BEFORE implementation in `tests/unit/test_search_service.py`
- [ ] T012 Implement `search_service.py` with `search_global()` using PostgreSQL full-text search and trigram matching in `formcraft-backend/app/services/search_service.py`
- [ ] T013 Write failing unit tests for `quickfill_service.py` (mapping logic, default keys, edge cases) BEFORE implementation in `tests/unit/test_quickfill_service.py`
- [ ] T014 Implement `quickfill_service.py` with `map_customer_to_fields()`, `get_quickfill_mappings()`, and `update_quickfill_mappings()` in `formcraft-backend/app/services/quickfill_service.py`
- [ ] T015 Run migration against development database and verify all objects created
- [ ] T016 [P] Implement materialized view refresh strategy (pg_cron or trigger-based) in `037_desk_search_quickfill.sql`

---

## Phase 3: User Story 1 — Global Search Bar

**Story Goal**: Operator can use a global search bar on the Form Desk to find templates, submissions, and customers instantly.

**Independent Test Criteria**: Type a template name → see results in < 300ms; type a reference number → navigate to submission; type a customer name → see recent activity count; mixed-type results are grouped.

- [ ] T017 [US1] Implement exact reference number query with RLS filtering in `formcraft-backend/app/services/search_service.py`
- [ ] T018 [US1] Implement FastAPI router `search.py` with `GET /search` endpoint in `formcraft-backend/app/api/routes/search.py`
- [ ] T019 [US1] Implement FastAPI router `search.py` with `GET /search/reference` endpoint in `formcraft-backend/app/api/routes/search.py`
- [ ] T020 [US1] Add rate limiting middleware for search endpoints (50 req/min) in `formcraft-backend/app/middleware/rate_limit.py`
- [ ] T021 [US1] [P] Create Angular `SearchService` with debounced `search()` and `searchByReference()` methods in `formcraft-frontend/src/app/core/services/search.service.ts`
- [ ] T022 [US1] Add i18n translation keys for Global Search UI strings in `formcraft-frontend/src/assets/i18n/en.json` and `ar.json`
- [ ] T023 [US1] Create `GlobalSearchBarComponent` with debounced input (200ms), grouped results dropdown, keyboard navigation, and ARIA labels in `formcraft-frontend/src/app/shared/components/global-search/global-search-bar.component.ts`
- [ ] T024 [US1] Create `GlobalSearchBarComponent` HTML template with section headers (Templates, Submissions, Customers) using translation keys in `formcraft-frontend/src/app/shared/components/global-search/global-search-bar.component.html`
- [ ] T025 [US1] Create `GlobalSearchBarComponent` styles for dropdown, keyboard highlight, and responsive RTL/LTR layout in `formcraft-frontend/src/app/shared/components/global-search/global-search-bar.component.scss`
- [ ] T026 [US1] Wire `GlobalSearchBarComponent` into Form Desk shell/layout (top navigation bar)
- [ ] T027 [US1] [P] Write frontend unit tests for `GlobalSearchBarComponent` debounce, keyboard nav, and grouping in `formcraft-frontend/src/app/shared/components/global-search/global-search-bar.component.spec.ts`
- [ ] T028 [US1] [P] Write integration test: search by reference number navigates to submission detail page

---

## Phase 4: User Story 2 — Quick Fill Mode

**Story Goal**: Operator selects a template and customer to auto-populate form fields, reducing repeat-customer form completion time by 50%+.

**Independent Test Criteria**: Select template → click Quick Fill → search customer → form loads with matching fields pre-filled (light blue background) → print → submission linked to customer.

- [ ] T029 [US2] Implement FastAPI router `quickfill.py` with `GET /quickfill/customers` fuzzy search endpoint in `formcraft-backend/app/api/routes/quickfill.py`
- [ ] T030 [US2] Implement FastAPI router `quickfill.py` with `POST /quickfill/map` field mapping endpoint in `formcraft-backend/app/api/routes/quickfill.py`
- [ ] T031 [US2] [P] Create Angular `QuickFillService` with `autoFill()`, `markAutoFilled()`, and `saveToProfile()` methods in `formcraft-frontend/src/app/core/services/quickfill.service.ts`
- [ ] T032 [US2] Add i18n translation keys for Quick Fill dialog and related UI strings in `formcraft-frontend/src/assets/i18n/en.json` and `ar.json`
- [ ] T033 [US2] Create `QuickFillDialogComponent` with customer search bar, result list, customer card display, and ARIA attributes in `formcraft-frontend/src/app/shared/components/quickfill-dialog/quickfill-dialog.component.ts`
- [ ] T034 [US2] Create `QuickFillDialogComponent` HTML template with search input, customer cards, and select action using translation keys in `formcraft-frontend/src/app/shared/components/quickfill-dialog/quickfill-dialog.component.html`
- [ ] T035 [US2] Create `QuickFillDialogComponent` styles for dialog, search results, and selection highlight in `formcraft-frontend/src/app/shared/components/quickfill-dialog/quickfill-dialog.component.scss`
- [ ] T036 [US2] Integrate Quick Fill button into template selection flow (desk dashboard / template list)
- [ ] T037 [US2] Modify `FormFillerComponent` to accept pre-populated field values from Quick Fill and apply `auto-filled` CSS class
- [ ] T038 [US2] Add "Save to Profile" action in submission success flow when customer is linked
- [ ] T039 [US2] [P] Write frontend unit tests for `QuickFillDialogComponent` search, selection, and dialog flow in `formcraft-frontend/src/app/shared/components/quickfill-dialog/quickfill-dialog.component.spec.ts`
- [ ] T040 [US2] [P] Write frontend unit tests for `QuickFillService` mapping, marking, and profile save in `formcraft-frontend/src/app/core/services/quickfill.service.spec.ts`
- [ ] T041 [US2] [P] Write integration test: Quick Fill → print → verify submission linked to customer and customer profile optionally updated

---

## Phase 5: Polish & Cross-Cutting Concerns

**Goal**: Performance validation, RLS compliance, and operator-facing polish.

- [ ] T042 [P] Benchmark global search latency: 95th percentile < 300ms against test dataset (1k templates, 100k submissions, 50k customers)
- [ ] T043 [P] Verify RLS compliance: operator A cannot see operator B's branch submissions in search results
- [ ] T044 [P] Verify mixed-script Arabic/English search returns correct results with diacritics removed
- [ ] T045 [P] Add `localStorage` recent searches cache (last 10 queries) to `SearchService`
- [ ] T046 [P] Add loading and empty states to `GlobalSearchBarComponent` and `QuickFillDialogComponent`
- [ ] T047 [P] Run backend linter (`ruff check .`) and fix any issues
- [ ] T048 [P] Run frontend linter (`ng lint`) and fix any issues
- [ ] T049 [P] Update `AGENTS.md` with F037 active technology stack (if not already present)
- [ ] T050 Final regression test: existing Form Desk workflows (template selection, form filling, submission history) remain unaffected

---

## Parallel Execution Examples

**Within Phase 2 (Foundational)**:
- T006–T010 (migration SQL) can be written in parallel with T011–T013 (service implementation) since file paths don't overlap.
- T015 and T016 (unit tests) can run in parallel once T011–T012 are stable.

**Within Phase 3 (US1)**:
- T017–T018 (backend endpoints) and T020–T023 (frontend components) are parallel.
- T025 and T026 (tests) run in parallel after components are complete.

**Within Phase 4 (US2)**:
- T027–T028 (backend endpoints) and T029–T032 (frontend components) are parallel.
- T036–T038 (tests) run in parallel after components are complete.

**Across Phases**:
- Phase 3 (US1) and Phase 4 (US2) can be developed in parallel once Phase 2 (Foundational) is complete, assuming separate developers/agents work on each story.

## Implementation Strategy

1. **MVP Scope**: Deliver User Story 1 (Global Search) first. It provides immediate value and validates the search infrastructure.
2. **Incremental Delivery**: Foundational layer (Phase 2) → US1 (Phase 3) → US2 (Phase 4) → Polish (Phase 5).
3. **Branch Safety**: All changes stay on `037-desk-search-quickfill-implementation`. No modifications to files actively being worked on by the F038 agent (Codex).
4. **Testing**: Unit tests written alongside implementation; integration tests after story completion.
