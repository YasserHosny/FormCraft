# Implementation Plan: New-Theme Admin Pages - Export, Portal, Integration

**Branch**: `055-spark3-missing-pages` | **Date**: 2026-06-01 | **Spec**: `formcraft-specs/specs/055-spark3-missing-pages/spec.md`
**Input**: Feature specification from `formcraft-specs/specs/055-spark3-missing-pages/spec.md`

## Summary

Implement three missing Spark 3 admin pages for Export, Portal, and Integration under `/ui/admin/*`, replacing classic-theme redirects with new-theme Angular standalone components. The feature is frontend-only: reuse existing Angular services and Zod models, preserve existing backend API contracts, add route guards for admin-only access, and match the visual, RTL, and i18n behavior of the current new-theme Analytics page.

## Technical Context

**Language/Version**: TypeScript / Angular 19 frontend; Python 3.12 backend unchanged  
**Primary Dependencies**: Angular standalone components, Angular Router, Angular Material, RxJS, ngx-translate, existing `DataExportService`, `PortalService`, `IntegrationService`, existing Zod models  
**Storage**: No schema/storage changes; reads/writes through existing Supabase-backed backend APIs  
**Testing**: Angular unit/component tests via existing frontend test runner; manual quickstart checks for RTL/LTR, role guard, and download behavior  
**Target Platform**: Browser-based FormCraft Angular application under `/ui/`  
**Project Type**: Frontend web application increment in existing polyrepo  
**Performance Goals**: Each new `/ui/admin/*` page renders initial shell and loading state immediately, completes normal data load within 2 seconds on standard connection, and supports export downloads up to 50,000 records through existing API behavior  
**Constraints**: No backend endpoints, migrations, or API contract changes; zero hardcoded user-visible strings; admin-only routes; RTL is primary; no credential/webhook creation in this increment  
**Scale/Scope**: Three admin pages, route-table update, toolbar route correction, i18n additions, focused tests/quickstart verification

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Arabic-First, RTL-Native**: PASS. All new pages bind to the existing new-theme layout direction and include Arabic and English translation keys.
- **Pixel-Perfect Print Fidelity**: N/A. No canvas or PDF rendering changes.
- **AI Suggestion, Never Auto-Apply**: N/A. No AI workflow.
- **Deterministic Over Probabilistic**: PASS. UI consumes deterministic backend responses and introduces no AI/probabilistic logic.
- **Test-First Development**: PASS with requirement. Tasks create route/component/service-interaction tests before implementation tasks.
- **Normalized Data Model**: PASS. No data model or migration changes.
- **Translation-Key Architecture**: PASS with requirement. All labels, errors, buttons, and empty states use keys in both `en.json` and `ar.json`.
- **Security and Auditability**: PASS. Existing admin APIs remain authenticated; new routes use `RoleGuard` with `roles: ['admin']`.
- **Simplicity and YAGNI**: PASS. Existing services are reused; creation flows, backend changes, export schedules, and broad abstractions stay out of scope.

## Project Structure

### Documentation

```text
formcraft-specs/specs/055-spark3-missing-pages/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── admin-pages-contract.md
└── tasks.md
```

### Source Code

```text
formcraft-frontend/src/app/
├── core/services/
│   ├── data-export.service.ts
│   ├── portal.service.ts
│   └── integration.service.ts
├── features/ui-redesign/
│   ├── ui-redesign.routes.ts
│   ├── shell/toolbar.component.ts
│   └── admin/
│       ├── analytics.component.*
│       ├── export.component.*
│       ├── portal.component.*
│       └── integrations.component.*
├── shared/models/
│   ├── integration.models.ts
│   └── portal.models.ts
└── assets/i18n/
    ├── en.json
    └── ar.json
```

**Structure Decision**: Add new standalone Spark 3 admin components under `features/ui-redesign/admin/`, colocated with the existing new-theme Analytics page. Reuse existing classic admin services and shared models rather than copying classic components or changing backend contracts.

## Phase 0: Research

Research decisions are captured in `research.md`.

## Phase 1: Design & Contracts

Data model, UI/API contracts, and verification scenarios are captured in:

- `data-model.md`
- `contracts/admin-pages-contract.md`
- `quickstart.md`

## Post-Design Constitution Check

- **Arabic-First, RTL-Native**: PASS. Design requires explicit RTL/LTR quickstart checks and translation keys for all strings.
- **Test-First Development**: PASS. Tasks include tests before each page implementation.
- **Translation-Key Architecture**: PASS. Contract requires no raw strings in templates/components except technical enum values rendered through translations.
- **Security and Auditability**: PASS. Routes remain guarded by `RoleGuard`; backend audit/security remains unchanged.
- **Simplicity and YAGNI**: PASS. Scope remains frontend-only and manage-existing-only for integrations.

## Complexity Tracking

No constitution violations.
