# Implementation Plan: New Theme Desk Live Data Integration

**Branch**: `050-new-theme-desk-data` | **Date**: 2026-05-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `formcraft-specs/specs/050-new-theme-desk-data/spec.md`

## Summary

Replace all hardcoded mock data in the new-theme desk components (`/ui/desk`) with live API data using existing services. The classic desk already has fully working services (`DeskService`, `DraftService`, `HistoryService`, `FormFillerService`, `CustomerService`, `ConditionEngineService`, `AutoFillService`, `FillerTafqeetService`, `ValidationService`, `SubmissionService`). This feature wires those same services into the new-theme standalone components while preserving the redesigned UI layout. No new backend endpoints are needed.

## Technical Context

**Language/Version**: TypeScript / Angular 19 (standalone components)
**Primary Dependencies**: Angular Material, RxJS, ngx-translate, existing desk services (providedIn: 'root')
**Storage**: Supabase PostgreSQL (accessed via existing REST APIs through desk services)
**Testing**: Jasmine/Karma (unit), Playwright (e2e)
**Target Platform**: Web browser (desktop-first, RTL-primary)
**Project Type**: Web application (frontend-only changes)
**Performance Goals**: Dashboard loads <3s, validation feedback <500ms, auto-fill <1s
**Constraints**: No new backend work. All services are `providedIn: 'root'` and can be injected directly into standalone components.
**Scale/Scope**: 3 components to modify (dashboard, form-filler, customers), 1 shared mock-data file to delete, ~11 existing services to wire in.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arabic-First, RTL-Native | PASS | All existing services support Arabic. New theme components already have RTL layout. |
| II. Pixel-Perfect Print Fidelity | N/A | No print/PDF changes in this feature. Form filler delegates to classic PDF renderer. |
| III. AI Suggestion, Never Auto-Apply | N/A | No AI integration in desk components. |
| IV. Deterministic Over Probabilistic | PASS | Validation rules are deterministic (existing validators reused). |
| V. Test-First Development | PASS | Integration test per user story written before implementation (see tasks.md). |
| VI. Normalized Data Model | PASS | No schema changes. Reusing existing normalized entities. |
| VII. Translation-Key Architecture | PASS | New theme components use ngx-translate. No hardcoded strings will be introduced. |
| VIII. Security and Auditability | PASS | RBAC enforced via RoleGuard on routes. Services use JWT auth via interceptor. |
| IX. Simplicity and YAGNI | PASS | No new abstractions — directly inject existing services. Delete mock data entirely. |

## Project Structure

### Documentation (this feature)

```text
formcraft-specs/specs/050-new-theme-desk-data/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (N/A — no new contracts)
├── checklists/          # Quality checklists
│   └── requirements.md
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
formcraft-frontend/src/app/features/
├── ui-redesign/
│   ├── desk/
│   │   ├── dashboard.component.ts       # MODIFY: wire DeskService, DraftService, HistoryService
│   │   ├── dashboard.component.html     # MODIFY: replace hardcoded KPIs/data with bound properties
│   │   ├── dashboard.component.scss     # KEEP: no changes needed
│   │   ├── form-filler.component.ts     # MODIFY: wire FormFillerService, ConditionEngine, etc.
│   │   ├── form-filler.component.html   # MODIFY: render real template fields dynamically
│   │   ├── form-filler.component.scss   # KEEP: no changes needed
│   │   ├── customers.component.ts       # MODIFY: wire CustomerService
│   │   ├── customers.component.html     # MODIFY: render real customer data
│   │   └── customers.component.scss     # KEEP: no changes needed
│   └── shared/
│       └── mock-data.ts                 # DELETE: remove all mock data
├── desk/
│   └── services/                        # REUSE: all services injected as-is
│       ├── desk.service.ts              # getDashboard(), pinTemplate(), unpinTemplate()
│       ├── draft.service.ts             # saveDraft(), updateDraft(), getDraft(), listDrafts()
│       ├── history.service.ts           # getSubmissions()
│       ├── submission.service.ts        # submit()
│       ├── form-filler.service.ts       # getTemplate()
│       ├── customer.service.ts          # list(), getById(), search(), getAutoPopulateData()
│       ├── auto-fill.service.ts         # executeAutoFill(), clearAutoFill()
│       ├── condition-engine.service.ts  # initialize(), visibilityChanged$, requiredChanged$
│       ├── validation.service.ts        # validation logic
│       └── filler-tafqeet.service.ts    # compute()
```

**Structure Decision**: Frontend-only modifications within the existing `ui-redesign/desk/` directory. No new files created except test files. Existing services from `desk/services/` are injected directly (all `providedIn: 'root'`).

## Complexity Tracking

No constitution violations — table not needed.
