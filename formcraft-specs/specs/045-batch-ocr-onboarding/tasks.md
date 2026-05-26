# Tasks: Batch OCR Onboarding

**Input**: Design documents from `formcraft-specs/specs/045-batch-ocr-onboarding/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Phase 1: Setup

**Purpose**: Add F045 storage, schemas, service shells, and route wiring.

- [X] T001 Create migration `formcraft-backend/migrations/042_batch_ocr_onboarding.sql` for OCR onboarding batches, items, review decisions, duplicate candidates, indexes, RLS enablement, and grants
- [X] T002 [P] Create Pydantic request/response schemas in `formcraft-backend/app/schemas/ocr_onboarding.py`
- [X] T003 [P] Create service skeleton and conversion helpers in `formcraft-backend/app/services/ocr_onboarding_service.py`
- [X] T004 Create FastAPI router skeleton in `formcraft-backend/app/api/routes/ocr_onboarding.py`
- [X] T005 Register OCR onboarding router in `formcraft-backend/app/main.py`
- [X] T006 [P] Create Angular API service in `formcraft-frontend/src/app/core/services/ocr-onboarding.service.ts`
- [X] T007 Add admin route entry for OCR onboarding in `formcraft-frontend/src/app/features/admin/admin.module.ts`

## Phase 2: Foundational Tests

**Purpose**: Lock lifecycle and contract behavior before implementation.

- [X] T008 [P] Add unit tests for batch file validation, 200-item cap, and item creation in `formcraft-backend/tests/unit/test_ocr_onboarding_service.py`
- [X] T009 [P] Add unit tests for bulk accept eligibility and below-threshold skipping in `formcraft-backend/tests/unit/test_ocr_onboarding_service.py`
- [X] T010 [P] Add unit tests for item retry state transitions in `formcraft-backend/tests/unit/test_ocr_onboarding_service.py`
- [X] T011 Add integration-style route tests for create/list/detail/bulk-accept/retry endpoints in `formcraft-backend/tests/integration/test_ocr_onboarding_routes.py`

## Phase 3: User Story 1 - Upload a Legacy Form Library (Priority: P1)

**Goal**: Admin creates a batch of scanned forms and sees item states/progress.

**Independent Test**: Upload mixed valid/invalid files and confirm valid items are queued while invalid files are reported without blocking the batch.

- [X] T012 [US1] Implement `create_batch()` in `formcraft-backend/app/services/ocr_onboarding_service.py`
- [X] T013 [US1] Implement list/detail serialization in `formcraft-backend/app/services/ocr_onboarding_service.py`
- [X] T014 [US1] Implement `POST /api/ocr-onboarding/batches`, `GET /batches`, and `GET /batches/{batch_id}` in `formcraft-backend/app/api/routes/ocr_onboarding.py`
- [X] T015 [P] [US1] Create Angular onboarding module/routing files in `formcraft-frontend/src/app/features/admin/ocr-onboarding/`
- [X] T016 [P] [US1] Create batch list component in `formcraft-frontend/src/app/features/admin/ocr-onboarding/ocr-batch-list.component.ts`
- [X] T017 [P] [US1] Create batch create component in `formcraft-frontend/src/app/features/admin/ocr-onboarding/ocr-batch-create.component.ts`
- [X] T018 [US1] Add Arabic/English translation keys for batch create/list states in `formcraft-frontend/src/assets/i18n/ar.json` and `formcraft-frontend/src/assets/i18n/en.json`

## Phase 4: User Story 2 - Review and Bulk Accept Results (Priority: P2)

**Goal**: Reviewer triages confidence-ranked items and explicitly bulk-accepts eligible items.

**Independent Test**: Seed items with varied confidence and confirm only selected threshold-eligible items are accepted/converted.

- [X] T019 [US2] Implement `record_decision()` and `bulk_accept()` in `formcraft-backend/app/services/ocr_onboarding_service.py`
- [X] T020 [US2] Implement decision and bulk-accept endpoints in `formcraft-backend/app/api/routes/ocr_onboarding.py`
- [X] T021 [P] [US2] Create batch detail/review component in `formcraft-frontend/src/app/features/admin/ocr-onboarding/ocr-batch-detail.component.ts`
- [X] T022 [US2] Wire frontend bulk accept and item decision actions in `formcraft-frontend/src/app/features/admin/ocr-onboarding/ocr-batch-detail.component.ts`
- [X] T023 [US2] Add Arabic/English translation keys for review, confidence, and bulk actions in `formcraft-frontend/src/assets/i18n/ar.json` and `formcraft-frontend/src/assets/i18n/en.json`

## Phase 5: User Story 3 - Resolve Duplicates and Failed Items (Priority: P3)

**Goal**: Admin retries failures and resolves duplicate candidates without losing history.

**Independent Test**: Mark failed/duplicate samples, retry one failed item, resolve a duplicate, and confirm review history remains.

- [X] T024 [US3] Implement `retry_item()` and duplicate resolution service methods in `formcraft-backend/app/services/ocr_onboarding_service.py`
- [X] T025 [US3] Implement retry and duplicate resolution endpoints in `formcraft-backend/app/api/routes/ocr_onboarding.py`
- [X] T026 [US3] Add retry and duplicate actions to `formcraft-frontend/src/app/features/admin/ocr-onboarding/ocr-batch-detail.component.ts`
- [X] T027 [US3] Add Arabic/English translation keys for retry, duplicate evidence, and failure summaries in `formcraft-frontend/src/assets/i18n/ar.json` and `formcraft-frontend/src/assets/i18n/en.json`

## Phase 6: Polish & Validation

- [X] T028 [P] Add audit logging calls for batch create, decision, bulk accept, retry, and duplicate resolution in `formcraft-backend/app/services/ocr_onboarding_service.py`
- [X] T029 [P] Validate RLS/migration naming and update `formcraft-specs/specs/045-batch-ocr-onboarding/quickstart.md` if endpoint behavior changes
- [X] T030 Run backend tests for F045 with `cd formcraft-backend && pytest tests/unit/test_ocr_onboarding_service.py tests/integration/test_ocr_onboarding_routes.py`
- [X] T031 Run lint for touched backend code with `cd formcraft-backend && ruff check app/schemas/ocr_onboarding.py app/services/ocr_onboarding_service.py app/api/routes/ocr_onboarding.py tests/unit/test_ocr_onboarding_service.py tests/integration/test_ocr_onboarding_routes.py`
- [X] T032 Run frontend build or targeted TypeScript validation for touched Angular files

## Dependencies

- Phase 1 before Phase 2.
- Phase 2 tests before feature implementation.
- US1 before US2 and US3 UI work.
- US2 and US3 can proceed in parallel after US1 backend endpoints exist.

## Parallel Opportunities

- T002, T003, and T006 can run in parallel after T001 starts.
- T008, T009, and T010 can run in parallel.
- T015, T016, and T017 can run in parallel after the Angular service exists.

## Implementation Strategy

1. Deliver MVP with setup, tests, and US1.
2. Add explicit bulk acceptance for US2.
3. Add retries and duplicate resolution for US3.
4. Finish with audit, translation, and validation.
