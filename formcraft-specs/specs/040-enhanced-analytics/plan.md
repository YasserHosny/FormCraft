# Implementation Plan: Enhanced Analytics Dashboard

**Branch**: `040-enhanced-analytics` | **Date**: 2026-05-26 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/040-enhanced-analytics/spec.md`

## Summary

Extend F027 analytics with field-level, operator-level, compliance, and enhanced template usage analytics. Introduce pre-aggregated materialized views and companion tables to meet performance targets (5s for field analytics, 3s for operator analytics, 10s for compliance scorecards). Frontend adds four new analytics views with Chart.js visualizations, CSV/PNG export, and RTL-native layouts.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript / Angular 19 (frontend)
**Primary Dependencies**: FastAPI, Angular Material, Chart.js (ng2-charts), Supabase PostgreSQL, openpyxl, WeasyPrint
**Storage**: Supabase PostgreSQL with materialized views; existing tables: `submissions`, `templates`, `pages`, `elements`, `profiles`, `departments`, `branches`, `audit_logs`
**Testing**: pytest (backend), Angular TestBed (frontend)
**Target Platform**: Linux server / Web browser
**Project Type**: Web application (frontend + backend)
**Performance Goals**: <5s field analytics (50 fields, 10k submissions), <3s operator analytics (100 operators), <10s compliance scorecards (500+ templates)
**Constraints**: RLS-enforced, Arabic-first RTL, pixel-perfect PDF export, JWT auth
**Scale/Scope**: Up to 10k submissions/day, 500+ templates, 100+ operators per org

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| Arabic-First RTL | PASS | All new UI components must support RTL; chart labels and legends use i18n keys |
| Pixel-Perfect PDF | PASS | Analytics exports use existing WeasyPrint infrastructure; no new canvas elements |
| AI Suggestion Never Auto-Apply | PASS | No AI features in this analytics feature |
| Deterministic Over Probabilistic | PASS | All analytics are deterministic aggregations |
| Test-First Development | PASS | Contract tests for all new API endpoints; unit tests for aggregation logic |
| Normalized Data Model | PASS | New companion tables use normalized schema with FKs; materialized views are read-only aggregates |
| Translation-Key Architecture | PASS | All UI strings use i18n keys; chart tooltips and labels are translatable |
| Security and Auditability | PASS | RLS on all new tables; analytics access logged via existing audit infrastructure |
| Simplicity and YAGNI | PASS | No real-time collaboration, no AI, no bulk automation beyond spec scope |

## Project Structure

### Documentation (this feature)

```text
specs/040-enhanced-analytics/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── analytics-api.md
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
formcraft-backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── analytics.py          # F040 analytics endpoints
│   ├── schemas/
│   │   └── analytics.py              # Pydantic request/response models
│   ├── services/
│   │   └── analytics/
│   │       ├── field_analytics.py
│   │       ├── operator_analytics.py
│   │       ├── compliance_analytics.py
│   │       ├── template_analytics.py
│   │       └── export_service.py
│   └── models/
│       └── analytics.py              # SQLAlchemy models for new tables
├── migrations/
│   └── f040_analytics_tables.sql     # Supabase migration
└── tests/
    ├── contract/
    │   └── test_analytics_api.py
    ├── unit/
    │   └── test_analytics_services.py
    └── integration/
        └── test_analytics_flow.py

formcraft-frontend/
├── src/app/features/
│   └── analytics/
│       ├── analytics-routing.module.ts
│       ├── analytics.module.ts
│       ├── components/
│       │   ├── field-analytics/
│       │   ├── operator-analytics/
│       │   ├── compliance-analytics/
│       │   ├── template-usage-analytics/
│       │   └── export-dialog/
│       ├── services/
│       │   └── analytics.service.ts
│       └── models/
│           └── analytics.model.ts
└── src/assets/i18n/
    ├── ar.json                         # Arabic analytics keys
    └── en.json                         # English analytics keys
```

**Structure Decision**: Standard web application structure with separate backend (`formcraft-backend`) and frontend (`formcraft-frontend`) directories. Analytics feature is isolated in dedicated backend service modules and frontend feature module.

## Complexity Tracking

No constitution violations requiring justification. All gates pass.
