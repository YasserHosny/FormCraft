# Task Breakdown: Enhanced Analytics Dashboard

**Feature**: 040-enhanced-analytics
**Branch**: `040-enhanced-analytics`
**Date**: 2026-05-26
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Dependency Graph

```text
Phase 1 (Setup) ───────────────────────────────────────┐
Phase 2 (Foundational) ────────────────────────────────┤
Phase 3 (US1 Field-Level) ─────┐                       │
Phase 4 (US2 Operator) ────────┼─── ALL PARALLEL ─────┤──→ Phase 7 (Polish)
Phase 5 (US3 Compliance) ──────┘                       │
Phase 6 (US4 Template Usage) ────────────────────────────┘
```

**Story Dependencies**: US1 → US2 → US3 → US4 (sequential priority, but technically parallelizable after foundational phase)

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only)

---

## Phase 1 — Setup & Infrastructure

*Goal: Create database schema, materialized views, and shared infrastructure.*

### Independent Test Criteria
- Migration applies cleanly via `supabase db push`
- All new tables have RLS policies enforced
- Materialized view `mv_template_usage_funnel` exists and is indexable

- [ ] T001 Create Supabase migration `formcraft-backend/migrations/f040_analytics_tables.sql` — define `field_analytics`, `operator_analytics`, `compliance_scorecard_cache`, `analytics_aggregation_log` tables with indexes and constraints per data-model.md
- [ ] T002 [P] Create materialized view `mv_template_usage_funnel` with `CREATE UNIQUE INDEX` for `REFRESH MATERIALIZED VIEW CONCURRENTLY` support in `formcraft-backend/migrations/f040_analytics_tables.sql`
- [ ] T003 [P] Add RLS policies to all new tables in `formcraft-backend/migrations/f040_analytics_tables.sql` — org_id scoping, admin-only for compliance cache
- [ ] T004 Apply migration to local Supabase and verify tables + indexes + RLS with `supabase db push`
- [ ] T005 Create backend analytics services directory `formcraft-backend/app/services/analytics/` with `__init__.py`
- [ ] T006 [P] Create frontend analytics feature module `formcraft-frontend/src/app/features/analytics/` with routing, module, and empty component shells
- [ ] T007 [P] Add i18n translation keys for analytics module to `formcraft-frontend/src/assets/i18n/ar.json` and `en.json` — keys for all chart labels, table headers, error states, and export buttons
- [ ] T007a [P] Create SQLAlchemy model in `formcraft-backend/app/models/analytics.py` for `AnalyticsAggregationLog` entity (tracks materialized view refresh status per data-model.md)

---

## Phase 2 — Foundational (Blocking Prerequisites)

*Goal: Build shared schemas, base services, and utilities used by all user stories.*

### Independent Test Criteria
- All Pydantic schemas validate correctly against contract examples
- Base analytics service returns RLS-scoped queries
- Export utilities generate valid CSV and PNG

- [ ] T008 Create Pydantic request/response schemas in `formcraft-backend/app/schemas/analytics.py` — FieldAnalyticsResponse, OperatorAnalyticsResponse, ComplianceScorecardResponse, TemplateUsageResponse, BusiestHoursResponse, ExportRequest
- [ ] T009 [P] Create Zod-equivalent frontend models in `formcraft-frontend/src/app/features/analytics/models/analytics.model.ts`
- [ ] T010 Create base analytics service `formcraft-backend/app/services/analytics/base_analytics.py` with `apply_org_scope(query, org_id)` and `apply_branch_scope(query, branch_id)` helpers for RLS query composition
- [ ] T011 [P] Create analytics export service `formcraft-backend/app/services/analytics/export_service.py` — CSV generation (using Python csv module), PNG chart rendering (using matplotlib), PDF report generation (using WeasyPrint with RTL support)
- [ ] T012 Write contract tests in `formcraft-backend/tests/contract/test_analytics_api.py` for all endpoint schemas (response shape validation only, no business logic)
- [ ] T013 [P] Create analytics frontend service `formcraft-frontend/src/app/features/analytics/services/analytics.service.ts` with HTTP client methods for all analytics endpoints and export
- [ ] T013a [P] Extend template settings backend and frontend to support per-template telemetry toggle (FR-009) — add `telemetry_enabled` boolean to templates table (or org_settings), admin UI toggle in template editor, default disabled

---

## Phase 3 — User Story 1: Field-Level Analytics (P1)

*Goal: As an org admin, see per-field error rates, common errors, empty rates, and fill times for a selected template.*

### Independent Test Criteria
- Navigate to `/admin/analytics/fields`, select template, see table with error_rate, top_errors, empty_rate, avg_fill_time_ms
- Fields with error_rate > 20% show warning indicator
- Date range filter scopes metrics correctly

- [ ] T014 [P] [US1] Write unit tests `formcraft-backend/tests/unit/test_field_analytics_service.py` — valid aggregation computation, empty telemetry handling, date range scoping (tests will fail initially per TDD)
- [ ] T015 [US1] Create SQLAlchemy model `formcraft-backend/app/models/analytics.py` for `FieldAnalytics` entity with all fields per data-model.md (minimal model to satisfy test imports)
- [ ] T016 [US1] Implement field analytics service `formcraft-backend/app/services/analytics/field_analytics.py` — aggregate error counts, error types JSON, empty counts, avg fill time from submissions/elements; respect telemetry toggle (make T014 tests pass)
- [ ] T017 [P] [US1] Implement backend endpoint `GET /api/analytics/fields` in `formcraft-backend/app/api/routes/analytics.py` with query params template_id, from, to
- [ ] T018 [P] [US1] Create `FieldAnalyticsComponent` in `formcraft-frontend/src/app/features/analytics/components/field-analytics/` with Angular Material table, warning indicators for >20% error rate, date range picker
- [ ] T019 [US1] Add field analytics route `/admin/analytics/fields` to `formcraft-frontend/src/app/features/analytics/analytics-routing.module.ts`
- [ ] T020 [P] [US1] Wire up frontend component to analytics service, bind table data, implement warning highlighting and top 3 error display

---

## Phase 4 — User Story 2: Operator Performance Analytics (P2)

*Goal: As an org admin, see per-operator metrics and busiest hours heatmap.*

### Independent Test Criteria
- Navigate to `/admin/analytics/operators`, see table with forms_filled, avg_fill_time, error_rate, coaching_flag
- Coaching indicator appears for operators with significantly higher error rate than org average
- Busiest hours heatmap renders by hour and day of week

- [ ] T021 [P] [US2] Write unit tests `formcraft-backend/tests/unit/test_operator_analytics_service.py` — productivity aggregation, coaching flag logic (significantly above org average), busiest hours heatmap computation (tests will fail initially per TDD)
- [ ] T022 [US2] Create SQLAlchemy model in `formcraft-backend/app/models/analytics.py` for `OperatorAnalytics` entity (minimal model to satisfy test imports)
- [ ] T023 [US2] Implement operator analytics service `formcraft-backend/app/services/analytics/operator_analytics.py` — forms filled per period, avg fill time, error rate, coaching flag (significantly above org average), busiest_hours JSON aggregation (make T021 tests pass)
- [ ] T024 [P] [US2] Implement backend endpoints `GET /api/analytics/operators` and `GET /api/analytics/operators/busiest-hours` in `formcraft-backend/app/api/routes/analytics.py`
- [ ] T025 [P] [US2] Create `OperatorAnalyticsComponent` in `formcraft-frontend/src/app/features/analytics/components/operator-analytics/` with Angular Material table, coaching badge, period_type selector
- [ ] T026 [P] [US2] Create `BusiestHoursComponent` in `formcraft-frontend/src/app/features/analytics/components/operator-analytics/busiest-hours/` with Chart.js heatmap visualization
- [ ] T027 [US2] Add operator analytics route `/admin/analytics/operators` to analytics routing module
- [ ] T028 [P] [US2] Wire up frontend components to analytics service, bind table data, implement coaching flag conditional styling

---

## Phase 5 — User Story 3: Compliance Analytics (P3)

*Goal: As an org admin, see compliance scorecards and drill into non-compliant templates.*

### Independent Test Criteria
- Navigate to `/admin/analytics/compliance`, see scorecards with validator_coverage_pct, bilingual_label_pct, quality_score_avg
- Click non-compliant count to see list of templates and missing validators/labels
- Customer data access spike alert displays when detected

- [ ] T029 [P] [US3] Write unit tests `formcraft-backend/tests/unit/test_compliance_analytics_service.py` — validator coverage calculation, bilingual label detection, quality score weighted formula, cache hit/miss logic (tests will fail initially per TDD)
- [ ] T030 [US3] Create SQLAlchemy model in `formcraft-backend/app/models/analytics.py` for `ComplianceScorecardCache` entity (minimal model to satisfy test imports)
- [ ] T031 [US3] Implement compliance analytics service `formcraft-backend/app/services/analytics/compliance_analytics.py` — compute validator coverage (40%), bilingual labels (30%), template structure completeness (30%); cache results in `compliance_scorecard_cache` with 24h TTL; detect audit_log access spikes (make T029 tests pass)
- [ ] T032 [P] [US3] Implement backend endpoints `GET /api/analytics/compliance` and `GET /api/analytics/compliance/templates-needing-attention` in `formcraft-backend/app/api/routes/analytics.py`
- [ ] T033 [P] [US3] Create `ComplianceAnalyticsComponent` in `formcraft-frontend/src/app/features/analytics/components/compliance-analytics/` with Angular Material cards for scorecards, drill-down list for non-compliant templates
- [ ] T034 [US3] Add compliance analytics route `/admin/analytics/compliance` to analytics routing module
- [ ] T035 [P] [US3] Wire up frontend component to analytics service, bind scorecard data, implement drill-down navigation and spike alert banner

---

## Phase 6 — User Story 4: Enhanced Template Usage Analytics (P4)

*Goal: As an org admin, see template completion funnel, version adoption, and department/branch breakdown.*

### Independent Test Criteria
- Navigate to `/admin/analytics/templates`, select template, see funnel chart (started → draft → submitted → printed)
- Version adoption chart shows percentage per version over time
- Department grouping breaks down usage by department

- [ ] T036 [P] [US4] Write unit tests `formcraft-backend/tests/unit/test_template_analytics_service.py` — funnel conversion rate accuracy, version adoption timeline correctness, department grouping (tests will fail initially per TDD)
- [ ] T037 [US4] Implement template usage analytics service `formcraft-backend/app/services/analytics/template_analytics.py` — query `mv_template_usage_funnel` for funnel data; compute conversion rates; version adoption from submissions table; department/branch breakdown with group_by support (make T036 tests pass)
- [ ] T038 [P] [US4] Implement backend endpoints `GET /api/analytics/templates/usage` and `GET /api/analytics/templates/version-adoption` in `formcraft-backend/app/api/routes/analytics.py`
- [ ] T039 [P] [US4] Create `TemplateUsageAnalyticsComponent` in `formcraft-frontend/src/app/features/analytics/components/template-usage-analytics/` with Chart.js funnel chart (stacked bar), version adoption line chart, department comparison table
- [ ] T040 [US4] Add template usage analytics route `/admin/analytics/templates` to analytics routing module
- [ ] T041 [P] [US4] Wire up frontend component to analytics service, bind funnel data, implement group_by selector (none / department / branch)

---

## Phase 7 — Polish & Cross-Cutting Concerns

*Goal: Export functionality, materialized view refresh automation, integration tests, performance validation, and final QA.*

### Independent Test Criteria
- All four analytics views support CSV/PNG/PDF export
- Materialized view refresh runs every 15 minutes without blocking reads
- `ruff check .` passes on all modified Python files
- All contract tests pass

- [ ] T042 Implement export endpoint `POST /api/analytics/export` in `formcraft-backend/app/api/routes/analytics.py` — delegate to export_service with format validation, return signed Supabase Storage URL
- [ ] T043 [P] Create `ExportDialogComponent` in `formcraft-frontend/src/app/features/analytics/components/export-dialog/` with format selector (CSV/PNG/PDF), date range, and download trigger
- [ ] T044 [P] Add export button to all four analytics views (field, operator, compliance, template usage) invoking the export dialog
- [ ] T045 Create scheduled refresh function `formcraft-backend/app/services/analytics/refresh_scheduler.py` — refresh `mv_template_usage_funnel` every 15 minutes, log to `analytics_aggregation_log`, emit structured metrics
- [ ] T046 [P] Write integration tests `formcraft-backend/tests/integration/test_analytics_flow.py` — end-to-end: create submission → trigger aggregation → verify field analytics response → verify operator analytics → verify compliance scorecard → verify template funnel
- [ ] T047 [P] Create `AnalyticsDashboardComponent` in `formcraft-frontend/src/app/features/analytics/components/analytics-dashboard/` with navigation tabs to all four analytics sub-views
- [ ] T048 Add analytics module lazy-loaded route `/admin/analytics` to main app routing
- [ ] T049 Run `ruff check .` on all modified Python files and fix all reported issues
- [ ] T050 Run contract tests `pytest formcraft-backend/tests/contract/test_analytics_api.py` and ensure all pass
- [ ] T051 Run quickstart.md smoke tests (all 6 API tests) and document any gaps
- [ ] T051a [P] Add Prometheus histogram instrumentation to all analytics endpoints in `formcraft-backend/app/api/routes/analytics.py` — buckets [0.5s, 1s, 2s, 5s, 10s] per NFR-006

---

## Parallel Execution Examples

### Within Phase 1 (all parallel after T001)
```text
T001 → T002, T003, T005, T006, T007 (all [P])
T004 (after T001-T003)
```

### Within Phase 2 (all parallel after T008)
```text
T008 → T009, T010, T011, T012, T013 (all [P])
```

### Within Phase 3 (US1)
```text
T014 → T015, T016 (parallel)
T016 → T017, T018 (parallel)
T017, T018, T019 → T020 (wire-up)
```

### Within Phase 4 (US2)
```text
T021 → T022, T023 (parallel)
T023 → T024, T025, T026 (parallel)
T024, T025, T026, T027 → T028 (wire-up)
```

### Within Phase 5 (US3)
```text
T029 → T030, T031 (parallel)
T031 → T032, T033 (parallel)
T032, T033, T034 → T035 (wire-up)
```

### Within Phase 6 (US4)
```text
T036 → T037, T038 (parallel)
T038, T039 → T040, T041 (wire-up)
```

### Within Phase 7 (Polish)
```text
T042, T045 → T043, T044, T046, T047, T048 (all [P])
T049, T050, T051 (sequential QA)
```

---

## Implementation Strategy

**MVP First**: Deploy Phase 1 + Phase 2 + Phase 3 (Field-Level Analytics only) as the initial release. This provides the highest-value feature (P1) with the least risk.

**Incremental Delivery**:
- Sprint 1: Phase 1 + Phase 2 + Phase 3 (US1)
- Sprint 2: Phase 4 (US2) + Phase 5 (US3)
- Sprint 3: Phase 6 (US4) + Phase 7 (Polish)

**Parallel Opportunities**: Each user story phase can be developed in parallel after foundational phase is complete, since each story targets a distinct analytics domain with minimal shared state.

**Testing Strategy**: Contract tests validate API shapes (T012). Unit tests cover aggregation logic (T015, T022, T030, T037). Integration tests verify end-to-end data flow (T046). Manual smoke tests follow quickstart.md scenarios.

---

## Task Count Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| Phase 1 — Setup | 7 | Migration, RLS, views, directories, i18n |
| Phase 2 — Foundational | 6 | Schemas, base services, export, contract tests |
| Phase 3 — US1 Field-Level | 7 | Backend services, endpoints, frontend table, warnings |
| Phase 4 — US2 Operator | 8 | Backend services, endpoints, coaching, heatmap |
| Phase 5 — US3 Compliance | 7 | Scorecards, cache, drill-down, alerts |
| Phase 6 — US4 Template Usage | 6 | Funnel, version adoption, department breakdown |
| Phase 7 — Polish | 10 | Export, refresh scheduler, integration tests, QA |
| **Total** | **51** | |
