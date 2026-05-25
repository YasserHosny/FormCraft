# Implementation Plan: Batch Operations & Print Queue

**Branch**: `036-batch-operations-implementation` | **Date**: 2026-05-26 | **Spec**: [spec.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/036-batch-operations/spec.md)
**Input**: Feature specification from `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-specs/specs/036-batch-operations/spec.md`

## Summary

Add batch form generation and print queue management to Form Desk. Operators and admins can upload CSV/Excel data sources, map columns to template fields, validate rows, and generate hundreds of pre-filled PDFs as background jobs. The queue dashboard provides real-time progress tracking, download options (ZIP, merged PDF, printer queue), and error reporting. Admins can configure scheduled recurring batches with API data sources and cron expressions. All batch-generated forms are logged as individual submissions with batch metadata.

## Technical Context

**Language/Version**: Python 3.12 backend; TypeScript / Angular 19 frontend  
**Primary Dependencies**: FastAPI, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, WeasyPrint (existing PDF renderer), APScheduler (existing scheduler), openpyxl, Python csv module, existing notification/email infrastructure, existing validation/condition/tafqeet services  
**Storage**: Supabase PostgreSQL; extend existing `templates`, `pages`, `elements`, `form_submissions` (add `batch_job_id` and `batch_generated`), `profiles`, `organizations`, `departments`, `branches`; add `batch_jobs`, `batch_schedules`, `batch_errors`, `batch_data_sources` tables  
**Testing**: `pytest` backend unit/integration/contract tests; Angular focused service/component tests where present  
**Target Platform**: Angular SPA + FastAPI backend on existing container infrastructure  
**Project Type**: Web application with background job processing and Angular SPA frontend  
**Performance Goals**: Batch generation of 500 PDFs within 5 minutes; validation of 1,000 rows within 10 seconds; queue dashboard progress updates within 2 seconds; scheduled jobs execute within 5 minutes of configured time  
**Constraints**: Background jobs run in-process via async worker pattern (APScheduler for recurring, polling-based status for on-demand); PDF generation reuses existing WeasyPrint renderer; file uploads limited to 10 MB CSV/XLSX with MIME validation; raw data sources auto-purged after 30 days; org-level `max_batch_size` enforced; duplicate row detection during validation; mapping re-validated before generation; Arabic-first RTL UI  
**Scale/Scope**: On-demand batch jobs and scheduled recurring batches per org/template; initial scope covers CSV/XLSX/clipboard input, column mapping, row validation, background PDF generation, queue dashboard, ZIP/merged download, printer queue, error reports, and scheduled API-driven batches

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution source: `/media/yasserhosny/My Passport/Work/Projects/FormCraft/.specify/memory/constitution.md`.

| Principle | Gate Result | Plan Response |
|-----------|-------------|---------------|
| I. Arabic-First, RTL-Native | PASS | Batch queue UI, column mapper, validation grid, and error reports use translation keys, default Arabic, mirror RTL/LTR spacing, and `dir="auto"` for mixed content. |
| II. Pixel-Perfect Print Fidelity | PASS | Batch-generated PDFs reuse the existing WeasyPrint renderer and deterministic template schema; no new print path or coordinate changes. |
| III. AI Suggestion, Never Auto-Apply | PASS | No AI suggestions introduced. |
| IV. Deterministic Over Probabilistic | PASS | Row validation reuses existing deterministic validator library; country-specific rules (national ID, IBAN, VAT, phone) remain hard-coded. |
| V. Test-First Development | PASS WITH TASK REQUIREMENT | Tasks must create failing contract/unit tests for batch validation, background generation, queue status, cancellation, scheduled API pulls, and error reporting before implementation. |
| VI. Normalized Data Model | PASS | New `batch_jobs`, `batch_schedules`, `batch_errors`, and `batch_data_sources` tables are normalized with foreign keys, audit fields, and migrations; column mappings stored as JSONB with schema validation. |
| VII. Translation-Key Architecture | PASS WITH TASK REQUIREMENT | All batch queue UI strings, validation messages, error reports, and email notifications use i18n translation keys. |
| VIII. Security and Auditability | PASS | Batch routes require authenticated operator/admin roles; file uploads validated by MIME and extension; virus scan via ClamAV if available; error reports downloadable only by job creator or admin; scheduled API credentials stored encrypted; audit logs record batch job creation, cancellation, and completion. |
| IX. Simplicity and YAGNI | PASS WITH JUSTIFIED EXCEPTIONS | Background job tracker is required for progress and cancellation; in-process async generation is sufficient for initial scope. No general-purpose bulk automation engine (F036 is narrowly scoped to template+data-source PDF generation). No distributed task queue (Celery/RQ) deferred. |

No blocking gate failures. Complexity exceptions are documented below.

## Project Structure

### Documentation (this feature)

```text
/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-specs/specs/036-batch-operations/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
└── tasks.md             # Created by speckit-tasks, not by this plan
```

### Source Code (repository root)

```text
/media/yasserhosny/My Passport/Work/Projects/FormCraft/
├── formcraft-backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   └── batch_jobs.py           # batch job CRUD, start, cancel, download
│   │   ├── schemas/
│   │   │   └── batch.py                # batch DTOs
│   │   └── services/
│   │       ├── batch_service.py        # job orchestration, status, cancellation
│   │       ├── batch_generation_service.py  # background PDF generation loop
│   │       ├── batch_validation_service.py  # row validation, duplicate detection
│   │       ├── batch_schedule_service.py    # recurring schedules via APScheduler
│   │       └── batch_data_source_service.py # CSV/XLSX/clipboard parse, column extract
│   ├── migrations/
│   │   └── 036_batch_operations.sql
│   └── tests/
│       ├── unit/
│       │   ├── test_batch_validation.py
│       │   ├── test_batch_generation.py
│       │   └── test_batch_schedule.py
│       └── integration/
│           └── test_batch_jobs_routes.py
└── formcraft-frontend/
    └── src/app/
        ├── core/services/
        │   └── batch.service.ts
        └── features/desk/
            └── batch-queue/
                ├── batch-queue.module.ts
                ├── batch-list/
                ├── batch-create-wizard/
                │   ├── step-template/
                │   ├── step-data-source/
                │   ├── step-column-mapper/
                │   ├── step-validation/
                │   └── step-generate/
                ├── batch-detail/
                └── batch-error-report/
```

**Structure Decision**: Keep batch operations inside the existing `desk` feature because the primary user journey starts at `/desk/queue`. Add a dedicated `batch-queue` sub-feature with a multi-step wizard. Reuse the existing PDF renderer, validation services, and notification infrastructure. Backend uses focused services: one for orchestration/status, one for generation, one for validation, one for scheduling, and one for data source parsing. This keeps each service independently testable and avoids a monolithic batch module.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Background job tracker | Operators need real-time progress, cancellation, and download of partial results. | Synchronous generation would block the HTTP request and timeout for large batches. |
| Scheduled recurring batches | Admins need routine automation (statements, certificates) without manual intervention. | Manual-only batches would not satisfy the automation requirement and would create operational toil. |
| Duplicate row detection | Enterprise data sources often contain duplicates that must be flagged before mass generation. | Skipping duplicates silently would produce incorrect batch counts and confuse operators. |
| Column auto-mapping | Well-named CSV headers should reduce manual mapping effort. | Pure manual mapping is acceptable for small batches but would be painful for 50+ column data sources. |

## Phase 0: Research

See [research.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/036-batch-operations/research.md).

## Phase 1: Design & Contracts

See [data-model.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/036-batch-operations/data-model.md), [contracts/openapi.yaml](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/036-batch-operations/contracts/openapi.yaml), and [quickstart.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/036-batch-operations/quickstart.md).

## Constitution Check - Post Design

Post-design check remains acceptable. The design keeps batch data normalized and org-scoped, reuses the existing deterministic PDF renderer and validators, requires translation-key UI, enforces file upload security limits, stores scheduled API credentials encrypted, and records audit logs for job lifecycle events. Background job complexity is narrowly scoped to in-process async generation with polling-based status updates; no distributed queue infrastructure is introduced.
