# Implementation Plan: New-Theme Admin Console Analytics — Real Data Integration

**Branch**: `054-analytics-real-data` | **Date**: 2026-06-01 | **Spec**: [spec.md](./spec.md)

---

## Summary

The new-theme Admin Console Analytics page currently renders entirely hardcoded data. This plan wires it to real API data by: (1) adding a `DashboardAnalyticsService` on the FastAPI backend with 4 new endpoints under `/api/analytics/dashboard/`, (2) extending the Angular `AnalyticsService` and `AnalyticsComponent` with reactive filter state and real HTTP calls, and (3) binding all chart and KPI elements to live API responses — without altering the new theme's HTML structure.

---

## Technical Context

**Language/Version**: Python 3.12 (backend) / TypeScript 5 + Angular 19 (frontend)
**Primary Dependencies**: FastAPI, Supabase PostgreSQL, `cachetools` (already in requirements), Angular Material, ngx-translate, RxJS
**Storage**: Supabase PostgreSQL — read-only queries against existing `submissions`, `templates`, `departments`, `branches`, `profiles` tables. No schema changes.
**Testing**: pytest + httpx (backend contract tests); Angular TestBed (frontend unit tests)
**Target Platform**: Web (Bunny Magic Containers); admin route only
**Performance Goals**: All 4 new endpoints respond ≤2 s for orgs with ≤100K submissions; frontend filter change completes full refresh ≤3 s
**Constraints**:
- 5-minute TTL cache per `(org_id, period, department_id, branch_id)` via `cachetools.TTLCache`
- Admin-only endpoints — `require_role(Role.ADMIN)` dep on all 4 routes
- HTML structure of `analytics.component.html` MUST NOT change (Angular bindings only)
- All user-visible strings via i18n keys; Arabic numbers via `formatValue` / `toLocaleString('ar-EG')`
**Scale/Scope**: Per-org aggregate queries; up to 100K submissions; 1 024-slot in-memory cache

---

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arabic-First / RTL | ✅ Pass | FR-020/022: RTL number formatting and i18n keys required |
| II. Print Fidelity | ✅ N/A | No PDF output in this feature |
| III. AI — Never Auto-Apply | ✅ N/A | No AI in this feature |
| IV. Deterministic Validators | ✅ N/A | No form validators in this feature |
| V. Test-First | ✅ Pass | Contract tests written before routes; unit tests for service methods |
| VI. Normalized Data Model | ✅ Pass | No schema changes; read-only queries against existing normalized tables |
| VII. Translation-Key Architecture | ✅ Pass | FR-022: all new strings via i18n keys in en.json + ar.json |
| VIII. Security & Auditability | ✅ Pass | `require_role(Role.ADMIN)` on all endpoints; 403 for non-admin |
| IX. Simplicity / YAGNI | ✅ Pass | No new libraries; `cachetools` already declared; no new abstractions |

No violations — no complexity justification table needed.

---

## Project Structure

### Documentation (this feature)

```text
formcraft-specs/specs/054-analytics-real-data/
├── plan.md              ← this file
├── spec.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── dashboard-api.md
├── checklists/
│   └── requirements.md
└── tasks.md             ← created by /speckit.tasks
```

### Source Code Layout

```text
formcraft-backend/
├── app/
│   ├── schemas/
│   │   └── analytics.py              EXTEND — 7 new Pydantic models
│   ├── services/analytics/
│   │   ├── base_analytics.py         UNCHANGED
│   │   └── dashboard_analytics.py    NEW — DashboardAnalyticsService
│   └── api/routes/
│       └── analytics.py              EXTEND — 4 new routes under /dashboard/
└── tests/integration/
    └── test_dashboard_analytics_routes.py    NEW — contract tests (write first)

formcraft-frontend/src/app/
├── features/analytics/
│   ├── models/
│   │   └── analytics.model.ts        EXTEND — 8 new TypeScript interfaces
│   └── services/
│       └── analytics.service.ts      EXTEND — 4 new methods
└── features/ui-redesign/admin/
    ├── analytics.component.ts        REPLACE hardcoded data with reactive API state
    └── analytics.component.html      BIND only — no structural changes

formcraft-frontend/src/assets/i18n/
├── en.json                           EXTEND — analytics.dashboard.* keys
└── ar.json                           EXTEND — same keys in Arabic
```

---

## Phase 0: Research (Complete)

See [research.md](./research.md) for all decisions. Summary:

| Decision | Resolution |
|----------|------------|
| Caching library | `cachetools.TTLCache(maxsize=1024, ttl=300)` — already in requirements |
| Admin role check | `Depends(require_role(Role.ADMIN))` from `app.api.deps` |
| Submissions timestamp field | `created_at` (not `submitted_at`); confirmed via existing service code |
| Yearly granularity | Monthly buckets, 12 points (Jan → current month) |
| Chart rendering | Pure CSS percentage heights/widths — no new charting library |
| Filter pill UX | `MatMenu` triggered from existing pill element |
| Operator table period | Always `period_type=week`; respects `branch_id` only |
| Previous-period delta | Same window width shifted back (e.g., 30d → −60d to −30d) |

---

## Phase 1: Design & Contracts (Complete)

See [data-model.md](./data-model.md) and [contracts/dashboard-api.md](./contracts/dashboard-api.md).

### New Backend Endpoint Summary

| Route | Auth | Cache TTL | Returns |
|-------|------|-----------|---------|
| `GET /api/analytics/dashboard/summary` | Admin | 300 s | `DashboardSummaryResponse` |
| `GET /api/analytics/dashboard/submissions-over-time` | Admin | 300 s | `SubmissionsOverTimeResponse` |
| `GET /api/analytics/dashboard/department-distribution` | Admin | 300 s | `DepartmentDistributionResponse` |
| `GET /api/analytics/dashboard/top-templates` | Admin | 300 s | `TopTemplatesResponse` |

### New Frontend Service Methods

```typescript
getDashboardSummary(filter: DashboardFilter): Observable<DashboardSummaryResponse>
getSubmissionsOverTime(filter: DashboardFilter): Observable<SubmissionsOverTimeResponse>
getDepartmentDistribution(filter: Omit<DashboardFilter, 'departmentId'>): Observable<DepartmentDistributionResponse>
getTopTemplates(filter: DashboardFilter, limit?: number): Observable<TopTemplatesResponse>
```

### Component State Model

```typescript
// AnalyticsComponent properties (replaces hardcoded arrays)
filter: DashboardFilter = { period: '30d' };
summary: DashboardSummaryResponse | null = null;
timeSeries: SubmissionsOverTimeResponse | null = null;
distribution: DepartmentDistributionResponse | null = null;
topTemplates: TopTemplatesResponse | null = null;
operators: OperatorAnalyticsItem[] = [];

loadingStates = { summary: false, timeSeries: false, distribution: false, topTemplates: false, operators: false };
errorStates  = { summary: false, timeSeries: false, distribution: false, topTemplates: false, operators: false };

departments: { id: string; name: string }[] = [];  // filter pill list
branches:    { id: string; name: string }[] = [];  // filter pill list
```

### Key Computed Properties (replacing hardcoded arrays)

| Old hardcoded | New computed |
|---|---|
| `lineData: number[]` | `get lineData(): number[]` — maps `timeSeries.points.map(p => p.count)` |
| `lineMax: number` | `timeSeries?.peakCount \|\| 1` |
| `donutData: DonutSegment[]` | `distribution?.departments.map(d => ({ label: d.departmentName, value: d.percentage, color: palette[i % 6] }))` |
| `barData: BarItem[]` | `topTemplates?.templates.map(t => ({ label: t.templateName, value: t.count, code: t.templateCode }))` |
| `operators: Operator[]` | Mapped from `OperatorAnalyticsItem[]`; `accuracy = 100 − (errorRate * 100)` |

### Parallel API Fan-Out on Filter Change

```typescript
loadAllWidgets(): void {
  // 5 parallel calls; each sets its own loading/error state
  forkJoin({
    summary:      this.analyticsService.getDashboardSummary(this.filter),
    timeSeries:   this.analyticsService.getSubmissionsOverTime(this.filter),
    distribution: this.analyticsService.getDepartmentDistribution(this.filter),
    topTemplates: this.analyticsService.getTopTemplates(this.filter),
    operators:    this.analyticsService.getOperatorAnalytics('week', undefined, undefined, this.filter.branchId),
  }).subscribe({ ... });
}
```

---

## Implementation Order (for /speckit.tasks)

Tasks should be ordered:

1. **Backend — Pydantic schemas** (foundation for contract tests)
2. **Backend — Contract tests** (failing, TDD red phase)
3. **Backend — `DashboardAnalyticsService`** (green phase)
4. **Backend — Routes** (wire service to FastAPI router)
5. **Frontend — TypeScript interfaces** (foundation for service/component)
6. **Frontend — `AnalyticsService` methods** (4 new HTTP methods)
7. **Frontend — Filter state + `loadAllWidgets()`** (reactive core)
8. **Frontend — KPI card bindings** (simplest visual change)
9. **Frontend — Line chart bindings** (period toggle + time-series)
10. **Frontend — Donut chart bindings** (department distribution)
11. **Frontend — Bar chart bindings** (top templates)
12. **Frontend — Operator table bindings** (existing endpoint, new wiring)
13. **Frontend — Filter pills** (department + branch dropdowns)
14. **Frontend — Loading skeletons** (UX polish)
15. **Frontend — Error states + retry** (resilience)
16. **Frontend — i18n keys** (en.json + ar.json)
17. **Integration smoke test** (verify no mock literals remain)
