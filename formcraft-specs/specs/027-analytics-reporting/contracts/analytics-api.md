# API Contract: Analytics Dashboard

**Base path**: `/api/analytics`
**Auth**: Required (Bearer token)
**Role gate**: org_admin (all org data), branch_manager (department-scoped), operator (own data)

---

## Endpoints

### GET /api/analytics/overview

Dashboard overview KPIs for the selected period.

**Query params**:
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| preset | string | no | this_month | One of: today, this_week, this_month, this_quarter, this_year, last_7_days, last_30_days, custom |
| date_from | string (YYYY-MM-DD) | no | — | Required if preset=custom |
| date_to | string (YYYY-MM-DD) | no | — | Required if preset=custom |

**Response 200**:
```json
{
  "period_label": "May 2026",
  "total_submissions": 1234,
  "previous_total": 1100,
  "change_pct": 12.2,
  "by_status": {
    "printed": 1000,
    "submitted": 234
  },
  "daily_trend": [
    {"date": "2026-05-01", "count": 45},
    {"date": "2026-05-02", "count": 52}
  ],
  "previous_daily_trend": [
    {"date": "2026-04-01", "count": 38},
    {"date": "2026-04-02", "count": 41}
  ]
}
```

**Scoping**: Automatically scoped by user role. Branch Manager sees department only. Operator sees own submissions only.

---

### GET /api/analytics/by-branch

Submission breakdown by branch.

**Query params**: Same date params as `/overview`.

**Response 200**:
```json
{
  "branches": [
    {"branch_id": "uuid", "branch_name": "Main Branch", "department_name": "Operations", "total": 500, "pct_of_org": 40.5},
    {"branch_id": "uuid", "branch_name": "Downtown", "department_name": "Operations", "total": 350, "pct_of_org": 28.3}
  ],
  "total": 1234
}
```

---

### GET /api/analytics/templates

Template usage rankings.

**Query params**: Same date params + optional `limit` (int, default 20).

**Response 200**:
```json
{
  "templates": [
    {"template_id": "uuid", "template_name": "Cheque Request", "version": 3, "fill_count": 450, "is_deleted": false},
    {"template_id": "uuid", "template_name": "Transfer Form", "version": 1, "fill_count": 320, "is_deleted": false}
  ]
}
```

---

### GET /api/analytics/template-versions/{template_id}

Version adoption timeline for a specific template.

**Query params**: Same date params as `/overview`.

**Response 200**:
```json
{
  "template_name": "Cheque Request",
  "versions": [
    {
      "version": 1, "first_used": "2026-01-15", "last_used": "2026-03-20", "total": 200,
      "daily_counts": [{"date": "2026-01-15", "count": 5}, {"date": "2026-01-16", "count": 8}]
    },
    {
      "version": 2, "first_used": "2026-03-01", "last_used": "2026-05-24", "total": 450,
      "daily_counts": [{"date": "2026-03-01", "count": 3}, {"date": "2026-03-02", "count": 12}]
    }
  ]
}
```

---

### GET /api/analytics/operators

Operator productivity report.

**Query params**: Same date params + optional `branch_id` (UUID).

**Response 200**:
```json
{
  "operators": [
    {
      "operator_id": "uuid",
      "operator_name": "Ahmed Ali",
      "operator_email": "ahmed@org.com",
      "branch_name": "Main Branch",
      "total": 125,
      "daily_counts": [
        {"date": "2026-05-01", "count": 8},
        {"date": "2026-05-02", "count": 6}
      ]
    }
  ]
}
```

---

### GET /api/analytics/branch-comparison

Side-by-side branch comparison.

**Query params**: Same date params + optional `branch_ids` (comma-separated UUIDs, max 5).

**Response 200**:
```json
{
  "branches": [
    {
      "branch_id": "uuid",
      "branch_name": "Main Branch",
      "total_submissions": 500,
      "active_operators": 8,
      "top_template": "Cheque Request",
      "previous_total": 450,
      "change_pct": 11.1
    }
  ]
}
```

---

### GET /api/analytics/transactions

Transaction register (paginated).

**Query params**:
| Param | Type | Required | Default |
|-------|------|----------|---------|
| preset / date_from / date_to | string | no | this_month |
| template_id | UUID | no | — |
| operator_id | UUID | no | — |
| branch_id | UUID | no | — |
| status | string | no | — |
| search | string | no | — |
| page | int | no | 1 |
| limit | int | no | 25 |
| sort_by | string | no | created_at |
| sort_dir | string | no | desc |

**Response 200**:
```json
{
  "items": [
    {
      "reference_number": "FC-abc12345-2026-05-0001",
      "template_name": "Cheque Request",
      "operator_name": "Ahmed Ali",
      "branch_name": "Main Branch",
      "status": "printed",
      "created_at": "2026-05-24T10:30:00Z"
    }
  ],
  "total": 1234,
  "page": 1,
  "limit": 25
}
```

---

### GET /api/analytics/export

Export any analytics view as CSV.

**Query params**: Same as the specific view endpoint + `view` param (overview, branches, templates, operators, transactions).

**Response 200**: `text/csv; charset=utf-8` with BOM, `Content-Disposition: attachment; filename="analytics-{view}-{date}.csv"`

---

### POST /api/analytics/export-pdf

Export a report as PDF.

**Body**:
```json
{
  "view": "overview",
  "preset": "this_month",
  "date_from": null,
  "date_to": null,
  "chart_image_base64": "data:image/png;base64,..."
}
```

**Response 200**: `application/pdf`, `Content-Disposition: inline; filename="analytics-overview-2026-05.pdf"`

---

## Error Responses

| Status | When |
|--------|------|
| 401 | No valid auth token |
| 403 | Role insufficient (e.g., Viewer accessing analytics) |
| 422 | Invalid date range (date_from > date_to), invalid preset |
| 404 | Template not found (for version endpoint) |
