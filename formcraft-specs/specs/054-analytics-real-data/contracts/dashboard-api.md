# API Contracts: Dashboard Analytics Endpoints

**Feature**: 054-analytics-real-data
**Base path**: `/api/analytics/dashboard`
**Auth**: All endpoints require `Authorization: Bearer <JWT>` with `role = admin`. Non-admin returns 403.

---

## GET /api/analytics/dashboard/summary

Returns the four KPI card values for the admin dashboard.

### Query Parameters

| Param | Type | Required | Default | Validation |
|-------|------|----------|---------|------------|
| `period` | string | No | `30d` | Must be one of: `7d`, `30d`, `90d`, `yearly` |
| `department_id` | UUID string | No | – | Valid UUID; must belong to caller's org |
| `branch_id` | UUID string | No | – | Valid UUID; must belong to caller's org |

### Response 200

```json
{
  "total_forms_filled": 7284,
  "total_forms_filled_prev": 6148,
  "delta_pct": 18.48,
  "active_templates": 12,
  "total_templates": 47,
  "avg_fill_time_ms": 222000,
  "avg_fill_time_prev_ms": 284000,
  "fill_time_delta_pct": -21.83,
  "unique_customers": 2841,
  "new_customers_this_week": 47,
  "period": "30d",
  "cache_expires_at": "2026-06-01T14:35:00Z"
}
```

### Error Responses

| Status | Condition |
|--------|-----------|
| 401 | Missing or invalid JWT |
| 403 | Authenticated user is not admin role |
| 422 | Invalid `period` value or malformed UUID |

### Cache Behaviour

Cached for 300 seconds per `(org_id, period, department_id, branch_id)` key. `cache_expires_at` indicates when the backend will re-query.

---

## GET /api/analytics/dashboard/submissions-over-time

Returns daily or monthly submission counts for the trend line chart.

### Query Parameters

Same as `/summary`: `period`, `department_id?`, `branch_id?`

### Response 200

```json
{
  "points": [
    { "date": "2026-05-01", "count": 218 },
    { "date": "2026-05-02", "count": 195 },
    "..."
  ],
  "peak_date": "2026-05-25",
  "peak_count": 312,
  "granularity": "daily",
  "cache_expires_at": "2026-06-01T14:35:00Z"
}
```

**Granularity rules**:
- `7d`, `30d`, `90d` → `"daily"` — one point per calendar day in the range
- `yearly` → `"monthly"` — one point per calendar month (Jan–current), `date` = first day of month

**Zero-fill**: Days/months with no submissions are included as `{ "date": "...", "count": 0 }` to maintain a continuous series.

### Error Responses

Same as `/summary`.

---

## GET /api/analytics/dashboard/department-distribution

Returns submission share by department for the donut chart.

### Query Parameters

| Param | Type | Required | Default |
|-------|------|----------|---------|
| `period` | string | No | `30d` |
| `branch_id` | UUID string | No | – |

(No `department_id` filter — distribution is always org-wide or branch-scoped.)

### Response 200

```json
{
  "departments": [
    {
      "department_id": "a1b2c3d4-...",
      "department_name": "الحسابات الجارية",
      "count": 2767,
      "percentage": 38.0
    },
    {
      "department_id": "e5f6g7h8-...",
      "department_name": "القروض الشخصية",
      "count": 1603,
      "percentage": 22.0
    }
  ],
  "total": 7284,
  "cache_expires_at": "2026-06-01T14:35:00Z"
}
```

**Ordering**: Descending by `count`.
**Percentage**: Rounded to 1 decimal place; sum may differ from 100.0 by ±0.1 due to rounding. Departments with `null` department_id are excluded.

---

## GET /api/analytics/dashboard/top-templates

Returns the most-used templates for the bar chart.

### Query Parameters

| Param | Type | Required | Default | Validation |
|-------|------|----------|---------|------------|
| `period` | string | No | `30d` | `7d \| 30d \| 90d \| yearly` |
| `department_id` | UUID string | No | – | |
| `branch_id` | UUID string | No | – | |
| `limit` | integer | No | `7` | 1–20 inclusive |

### Response 200

```json
{
  "templates": [
    {
      "template_id": "uuid-...",
      "template_name": "طلب فتح حساب جاري",
      "template_code": "AC-001",
      "count": 1837
    },
    {
      "template_id": "uuid-...",
      "template_name": "تحديث بيانات KYC",
      "template_code": "KYC-018",
      "count": 1284
    }
  ],
  "cache_expires_at": "2026-06-01T14:35:00Z"
}
```

**Ordering**: Descending by `count`.

---

## Frontend Service Method Signatures

```typescript
// In AnalyticsService (formcraft-frontend/.../analytics.service.ts)

getDashboardSummary(filter: DashboardFilter): Observable<DashboardSummaryResponse>

getSubmissionsOverTime(filter: DashboardFilter): Observable<SubmissionsOverTimeResponse>

getDepartmentDistribution(filter: Omit<DashboardFilter, 'departmentId'>): Observable<DepartmentDistributionResponse>

getTopTemplates(filter: DashboardFilter, limit?: number): Observable<TopTemplatesResponse>
```

All methods map `DashboardFilter` to HTTP query params:
- `filter.period` → `period`
- `filter.departmentId` → `department_id` (omitted if undefined)
- `filter.branchId` → `branch_id` (omitted if undefined)

---

## Contract Test Requirements (Constitution V — Test-First)

Each endpoint MUST have a contract test verifying:
1. Response shape matches the schema above (required fields present, correct types)
2. Admin auth returns 200; missing auth returns 401; non-admin auth returns 403
3. Invalid `period` value returns 422
4. Empty result (no submissions in org) returns valid response with zeros/empty arrays

Test file: `formcraft-backend/tests/integration/test_dashboard_analytics_routes.py`
