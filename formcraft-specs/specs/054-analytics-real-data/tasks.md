# Tasks: New-Theme Admin Console Analytics — Real Data Integration

**Feature**: 054-analytics-real-data
**Branch**: `054-analytics-real-data`
**Input**: plan.md · spec.md · data-model.md · contracts/dashboard-api.md · research.md · quickstart.md

## Format: `[ID] [P?] [Story?] Description — file path`

- **[P]**: Parallelisable (different files, no dependency on incomplete peer tasks)
- **[Story]**: User story label — [US1]…[US7] maps to spec.md user stories
- Constitution V (TDD): contract tests written and verified failing **before** each service/route task

---

## Phase 1: Setup

**Purpose**: Verify branch, skeleton files, and shared test fixtures exist before any implementation.

- [x] T001 Verify branch `054-analytics-real-data` is checked out and `SPECIFY_FEATURE=054-analytics-real-data` is set in the shell
- [x] T002 Create empty skeleton file `formcraft-backend/app/services/analytics/dashboard_analytics.py` with module docstring and `DashboardAnalyticsService` class stub (no methods yet)
- [x] T003 Create empty contract test file `formcraft-backend/tests/integration/test_dashboard_analytics_routes.py` with imports, auth fixtures reused from existing integration tests, and four empty test functions (one per endpoint)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared Pydantic schemas, TypeScript interfaces, and backend utility that every user story depends on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T004 [P] Add 7 new Pydantic models to `formcraft-backend/app/schemas/analytics.py`: `DashboardSummaryResponse`, `TimeSeriesPoint`, `SubmissionsOverTimeResponse`, `DepartmentShareItem`, `DepartmentDistributionResponse`, `TopTemplateItem`, `TopTemplatesResponse` — field shapes as documented in `data-model.md`
- [x] T005 [P] Add `_period_to_dates(period: str) -> tuple[date, date, date, date]` helper to `formcraft-backend/app/services/analytics/base_analytics.py` — returns `(current_from, current_to, prev_from, prev_to)` per the period-to-date logic in `research.md` Decision 8
- [x] T006 [P] Add 8 new TypeScript interfaces to `formcraft-frontend/src/app/features/analytics/models/analytics.model.ts`: `DashboardFilter`, `DashboardSummaryResponse`, `TimeSeriesPoint`, `SubmissionsOverTimeResponse`, `DepartmentShareItem`, `DepartmentDistributionResponse`, `TopTemplateItem`, `TopTemplatesResponse` — shapes as in `data-model.md`
- [x] T007 Add `TTLCache` import and class-level `_cache: TTLCache` attribute (size 1024, ttl 300) to `DashboardAnalyticsService` in `formcraft-backend/app/services/analytics/dashboard_analytics.py`; add `_cache_key(org_id, period, department_id, branch_id) -> tuple` private method
- [x] T008 Register the four new dashboard routes on the existing analytics router in `formcraft-backend/app/api/routes/analytics.py` — add `router.get("/dashboard/summary")`, `router.get("/dashboard/submissions-over-time")`, `router.get("/dashboard/department-distribution")`, `router.get("/dashboard/top-templates")` stubs that return HTTP 501 (not-yet-implemented) so the router is discoverable immediately

**Checkpoint**: `pytest tests/integration/test_dashboard_analytics_routes.py` runs (all 4 test functions exist); `ng build --dry-run` compiles with no type errors on new interfaces.

---

## Phase 3: User Story 1 — Live KPI Cards (Priority: P1) 🎯 MVP

**Goal**: The four KPI cards on the analytics page display real org-scoped data with accurate deltas instead of hardcoded values.

**Independent Test**: Navigate to `/ui/admin/analytics`; submit one additional form in the org; reload — "Total forms filled" increments by 1. The `deltaPct`, `activeTemplates`, `totalTemplates`, `avgFillTimeMs`, `uniqueCustomers`, and `newCustomersThisWeek` fields all match a direct Supabase query for the same period.

### Contract Tests for US1 (write first — must FAIL before T012)

- [x] T009 [US1] Write contract test `test_summary_returns_200_for_admin` in `formcraft-backend/tests/integration/test_dashboard_analytics_routes.py` — asserts response shape matches `DashboardSummaryResponse` fields; run `pytest -k test_summary` and confirm it **fails** (501)
- [x] T010 [US1] Write contract test `test_summary_requires_admin_role` in same file — asserts 401 for no auth, 403 for operator-role JWT; run and confirm **fails**

### Implementation for US1 (backend)

- [x] T011 [US1] Implement `DashboardAnalyticsService.get_summary(org_id, period, department_id, branch_id)` in `formcraft-backend/app/services/analytics/dashboard_analytics.py`:
  - Call `_period_to_dates(period)` for current and previous windows
  - Query `submissions` table for `COUNT(*)` filtered by `org_id`, `created_at` range, optional `department_id`, optional `branch_id`
  - Query `submissions` for `COUNT(DISTINCT customer_id)` (current period) and first-submission-this-week count
  - Query `templates` for `COUNT(*) WHERE org_id = ? AND status = 'published'` and total count
  - Compute `delta_pct`, `fill_time_delta_pct` (null-safe)
  - Store result in `_cache` keyed by `_cache_key(...)`; return cached result on hit
- [x] T012 [US1] Wire `GET /api/analytics/dashboard/summary` route in `formcraft-backend/app/api/routes/analytics.py` to `DashboardAnalyticsService.get_summary()`; apply `Depends(require_role(Role.ADMIN))` and `Depends(get_current_user)`; replace the 501 stub
- [x] T013 [US1] Run `pytest -k test_summary` — both T009 and T010 tests must now **pass**

### Implementation for US1 (frontend)

- [ ] T014 [US1] Add `getDashboardSummary(filter: DashboardFilter): Observable<DashboardSummaryResponse>` to `formcraft-frontend/src/app/features/analytics/services/analytics.service.ts` — maps `DashboardFilter` to query params `period`, `department_id?`, `branch_id?`; calls `GET /api/analytics/dashboard/summary`
- [ ] T015 [US1] Replace the `AnalyticsComponent` class body in `formcraft-frontend/src/app/features/ui-redesign/admin/analytics.component.ts`:
  - Add `filter: DashboardFilter = { period: '30d' }` property
  - Add `summary: DashboardSummaryResponse | null = null` property
  - Add `loadingStates` and `errorStates` objects (one boolean per widget: `summary`, `timeSeries`, `distribution`, `topTemplates`, `operators`)
  - Add `loadAllWidgets()` method skeleton (initially only calls `getDashboardSummary`)
  - Call `loadAllWidgets()` in `ngOnInit()`
  - Inject `AnalyticsService` via constructor
  - Keep `formatValue()` helper; add `formatMsToTime(ms: number | null): string` helper (returns "M:SS" or "–")
- [ ] T016 [US1] Bind KPI cards in `formcraft-frontend/src/app/features/ui-redesign/admin/analytics.component.html`:
  - Replace hardcoded `value="٧,٢٨٤"` → bind `[value]="formatValue(summary?.totalFormsFilled)"` (and similar for all 4 cards)
  - Replace hardcoded `delta="+18.4% ..."` → bind computed delta string from `summary?.deltaPct`
  - Replace hardcoded `value="١٢ / ٤٧"` → bind `"{{ summary?.activeTemplates }} / {{ summary?.totalTemplates }}"`
  - Replace hardcoded `value="٣:٤٢"` → bind `formatMsToTime(summary?.avgFillTimeMs)`
  - Replace hardcoded `value="٢,٨٤١"` → bind `formatValue(summary?.uniqueCustomers)`
  - Add `*ngIf="!loadingStates.summary && !errorStates.summary"` guard on the KPI grid wrapper (skeleton and error are wired in US7)
- [ ] T017 [US1] Manually verify at `http://localhost:4200/ui/admin/analytics` that KPI cards show real numbers; confirm `/api/analytics/dashboard/summary` appears in DevTools Network tab

**Checkpoint**: All four KPI cards display live values. T009 and T010 pass. No hardcoded KPI numbers remain in the component.

---

## Phase 4: User Story 2 — Submissions-Over-Time Line Chart (Priority: P1)

**Goal**: The trend line chart renders bars proportional to real daily (or monthly) submission counts and highlights the actual peak value and date. Period toggles (7d/30d/90d/yearly) reload the chart with correct granularity.

**Independent Test**: Switch from 30-day to 7-day — chart shows exactly 7 bars, peak overlay shows a real date/count different from the hardcoded "١٢٤ — ٢٥ مايو". Switch to yearly — 12 bars appear.

### Contract Test for US2 (write first — must FAIL before T021)

- [x] T018 [US2] Write contract tests `test_time_series_daily_granularity` and `test_time_series_monthly_granularity` in `formcraft-backend/tests/integration/test_dashboard_analytics_routes.py` — assert `granularity` field equals `"daily"` for `period=30d` and `"monthly"` for `period=yearly`; assert `len(points)` matches expected day/month count; run and confirm **fails** (501)

### Implementation for US2 (backend)

- [x] T019 [US2] Implement `DashboardAnalyticsService.get_submissions_over_time(org_id, period, department_id, branch_id)` in `formcraft-backend/app/services/analytics/dashboard_analytics.py`:
  - Call `_period_to_dates(period)` for `current_from`, `current_to`
  - Query `submissions` for `created_at` within range (filtered by org/dept/branch)
  - Group by `date(created_at)` for daily; by `date_trunc('month', created_at)` for yearly
  - Zero-fill missing days/months to produce a continuous series
  - Identify `peak_date` and `peak_count`; set `granularity = 'monthly' if period == 'yearly' else 'daily'`
  - Cache result; return `SubmissionsOverTimeResponse`
- [x] T020 [US2] Wire `GET /api/analytics/dashboard/submissions-over-time` route in `formcraft-backend/app/api/routes/analytics.py`; replace 501 stub; apply admin dep
- [x] T021 [US2] Run `pytest -k test_time_series` — T018 tests must now **pass**

### Implementation for US2 (frontend)

- [x] T022 [US2] Add `getSubmissionsOverTime(filter: DashboardFilter): Observable<SubmissionsOverTimeResponse>` to `formcraft-frontend/src/app/features/analytics/services/analytics.service.ts`
- [x] T023 [US2] Extend `AnalyticsComponent` in `formcraft-frontend/src/app/features/ui-redesign/admin/analytics.component.ts`:
  - Add `timeSeries: SubmissionsOverTimeResponse | null = null` property
  - Add `get lineData(): number[]` computed getter — maps `timeSeries?.points.map(p => p.count) ?? []`
  - Add `get lineMax(): number` — returns `timeSeries?.peakCount || 1`
  - Add `get peakLabel(): string` — formats `timeSeries?.peakCount` + `timeSeries?.peakDate` in Arabic locale
  - Add `activePeriod: '7d' | '30d' | '90d' | 'yearly' = '30d'` property
  - Add `setPeriod(p: DashboardFilter['period'])` method — updates `filter.period` + calls `loadAllWidgets()`
  - Include `getSubmissionsOverTime` call in `loadAllWidgets()`
- [x] T024 [US2] Bind line chart in `formcraft-frontend/src/app/features/ui-redesign/admin/analytics.component.html`:
  - Replace hardcoded `lineData = [42, 58, ...]` — `*ngFor` already uses `lineData` (getter now returns real data)
  - Replace hardcoded `lineMax = 130` — `lineMax` getter returns real peak
  - Replace hardcoded overlay `<span class="chart-highlight">١٢٤</span>` → `{{ formatValue(timeSeries?.peakCount) }}`
  - Replace hardcoded `<span class="chart-date">٢٥ مايو</span>` → `{{ peakLabel }}`
  - Add `(click)="setPeriod('7d')"` etc. on the four period toggle buttons; bind `[class.active]="activePeriod === '7d'"` etc.
- [x] T025 [US2] Manually verify period toggles reload the chart and peak label updates correctly; confirm chart shows 12 bars on yearly view

**Checkpoint**: Line chart and period toggles fully functional. T018 passes. No hardcoded `lineData` array or `lineMax` literal in component.

---

## Phase 5: User Story 3 — Department Donut Chart (Priority: P2)

**Goal**: The donut chart segments and legend percentages reflect real department distribution from the database.

**Independent Test**: Create submissions in exactly two departments (60% / 40%); confirm the two donut legend values show approximately 60% and 40%.

### Contract Test for US3 (write first — must FAIL before T028)

- [x] T026 [US3] Write contract test `test_department_distribution_shape` in `formcraft-backend/tests/integration/test_dashboard_analytics_routes.py` — asserts `departments` is a list, each item has `department_id`, `department_name`, `count`, `percentage`; percentages sum to ~100 (±0.5 tolerance); run and confirm **fails**

### Implementation for US3 (backend)

- [x] T027 [US3] Implement `DashboardAnalyticsService.get_department_distribution(org_id, period, branch_id)` in `formcraft-backend/app/services/analytics/dashboard_analytics.py`:
  - Query `submissions` grouped by `department_id`; join `departments` for name
  - Exclude rows where `department_id IS NULL`
  - Compute `percentage = round(count / total * 100, 1)` per department
  - Order by count desc; cache and return `DepartmentDistributionResponse`
- [x] T028 [US3] Wire `GET /api/analytics/dashboard/department-distribution` route in `formcraft-backend/app/api/routes/analytics.py`; replace 501 stub; apply admin dep; run T026 test — must **pass**

### Implementation for US3 (frontend)

- [x] T029 [US3] Add `getDepartmentDistribution(filter: Omit<DashboardFilter, 'departmentId'>): Observable<DepartmentDistributionResponse>` to `formcraft-frontend/src/app/features/analytics/services/analytics.service.ts`
- [x] T030 [US3] Extend `AnalyticsComponent` in `formcraft-frontend/src/app/features/ui-redesign/admin/analytics.component.ts`:
  - Add `distribution: DepartmentDistributionResponse | null = null` property
  - Remove hardcoded `donutData: DonutSegment[]` array
  - Add `get donutData(): DonutSegment[]` getter — maps `distribution?.departments` to `{ label, value: percentage, color: palette[i % palette.length] }` where `palette` is the existing 6-colour array
  - Add `get donutTotal(): number` getter — returns `distribution?.total ?? 0`
  - Include `getDepartmentDistribution` call in `loadAllWidgets()`
- [x] T031 [US3] Bind donut chart in `formcraft-frontend/src/app/features/ui-redesign/admin/analytics.component.html`:
  - `donutData` is already bound via `*ngFor` — the getter replaces the removed array (no template change needed beyond confirming binding still works)
  - Replace hardcoded donut center value `7,284` → `{{ formatValue(donutTotal) }}`

**Checkpoint**: Donut chart shows real department percentages. T026 passes. Hardcoded `donutData` array gone.

---

## Phase 6: User Story 4 — Top Templates Bar Chart (Priority: P2)

**Goal**: The "Most Used Templates" bar chart ranks real templates by submission count with proportional bar widths.

**Independent Test**: Confirm the first bar's template name and count match a direct `SELECT template_id, COUNT(*) FROM submissions GROUP BY template_id ORDER BY COUNT(*) DESC LIMIT 1` query for the current period.

### Contract Test for US4 (write first — must FAIL before T035)

- [x] T032 [US4] Write contract test `test_top_templates_ordered_desc` in `formcraft-backend/tests/integration/test_dashboard_analytics_routes.py` — asserts `templates` list is ordered by `count` descending; asserts default response has ≤7 items; asserts `limit=3` query param returns ≤3 items; run and confirm **fails**

### Implementation for US4 (backend)

- [x] T033 [US4] Implement `DashboardAnalyticsService.get_top_templates(org_id, period, department_id, branch_id, limit)` in `formcraft-backend/app/services/analytics/dashboard_analytics.py`:
  - Query `submissions` grouped by `template_id`; join `templates` for `name` and `code`
  - Filter by `created_at` range, org, optional dept/branch
  - Order by count desc, limit to `limit` (default 7, max 20)
  - Cache and return `TopTemplatesResponse`
- [x] T034 [US4] Wire `GET /api/analytics/dashboard/top-templates` route in `formcraft-backend/app/api/routes/analytics.py`; accept `limit: int = Query(7, ge=1, le=20)`; replace 501 stub; apply admin dep; run T032 test — must **pass**

### Implementation for US4 (frontend)

- [x] T035 [US4] Add `getTopTemplates(filter: DashboardFilter, limit?: number): Observable<TopTemplatesResponse>` to `formcraft-frontend/src/app/features/analytics/services/analytics.service.ts`
- [x] T036 [US4] Extend `AnalyticsComponent` in `formcraft-frontend/src/app/features/ui-redesign/admin/analytics.component.ts`:
  - Add `topTemplates: TopTemplatesResponse | null = null` property
  - Remove hardcoded `barData: BarItem[]` array
  - Add `get barData(): BarItem[]` getter — maps `topTemplates?.templates` to `{ label: templateName, value: count, code: templateCode }`
  - `barMax` getter already uses `this.barData[0]?.value || 1` — no change needed
  - Include `getTopTemplates` call in `loadAllWidgets()`
- [x] T037 [US4] Verify bar chart template — `*ngFor="let b of barData"` already iterates the getter; `getBarWidth()` already computes proportional widths — confirm no template changes required; test visually at `/ui/admin/analytics`

**Checkpoint**: Bar chart shows real templates. T032 passes. Hardcoded `barData` array gone.

---

## Phase 7: User Story 5 — Operator Performance Table (Priority: P2)

**Goal**: The operator table shows real top-5 operators for the current week, with real names, branches, form counts, avg times, and accuracy rates.

**Independent Test**: Top operator name and `forms` count match the `/api/analytics/operators?period_type=week` response's first operator.

- [x] T038 [US5] Extend `AnalyticsComponent` in `formcraft-frontend/src/app/features/ui-redesign/admin/analytics.component.ts`:
  - Remove hardcoded `operators: Operator[]` array
  - Add `operators: OperatorAnalyticsItem[] = []` property (import `OperatorAnalyticsItem` from models)
  - Include `getOperatorAnalytics('week', undefined, undefined, this.filter.branchId)` call in `loadAllWidgets()`; on success set `this.operators = response.operators.slice(0, 5)`
  - Add `get operatorRows()` getter mapping `OperatorAnalyticsItem` to the display shape:
    - `name = operatorName`, `branch` (fetched from branch list or left as branch_id string initially), `forms = formsFilled`, `time = formatMsToTime(avgFillTimeMs)`, `accuracy = +(100 - errorRate * 100).toFixed(1)`, `color = palette[i % 6]`
- [x] T039 [US5] Bind operator table in `formcraft-frontend/src/app/features/ui-redesign/admin/analytics.component.html`:
  - Replace `*ngFor="let o of operators"` — the `operators` property is now `OperatorAnalyticsItem[]` mapped via `operatorRows` getter; update the `*ngFor` to iterate `operatorRows`
  - Confirm `{{ o.name }}`, `{{ o.branch }}`, `{{ o.forms }}`, `{{ o.time }}`, `{{ o.accuracy }}%` bindings map to the display shape from `operatorRows`
- [x] T040 [US5] Manually verify table shows real operator names and non-mock numbers; confirm `accuracy` renders as `100 - errorRate * 100` correctly

**Checkpoint**: Operator table displays live data. No hardcoded operator array remains.

---

## Phase 8: User Story 6 — Period and Department/Branch Filters (Priority: P3)

**Goal**: Period toggle buttons and department/branch filter pills are fully functional — selecting any filter reloads all five widgets with scoped data.

**Independent Test**: Select a specific department; all four KPIs, line chart, donut, bar chart, and operator table update to show only that department's data. Active period button has `active` CSS class.

- [x] T041 [US6] Extend `AnalyticsComponent` in `formcraft-frontend/src/app/features/ui-redesign/admin/analytics.component.ts`:
  - Add `departments: { id: string; name: string }[] = []` and `branches: { id: string; name: string }[] = []` properties
  - Add `selectedDeptLabel: string` and `selectedBranchLabel: string` computed strings for pill display text
  - Fetch departments and branches from existing org services (or add minimal `/api/departments` + `/api/branches` list calls) on `ngOnInit()`, in parallel with `loadAllWidgets()`
  - Add `setDepartment(id: string | undefined)` and `setBranch(id: string | undefined)` methods — update `filter` + call `loadAllWidgets()`
- [x] T042 [US6] Import `MatMenuModule` in the `imports` array of `AnalyticsComponent` in `formcraft-frontend/src/app/features/ui-redesign/admin/analytics.component.ts`
- [x] T043 [US6] Wire filter pills in `formcraft-frontend/src/app/features/ui-redesign/admin/analytics.component.html`:
  - Add `[matMenuTriggerFor]="deptMenu"` to the department filter pill `<div>` (no structural change — attribute addition only)
  - Add `<mat-menu #deptMenu>` sibling listing departments from `departments` array with `(click)="setDepartment(dept.id)"` per item; include "All Departments" option that calls `setDepartment(undefined)`
  - Add `[matMenuTriggerFor]="branchMenu"` to the branch filter pill
  - Add `<mat-menu #branchMenu>` listing branches similarly
  - Update `<span>` inside each pill to show `selectedDeptLabel` / `selectedBranchLabel`
  - Confirm period toggle `(click)="setPeriod(...)"` bindings from T024 apply the `active` class correctly

**Checkpoint**: All three filter controls (period/dept/branch) reload all widgets. Active states render correctly.

---

## Phase 9: User Story 7 — Loading and Error States (Priority: P3)

**Goal**: Skeleton placeholders appear while data loads; per-widget inline error with retry appears on failure; filter changes show previous data until new data arrives.

**Independent Test**: Throttle to Slow 3G — skeletons appear before data. Simulate a 500 on the summary endpoint — only KPI section shows error; other widgets still load.

- [x] T044 [US7] Add skeleton CSS classes to `formcraft-frontend/src/app/features/ui-redesign/admin/analytics.component.scss` — `.skeleton-line`, `.skeleton-box` with animated shimmer; use existing SCSS variables for colours
- [x] T045 [US7] Add skeleton placeholder markup inside each widget card in `formcraft-frontend/src/app/features/ui-redesign/admin/analytics.component.html`:
  - KPI grid: add `<div *ngIf="loadingStates.summary" class="kpi-grid skeleton-grid">` with 4 placeholder cards
  - Line chart body: add `<div *ngIf="loadingStates.timeSeries" class="skeleton-box chart-skeleton"></div>`
  - Donut body: add `<div *ngIf="loadingStates.distribution" class="skeleton-box donut-skeleton"></div>`
  - Bar chart body: add `<div *ngIf="loadingStates.topTemplates" class="skeleton-box bar-skeleton"></div>`
  - Operator table: add `<div *ngIf="loadingStates.operators" class="skeleton-box table-skeleton"></div>`
- [x] T046 [US7] Add per-widget error state markup in `formcraft-frontend/src/app/features/ui-redesign/admin/analytics.component.html`:
  - For each widget: add `<div *ngIf="errorStates.X" class="widget-error">{{ 'analytics.dashboard.error' | translate }} <button (click)="retryWidget('X')">{{ 'analytics.dashboard.retry' | translate }}</button></div>`
  - Add `retryWidget(widget: string)` method to the component that re-invokes only the relevant API call and clears the error state for that widget
- [x] T047 [US7] Update `loadAllWidgets()` and individual widget loaders in `formcraft-frontend/src/app/features/ui-redesign/admin/analytics.component.ts` to:
  - Set `loadingStates.X = true` before each call (only on first load, not on filter re-fetches — use an `initialLoad` flag)
  - Set `loadingStates.X = false` and `errorStates.X = false` on success
  - Set `loadingStates.X = false` and `errorStates.X = true` on error; keep previous data in place

**Checkpoint**: Skeleton and error states render correctly. Previous data persists during filter-change refetches.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: i18n keys, final cleanup, and integration validation.

- [x] T048 [P] Add `analytics.dashboard.*` translation keys to `formcraft-frontend/src/assets/i18n/en.json` — `loading`, `error`, `retry`, `empty`, `filter.period`, `filter.department`, `filter.branch`, `filter.all_departments`, `filter.all_branches`, `periods.7d`, `periods.30d`, `periods.90d`, `periods.yearly` (values as listed in `quickstart.md`)
- [x] T049 [P] Add the same keys with Arabic values to `formcraft-frontend/src/assets/i18n/ar.json` — translate all strings to Arabic RTL
- [x] T050 Audit `formcraft-frontend/src/app/features/ui-redesign/admin/analytics.component.ts` and confirm zero hardcoded numeric literals or mock arrays remain — the file must contain no inline `42`, `58`, `51...` numbers or hardcoded Arabic name strings matching the original mock data
- [x] T051 Run the full backend test suite `pytest formcraft-backend/tests/` and confirm all contract tests (T009, T010, T018, T026, T032) pass; fix any regressions
- [x] T052 Run `ng build formcraft-frontend` (production build) and confirm zero TypeScript errors and zero i18n missing-key warnings for the analytics module

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — **blocks all user stories**
- **Phase 3–9 (User Stories)**: All depend on Phase 2 completion; stories can proceed in priority order or in parallel per team capacity
- **Phase 10 (Polish)**: Depends on all desired stories being complete (at minimum Phase 3–7 for an MVP)

### User Story Dependencies

| Story | Depends on | Can parallel with |
|-------|-----------|-------------------|
| US1 (P1 — KPI Cards) | Phase 2 | US2 (frontend only) |
| US2 (P1 — Line Chart) | Phase 2 + US1 backend | US3, US4, US5 (frontend) |
| US3 (P2 — Donut) | Phase 2 | US4, US5 (backend independent) |
| US4 (P2 — Bar Chart) | Phase 2 | US3, US5 (backend independent) |
| US5 (P2 — Operators) | Phase 2 | US3, US4 (no new backend) |
| US6 (P3 — Filters) | US1–US5 complete | — |
| US7 (P3 — Loading/Error) | US1–US5 bindings exist | US6 |

### Within Each User Story

1. Contract test written → verified failing → backend service → backend route → test passes
2. Frontend interface → service method → component state → template binding

---

## Parallel Execution Examples

### Parallel — Phase 2 (all can run simultaneously)

```
Task T004: Add Pydantic schemas to app/schemas/analytics.py
Task T005: Add _period_to_dates to base_analytics.py
Task T006: Add TypeScript interfaces to analytics.model.ts
```

### Parallel — US3 backend + US4 backend (after Phase 2)

```
Task T026–T028: Department distribution endpoint
Task T032–T034: Top templates endpoint
```

### Parallel — US3 frontend + US4 frontend + US5 frontend (after Phase 3 complete)

```
Task T029–T031: Donut chart frontend
Task T035–T037: Bar chart frontend
Task T038–T040: Operator table frontend
```

### Parallel — Phase 10

```
Task T048: en.json i18n keys
Task T049: ar.json i18n keys
```

---

## Implementation Strategy

### MVP (User Stories 1 & 2 only — P1)

1. Phase 1: Setup
2. Phase 2: Foundational schemas + interfaces + cache
3. Phase 3: US1 — KPI cards with real data
4. Phase 4: US2 — line chart with period toggle
5. **STOP and VALIDATE**: Four real KPIs + working line chart; no mock data for these widgets
6. Deploy/demo to stakeholders

### Full Delivery (All User Stories)

Continue with Phase 5 → 6 → 7 → 8 → 9 → 10 in sequence or in parallel across the backend and frontend tracks.

### Parallel Team Strategy (2 developers)

- **Developer A (backend)**: T001–T008, then T009–T013, T018–T021, T026–T028, T032–T034
- **Developer B (frontend)**: T006 (can start in Phase 2), then T014–T017, T022–T025, T029–T031, T035–T040
- Merge when each story's backend and frontend are both complete

---

## Summary

| Phase | User Story | Priority | Tasks | Backend | Frontend |
|-------|-----------|----------|-------|---------|---------|
| 1 | Setup | – | T001–T003 | 2 | 1 |
| 2 | Foundational | – | T004–T008 | 3 | 2 |
| 3 | US1 KPI Cards | P1 🎯 | T009–T017 | 5 | 4 |
| 4 | US2 Line Chart | P1 | T018–T025 | 3 | 4 |
| 5 | US3 Donut | P2 | T026–T031 | 3 | 3 |
| 6 | US4 Bar Chart | P2 | T032–T037 | 3 | 3 |
| 7 | US5 Operators | P2 | T038–T040 | 0 | 3 |
| 8 | US6 Filters | P3 | T041–T043 | 0 | 3 |
| 9 | US7 Loading/Error | P3 | T044–T047 | 0 | 4 |
| 10 | Polish | – | T048–T052 | 1 | 4 |
| **Total** | | | **52** | **20** | **31** |
