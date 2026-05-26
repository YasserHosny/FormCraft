# Implementation Plan: Platform Admin Console

**Branch**: `039-platform-admin-console` | **Date**: 2026-05-26 | **Spec**: [spec.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/039-platform-admin-console/spec.md)
**Input**: Feature specification from `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-specs/specs/039-platform-admin-console/spec.md`

## Summary

Add a `/platform` admin console for PC-01. Platform admins (`is_platform_admin=true`) can list all organizations with search/filter/sort, create new organizations with first-admin invitation, view org details across Profile/Subscription/Users/Stats tabs, suspend/reactivate organizations (revoking all sessions immediately), and monitor platform health via a dashboard with pre-aggregated metrics, charts, and tier-limit alerts. Backend adds platform-scoped API routes, a materialized view for aggregate metrics, audit logging for all platform actions, and Supabase session revocation on suspension. Frontend adds a dedicated `platform` feature module with guards, context switcher for dual-role users, and Angular Material dashboards.

## Technical Context

**Language/Version**: Python 3.12 backend; TypeScript / Angular 19 frontend  
**Primary Dependencies**: FastAPI, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, ngx-translate, RxJS, Pydantic, ng2-charts/Chart.js, existing notification/email infrastructure  
**Storage**: Supabase PostgreSQL; extend existing `organizations`, `org_settings`, `profiles`, `templates`, `submissions`, `audit_logs`; add materialized view `platform_metrics_mv` and optional `domain` unique column on `organizations`  
**Testing**: `pytest` backend unit/integration tests; Angular focused service/component tests where present  
**Target Platform**: Angular SPA + FastAPI backend on existing container infrastructure  
**Project Type**: Web application with admin SPA and API backend  
**Performance Goals**: Dashboard loads aggregate metrics for 100+ orgs within 3 seconds (materialized view); org search/filter within 3 seconds (database indexes); suspension takes effect within 30 seconds (immediate session revocation)  
**Constraints**: Platform routes are protected by `PlatformAdminGuard` checking `is_platform_admin`; all platform actions are audit-logged; org deletion is blocked if submissions exist; org creation rate-limited at 10/hour per platform admin; custom domain validated for uniqueness; context switcher provided for dual-role users; dashboard metrics sourced from materialized view refreshed every 5 minutes  
**Scale/Scope**: Platform-wide administration for tens to hundreds of organizations; single platform admin interface; no multi-platform-admin role hierarchy in this feature

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution source: `/media/yasserhosny/My Passport/Work/Projects/FormCraft/.specify/memory/constitution.md`.

| Principle | Gate Result | Plan Response |
|-----------|-------------|---------------|
| I. Arabic-First, RTL-Native | PASS | Platform console UI uses translation keys, default Arabic, and mirrors RTL/LTR spacing correctly. Charts use locale-aware formatting. |
| II. Pixel-Perfect Print Fidelity | PASS | No PDF or canvas changes in this feature. |
| III. AI Suggestion, Never Auto-Apply | PASS | No AI suggestions or auto-application are introduced. |
| IV. Deterministic Over Probabilistic | PASS | Org suspension, rate limiting, and domain uniqueness checks are deterministic service validations. |
| V. Test-First Development | PASS WITH TASK REQUIREMENT | Tasks must create failing backend contract tests for platform routes, session revocation, rate limiting, and materialized view refresh before implementation. Frontend tests for guard and service behavior must precede component code. |
| VI. Normalized Data Model | PASS | Materialized view is a read-only projection; all writes go to normalized `organizations`, `profiles`, `audit_logs`. Optional `domain` column adds a unique constraint. |
| VII. Translation-Key Architecture | PASS WITH TASK REQUIREMENT | All platform UI strings must use `en.json`/`ar.json` keys; no hardcoded labels in tables, forms, or chart tooltips. |
| VIII. Security and Auditability | PASS | `PlatformAdminGuard` enforces role; all platform actions write to `audit_logs`; session revocation on suspension is immediate; rate limiting prevents abuse. |
| IX. Simplicity and YAGNI | PASS | Scope is strictly platform org management and dashboard. No billing integration, no org-level impersonation, no SSO for platform admins, no real-time websocket updates. |

No blocking gate failures.

## Project Structure

### Documentation (this feature)

```text
/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-specs/specs/039-platform-admin-console/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── tasks.md             # Created by speckit-tasks, not by this plan
```

### Source Code (repository root)

```text
/media/yasserhosny/My Passport/Work/Projects/FormCraft/
├── formcraft-backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   └── platform.py           # platform dashboard, org CRUD, suspend/reactivate
│   │   ├── schemas/
│   │   │   └── platform.py           # platform DTOs (OrgCreate, OrgDetail, PlatformMetrics)
│   │   └── services/
│   │       ├── platform_service.py     # org list/filter, creation with invitation, suspension
│   │       └── platform_metrics_service.py  # materialized view refresh, alert computation
│   ├── migrations/
│   │   └── 039_platform_admin_console.sql
│   └── tests/
│       ├── unit/
│       │   ├── test_platform_service.py
│       │   └── test_platform_metrics_service.py
│       └── integration/
│           └── test_platform_routes.py
└── formcraft-frontend/
    └── src/app/
        ├── core/guards/
        │   └── platform-admin.guard.ts
        ├── core/services/
        │   └── platform.service.ts
        ├── features/platform/
        │   ├── platform.module.ts
        │   ├── platform-routing.module.ts
        │   ├── platform-layout/
        │   │   ├── platform-layout.component.ts
        │   │   └── context-switcher/
        │   ├── platform-dashboard/
        │   │   ├── platform-dashboard.component.ts
        │   │   └── platform-dashboard.component.html
        │   ├── organization-list/
        │   │   ├── organization-list.component.ts
        │   │   └── organization-list.component.html
        │   ├── organization-create/
        │   │   ├── organization-create.component.ts
        │   │   └── organization-create.component.html
        │   └── organization-detail/
        │       ├── organization-detail.component.ts
        │       ├── organization-detail.component.html
        │       └── tabs/
        │           ├── profile-tab/
        │           ├── subscription-tab/
        │           ├── users-tab/
        │           └── stats-tab/
        └── shared/models/
            └── platform.models.ts
```

**Structure Decision**: Use the existing backend/frontend split. Add a single `platform.py` backend route module because all platform endpoints share the same `is_platform_admin` guard and audit-log requirements. Keep platform logic in focused services so org creation, suspension with session revocation, metrics aggregation, and rate limiting remain independently testable. Add a dedicated Angular `platform` feature module to keep the console separate from org-level `/admin` and `/desk` routing.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Materialized view for metrics | Dashboard must load aggregate metrics for 100+ orgs in under 3 seconds. | On-demand aggregation with `COUNT(*)` across multiple tables would violate SC-001 at scale. |
| Session revocation on suspension | Suspension must take effect within 30 seconds for currently logged-in users. | Waiting for sessions to expire naturally would violate SC-003 and create a security gap. |
| Rate limiting on org creation | Prevents accidental or malicious bulk org creation by platform admins. | No limit would risk platform abuse and data sprawl without audit awareness. |

## Phase 0: Research

See [research.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/039-platform-admin-console/research.md).

## Phase 1: Design & Contracts

See [data-model.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/039-platform-admin-console/data-model.md), [contracts/openapi.yaml](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/039-platform-admin-console/contracts/openapi.yaml), and [quickstart.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/039-platform-admin-console/quickstart.md).

## Constitution Check - Post Design

Post-design check remains acceptable. The design uses a normalized data model with a read-only materialized view for performance, deterministic validation for suspension and rate limiting, translation-key UI for the platform console, full audit logging for all platform actions, and immediate session revocation to meet security and performance targets. No AI, canvas, or probabilistic components are introduced.
