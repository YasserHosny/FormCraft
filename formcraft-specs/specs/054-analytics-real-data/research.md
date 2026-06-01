# Research: New-Theme Admin Console Analytics — Real Data Integration

**Feature**: 054-analytics-real-data
**Generated**: 2026-06-01

---

## Decision 1 — Caching Library

**Decision**: Use `cachetools.TTLCache` (already in `requirements.txt` v5.5.1) for server-side result caching.

**Rationale**: `cachetools` is already a declared dependency (used by the AI service). `TTLCache(maxsize=1024, ttl=300)` provides a per-process in-memory cache with a 5-minute expiry. Each cache key is a tuple of `(org_id, period, department_id, branch_id)`. No Redis, no external service, no new dependency — fully YAGNI-compliant.

**Alternatives considered**:
- `aiocache` with Redis backend — over-engineered for a single-process service at current scale; adds Redis operational burden.
- No caching (always-live) — rejected because SC-007 requires <2 s for 100K submissions; aggregation queries at that volume without caching are likely to exceed this on cold runs.
- Materialized views (Supabase) — viable long-term but requires schema changes (schema-freeze constraint in FR-007).

**Implementation note**: Each `DashboardAnalyticsService` method will have an explicit `_cache: TTLCache` class-level attribute. Cache lookup happens before the Supabase query; result is stored on cache miss. Thread safety is acceptable because FastAPI runs in a single async thread per worker.

---

## Decision 2 — Admin Role Enforcement

**Decision**: Use the existing `require_role(Role.ADMIN)` dependency factory from `app.api.deps` as the `Depends(...)` argument for all four new routes.

**Rationale**: `require_role` is the established RBAC pattern in this codebase. It returns 403 for wrong roles and delegates 401 handling to `get_current_user`. This is exactly what FR-006 specifies.

**Alternatives considered**:
- Inline role check (`if current_user.role != "admin"`) — used in existing compliance routes but is less composable; `require_role` is cleaner for new code.

---

## Decision 3 — Submissions Table Field Names (Verified)

**Decision**: Query the `submissions` table using `created_at` (not `submitted_at`); filter by `org_id`, `department_id`, `branch_id`, `template_id`. Use `customer_id` for distinct customer count.

**Rationale**: Existing `operator_analytics.py` and `template_analytics.py` both query `submissions` using `created_at`. The `mv_template_usage_funnel` materialized view is already used for funnel metrics; the raw `submissions` table is used for time-series and distribution queries. The `department_id` and `branch_id` columns are confirmed present (used in `_get_department_breakdown` and `apply_branch_scope`).

**Field assumptions confirmed**:
- `submissions.created_at` — ISO timestamp, used for all date filtering
- `submissions.org_id` — UUID, used for org scoping
- `submissions.department_id` — UUID (nullable), used for department distribution
- `submissions.branch_id` — UUID (nullable), used for branch filtering
- `submissions.template_id` — UUID, used for top-templates ranking
- `submissions.customer_id` — UUID (nullable), used for distinct customer count
- `templates.status` — string; `"published"` = active template (confirmed in `public_portal.py`)
- `templates.org_id` — UUID, scopes template counts to org

---

## Decision 4 — Yearly Period Granularity

**Decision**: The `yearly` period returns 12 data points, one per calendar month (first day of each month as the date key), covering the 12 months up to and including the current month.

**Rationale**: Clarified in session 2026-06-01. Monthly buckets are standard in analytics tools (Mixpanel, Amplitude, Metabase), reduce chart noise, and match the 12-bar visual representation naturally.

**Implementation note**: Backend truncates `created_at` to month using `date_trunc('month', created_at)`. Frontend formats monthly dates as `MMM YYYY` in Arabic locale.

---

## Decision 5 — Frontend Chart Rendering (No New Library)

**Decision**: Render SVG bar chart and donut chart using pure computed values in the Angular component — no new charting library.

**Rationale**:
- Constitution locks UI library to Angular Material; no chart library is in scope.
- FR-021 forbids HTML structure changes; the existing template already has `.mini-bars` and `.donut-placeholder` elements.
- The line chart is already structured as `<div class="mini-bar">` elements with `[style.height.%]` binding — we replace the `lineData` array with real API data.
- The donut chart already has a `.donut-placeholder` div and a legend — we replace `donutData` array.
- No `<canvas>` or SVG path math needed; CSS percentage heights/widths handle proportional rendering.

---

## Decision 6 — Department & Branch Filter Pill UX

**Decision**: Wrap each existing filter pill `<div>` with Angular Material `MatMenu`. The pill acts as the trigger (`[matMenuTriggerFor]`); the menu shows a list of departments/branches fetched on first open (lazy-loaded).

**Rationale**: `MatMenu` from Angular Material is already imported across the codebase and requires zero structural DOM change to the pill element — only adding the `[matMenuTriggerFor]` attribute and `<mat-menu>` sibling. This satisfies FR-021 (no HTML structure changes beyond Angular binding attributes). Departments and branches are fetched once on component init alongside the dashboard data.

---

## Decision 7 — Operator Table Period Handling

**Decision**: The operator table always calls `GET /api/analytics/operators?period_type=week` regardless of the dashboard period filter. It does, however, respect the `branch_id` filter.

**Rationale**: User Story 5 labels the table "أعلى الموظفين أداءً هذا الأسبوع" (top performers this week) — the subtitle is fixed to "this week". The existing `/api/analytics/operators` endpoint uses `period_type` (day/week/month), not the dashboard's `period` param. Mapping `7d/30d/90d/yearly` to `day/week/month` would be lossy and semantically wrong for the table's stated scope.

---

## Decision 8 — Period-to-Date Conversion

**Decision**: The backend converts `period` strings to `(from_date, to_date)` pairs using a shared utility:

| period | from_date | to_date |
|--------|-----------|---------|
| `7d`   | today − 7 days | today |
| `30d`  | today − 30 days | today |
| `90d`  | today − 90 days | today |
| `yearly` | Jan 1 of current year | today |

The "previous period" for delta computation uses the same window width shifted one period back (e.g., for `30d`: from −60d to −30d).

**Rationale**: Simple, deterministic, timezone-naive (UTC) arithmetic. Consistent with how existing analytics services compute their ranges.
