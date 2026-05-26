# Analytics API Contract

**Feature**: 040-enhanced-analytics
**Date**: 2026-05-26
**Base Path**: `/api/analytics`

---

## Endpoints

### Field-Level Analytics

#### GET /api/analytics/fields

Returns field-level analytics for a specific template.

**Query Parameters**:
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| template_id | UUID | Yes | Template to analyze |
| from | date | No | Start date (inclusive) |
| to | date | No | End date (inclusive) |

**Response 200**:
```json
{
  "template_id": "uuid",
  "template_name": "string",
  "template_version": 3,
  "period": { "from": "2026-05-01", "to": "2026-05-26" },
  "fields": [
    {
      "field_key": "customer_name",
      "error_rate": 0.05,
      "top_errors": [
        { "message": "Required field", "count": 12 }
      ],
      "empty_rate": 0.02,
      "avg_fill_time_ms": 4500,
      "warning": false
    }
  ],
  "computed_at": "2026-05-26T10:00:00Z"
}
```

**Errors**:
- 404 — Template not found or no analytics data available
- 403 — User lacks permission for this template's org

---

### Operator Analytics

#### GET /api/analytics/operators

Returns operator-level analytics.

**Query Parameters**:
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| period_type | string | No | `day`, `week`, `month` (default: `week`) |
| from | date | No | Start date |
| to | date | No | End date |
| branch_id | UUID | No | Filter by branch |

**Response 200**:
```json
{
  "period_type": "week",
  "period": { "from": "2026-05-19", "to": "2026-05-26" },
  "operators": [
    {
      "operator_id": "uuid",
      "operator_name": "Ali Samir",
      "forms_filled": 42,
      "avg_fill_time_ms": 120000,
      "error_rate": 0.08,
      "coaching_flag": false
    }
  ],
  "org_average_error_rate": 0.06,
  "computed_at": "2026-05-26T10:00:00Z"
}
```

---

### Compliance Scorecard

#### GET /api/analytics/compliance

Returns compliance scorecard for the organization.

**Query Parameters**: None (scoped to user's org via JWT/RLS)

**Response 200**:
```json
{
  "org_id": "uuid",
  "validator_coverage_pct": 92.5,
  "bilingual_label_pct": 78.0,
  "quality_score_avg": 84.3,
  "templates_needing_attention": 7,
  "customer_data_access_spike": false,
  "computed_at": "2026-05-26T10:00:00Z",
  "cache_expires_at": "2026-05-27T10:00:00Z"
}
```

**Errors**:
- 403 — Admin role required

#### GET /api/analytics/compliance/templates-needing-attention

Returns list of non-compliant templates with specific issues.

**Response 200**:
```json
{
  "templates": [
    {
      "template_id": "uuid",
      "template_name": "KYC Form",
      "quality_score": 65.0,
      "missing_validators": ["national_id", "phone"],
      "missing_bilingual_labels": ["address_line_1"]
    }
  ]
}
```

---

### Enhanced Template Usage Analytics

#### GET /api/analytics/templates/usage

Returns template usage analytics with completion funnel.

**Query Parameters**:
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| template_id | UUID | No | Specific template (omit for all) |
| from | date | No | Start date |
| to | date | No | End date |
| group_by | string | No | `department`, `branch`, or none (default) |

**Response 200**:
```json
{
  "template_id": "uuid",
  "template_name": "Cheque v3",
  "funnel": {
    "started_count": 150,
    "draft_count": 30,
    "submitted_count": 100,
    "printed_count": 95,
    "conversion_rates": {
      "started_to_submitted": 0.667,
      "submitted_to_printed": 0.950
    }
  },
  "avg_fill_time_ms": 180000,
  "by_department": [
    {
      "department_id": "uuid",
      "department_name": "Retail",
      "submitted_count": 60
    }
  ],
  "computed_at": "2026-05-26T10:00:00Z"
}
```

#### GET /api/analytics/templates/version-adoption

Returns version adoption timeline for a template.

**Query Parameters**:
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| template_id | UUID | Yes | Template to analyze |
| from | date | No | Start date |
| to | date | No | End date |

**Response 200**:
```json
{
  "template_id": "uuid",
  "template_name": "Cheque",
  "adoption": [
    {
      "version": 1,
      "day": "2026-05-01",
      "count": 20,
      "pct_of_total": 0.20
    },
    {
      "version": 2,
      "day": "2026-05-01",
      "count": 80,
      "pct_of_total": 0.80
    }
  ]
}
```

---

### Busiest Hours Heatmap

#### GET /api/analytics/operators/busiest-hours

Returns submission volume heatmap by hour and day of week.

**Query Parameters**:
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| from | date | No | Start date |
| to | date | No | End date |
| branch_id | UUID | No | Filter by branch |

**Response 200**:
```json
{
  "heatmap": [
    {
      "hour": 9,
      "day_of_week": 0,
      "submission_count": 45
    }
  ],
  "peak_hour": 10,
  "peak_day": 1,
  "computed_at": "2026-05-26T10:00:00Z"
}
```

---

### Export

#### POST /api/analytics/export

Exports analytics data to CSV or PNG.

**Request Body**:
```json
{
  "report_type": "field_analytics",
  "template_id": "uuid",
  "from": "2026-05-01",
  "to": "2026-05-26",
  "format": "csv"
}
```

**Response 200**:
```json
{
  "download_url": "https://storage.formcraft.app/exports/analytics_123.csv",
  "expires_at": "2026-05-26T12:00:00Z"
}
```

**Supported report_type values**: `field_analytics`, `operator_analytics`, `compliance_scorecard`, `template_usage`, `busiest_hours`

**Supported format values**: `csv`, `png`, `pdf`

---

## Authentication & Authorization

All endpoints require valid JWT from Supabase Auth.

| Endpoint | Required Role | RLS Notes |
|----------|--------------|-----------|
| GET /api/analytics/fields | Admin, Designer, Operator (own) | Branch managers see branch-scoped data |
| GET /api/analytics/operators | Admin, Designer | Branch managers see branch-scoped data |
| GET /api/analytics/compliance | Admin only | Org-scoped |
| GET /api/analytics/templates/* | Admin, Designer | Org-scoped |
| GET /api/analytics/operators/busiest-hours | Admin, Designer | Branch managers see branch-scoped data |
| POST /api/analytics/export | Admin, Designer | Same scoping as target report |
