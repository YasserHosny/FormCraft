# Tasks: Data Retention and Archival

**Feature**: F044 — Data Retention and Archival  
**Branch**: `044-data-retention-archival`  
**Date**: 2026-05-26  
**Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

---

## Dependency Graph

```text
Phase 1 (Setup)
  └── Phase 2 (Foundational)
        └── Phase 3 (US1: Configure Retention Policies)
              └── Phase 4 (US2: Archive and Purge Eligible Data)
                    └── Phase 5 (US3: Apply Legal Holds and Privacy Requests)
                          └── Phase 6 (Polish & Cross-Cutting)
```

**Story Independence Notes**:
- US1 can be independently tested end-to-end once Phase 2 is complete.
- US2 requires US1 (needs policies to trigger jobs) but job engine components can be developed in parallel with US1 frontend.
- US3 requires US2 job engine but can be tested independently using mock jobs.

**Parallel Execution Opportunities**:
- Backend models/schemas and frontend components can be built in parallel within each phase.
- US1 frontend screens and US2 job service backend can be developed concurrently after Phase 2.

---

## Phase 1: Setup

**Goal**: Initialize project structure and migrations for the retention feature.

- [X] T001 [P] Create backend API router file `formcraft-backend/app/api/routes/retention.py`
- [X] T002 [P] Create backend model files: `formcraft-backend/app/models/retention_policy.py`, `retention_job.py`, `legal_hold.py`, `archive_manifest.py`, `privacy_request.py`
- [X] T003 [P] Create backend schema files: `formcraft-backend/app/schemas/retention.py`, `job.py`
- [X] T004 [P] Create backend service stubs: `formcraft-backend/app/services/retention_policy_service.py`, `retention_job_service.py`, `legal_hold_service.py`, `archive_manifest_service.py`, `preview_service.py`
- [X] T005 [P] Create frontend feature module directory `formcraft-frontend/src/app/features/admin/retention/` with subdirectories `components/`, `services/`, `models/`
- [X] T006 [P] Generate Supabase migration `044_add_retention_tables.sql` in `formcraft-backend/migrations/` covering: retention_policies, retention_jobs, legal_holds, archive_manifests, privacy_requests, and `archive` schema with shadow tables
- [X] T007 Register new API router in `formcraft-backend/app/main.py` under `/api/retention` prefix
- [X] T008 Register frontend feature route in `formcraft-frontend/src/app/features/admin/admin.module.ts` for `admin/retention`

---

## Phase 2: Foundational

**Goal**: Build shared infrastructure that all user stories depend on.

- [X] T009 [P] Create Pydantic schemas for all retention entities in `formcraft-backend/app/schemas/retention.py` (PolicyCreate, PolicyUpdate, PolicyResponse, JobCreate, JobResponse, HoldCreate, HoldResponse, ManifestResponse, PreviewResponse)
- [X] T010 [P] Create SQLAlchemy/Supabase models in `formcraft-backend/app/models/` with `created_at`, `updated_at`, `created_by` audit fields and RLS policies
- [X] T011 [P] Implement `AuditLogger` integration in `formcraft-backend/app/services/retention_job_service.py` to write compliance events to existing `audit_logs` table
- [X] T012 [P] Implement SHA-256 utility inline in `formcraft-backend/app/services/retention_job_service.py` for canonical JSON hashing
- [X] T013 [P] Implement `PreviewService` in `formcraft-backend/app/services/preview_service.py` with read-only transaction, indexed date-range scans, and COUNT(*) pattern
- [X] T014 [P] Create Angular models in `formcraft-frontend/src/app/features/admin/retention/models/retention.model.ts` (interfaces matching backend schemas)
- [X] T015 [P] Create `RetentionService` in `formcraft-frontend/src/app/features/admin/retention/services/retention.service.ts` with RxJS HTTP calls to all retention endpoints
- [X] T016 [P] Add i18n translation keys for retention to `formcraft-frontend/src/assets/i18n/en.json` and `ar.json`

---

## Phase 3: User Story 1 — Configure Retention Policies

**Goal**: Compliance admins can define retention policies and preview their impact without modifying data.

**Independent Test Criteria**:
- Create a policy in a sandbox organization and confirm the preview identifies eligible records without changing data.
- Verify blocked records are flagged when audit minimums conflict.

> **Test-First Note (Constitution V)**: Within each story phase, test tasks should be started before or in parallel with their corresponding implementation tasks, but tests must be written and failing before the implementation is considered complete.

- [X] T017 [P] [US1] Implement `RetentionPolicyService.create_policy` in `formcraft-backend/app/services/retention_policy_service.py` with conflict detection (org + data_class + scope)
- [X] T018 [P] [US1] Implement `RetentionPolicyService.update_policy` in `formcraft-backend/app/services/retention_policy_service.py` with active-job guard
- [X] T019 [P] [US1] Implement `RetentionPolicyService.delete_policy` in `formcraft-backend/app/services/retention_policy_service.py` with job-existence guard
- [X] T020 [US1] Implement `RetentionPolicyService.list_policies` and `get_policy` with pagination and filters
- [X] T021 [US1] Implement `PreviewService.generate_preview` returning affected counts, date ranges, affected forms, blocked records, and downstream references
- [X] T022 [P] [US1] Build backend API endpoints in `formcraft-backend/app/api/routes/retention.py`: GET /policies, POST /policies, GET /policies/{id}, PUT /policies/{id}, DELETE /policies/{id}, POST /policies/{id}/preview
- [X] T023 [P] [US1] Write backend unit tests `formcraft-backend/tests/unit/services/test_retention_policy_service.py` covering create, conflict, update guard, delete guard, and preview logic
- [X] T024 [P] [US1] Write backend integration tests `formcraft-backend/tests/integration/test_retention_api.py` covering policy CRUD and preview endpoints
- [X] T025 [P] [US1] Build frontend `PolicyListComponent` in `formcraft-frontend/src/app/features/admin/retention/components/policy-list/`
- [X] T026 [P] [US1] Build frontend `PolicyFormComponent` in `formcraft-frontend/src/app/features/admin/retention/components/policy-form/` with Angular Material form fields for data_class, action, period, scope, legal_basis
- [X] T027 [P] [US1] Build frontend `PolicyPreviewComponent` in `formcraft-frontend/src/app/features/admin/retention/components/policy-preview/` displaying affected counts, blocked records, and downstream references
- [X] T028 [P] [US1] Write frontend unit tests for policy list, form, and preview components

---

## Phase 4: User Story 2 — Archive and Purge Eligible Data

**Goal**: The system runs approved retention jobs that archive or purge records and preserve evidence.

**Independent Test Criteria**:
- Run a retention job against eligible sample records and confirm archive manifests, purge results, and audit events match the preview.
- Verify interrupted jobs resume from checkpoint without re-processing committed batches.

- [X] T029 [US2] Implement `RetentionJobService.create_job` in `formcraft-backend/app/services/retention_job_service.py` with duplicate-active-job guard
- [X] T030 [US2] Implement `RetentionJobService.process_pending_jobs` batch executor with cursor-based checkpointing, 1,000-record batches, and per-batch commit
- [X] T031 [US2] Implement archive action: copy records to `archive` schema, update operational record status, generate `archive_manifests` entry with SHA-256 hash
- [X] T032 [US2] Implement purge action: delete operational records after reference-check (reports, exports, PDFs, portal sessions), write purge evidence to `audit_logs` with SHA-256
- [X] T032a [US2] Implement archive storage failure recovery in `formcraft-backend/app/services/retention_job_service.py`: if Supabase Storage cold export fails, mark manifest integrity_status as 'failed', record error in job error_log, and leave records in archive schema so job can resume/retry
- [X] T033 [US2] Implement mask action: redact PII fields in-place, write masking evidence to `audit_logs`
- [X] T034 [US2] Implement job pause/resume logic with checkpoint cursor persistence and idempotent re-execution guard
- [X] T035 [US2] Integrate APScheduler in `formcraft-backend/app/core/scheduler.py` to trigger `process_pending_jobs` every 5 minutes
- [X] T036 [P] [US2] Build backend API endpoints in `formcraft-backend/app/api/routes/retention.py`: GET /jobs, POST /jobs, GET /jobs/{id}, POST /jobs/{id}/pause, POST /jobs/{id}/resume
- [X] T037 [P] [US2] Write backend unit tests `formcraft-backend/tests/unit/services/test_retention_job_service.py` covering batch processing, checkpoint resume, archive manifest hashing, and purge reference checks
- [X] T038 [P] [US2] Write backend integration tests for job lifecycle endpoints (create, pause, resume, completion)
- [X] T039 [P] [US2] Build frontend `JobListComponent` in `formcraft-frontend/src/app/features/admin/retention/components/job-list/` with status badges and pagination
- [X] T040 [P] [US2] Build frontend `JobDetailComponent` in `formcraft-frontend/src/app/features/admin/retention/components/job-detail/` showing progress bars, evaluated/actioned/error counts, skipped records table, and error log
- [X] T041 [P] [US2] Write frontend unit tests for job list and detail components

---

## Phase 5: User Story 3 — Apply Legal Holds and Privacy Requests

**Goal**: Compliance admins can place legal holds and handle privacy requests without destroying required evidence.

**Independent Test Criteria**:
- Place a legal hold on a customer or submission and confirm retention jobs skip held records and report the reason.
- Verify a privacy request blocked by a legal hold shows the conflict and permits only masking or deferral.

- [X] T042 [US3] Implement `LegalHoldService.create_hold` in `formcraft-backend/app/services/legal_hold_service.py` with duplicate-active-hold guard for scope
- [X] T043 [US3] Implement `LegalHoldService.release_hold` and list/get methods
- [X] T044 [US3] Modify `RetentionJobService.process_pending_jobs` to query `legal_holds` per batch and skip held records, recording skip reason in `skipped_records`
- [X] T045 [US3] Implement `PrivacyRequestService.create_request` in `formcraft-backend/app/services/privacy_request_service.py` with automatic conflict detection against active holds
- [X] T046 [US3] Implement `PrivacyRequestService.resolve_request` allowing admin to approve, reject, or mask when deletion is blocked by hold
- [X] T047 [P] [US3] Build backend API endpoints: GET /holds, POST /holds, DELETE /holds/{id}, GET /privacy-requests, POST /privacy-requests, POST /privacy-requests/{id}/resolve
- [X] T048 [P] [US3] Write backend unit tests `formcraft-backend/tests/unit/services/test_legal_hold_service.py` and `test_privacy_request_service.py`
- [X] T049 [P] [US3] Write backend integration tests for holds and privacy request endpoints
- [X] T050 [P] [US3] Build frontend `LegalHoldListComponent` in `formcraft-frontend/src/app/features/admin/retention/components/legal-hold-list/`
- [X] T051 [P] [US3] Build frontend `LegalHoldFormComponent` in `formcraft-frontend/src/app/features/admin/retention/components/legal-hold-form/`
- [X] T052 [P] [US3] Build frontend `ArchiveManifestListComponent` in `formcraft-frontend/src/app/features/admin/retention/components/archive-manifest-list/` with integrity status and search
- [X] T053 [P] [US3] Build frontend `ArchiveRestoreDialogComponent` in `formcraft-frontend/src/app/features/admin/retention/components/archive-restore-dialog/` with restore conditions validation
- [X] T054 [P] [US3] Write frontend unit tests for hold list, hold form, manifest list, and restore dialog
- [X] T054a [US3] Implement per-record compliance traceability view in backend `formcraft-backend/app/services/retention_job_service.py` and expose endpoint GET /records/{record_id}/retention-history to satisfy SC-005
- [X] T054b [US3] Build frontend `RecordRetentionHistoryComponent` in `formcraft-frontend/src/app/features/admin/retention/components/record-retention-history/` showing why a record was retained, archived, or purged

---

## Phase 6: Polish & Cross-Cutting Concerns

**Goal**: Finalize documentation, RLS policies, webhook integration, RTL testing, and end-to-end validation.

- [X] T055 [P] Add comprehensive RLS policies to all new tables via migration (`retention_policies`, `retention_jobs`, `legal_holds`, `archive_manifests`, `privacy_requests`, `archive.*` schema tables)
- [X] T056 [P] Add retention event types to existing webhook subscription system (`retention.job.started`, `retention.job.completed`, `retention.job.failed`, `retention.hold.created`, `retention.hold.released`, `retention.manifest.restored`)
- [X] T057 [P] Implement webhook payload builders in `formcraft-backend/app/services/retention_job_service.py` and `legal_hold_service.py`
- [X] T058 [P] Verify all admin retention UI components render correctly in RTL mode (Arabic) with mixed Arabic-English content
- [X] T059 [P] Run backend linter: `cd formcraft-backend && ruff check app/models/retention_*.py app/schemas/retention.py app/services/retention_*.py app/services/preview_service.py app/services/legal_hold_service.py app/services/archive_manifest_service.py app/services/privacy_request_service.py app/api/routes/retention.py`
- [X] T060 [P] Run backend tests: `cd formcraft-backend && pytest tests/unit/services/test_retention*.py tests/integration/test_retention_api.py -v`
- [X] T061 [P] Run frontend tests: `cd formcraft-frontend && ng test --include='**/retention/**' --watch=false`
- [X] T062 Update feature spec status to "Implemented" and add final implementation notes to `formcraft-specs/specs/044-data-retention-archival/spec.md`

---

## Summary

| Phase | Story | Task Count | Parallel Tasks |
|-------|-------|------------|----------------|
| Phase 1 | Setup | 8 | 8 |
| Phase 2 | Foundational | 8 | 8 |
| Phase 3 | US1 | 12 | 9 |
| Phase 4 | US2 | 14 | 7 |
| Phase 5 | US3 | 15 | 8 |
| Phase 6 | Polish | 8 | 8 |
| **Total** | | **65** | **48** |

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1: Configure Retention Policies) provides a complete, independently testable increment.
