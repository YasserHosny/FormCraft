# Implementation Plan: Analytics & Reporting Dashboard

**Branch**: `027-analytics-reporting` | **Date**: 2026-05-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `formcraft-specs/specs/027-analytics-reporting/spec.md`

## Summary

Add organization-level analytics and operational reporting to FormCraft. The full analytics dashboard lives in the Admin Console (`/admin/analytics`) for Org Admin and Branch Manager roles. Operators get a lightweight "My Stats" widget on the Form Desk dashboard. All analytics are computed live from existing `submissions`, `templates`, `profiles`, `departments`, and `branches` tables — no pre-aggregation or background jobs. Supports submission volume trends, template usage rankings, operator productivity metrics, branch comparison, transaction register, and CSV/PDF export. All views are bilingual (Arabic/English) and respect multi-tenant + role-based data scoping.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript / Angular 19 (frontend)
**Primary Dependencies**: FastAPI, Supabase (PostgreSQL + Auth), Angular Material, WeasyPrint (PDF export), ng2-charts / Chart.js (frontend charting)
**Storage**: Supabase PostgreSQL — live aggregation queries against existing tables (submissions, templates, profiles, departments, branches)
**Testing**: pytest (backend), Jasmine/Karma (frontend)
**Target Platform**: Web application (SPA + REST API)
**Project Type**: Web service — new route module + new Angular feature module
**Performance Goals**: Dashboard loads < 3s for 100K submissions, CSV export < 10s for 50K rows, PDF export < 15s
**Constraints**: Multi-tenant isolation via RLS (`current_setting('app.current_org_id', true)::UUID`), role-based scoping (org_admin → all, branch_manager → department, operator → own)
**Scale/Scope**: Up to 100,000 submissions per organization, ~10 new backend endpoints, 1 new frontend feature module with ~8 components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution is a template (not project-specific). No gates defined — proceeding.

## Project Structure

### Documentation (this feature)

```text
formcraft-specs/specs/027-analytics-reporting/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API contracts)
│   ├── analytics-api.md
│   └── operator-stats-api.md
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
formcraft-backend/
├── app/
│   ├── api/routes/
│   │   └── analytics.py            # New: analytics API endpoints
│   ├── services/
│   │   └── analytics_service.py    # New: analytics query logic
│   └── schemas/
│       └── analytics.py            # New: Pydantic response models
└── tests/
    └── test_analytics.py           # New: analytics endpoint tests

formcraft-frontend/
├── src/app/features/
│   └── admin/
│       └── analytics/              # New: analytics feature module
│           ├── analytics.module.ts
│           ├── analytics-routing.module.ts
│           ├── components/
│           │   ├── analytics-dashboard/        # Overview with KPI cards + trend chart
│           │   ├── template-analytics/         # Template usage rankings
│           │   ├── operator-productivity/      # Operator metrics table
│           │   ├── branch-comparison/          # Branch side-by-side
│           │   ├── transaction-register/       # Submission listing
│           │   ├── date-range-picker/          # Shared date range filter
│           │   └── report-export/              # Export button/dialog
│           └── services/
│               └── analytics.service.ts        # API client
├── src/app/features/desk/
│   └── components/
│       └── operator-stats-widget/  # New: My Stats widget for Form Desk
└── src/app/shared/
    └── models/
        └── analytics.models.ts     # New: TypeScript interfaces
```

**Structure Decision**: Follows existing project conventions — new route file in `app/api/routes/`, new service in `app/services/`, new Angular feature module under `features/admin/analytics/`, operator widget in `features/desk/`.

## Complexity Tracking

No constitution violations — no justifications needed.
