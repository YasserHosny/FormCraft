# Tasks: Batch Operations & Print Queue

**Input**: Design documents from `/specs/036-batch-operations/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included per the FormCraft constitution (Test-First Development). Each story phase includes failing tests before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 [P] Create backend route stub `formcraft-backend/app/api/routes/batch_jobs.py`
- [X] T002 [P] Create backend schemas `formcraft-backend/app/schemas/batch.py`
- [X] T003 [P] Create frontend feature module `formcraft-frontend/src/app/features/desk/batch-queue/batch-queue.module.ts`
- [X] T004 [P] Create frontend service stub `formcraft-frontend/src/app/core/services/batch.service.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create database migration `formcraft-backend/migrations/036_batch_operations.sql` (batch_jobs, batch_data_sources, batch_schedules, batch_errors tables with RLS; plus ALTER TABLE form_submissions ADD COLUMN batch_job_id UUID REFERENCES batch_jobs(id) ON DELETE SET NULL, ADD COLUMN batch_generated BOOLEAN NOT NULL DEFAULT FALSE)
- [X] T006 [P] Implement batch job SQLAlchemy models in `formcraft-backend/app/models/batch.py`
- [X] T007 [P] Implement batch data source service in `formcraft-backend/app/services/batch_data_source_service.py` (CSV/XLSX parse, column extract, storage upload)
- [X] T008 [P] Implement batch validation service in `formcraft-backend/app/services/batch_validation_service.py` (row validation, duplicate detection, mapping re-validation)
- [X] T009 Implement batch generation service in `formcraft-backend/app/services/batch_generation_service.py` (async PDF generation loop, progress updates, cancellation support)
- [X] T010 [P] Implement batch schedule service in `formcraft-backend/app/services/batch_schedule_service.py` (APScheduler integration, cron compute, API pull)
- [X] T011 Implement batch orchestration service in `formcraft-backend/app/services/batch_service.py` (job lifecycle, status tracking, download preparation)
- [X] T012 Wire batch routes into `formcraft-backend/app/main.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Batch Form Generation from Data Source (Priority: P1) 🎯 MVP

**Goal**: Operators can select a template, upload CSV/Excel, map columns, validate rows, and generate batch PDFs with real-time progress.

**Independent Test**: Navigate to `/desk/queue`, create new batch job, upload CSV, map columns, validate, generate 100 PDFs, download as ZIP.

### Tests for User Story 1 (Test-First) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T013 [P] [US1] Contract test for `POST /api/batch-jobs` in `formcraft-backend/tests/integration/test_batch_jobs_routes.py`
- [X] T014 [P] [US1] Unit test for CSV parsing and column extraction in `formcraft-backend/tests/unit/test_batch_data_source_service.py`
- [X] T015 [P] [US1] Unit test for row validation and duplicate detection in `formcraft-backend/tests/unit/test_batch_validation.py`
- [X] T016 [P] [US1] Unit test for async PDF generation loop and progress updates in `formcraft-backend/tests/unit/test_batch_generation.py`
- [X] T017 [P] [US1] Unit test for batch orchestration (create, start, cancel) in `formcraft-backend/tests/unit/test_batch_service.py`

### Implementation for User Story 1

- [X] T018 [P] [US1] Implement `POST /api/batch-jobs` endpoint in `formcraft-backend/app/api/routes/batch_jobs.py` (create job, upload data source)
- [X] T019 [P] [US1] Implement `POST /api/batch-jobs/{id}/validate` endpoint in `formcraft-backend/app/api/routes/batch_jobs.py` (row validation with duplicate detection)
- [X] T020 [P] [US1] Implement column auto-mapping logic in `formcraft-backend/app/services/batch_data_source_service.py`
- [X] T021 [P] [US1] Implement `POST /api/batch-jobs/{id}/start` endpoint in `formcraft-backend/app/api/routes/batch_jobs.py` (trigger background generation with mapping re-validation)
- [X] T022 [P] [US1] Implement `GET /api/batch-jobs/{id}` endpoint in `formcraft-backend/app/api/routes/batch_jobs.py` (poll status and progress)
- [X] T023 [P] [US1] Implement `GET /api/batch-jobs/{id}/download` endpoint in `formcraft-backend/app/api/routes/batch_jobs.py` (ZIP and merged PDF streaming)
- [X] T024 [P] [US1] Create batch queue list component `formcraft-frontend/src/app/features/desk/batch-queue/batch-list/batch-list.component.ts` + .html + .scss
- [X] T025 [P] [US1] Create batch create wizard component `formcraft-frontend/src/app/features/desk/batch-queue/batch-create-wizard/batch-create-wizard.component.ts` + .html + .scss
- [X] T026 [P] [US1] Create step-template component `formcraft-frontend/src/app/features/desk/batch-queue/batch-create-wizard/step-template/step-template.component.ts`
- [X] T027 [P] [US1] Create step-data-source component `formcraft-frontend/src/app/features/desk/batch-queue/batch-create-wizard/step-data-source/step-data-source.component.ts`
- [X] T028 [P] [US1] Create step-column-mapper component `formcraft-frontend/src/app/features/desk/batch-queue/batch-create-wizard/step-column-mapper/column-mapper.component.ts`
- [X] T029 [P] [US1] Create step-validation component `formcraft-frontend/src/app/features/desk/batch-queue/batch-create-wizard/step-validation/step-validation.component.ts`
- [X] T030 [P] [US1] Create step-generate component `formcraft-frontend/src/app/features/desk/batch-queue/batch-create-wizard/step-generate/step-generate.component.ts`
- [X] T031 [US1] Wire batch queue routing in `formcraft-frontend/src/app/features/desk/desk.module.ts`
- [ ] T032 [P] [US1] Add translation keys for batch wizard and validation UI in `formcraft-frontend/src/assets/i18n/en.json` and `ar.json`
- [X] T033 [P] [US1] Implement frontend batch service methods in `formcraft-frontend/src/app/core/services/batch.service.ts` (create, validate, start, poll, download)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Queue Dashboard & Job Management (Priority: P2)

**Goal**: Operators can view active/completed/failed jobs, track progress, download results, and review error reports.

**Independent Test**: Navigate to `/desk/queue`, see active job with progress bar, completed jobs with download links, failed job with error report.

### Tests for User Story 2 (Test-First) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T034 [P] [US2] Contract test for `GET /api/batch-jobs` (list with filters) in `formcraft-backend/tests/integration/test_batch_jobs_routes.py`
- [X] T035 [P] [US2] Unit test for error report CSV generation in `formcraft-backend/tests/unit/test_batch_service.py`
- [X] T036 [P] [US2] Unit test for job cancellation and partial results in `formcraft-backend/tests/unit/test_batch_generation.py`

### Implementation for User Story 2

- [X] T037 [P] [US2] Implement `GET /api/batch-jobs` endpoint in `formcraft-backend/app/api/routes/batch_jobs.py` (list with status filter, pagination)
- [X] T038 [P] [US2] Implement `POST /api/batch-jobs/{id}/cancel` endpoint in `formcraft-backend/app/api/routes/batch_jobs.py` (cancel running job, preserve partial results)
- [X] T039 [P] [US2] Implement `GET /api/batch-jobs/{id}/errors` endpoint in `formcraft-backend/app/api/routes/batch_jobs.py` (download error report CSV)
- [X] T040 [P] [US2] Enhance batch list component with progress bars, status filters, and cancel button in `formcraft-frontend/src/app/features/desk/batch-queue/batch-list/batch-list.component.ts`
- [X] T041 [P] [US2] Create batch detail component `formcraft-frontend/src/app/features/desk/batch-queue/batch-detail/batch-detail.component.ts` + .html + .scss (job stats, download links, error summary)
- [X] T042 [P] [US2] Create batch error report component `formcraft-frontend/src/app/features/desk/batch-queue/batch-error-report/batch-error-report.component.ts` + .html + .scss
- [X] T043 [P] [US2] Add download options (ZIP, merged PDF, printer queue) to batch detail UI
- [ ] T044 [P] [US2] Add translation keys for dashboard, progress, and error reporting in `formcraft-frontend/src/assets/i18n/en.json` and `ar.json`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Scheduled Recurring Batches (Priority: P3)

**Goal**: Admins can configure recurring batch jobs with API data sources, cron schedules, and email notifications.

**Independent Test**: Configure a weekly batch job with API data source and email notification, verify it auto-runs and notifies.

### Tests for User Story 3 (Test-First) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T045 [P] [US3] Contract test for batch schedule CRUD endpoints in `formcraft-backend/tests/integration/test_batch_jobs_routes.py`
- [X] T046 [P] [US3] Unit test for cron expression parsing and next-run computation in `formcraft-backend/tests/unit/test_batch_schedule.py`
- [X] T047 [P] [US3] Unit test for API data source pull and retry logic in `formcraft-backend/tests/unit/test_batch_schedule.py`
- [X] T048 [P] [US3] Unit test for schedule-triggered batch job creation in `formcraft-backend/tests/unit/test_batch_schedule.py`

### Implementation for User Story 3

- [X] T049 [P] [US3] Implement `GET /api/batch-schedules` endpoint in `formcraft-backend/app/api/routes/batch_jobs.py`
- [X] T050 [P] [US3] Implement `POST /api/batch-schedules` endpoint in `formcraft-backend/app/api/routes/batch_jobs.py` (create schedule with encrypted credentials)
- [X] T051 [P] [US3] Implement `PUT /api/batch-schedules/{id}` endpoint in `formcraft-backend/app/api/routes/batch_jobs.py`
- [X] T052 [P] [US3] Implement `DELETE /api/batch-schedules/{id}` endpoint in `formcraft-backend/app/api/routes/batch_jobs.py`
- [X] T053 [P] [US3] Implement APScheduler cron trigger registration in `formcraft-backend/app/services/batch_schedule_service.py`
- [X] T054 [P] [US3] Implement API data source HTTP client with retry logic in `formcraft-backend/app/services/batch_schedule_service.py`
- [X] T055 [P] [US3] Implement schedule execution orchestrator (pull API data, create batch job, notify) in `formcraft-backend/app/services/batch_schedule_service.py`
- [X] T056 [P] [US3] Create batch schedule admin component `formcraft-frontend/src/app/features/admin/batch-schedules/batch-schedule-admin.component.ts` + .html + .scss
- [ ] T057 [P] [US3] Create batch schedule form component `formcraft-frontend/src/app/features/admin/batch-schedules/batch-schedule-form/batch-schedule-form.component.ts`
- [X] T058 [P] [US3] Wire admin batch schedule routes in `formcraft-frontend/src/app/features/admin/admin.module.ts`
- [ ] T059 [P] [US3] Add translation keys for scheduled batch UI and notifications in `formcraft-frontend/src/assets/i18n/en.json` and `ar.json`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T060 [P] Add audit logging for batch job lifecycle events (create, start, cancel, complete, fail) in `formcraft-backend/app/core/audit.py` or batch service
- [ ] T061 [P] Add org-level `max_batch_size` enforcement in `formcraft-backend/app/services/batch_service.py`
- [ ] T062 [P] Add file upload security (MIME validation, extension whitelist, optional ClamAV scan) in `formcraft-backend/app/services/batch_data_source_service.py`
- [ ] T063 [P] Add nightly cleanup job for expired data sources (30-day retention) in `formcraft-backend/app/services/batch_schedule_service.py`
- [ ] T064 [P] Add email notification templates and delivery for batch completion/failure in `formcraft-backend/app/services/batch_service.py`
- [ ] T065 [P] Add printer queue integration for `download_format = printer_queue` in `formcraft-backend/app/services/batch_generation_service.py`
- [ ] T066 [P] Add RTL styling and responsive layout for batch queue wizard and dashboard in `formcraft-frontend/src/app/features/desk/batch-queue/`
- [ ] T067 [P] Run backend tests `pytest formcraft-backend/tests/unit/test_batch_*.py formcraft-backend/tests/integration/test_batch_jobs_routes.py`
- [ ] T068 [P] Run frontend build `ng build` to verify no compilation errors
- [ ] T069 [P] Update `formcraft-specs/specs/036-batch-operations/quickstart.md` with any final path or command changes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 queue/dashboard but is independently testable; dashboard UI can be built before generation logic is complete
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on US1 batch job creation logic; schedule execution creates batch jobs via the US1 path

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks (T001–T004) can run in parallel
- All Foundational tasks (T005–T012) can run in parallel except T009 and T011 which depend on T007/T008
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story can be written in parallel
- Frontend components within a story can be built in parallel with backend endpoints
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for POST /api/batch-jobs in tests/integration/test_batch_jobs_routes.py"
Task: "Unit test for CSV parsing in tests/unit/test_batch_data_source_service.py"
Task: "Unit test for row validation in tests/unit/test_batch_validation.py"
Task: "Unit test for async PDF generation in tests/unit/test_batch_generation.py"
Task: "Unit test for batch orchestration in tests/unit/test_batch_service.py"

# Launch all models for User Story 1 together:
Task: "Create batch job SQLAlchemy models in app/models/batch.py"
Task: "Create batch route stub in app/api/routes/batch_jobs.py"

# Launch frontend wizard steps in parallel:
Task: "Create step-template component"
Task: "Create step-data-source component"
Task: "Create step-column-mapper component"
Task: "Create step-validation component"
Task: "Create step-generate component"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
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
