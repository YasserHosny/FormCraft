# Implementation Plan: Operational Report Engine

**Branch**: `033-operational-reports` | **Date**: 2026-05-25 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/033-operational-reports/spec.md`

## Summary

Build an operational reporting engine providing transaction registers, daily reconciliation, period summaries, a custom report builder, and specialized financial reports. Reports query existing `submissions` table with aggregation, respect RLS, export to Excel/CSV/PDF, and support scheduling via email delivery. Designer-tagged "amount" fields enable financial aggregation. Cross-template custom reports auto-align shared fields by type tag.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript / Angular 19 (frontend)
**Primary Dependencies**: FastAPI, Angular Material, openpyxl (Excel), WeasyPrint (PDF reports), ng2-charts/Chart.js (frontend charts), APScheduler (report scheduling), Resend (email delivery)
**Storage**: Supabase PostgreSQL — queries against existing `submissions`, `templates`, `profiles`, `departments`, `branches` tables; new tables for report definitions and archives
**Testing**: pytest (backend), Jasmine/Karma (frontend)
**Target Platform**: Web application (SPA + API)
**Project Type**: Web service (Angular SPA + FastAPI backend)
**Performance Goals**: Transaction register 10K rows < 5s, reconciliation < 10s, custom reports 100K rows export < 60s
**Constraints**: All reports RLS-scoped, tiered role access (admin=all, branch_manager=register+reconciliation, operator=own history only), 12-month archive retention
**Scale/Scope**: Organizations with up to 1M submissions, 50 operators per branch, 500+ templates

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arabic-First, RTL-Native | PASS | Report UI uses Angular Material (RTL-ready). Excel/PDF exports preserve Arabic text direction. |
| II. Pixel-Perfect Print Fidelity | N/A | Reports are data exports, not canvas print output. PDF reports use WeasyPrint with RTL CSS. |
| III. AI Suggestion, Never Auto-Apply | N/A | No AI involved in reporting. |
| IV. Deterministic Over Probabilistic | PASS | All aggregation is deterministic SQL. |
| V. Test-First Development | PASS | Contract tests for all report endpoints. Unit tests for aggregation services. |
| VI. Normalized Data Model | PASS | New tables (report_templates, report_schedules, report_archives) follow normalized pattern with FK relationships. |
| VII. Translation-Key Architecture | PASS | All report UI labels use i18n keys. Report column headers support bilingual labels. |
| VIII. Security and Auditability | PASS | RLS policies on all report queries. Tiered role access. Audit log for report generation/export. |
| IX. Simplicity and YAGNI | PASS | No SFTP, no real-time dashboards, no embedded BI. Focused on SQL aggregation + file generation. |

**Gate Result**: PASS — No violations.

## Project Structure

### Documentation (this feature)

```text
specs/033-operational-reports/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── reports-api.md
│   └── report-scheduler-api.md
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
formcraft-backend/
├── app/
│   ├── api/routes/
│   │   ├── reports.py              # Report endpoints (transaction, reconciliation, period, financial)
│   │   ├── report_builder.py       # Custom report builder endpoints
│   │   └── report_schedules.py     # Schedule CRUD + history
│   ├── models/
│   │   └── report.py               # SQLAlchemy/Pydantic models for report entities
│   ├── schemas/
│   │   └── report.py               # Pydantic request/response schemas
│   ├── services/
│   │   ├── reports/
│   │   │   ├── __init__.py
│   │   │   ├── transaction_register.py   # Transaction register query builder
│   │   │   ├── reconciliation.py         # Daily reconciliation aggregation
│   │   │   ├── period_summary.py         # Period comparison logic
│   │   │   ├── financial_reports.py      # Beneficiary, void, signatory reports
│   │   │   ├── custom_builder.py         # Custom report query engine
│   │   │   ├── report_exporter.py        # Excel/CSV/PDF generation
│   │   │   └── report_scheduler.py       # APScheduler integration for recurring reports
│   │   └── email/
│   │       └── report_delivery.py        # Email delivery for scheduled reports
│   └── core/
│       └── report_permissions.py         # Tiered access control logic
└── tests/
    ├── contract/
    │   └── test_reports_api.py
    ├── unit/
    │   ├── test_transaction_register.py
    │   ├── test_reconciliation.py
    │   ├── test_period_summary.py
    │   ├── test_custom_builder.py
    │   └── test_report_exporter.py
    └── integration/
        └── test_report_scheduling.py

formcraft-frontend/
├── src/app/features/admin/
│   ├── reports/
│   │   ├── reports-routing.module.ts
│   │   ├── reports.module.ts
│   │   ├── transaction-register/
│   │   │   ├── transaction-register.component.ts
│   │   │   ├── transaction-register.component.html
│   │   │   └── transaction-register.component.scss
│   │   ├── daily-reconciliation/
│   │   │   ├── daily-reconciliation.component.ts
│   │   │   ├── daily-reconciliation.component.html
│   │   │   └── daily-reconciliation.component.scss
│   │   ├── period-summary/
│   │   │   ├── period-summary.component.ts
│   │   │   ├── period-summary.component.html
│   │   │   └── period-summary.component.scss
│   │   ├── report-builder/
│   │   │   ├── report-builder.component.ts
│   │   │   ├── report-builder.component.html
│   │   │   └── report-builder.component.scss
│   │   ├── financial-reports/
│   │   │   ├── beneficiary-report.component.ts
│   │   │   ├── void-reprint-register.component.ts
│   │   │   └── signatory-usage.component.ts
│   │   ├── report-schedules/
│   │   │   ├── report-schedules.component.ts
│   │   │   └── schedule-form-dialog.component.ts
│   │   └── shared/
│   │       ├── report-filter-panel.component.ts
│   │       ├── report-export-button.component.ts
│   │       └── period-comparison-indicator.component.ts
│   └── services/
│       └── reports.service.ts
└── src/app/core/services/
    └── (existing services — no new core services needed)
```

**Structure Decision**: Follows existing polyrepo pattern. Backend adds `services/reports/` module with submodules per report type. Frontend adds `features/admin/reports/` lazy-loaded module with sub-components per report view.

## Complexity Tracking

No violations — no complexity justification needed.
