# Tasks: Analytics & Reporting Dashboard

**Input**: Design documents from `formcraft-specs/specs/027-analytics-reporting/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Backend and frontend scaffolding for the analytics feature

- [ ] T001 Create Pydantic response schemas for all analytics endpoints in `formcraft-backend/app/schemas/analytics.py` — include SubmissionVolumeResponse, BranchBreakdownItem, TemplateUsageItem, OperatorProductivityItem, TransactionRegisterItem, OperatorStatsResponse, and shared DateRangeParams per data-model.md
- [ ] T002 [P] Create analytics Angular feature module with routing in `formcraft-frontend/src/app/features/admin/analytics/analytics.module.ts` and `analytics-routing.module.ts` — register lazy-loaded route `/admin/analytics`
- [ ] T003 [P] Create analytics TypeScript interfaces in `formcraft-frontend/src/app/shared/models/analytics.models.ts` — mirror backend response schemas
- [ ] T004 [P] Install ng2-charts and chart.js dependencies in `formcraft-frontend/` — add to package.json, import NgChartsModule in analytics module
- [ ] T005 Create analytics API service in `formcraft-frontend/src/app/features/admin/analytics/services/analytics.service.ts` — methods for each endpoint per contracts/analytics-api.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Backend service with shared query logic, date handling, and role-based scoping

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create analytics service in `formcraft-backend/app/services/analytics_service.py` — implement `AnalyticsService` class with constructor taking supabase client, helper methods: `_build_date_range(preset, date_from, date_to)` returning (start, end, previous_start, previous_end) per research.md R6, `_apply_role_scope(query, user)` per research.md R5 (org_admin→`WHERE org_id = :org_id`, branch_manager→join submissions.branch_id → branches.department_id to match user's department_id since submissions lacks department_id directly, operator→`WHERE operator_id = :user_id`)
- [ ] T007 Create analytics routes file in `formcraft-backend/app/api/routes/analytics.py` — register APIRouter with prefix `/analytics` and tags `["Analytics"]`, add to app router in `formcraft-backend/app/api/routes/__init__.py`
- [ ] T008 [P] Add recommended composite indexes via migration `formcraft-backend/migrations/029_analytics_indexes.sql` — `idx_submissions_org_created(org_id, created_at)` and `idx_submissions_branch_created(branch_id, created_at)` per data-model.md
- [ ] T009 [P] Create shared date-range-picker component in `formcraft-frontend/src/app/features/admin/analytics/components/date-range-picker/` — Angular Material datepicker with preset buttons (Today, This Week, This Month, This Quarter, This Year, Last 7 Days, Last 30 Days, Custom), emits `{preset, dateFrom, dateTo}`, i18n labels (AR/EN)

**Checkpoint**: Foundation ready — analytics service with scoping + date handling, routes registered, frontend module scaffolded

---

## Phase 3: User Story 1 — Submission Volume Dashboard (Priority: P1) MVP

**Goal**: Org Admin sees submission KPIs, trend chart, and branch breakdown on `/admin/analytics`

**Independent Test**: Create submissions across branches, verify dashboard shows correct totals, trends, and breakdowns with role scoping

### Implementation

- [ ] T010 [US1] Implement `get_overview()` method in `formcraft-backend/app/services/analytics_service.py` — query submissions with date_trunc grouping, compute total/previous_total/change_pct/daily_trend/by_status, apply role scoping
- [ ] T011 [US1] Implement `get_branch_breakdown()` method in `formcraft-backend/app/services/analytics_service.py` — join submissions with branches, group by branch, compute totals and pct_of_org
- [ ] T012 [US1] Add GET `/api/analytics/overview` endpoint in `formcraft-backend/app/api/routes/analytics.py` — parse DateRangeParams, call service, return SubmissionVolumeResponse
- [ ] T013 [US1] Add GET `/api/analytics/by-branch` endpoint in `formcraft-backend/app/api/routes/analytics.py` — parse DateRangeParams, call service, return branch breakdown
- [ ] T014 [US1] Create analytics-dashboard component in `formcraft-frontend/src/app/features/admin/analytics/components/analytics-dashboard/` — KPI cards (total, change %, by status), trend line chart (current vs previous period using ng2-charts), branch breakdown table with sorting, date-range-picker integration, empty state per FR-016, i18n labels
- [ ] T015 [US1] Add audit logging for analytics access — log `ANALYTICS_VIEWED` event in overview endpoint using existing AuditLogger

**Checkpoint**: MVP complete — Org Admin can view submission trends, branch breakdown, with role scoping and date filtering

---

## Phase 4: User Story 2 — Template Usage Analytics (Priority: P2)

**Goal**: Org Admin sees template usage rankings and version adoption curves

**Independent Test**: Create templates with varying submission counts, verify rankings and version timeline

### Implementation

- [ ] T016 [US2] Implement `get_template_usage()` method in `formcraft-backend/app/services/analytics_service.py` — join submissions with templates, group by template, rank by fill_count, handle deleted templates (is_deleted flag)
- [ ] T017 [US2] Implement `get_template_versions()` method in `formcraft-backend/app/services/analytics_service.py` — for a specific template_id, group submissions by (template_version, date_trunc('day', created_at)), compute first_used/last_used/total per version AND daily_counts time-series per version to power the adoption timeline chart (FR-005: "when operators transitioned between versions")
- [ ] T018 [US2] Add GET `/api/analytics/templates` endpoint in `formcraft-backend/app/api/routes/analytics.py` — parse DateRangeParams + limit, return TemplateUsageItem list
- [ ] T019 [US2] Add GET `/api/analytics/template-versions/{template_id}` endpoint in `formcraft-backend/app/api/routes/analytics.py` — return version adoption data
- [ ] T020 [US2] Create template-analytics component in `formcraft-frontend/src/app/features/admin/analytics/components/template-analytics/` — ranked list with bar chart, click-through to version adoption timeline, date-range-picker, deleted template label, i18n

**Checkpoint**: Template analytics fully functional — rankings + version adoption

---

## Phase 5: User Story 3 — Operator Productivity Report (Priority: P2)

**Goal**: Branch Manager/Org Admin sees per-operator submission counts with daily granularity

**Independent Test**: Create submissions from multiple operators, verify productivity table and daily breakdown

### Implementation

- [ ] T021 [US3] Implement `get_operator_productivity()` method in `formcraft-backend/app/services/analytics_service.py` — join submissions with profiles, group by operator, compute total and daily_counts, apply branch_id filter if provided
- [ ] T022 [US3] Add GET `/api/analytics/operators` endpoint in `formcraft-backend/app/api/routes/analytics.py` — parse DateRangeParams + optional branch_id, return OperatorProductivityItem list
- [ ] T023 [US3] Create operator-productivity component in `formcraft-frontend/src/app/features/admin/analytics/components/operator-productivity/` — table with operator name, email, branch, total, daily breakdown, sortable columns, branch filter dropdown (Org Admin only), date-range-picker, i18n

**Checkpoint**: Operator productivity report functional — per-operator metrics with scoping

---

## Phase 6: User Story 4 — Branch Comparison Report (Priority: P3)

**Goal**: Org Admin compares branch performance side-by-side

**Independent Test**: Create submissions across branches, verify comparison table and chart

### Implementation

- [ ] T024 [US4] Implement `get_branch_comparison()` method in `formcraft-backend/app/services/analytics_service.py` — for each branch: total_submissions, active_operators (distinct operator_id count), top_template, previous_total, change_pct; support optional branch_ids filter (max 5)
- [ ] T025 [US4] Add GET `/api/analytics/branch-comparison` endpoint in `formcraft-backend/app/api/routes/analytics.py` — parse DateRangeParams + optional branch_ids (comma-separated), return comparison data
- [ ] T026 [US4] Create branch-comparison component in `formcraft-frontend/src/app/features/admin/analytics/components/branch-comparison/` — table with all branches, selectable branch pairs for side-by-side trend chart, date-range-picker, i18n

**Checkpoint**: Branch comparison functional — side-by-side metrics and trend charts

---

## Phase 7: User Story 5 — Report Export (Priority: P3)

**Goal**: Export any analytics view as CSV or PDF

**Independent Test**: Load analytics view, export CSV and PDF, verify content matches filtered display

### Implementation

- [ ] T027 [US5] Implement `export_csv()` method in `formcraft-backend/app/services/analytics_service.py` — accept view name + filters, query data, format as CSV with UTF-8 BOM prefix per research.md R4, Arabic column headers based on Accept-Language
- [ ] T028 [US5] Implement `export_pdf()` method in `formcraft-backend/app/services/analytics_service.py` — accept view name + filters + optional chart_image_base64, render HTML report template via WeasyPrint, include chart image and summary table
- [ ] T029 [P] [US5] Create PDF report HTML templates in `formcraft-backend/app/services/pdf/templates/analytics/` — overview.html, templates.html, operators.html, transactions.html — styled for A4, RTL-aware, org logo header
- [ ] T030 [US5] Add GET `/api/analytics/export` endpoint in `formcraft-backend/app/api/routes/analytics.py` — view param + date filters, return CSV with Content-Disposition attachment header
- [ ] T031 [US5] Add POST `/api/analytics/export-pdf` endpoint in `formcraft-backend/app/api/routes/analytics.py` — accept body with view, filters, chart_image_base64, return PDF stream
- [ ] T032 [US5] Create report-export component in `formcraft-frontend/src/app/features/admin/analytics/components/report-export/` — export button dropdown (CSV/PDF), on PDF export: capture chart canvas as base64 PNG via Chart.js toBase64Image(), send to backend, trigger download
- [ ] T033 [US5] Add audit logging for exports — log `ANALYTICS_EXPORTED` with view name, format, and date range

**Checkpoint**: Export functional — CSV with Arabic support, PDF with embedded charts

---

## Phase 8: User Story 6 — Transaction Register (Priority: P3)

**Goal**: Paginated, filterable listing of all submissions for reconciliation

**Independent Test**: Create submissions with various templates/operators, verify filtering, sorting, pagination, and export

### Implementation

- [ ] T034 [US6] Implement `get_transactions()` method in `formcraft-backend/app/services/analytics_service.py` — join submissions+templates+profiles+branches, apply all filters (template_id, operator_id, branch_id, status, search on reference_number), paginate, sort, return items + total count
- [ ] T035 [US6] Add GET `/api/analytics/transactions` endpoint in `formcraft-backend/app/api/routes/analytics.py` — parse all query params per contract, return paginated TransactionRegisterItem list
- [ ] T036 [US6] Create transaction-register component in `formcraft-frontend/src/app/features/admin/analytics/components/transaction-register/` — Angular Material table with columns (ref#, template, operator, branch, status, date), filter bar (template dropdown, operator dropdown, branch dropdown, status select, search input), pagination (mat-paginator), sort headers, export button integration, i18n, empty state

**Checkpoint**: Transaction register functional — full CRUD-less operational ledger

---

## Phase 9: Operator Stats Widget (Form Desk)

**Goal**: Operators see their own stats widget on the Form Desk dashboard

**Independent Test**: Log in as operator, verify My Stats card shows correct counts and trend

### Implementation

- [ ] T037 Implement `get_operator_stats()` method in `formcraft-backend/app/services/analytics_service.py` — query own submissions for today/this_week/this_month counts + last 7 days daily trend, scoped to authenticated user only
- [ ] T038 Add GET `/api/desk/my-stats` endpoint in `formcraft-backend/app/api/routes/desk.py` — call analytics service, return OperatorStatsResponse per contracts/operator-stats-api.md
- [ ] T039 Create operator-stats-widget component in `formcraft-frontend/src/app/features/desk/components/operator-stats-widget/` — compact card with today/week/month KPI numbers, mini sparkline chart (last 7 days via ng2-charts line chart, no axes, minimal), i18n labels
- [ ] T040 Integrate operator-stats-widget into Form Desk dashboard in `formcraft-frontend/src/app/features/desk/` — add widget to desk dashboard layout, call my-stats API on init

**Checkpoint**: Operator widget live on Form Desk

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup, route guards, and navigation integration

- [ ] T041 [P] Add analytics route to admin sidebar navigation in `formcraft-frontend/src/app/features/admin/` — add "Analytics" menu item with chart icon, i18n label, route to `/admin/analytics`
- [ ] T042 [P] Add route guard for analytics — restrict `/admin/analytics` to org_admin and branch_manager roles in admin routing module
- [ ] T043 Wire analytics dashboard tabs — add tab navigation in analytics-dashboard component to switch between: Overview (US1), Templates (US2), Operators (US3), Branches (US4), Transactions (US6), with lazy rendering
- [ ] T044 [P] Add loading states — skeleton loaders for KPI cards, chart placeholders, table shimmer in all analytics components
- [ ] T045 [P] Add error handling — display user-friendly error messages when analytics API calls fail, retry button
- [ ] T046 Run migration 029 on Supabase Cloud — apply analytics indexes
- [ ] T047 [P] NFR performance validation — verify NFR-001 (dashboard loads < 3s with 100K submissions), NFR-002 (CSV export of 50K rows < 10s), NFR-003 (PDF generation < 15s) by running timed queries against a representative dataset and logging results
- [ ] T048 [P] NFR security validation — verify NFR-004 (multi-tenant isolation) by testing all analytics endpoints with users from different orgs, confirming zero cross-org data leakage; test branch_manager scoping returns only department branches; test operator scoping returns only own submissions
- [ ] T049 End-to-end validation — test all 10 quickstart.md scenarios manually, verify role scoping, date filtering, export, bilingual display

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on T001 (schemas) — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 completion — MVP
- **US2 (Phase 4)**: Depends on Phase 2 — independent of US1
- **US3 (Phase 5)**: Depends on Phase 2 — independent of US1/US2
- **US4 (Phase 6)**: Depends on Phase 2 — independent of US1/US2/US3
- **US5 (Phase 7)**: Depends on Phase 2 + at least one view story (US1) — needs data to export
- **US6 (Phase 8)**: Depends on Phase 2 — independent of other stories
- **Operator Widget (Phase 9)**: Depends on T006 (service) — independent of admin views
- **Polish (Phase 10)**: Depends on all story phases

### User Story Dependencies

- **US1 (P1)**: Foundation only → MVP
- **US2 (P2)**: Foundation only → can parallel with US1
- **US3 (P2)**: Foundation only → can parallel with US1/US2
- **US4 (P3)**: Foundation only → can parallel
- **US5 (P3)**: Foundation + US1 minimum (needs a view to export from)
- **US6 (P3)**: Foundation only → can parallel
- **Operator Widget**: Foundation only → can parallel with all admin stories

### Within Each User Story

- Backend service method → backend endpoint → frontend component
- All marked [P] within a story can run in parallel

### Parallel Opportunities

- T002, T003, T004 can run in parallel (Setup phase)
- T008, T009 can run in parallel (Foundational phase)
- US1 through US4 + US6 + Operator Widget can all start in parallel after Foundation
- T029 (PDF templates) can run in parallel with other US5 tasks
- T041, T042, T044, T045 can run in parallel (Polish phase)

---

## Parallel Example: User Story 1

```text
# After Foundation complete, launch backend tasks:
T010: get_overview() in analytics_service.py
T011: get_branch_breakdown() in analytics_service.py
# Then endpoints (depend on service methods):
T012: GET /api/analytics/overview
T013: GET /api/analytics/by-branch
# Then frontend (depends on endpoints):
T014: analytics-dashboard component
# Then audit (independent):
T015: audit logging
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T005)
2. Complete Phase 2: Foundational (T006–T009)
3. Complete Phase 3: User Story 1 (T010–T015)
4. **STOP and VALIDATE**: Test submission volume dashboard independently
5. Deploy/demo — admins can see submission trends immediately

### Incremental Delivery

1. Setup + Foundation → scaffolding ready
2. US1 → Submission volume dashboard (MVP!)
3. US2 + US3 → Template + operator analytics (parallel)
4. US4 + US6 → Branch comparison + transaction register (parallel)
5. US5 → Export (needs at least US1 views)
6. Operator Widget → Form Desk integration
7. Polish → navigation, guards, loading states, validation

### Parallel Team Strategy

With 3 developers after Foundation:
- Dev A: US1 (MVP) → US5 (Export)
- Dev B: US2 (Templates) → US4 (Branches) → Polish
- Dev C: US3 (Operators) → US6 (Transactions) → Operator Widget

---

## Notes

- No new database tables — all analytics computed live from existing submissions/templates/profiles
- Migration 029 only adds composite indexes for performance
- All endpoints behind auth + role scoping
- UTF-8 BOM for CSV Arabic compatibility
- Chart.js canvas → base64 PNG for PDF embedding
- Commit after each task or logical group
