# Implementation Plan: Data Retention and Archival

**Branch**: `044-data-retention-archival` | **Date**: 2026-05-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/044-data-retention-archival/spec.md`

## Summary

Build a compliance-focused data retention and archival system that allows compliance admins to define retention policies, preview their impact, execute archive/purge jobs via background workers, manage legal holds, and preserve immutable audit evidence. The system integrates with existing Supabase PostgreSQL, FastAPI backend, Angular frontend, and APScheduler infrastructure.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript / Angular 19 (frontend)
**Primary Dependencies**: FastAPI, Pydantic, SQLAlchemy/Supabase client (backend); Angular Material, ngx-translate, RxJS, ng2-charts (frontend)
**Storage**: Supabase PostgreSQL (operational + archive schema), Supabase Storage (cold tier for large blobs)
**Testing**: pytest (backend), Jasmine/Karma (frontend)
**Target Platform**: Linux server (Bunny Magic Containers), Web browser (Chrome/Firefox/Safari/Edge)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Preview 100k records in < 2 minutes; retention job batch processing ~1,000 records per minute
**Constraints**: RLS-enforced access, Arabic-first RTL UI, zero hardcoded strings, all retention evidence queryable for 7 years
**Scale/Scope**: Multi-tenant; per-organization policies; jobs run per-organization sequentially to avoid cross-tenant resource contention

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arabic-First, RTL-Native | PASS | All retention admin UI must render correctly in RTL; policy names and notices support Arabic i18n keys. |
| II. Pixel-Perfect Print Fidelity | N/A | No PDF output in this feature. |
| III. AI Suggestion, Never Auto-Apply | PASS | No AI features in this scope. |
| IV. Deterministic Over Probabilistic | PASS | Retention rules are deterministic based on policy + date + hold status. |
| V. Test-First Development | PASS | Every service, API endpoint, and job function requires tests before implementation. |
| VI. Normalized Data Model | PASS | All new entities normalized with foreign keys; versioned migrations required. |
| VII. Translation-Key Architecture | PASS | All UI strings via i18n keys; Arabic and English supported per FR-009. |
| VIII. Security and Auditability | PASS | RLS on new tables; retention actions audited; role-based access (Admin/Designer/Operator/Viewer — only Admin/Designer can configure retention). |
| IX. Simplicity and YAGNI | PASS | No bulk automation engine, no SSO, no OCR, no real-time collaboration. |

## Project Structure

### Documentation (this feature)

```text
specs/044-data-retention-archival/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── retention-api.md
│   └── job-webhooks.md
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
formcraft-backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── retention.py          # FastAPI routers: policies, jobs, holds, manifests
│   ├── models/
│   │   ├── retention_policy.py
│   │   ├── retention_job.py
│   │   ├── legal_hold.py
│   │   ├── archive_manifest.py
│   │   └── privacy_request.py
│   ├── schemas/
│   │   ├── retention.py                # Pydantic request/response schemas
│   │   └── job.py
│   ├── services/
│   │   ├── retention_policy_service.py
│   │   ├── retention_job_service.py
│   │   ├── legal_hold_service.py
│   │   ├── archive_manifest_service.py
│   │   └── preview_service.py
│   └── core/
│       └── scheduler.py              # APScheduler job definitions for retention
└── tests/
    ├── unit/
    │   ├── services/
    │   │   ├── test_retention_policy_service.py
    │   │   ├── test_retention_job_service.py
    │   │   └── test_preview_service.py
    └── integration/
        └── test_retention_api.py

formcraft-frontend/
├── src/app/
│   ├── features/
│   │   └── admin/
│   │       └── retention/
│   │           ├── components/
│   │           │   ├── policy-list/
│   │           │   ├── policy-form/
│   │           │   ├── policy-preview/
│   │           │   ├── job-list/
│   │           │   ├── job-detail/
│   │           │   ├── legal-hold-list/
│   │           │   ├── legal-hold-form/
│   │           │   ├── archive-manifest-list/
│   │           │   └── archive-restore-dialog/
│   │           ├── services/
│   │           │   └── retention.service.ts
│   │           ├── models/
│   │           │   └── retention.model.ts
│   │           └── retention-routing.module.ts
│   └── shared/
│       └── components/
│           └── retention-status-badge/
```

**Structure Decision**: Option 2 (Web application). The backend exposes REST APIs under `/api/v1/retention/*`. The frontend adds an `admin/retention` feature module under the existing admin section.

## Complexity Tracking

> No Constitution violations detected. The feature stays within approved architectural boundaries.
