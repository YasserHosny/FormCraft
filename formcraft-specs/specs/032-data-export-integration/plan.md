# Implementation Plan: Data Export & Integration

**Branch**: `032-data-export-integration` | **Date**: 2026-05-25 | **Spec**: [spec.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/032-data-export-integration/spec.md)
**Input**: Feature specification from `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-specs/specs/032-data-export-integration/spec.md`

## Summary

Add an Admin Console export and integration area for AC-07. The implementation introduces `/admin/export` for filtered direct-download submission exports and email-only recurring export schedules, template package export/import for `.formcraft` portability, and an integrations area for organization-scoped API credentials plus signed webhook subscriptions and delivery logs. Backend work uses FastAPI services over Supabase with normalized export/integration tables, existing template/page/element/submission data, and existing audit logging patterns.

## Technical Context

**Language/Version**: Python 3.12 backend; TypeScript / Angular 19 frontend  
**Primary Dependencies**: FastAPI, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, ngx-translate, RxJS, Python CSV/JSON libraries, `openpyxl` for workbook export, existing notification/email delivery infrastructure  
**Storage**: Supabase PostgreSQL; extend existing `templates`, `pages`, `elements`, `form_submissions`, `profiles`, `departments`, `branches`, `audit_logs`; add export schedule/delivery, integration credential, webhook subscription/delivery tables  
**Testing**: `pytest` backend unit/integration/contract tests; Angular build and focused component/service tests where present  
**Target Platform**: Enterprise web application deployed as Angular frontend + FastAPI backend on existing container infrastructure  
**Project Type**: Web application with API backend and Angular SPA frontend  
**Performance Goals**: Direct export up to 10,000 matching records completes in under 2 minutes; recurring export delivery within 15 minutes of schedule for 95% of runs; webhook delivery attempt recorded within 30 seconds for 95% of eligible events  
**Constraints**: Preserve org isolation via Supabase RLS and `org_id`; one-time exports are direct-download only and oversized requests are rejected; recurring exports are email-only; no SFTP/file-transfer in F32; active webhooks require signing secrets; full webhook payload previews are admin-only; all integration actions audited; Arabic/English UI with RTL/LTR support  
**Scale/Scope**: Org-scoped export/integration foundation for thousands of submissions per export, dozens of recurring schedules, dozens of webhook subscriptions/API credentials per organization, and template package portability across organizations/environments

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution source: `/media/yasserhosny/My Passport/Work/Projects/FormCraft/.specify/memory/constitution.md`.

| Principle | Gate Result | Plan Response |
|-----------|-------------|---------------|
| I. Arabic-First, RTL-Native | PASS | Export, package import, credential, and webhook admin UI must use translation keys, RTL/LTR mirroring, and `dir="auto"` for names, filters, payload previews, and Arabic/mixed content. |
| II. Pixel-Perfect Print Fidelity | PASS | F32 does not alter PDF rendering, canvas positions, or print output. Template packages preserve mm coordinates without transforming them. |
| III. AI Suggestion, Never Auto-Apply | PASS | No AI suggestions or auto-application are introduced. |
| IV. Deterministic Over Probabilistic | PASS | Export filtering, package validation, credential scoping, and webhook signing are deterministic rules. |
| V. Test-First Development | PASS WITH TASK REQUIREMENT | Tasks must create failing backend contract/unit tests before implementation for export limits, package round trip, credential scope/revoke, signed webhooks, and audit events. |
| VI. Normalized Data Model | PASS | New export schedules/deliveries, integration credentials, webhook subscriptions, and webhook deliveries are normalized tables with migrations, foreign keys, `created_at`, `updated_at`, and `created_by`. |
| VII. Translation-Key Architecture | PASS WITH TASK REQUIREMENT | New Angular admin/export/integration UI must add `en.json`/`ar.json` keys and avoid hardcoded user-facing text. |
| VIII. Security and Auditability | PASS | Admin-only export/schedule/integration management, designer/admin package permissions, org scoping, RLS, signed webhooks, hashed credentials, and audit events are required. |
| IX. Simplicity and YAGNI | JUSTIFIED EXCEPTIONS | F32 requires recurring export schedules and webhook retries. Scope is bounded to email-only recurring exports, three webhook retries, and no general-purpose automation engine, SFTP, file-transfer destinations, pre-built connectors, or custom connector builder. |

No blocking gate failures. Complexity exceptions are documented below.

## Project Structure

### Documentation (this feature)

```text
/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-specs/specs/032-data-export-integration/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
├── checklists/
│   └── requirements.md
└── tasks.md             # Created by speckit-tasks, not by this plan
```

### Source Code (repository root)

```text
/media/yasserhosny/My Passport/Work/Projects/FormCraft/
├── formcraft-backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   ├── admin_export.py          # new export preview/download/schedule/history endpoints
│   │   │   ├── integrations.py          # new credential/webhook management endpoints
│   │   │   └── templates.py             # extend with .formcraft package export/import endpoints
│   │   ├── schemas/
│   │   │   ├── export.py                # export request/response DTOs
│   │   │   ├── integration.py           # credential/webhook DTOs
│   │   │   └── template_package.py      # package manifest/import-review DTOs
│   │   └── services/
│   │       ├── export_service.py        # filtering, direct files, recurring schedule execution
│   │       ├── template_package_service.py
│   │       ├── integration_credential_service.py
│   │       └── webhook_service.py       # signing, dispatch, retries, delivery logs
│   ├── migrations/
│   │   └── 034_data_export_integration.sql
│   └── tests/
│       ├── unit/
│       │   ├── test_export_service.py
│       │   ├── test_template_package_service.py
│       │   └── test_webhook_service.py
│       └── integration/
│           └── test_data_export_integration_routes.py
└── formcraft-frontend/
    └── src/app/
        ├── core/services/
        │   ├── data-export.service.ts
        │   ├── integration.service.ts
        │   └── template.service.ts      # extend package export/import calls
        ├── features/admin/
        │   ├── data-export/
        │   │   ├── data-export.component.ts
        │   │   ├── data-export.component.html
        │   │   └── data-export.component.scss
        │   ├── export-schedules/
        │   │   ├── export-schedules.component.ts
        │   │   ├── export-schedules.component.html
        │   │   └── export-schedules.component.scss
        │   └── integrations/
        │       ├── integration-credentials.component.ts
        │       ├── webhook-subscriptions.component.ts
        │       ├── webhook-deliveries.component.ts
        │       └── integrations.component.scss
        └── shared/models/
            └── integration.models.ts
```

**Structure Decision**: Use the existing two-project web app layout (`formcraft-backend`, `formcraft-frontend`). Add admin-scoped backend route modules for export and integrations, extend `templates.py` only for package import/export because package portability belongs to templates, and add focused backend services rather than one broad integration service. On the frontend, keep all admin UI under `features/admin` and share typed models/API clients from `core/services` and `shared/models`.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Recurring export schedules | F32 requires daily/weekly recurring exports to email recipients. | One-time-only exports would fail the approved spec and keep routine compliance exports manual. |
| Webhook retry delivery | F32 requires webhook retries and delivery history. | Single-attempt delivery would be unreliable for temporary endpoint failures and fail the accepted workflow. |

## Phase 0: Research

See [research.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/032-data-export-integration/research.md).

## Phase 1: Design & Contracts

See [data-model.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/032-data-export-integration/data-model.md), [contracts/openapi.yaml](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/032-data-export-integration/contracts/openapi.yaml), and [quickstart.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/032-data-export-integration/quickstart.md).

## Constitution Check - Post Design

Post-design check remains acceptable. The design preserves org-scoped normalized tables with RLS, hashes integration credentials, requires signed webhook delivery, records full payload previews only in admin-protected delivery logs, keeps all user-facing UI translatable, and does not add SFTP, custom connectors, or a general automation engine. Recurring exports and webhook retries remain bounded to the approved F32 requirements.
