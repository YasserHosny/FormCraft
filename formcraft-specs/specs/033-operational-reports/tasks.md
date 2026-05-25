# Tasks: Operational Report Engine

**Input**: Design documents from `/specs/033-operational-reports/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks included as TDD approach is specified in plan.md constitution check.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 [P] Add `field_type_tag` enum column to `elements` table (nullable) per data-model.md
- [X] T002 [P] Create database migration for `report_templates`, `report_schedules`, `report_archives` tables with indexes and RLS policies
- [X] T003 [P] Seed pre-built report templates (system = true) for each organization
- [X] T004 Install backend dependencies: openpyxl, WeasyPrint, APScheduler, matplotlib in formcraft-backend/requirements.txt
- [X] T005 Create backend module structure: `formcraft-backend/app/services/reports/__init__.py` and submodules
- [X] T006 Create frontend module structure: `formcraft-frontend/src/app/features/admin/reports/` with routing and shared components

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Create Pydantic/SQLAlchemy models in `formcraft-backend/app/models/report.py` for report_templates, report_schedules, report_archives
- [X] T008 Create Pydantic schemas in `formcraft-backend/app/schemas/report.py` for request/response validation
- [X] T009 Implement tiered access control in `formcraft-backend/app/core/report_permissions.py` (admin=all, branch_manager=register+reconciliation branch-scoped, operator=own history only)
- [X] T010 Implement report export service in `formcraft-backend/app/services/reports/report_exporter.py` supporting Excel/CSV/PDF with RTL and Arabic text
- [X] T011 Implement async export job tracking in `formcraft-backend/app/services/reports/report_exporter.py` with polling endpoint support
- [X] T012 [P] Implement report archive storage integration with Supabase Storage in `formcraft-backend/app/services/reports/report_exporter.py`
- [X] T013 [P] Create frontend shared components: `report-filter-panel`, `report-export-button`, `period-comparison-indicator`
- [X] T014 [P] Create frontend reports service `formcraft-frontend/src/app/features/admin/services/reports.service.ts` with HTTP client methods

**Checkpoint**: Foundation ready - models, permissions, export infrastructure, and shared frontend components are in place

---

## Phase 3: User Story 1 - Transaction Register (Priority: P1) 🎯 MVP

**Goal**: Paginated transaction register with filters and export to Excel/CSV/PDF. Branch-scoped for branch managers.

**Independent Test**: Navigate to `/admin/reports/transactions`, apply date range filter, see paginated results, export to Excel.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T015 [P] [US1] Contract test for `GET /api/reports/transactions` in `formcraft-backend/tests/contract/test_reports_api.py`
- [ ] T016 [P] [US1] Contract test for `POST /api/reports/transactions/export` in `formcraft-backend/tests/contract/test_reports_api.py`
- [ ] T017 [P] [US1] Unit test for transaction register query builder in `formcraft-backend/tests/unit/test_transaction_register.py`

### Implementation for User Story 1

- [X] T018 [US1] Implement transaction register query builder in `formcraft-backend/app/services/reports/transaction_register.py`
- [X] T019 [US1] Implement `GET /api/reports/transactions` endpoint in `formcraft-backend/app/api/routes/reports.py` with pagination and RLS
- [X] T020 [US1] Implement `POST /api/reports/transactions/export` endpoint in `formcraft-backend/app/api/routes/reports.py` with sync (<10K) and async (>=10K) generation
- [X] T021 [US1] Implement transaction register frontend component in `formcraft-frontend/src/app/features/admin/reports/transaction-register/`
- [X] T022 [US1] Add frontend export button integration for transaction register Excel/CSV/PDF download

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Transaction register loads, filters, paginates, and exports correctly.

---

## Phase 4: User Story 2 - Daily Reconciliation (Priority: P2)

**Goal**: Per-operator, per-branch daily summary with totals. Includes zero-submission operators. Supports scheduling.

**Independent Test**: Navigate to daily reconciliation, select date and branch, see operator-level summary with totals.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T023 [P] [US2] Contract test for `GET /api/reports/reconciliation` in `formcraft-backend/tests/contract/test_reports_api.py`
- [ ] T024 [P] [US2] Unit test for daily reconciliation aggregation in `formcraft-backend/tests/unit/test_reconciliation.py`
- [ ] T025 [P] [US2] Integration test for scheduled reconciliation generation in `formcraft-backend/tests/integration/test_report_scheduling.py`

### Implementation for User Story 2

- [X] T026 [US2] Implement daily reconciliation aggregation in `formcraft-backend/app/services/reports/reconciliation.py`
- [X] T027 [US2] Implement `GET /api/reports/reconciliation` endpoint in `formcraft-backend/app/api/routes/reports.py`
- [X] T028 [US2] Implement daily reconciliation frontend component in `formcraft-frontend/src/app/features/admin/reports/daily-reconciliation/`
- [X] T029 [US2] Implement report scheduler service in `formcraft-backend/app/services/reports/report_scheduler.py` using APScheduler with PostgreSQL job store
- [X] T030 [US2] Implement `POST /api/reports/schedules` and related CRUD endpoints in `formcraft-backend/app/api/routes/report_schedules.py`
- [X] T031 [US2] Implement email delivery for scheduled reports via Resend in `formcraft-backend/app/services/email/report_delivery.py`
- [X] T032 [US2] Add schedule configuration dialog in `formcraft-frontend/src/app/features/admin/reports/report-schedules/`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Daily reconciliation generates, schedules, and emails correctly.

---

## Phase 5: User Story 3 - Period Summary (Priority: P3)

**Goal**: Aggregate totals for configurable periods (week/month/quarter/year) grouped by department/branch/template/operator with period-over-period comparison.

**Independent Test**: Generate monthly summary grouped by department, see this month vs. last month with trend arrows.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T033 [P] [US3] Contract test for `GET /api/reports/period-summary` in `formcraft-backend/tests/contract/test_reports_api.py`
- [ ] T034 [P] [US3] Unit test for period comparison logic in `formcraft-backend/tests/unit/test_period_summary.py`

### Implementation for User Story 3

- [X] T035 [US3] Implement period summary aggregation and comparison logic in `formcraft-backend/app/services/reports/period_summary.py`
- [X] T036 [US3] Implement `GET /api/reports/period-summary` endpoint in `formcraft-backend/app/api/routes/reports.py`
- [X] T037 [US3] Implement period summary frontend component with chart preview in `formcraft-frontend/src/app/features/admin/reports/period-summary/`
- [X] T038 [US3] Add chart rendering support (ng2-charts/Chart.js) for period comparison in frontend
- [X] T039 [US3] Add PDF export with embedded charts via WeasyPrint + matplotlib SVG in `formcraft-backend/app/services/reports/report_exporter.py`

**Checkpoint**: Period summary reports render correctly with comparison indicators and export to PDF with charts.

---

## Phase 6: User Story 4 - Custom Report Builder (Priority: P4)

**Goal**: Build custom reports by selecting dimensions, filters, aggregations, and chart types across multiple templates. Save and schedule.

**Independent Test**: Build a custom report selecting template fields + submission metadata, preview results, save and schedule.

### Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T040 [P] [US4] Contract test for `POST /api/reports/custom/preview` in `formcraft-backend/tests/contract/test_reports_api.py`
- [ ] T041 [P] [US4] Contract test for `POST /api/reports/custom/save` in `formcraft-backend/tests/contract/test_reports_api.py`
- [ ] T042 [P] [US4] Unit test for custom report query engine in `formcraft-backend/tests/unit/test_custom_builder.py`

### Implementation for User Story 4

- [X] T043 [US4] Implement custom report query engine with cross-template field alignment in `formcraft-backend/app/services/reports/custom_builder.py`
- [X] T044 [US4] Implement `POST /api/reports/custom/preview` endpoint in `formcraft-backend/app/api/routes/report_builder.py`
- [X] T045 [US4] Implement `POST /api/reports/custom/save` endpoint in `formcraft-backend/app/api/routes/report_builder.py`
- [X] T046 [US4] Implement custom report builder frontend component in `formcraft-frontend/src/app/features/admin/reports/report-builder/`
- [X] T047 [US4] Add live preview with chart rendering in custom report builder frontend
- [X] T048 [US4] Integrate saved custom reports with scheduler (`report_schedules` supports custom report templates)

**Checkpoint**: Custom reports can be built, previewed, saved, and scheduled with cross-template aggregation.

---

## Phase 7: User Story 5 - Specialized Financial Reports (Priority: P5)

**Goal**: Pre-built beneficiary, void & reprint, and signatory usage reports for financial audit.

**Independent Test**: Generate beneficiary report for a date range, see all transactions grouped by beneficiary with totals.

### Tests for User Story 5

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T049 [P] [US5] Contract tests for financial report endpoints in `formcraft-backend/tests/contract/test_reports_api.py`

### Implementation for User Story 5

- [X] T050 [US5] Implement financial reports aggregation in `formcraft-backend/app/services/reports/financial_reports.py`
- [X] T051 [US5] Implement `GET /api/reports/financial/beneficiary` endpoint in `formcraft-backend/app/api/routes/reports.py`
- [X] T052 [US5] Implement `GET /api/reports/financial/void-reprint` endpoint in `formcraft-backend/app/api/routes/reports.py`
- [X] T053 [US5] Implement `GET /api/reports/financial/signatory-usage` endpoint in `formcraft-backend/app/api/routes/reports.py`
- [X] T054 [US5] Implement beneficiary report frontend component in `formcraft-frontend/src/app/features/admin/reports/financial-reports/beneficiary-report.component.ts`
- [X] T055 [US5] Implement void & reprint register frontend component in `formcraft-frontend/src/app/features/admin/reports/financial-reports/void-reprint-register.component.ts`
- [X] T056 [US5] Implement signatory usage frontend component in `formcraft-frontend/src/app/features/admin/reports/financial-reports/signatory-usage.component.ts`

**Checkpoint**: All financial reports are accessible, filterable, and exportable from the frontend.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T057 [P] Implement archive cleanup job for expired reports (>12 months) via scheduled task
- [X] T058 [P] Implement `GET /api/reports/jobs/{job_id}` polling endpoint for async export status
- [X] T059 [P] Implement `GET /api/reports/archives` endpoint for report history listing
- [ ] T060 [P] Add frontend archive/history view in `formcraft-frontend/src/app/features/admin/reports/report-schedules/`
- [ ] T061 Add audit logging for all report generation and export actions
- [X] T062 Performance optimization: add `submissions(organization_id, created_at)` index if not exists
- [ ] T063 Add i18n translation keys for all report labels, column headers, and UI text (Arabic + English)
- [ ] T064 Security hardening: validate all report endpoints respect RLS boundaries (no cross-org/branch leakage)
- [ ] T065 Run quickstart.md validation scenarios end-to-end
- [ ] T066 Final code review, linting (ruff check), and cleanup

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 export infrastructure but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Builds on shared aggregation/export services
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Builds on shared query builder and export services
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Uses shared financial aggregation patterns

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before frontend integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks (T001-T006) can run in parallel
- All Foundational tasks marked [P] (T012-T014) can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models/services within a story can run in parallel where marked [P]
- Frontend and backend tasks for the same story can often run in parallel (with contract alignment)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for GET /api/reports/transactions in tests/contract/test_reports_api.py"
Task: "Contract test for POST /api/reports/transactions/export in tests/contract/test_reports_api.py"
Task: "Unit test for transaction register query builder in tests/unit/test_transaction_register.py"

# Launch backend + frontend implementation together:
Task: "Implement transaction register query builder in app/services/reports/transaction_register.py"
Task: "Implement transaction register frontend component in frontend/src/app/features/admin/reports/transaction-register/"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently via quickstart.md Scenario 1
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4 + 5 (smaller scope)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Financial aggregation strictly uses `field_type_tag = 'amount'` per data-model.md Decision 8
- Export limits: sync for <10K records, async job for >=10K, 400 error for >100K
- All RLS policies use `organization_id = auth.org_id()`
- Report archives auto-expire after 12 months
