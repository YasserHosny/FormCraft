# Data Model: New-Theme Admin Console Analytics

**Feature**: 054-analytics-real-data
**Generated**: 2026-06-01

---

## Existing Tables (Read-Only, No Schema Changes)

All queries are read-only against existing tables. No migrations required.

### `submissions`
| Column | Type | Used for |
|--------|------|---------|
| `id` | UUID PK | – |
| `org_id` | UUID FK | Org scoping on every query |
| `template_id` | UUID FK → templates | Top-templates ranking |
| `department_id` | UUID FK → departments (nullable) | Department distribution filter |
| `branch_id` | UUID FK → branches (nullable) | Branch filter |
| `customer_id` | UUID (nullable) | Distinct customer count |
| `created_at` | timestamptz | All date-range filters and time-series grouping |

### `templates`
| Column | Type | Used for |
|--------|------|---------|
| `id` | UUID PK | Join target from submissions |
| `org_id` | UUID FK | Org scoping |
| `name` | text | Top-templates label |
| `code` | text | Top-templates badge (e.g., "AC-001") |
| `status` | text | `'published'` = active; used for active/total count |

### `departments`
| Column | Type | Used for |
|--------|------|---------|
| `id` | UUID PK | Filter key; join from submissions |
| `org_id` | UUID FK | Org scoping |
| `name` | text | Department distribution legend label |

### `branches`
| Column | Type | Used for |
|--------|------|---------|
| `id` | UUID PK | Filter key; joined from profiles for filter pill list |
| `org_id` | UUID FK | Org scoping |
| `name` | text | Branch filter pill list |

### `profiles` (operators)
| Column | Type | Used for |
|--------|------|---------|
| `id` | UUID PK | Operator identity |
| `org_id` | UUID FK | Org scoping |
| `branch_id` | UUID FK → branches | Branch filter on operator table |
| `role` | text enum | Admin check (role = 'admin') |

---

## New Pydantic Schemas (Backend — `app/schemas/analytics.py` additions)

### `DashboardSummaryResponse`
| Field | Type | Description |
|-------|------|-------------|
| `total_forms_filled` | `int` | Submissions count in current period |
| `total_forms_filled_prev` | `int` | Submissions count in previous period of same length |
| `delta_pct` | `float \| None` | Percentage change (positive = growth); null if prev = 0 |
| `active_templates` | `int` | Templates with `status = 'published'` |
| `total_templates` | `int` | All templates in org |
| `avg_fill_time_ms` | `int \| None` | Mean of `(submitted_at - started_at)` in ms; null if no timing data |
| `avg_fill_time_prev_ms` | `int \| None` | Same for previous period |
| `fill_time_delta_pct` | `float \| None` | % improvement (negative = slower); null if prev null |
| `unique_customers` | `int` | `COUNT(DISTINCT customer_id)` in current period |
| `new_customers_this_week` | `int` | Customers whose first submission is within the last 7 days |
| `period` | `str` | Echo of the `period` query param (e.g., `"30d"`) |
| `cache_expires_at` | `datetime` | UTC timestamp when this cached result expires |

### `TimeSeriesPoint`
| Field | Type | Description |
|-------|------|-------------|
| `date` | `date` | ISO date; first day of month for yearly granularity |
| `count` | `int` | Submission count for this day/month |

### `SubmissionsOverTimeResponse`
| Field | Type | Description |
|-------|------|-------------|
| `points` | `list[TimeSeriesPoint]` | Ordered oldest → newest |
| `peak_date` | `date \| None` | Date of highest count; null if all zeros |
| `peak_count` | `int` | Highest count value |
| `granularity` | `Literal['daily', 'monthly']` | `'daily'` for 7d/30d/90d; `'monthly'` for yearly |
| `cache_expires_at` | `datetime` | Cache expiry |

### `DepartmentShareItem`
| Field | Type | Description |
|-------|------|-------------|
| `department_id` | `UUID` | Department UUID |
| `department_name` | `str` | Display name |
| `count` | `int` | Submission count |
| `percentage` | `float` | Rounded to 1 decimal; items sum to 100.0 |

### `DepartmentDistributionResponse`
| Field | Type | Description |
|-------|------|-------------|
| `departments` | `list[DepartmentShareItem]` | Ordered by count desc |
| `total` | `int` | Sum of all counts |
| `cache_expires_at` | `datetime` | Cache expiry |

### `TopTemplateItem`
| Field | Type | Description |
|-------|------|-------------|
| `template_id` | `UUID` | Template UUID |
| `template_name` | `str` | Template display name |
| `template_code` | `str` | Short code (e.g., "AC-001") |
| `count` | `int` | Submission count in period |

### `TopTemplatesResponse`
| Field | Type | Description |
|-------|------|-------------|
| `templates` | `list[TopTemplateItem]` | Ordered by count desc, max `limit` items |
| `cache_expires_at` | `datetime` | Cache expiry |

---

## New TypeScript Interfaces (Frontend — `analytics.model.ts` additions)

### `DashboardFilter`
```typescript
export interface DashboardFilter {
  period: '7d' | '30d' | '90d' | 'yearly';
  departmentId?: string;
  branchId?: string;
}
```

### `DashboardSummaryResponse`
```typescript
export interface DashboardSummaryResponse {
  totalFormsFilled: number;
  totalFormsFilledPrev: number;
  deltaPct: number | null;
  activeTemplates: number;
  totalTemplates: number;
  avgFillTimeMs: number | null;
  avgFillTimePrevMs: number | null;
  fillTimeDeltaPct: number | null;
  uniqueCustomers: number;
  newCustomersThisWeek: number;
  period: string;
  cacheExpiresAt: string;
}
```

### `TimeSeriesPoint`
```typescript
export interface TimeSeriesPoint {
  date: string;   // ISO date string
  count: number;
}
```

### `SubmissionsOverTimeResponse`
```typescript
export interface SubmissionsOverTimeResponse {
  points: TimeSeriesPoint[];
  peakDate: string | null;
  peakCount: number;
  granularity: 'daily' | 'monthly';
  cacheExpiresAt: string;
}
```

### `DepartmentShareItem`
```typescript
export interface DepartmentShareItem {
  departmentId: string;
  departmentName: string;
  count: number;
  percentage: number;
}
```

### `DepartmentDistributionResponse`
```typescript
export interface DepartmentDistributionResponse {
  departments: DepartmentShareItem[];
  total: number;
  cacheExpiresAt: string;
}
```

### `TopTemplateItem`
```typescript
export interface TopTemplateItem {
  templateId: string;
  templateName: string;
  templateCode: string;
  count: number;
}
```

### `TopTemplatesResponse`
```typescript
export interface TopTemplatesResponse {
  templates: TopTemplateItem[];
  cacheExpiresAt: string;
}
```

---

## Cache Key Structure

All four backend service methods share a cache keyed by:

```python
CacheKey = tuple[str, str, str | None, str | None]
# (org_id, period, department_id, branch_id)
```

`TTLCache(maxsize=1024, ttl=300)` — one cache instance per `DashboardAnalyticsService` class (class-level attribute shared across all requests).

---

## State Transitions (Frontend Filter State)

```
Initial load
  └─► DashboardFilter { period: '30d', departmentId: undefined, branchId: undefined }
        └─► loadAllWidgets()

Period toggle clicked
  └─► DashboardFilter.period = new value
        └─► loadAllWidgets()

Department filter selected
  └─► DashboardFilter.departmentId = selected UUID (or undefined to clear)
        └─► loadAllWidgets()

Branch filter selected
  └─► DashboardFilter.branchId = selected UUID (or undefined to clear)
        └─► loadAllWidgets()
```

`loadAllWidgets()` triggers 4 parallel HTTP calls:
1. `getDashboardSummary(filter)` → KPI cards
2. `getSubmissionsOverTime(filter)` → line chart
3. `getDepartmentDistribution(filter)` → donut chart
4. `getTopTemplates(filter)` → bar chart
+ `getOperatorAnalytics(period_type='week', branch_id)` → operator table (branch-filtered only)
