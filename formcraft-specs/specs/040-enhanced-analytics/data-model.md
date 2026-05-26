# Data Model: Enhanced Analytics Dashboard

**Feature**: 040-enhanced-analytics
**Date**: 2026-05-26

---

## Overview

This feature extends F027 analytics with new companion tables for pre-aggregated analytics data and materialized views for performance. It reuses existing `submissions`, `templates`, `pages`, `elements`, `profiles`, `departments`, `branches`, and `audit_logs` tables.

---

## New Tables

### field_analytics

Stores pre-aggregated field-level metrics per template version, refreshed hourly.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID PK | gen_random_uuid() | Surrogate key |
| org_id | UUID FK | → organizations.id, NOT NULL | Multi-tenant scoping |
| template_id | UUID FK | → templates.id, NOT NULL | Template reference |
| template_version | INT | NOT NULL | Template version scoped |
| field_key | TEXT | NOT NULL | Element field key |
| error_count | INT | DEFAULT 0, >= 0 | Total validation errors |
| error_types | JSONB | DEFAULT '{}' | Map of error_message → count |
| empty_count | INT | DEFAULT 0, >= 0 | Times left blank (non-required) |
| total_submissions | INT | DEFAULT 0, >= 0 | Submissions considered |
| avg_fill_time_ms | INT | NULL | Average milliseconds (NULL if telemetry disabled) |
| computed_at | TIMESTAMPTZ | DEFAULT now() | Aggregation timestamp |
| period_start | TIMESTAMPTZ | NOT NULL | Start of aggregation period |
| period_end | TIMESTAMPTZ | NOT NULL | End of aggregation period |
| retention_bucket | TEXT | DEFAULT 'hot', CHECK IN ('hot','archive') | Hot vs archive status |

**Indexes**:
- `idx_field_analytics_org_template(org_id, template_id, template_version)`
- `idx_field_analytics_period(period_start, period_end)`
- `idx_field_analytics_retention(retention_bucket, computed_at)`

**RLS**: `org_id` policy — users see only their org's data.

---

### operator_analytics

Stores pre-aggregated operator performance metrics per period.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID PK | gen_random_uuid() | Surrogate key |
| org_id | UUID FK | → organizations.id, NOT NULL | Multi-tenant scoping |
| operator_id | UUID FK | → auth.users.id, NOT NULL | Operator reference |
| period_type | TEXT | NOT NULL, CHECK IN ('day','week','month') | Aggregation granularity |
| period_start | DATE | NOT NULL | Period start date |
| forms_filled | INT | DEFAULT 0, >= 0 | Submissions created |
| avg_fill_time_ms | INT | NULL | Average form fill time |
| error_rate | DECIMAL(5,4) | DEFAULT 0.0000, >= 0, <= 1 | Validation failures per form ratio |
| busiest_hours | JSONB | DEFAULT '{}' | Heatmap data: {hour: {day: count}} |
| computed_at | TIMESTAMPTZ | DEFAULT now() | Aggregation timestamp |

**Indexes**:
- `idx_operator_analytics_org_operator(org_id, operator_id, period_type, period_start)`
- `idx_operator_analytics_period(period_type, period_start)`

**RLS**: `org_id` policy — branch managers see only their branch's operators via branch_id join through profiles.

---

### compliance_scorecard_cache

On-demand computed compliance metrics with 24h TTL caching.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID PK | gen_random_uuid() | Surrogate key |
| org_id | UUID FK | → organizations.id, NOT NULL | Multi-tenant scoping |
| validator_coverage_pct | DECIMAL(5,2) | DEFAULT 0.00, >= 0, <= 100 | % templates with full validator coverage |
| bilingual_label_pct | DECIMAL(5,2) | DEFAULT 0.00, >= 0, <= 100 | % templates with bilingual labels |
| quality_score_avg | DECIMAL(5,2) | DEFAULT 0.00, >= 0, <= 100 | Average quality score across templates |
| templates_needing_attention | INT | DEFAULT 0, >= 0 | Count of templates with quality score < 80 |
| customer_data_access_spike | BOOLEAN | DEFAULT FALSE | Unusual access pattern detected |
| computed_at | TIMESTAMPTZ | DEFAULT now() | Computation timestamp |
| cache_expires_at | TIMESTAMPTZ | NOT NULL | TTL expiration |

**Indexes**:
- `idx_compliance_cache_org(org_id, cache_expires_at)`

**RLS**: `org_id` policy — admin only.

---

### analytics_aggregation_log

Tracks materialized view refresh status for observability.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID PK | gen_random_uuid() | Surrogate key |
| view_name | TEXT | NOT NULL | Materialized view or table name |
| refresh_type | TEXT | NOT NULL, CHECK IN ('full','incremental') | Refresh strategy |
| started_at | TIMESTAMPTZ | NOT NULL | Refresh start time |
| completed_at | TIMESTAMPTZ | NULL | Refresh end time |
| duration_ms | INT | NULL | Computed duration |
| row_count | INT | NULL | Rows affected |
| status | TEXT | NOT NULL, CHECK IN ('running','success','failed') | Refresh status |
| error_message | TEXT | NULL | Error details if failed |

**Indexes**:
- `idx_agg_log_view_status(view_name, status, started_at DESC)`

**RLS**: No RLS — internal operational table, readable by admin only.

---

## Materialized Views

### mv_template_usage_funnel

Pre-aggregated template usage funnel: started → draft → submitted → printed.

```sql
CREATE MATERIALIZED VIEW mv_template_usage_funnel AS
SELECT
  org_id,
  template_id,
  template_version,
  date_trunc('day', created_at) AS day,
  COUNT(*) FILTER (WHERE status = 'started') AS started_count,
  COUNT(*) FILTER (WHERE status = 'draft') AS draft_count,
  COUNT(*) FILTER (WHERE status = 'submitted') AS submitted_count,
  COUNT(*) FILTER (WHERE status = 'printed') AS printed_count
FROM submissions
GROUP BY org_id, template_id, template_version, day;
```

**Refresh**: Every 15 minutes via `REFRESH MATERIALIZED VIEW CONCURRENTLY` (requires unique index).

**Index**: `CREATE UNIQUE INDEX idx_mv_funnel_unique ON mv_template_usage_funnel (org_id, template_id, template_version, day);`

---

## Existing Entities Used (from F027)

See F027 data-model.md for full details. Key reuse:
- `submissions` — primary data source for all aggregations
- `templates` — template metadata, version tracking
- `pages` / `elements` — compliance analytics (validator coverage, bilingual labels)
- `profiles` — operator metadata
- `departments` / `branches` — department/branch breakdown
- `audit_logs` — customer data access frequency

---

## Pydantic Response Models (backend)

### FieldAnalyticsItem
- field_key: str
- error_rate: float  # 0.0–1.0
- top_errors: list[{message: str, count: int}]  # top 3
- empty_rate: float  # 0.0–1.0, nullable for required fields
- avg_fill_time_ms: int | None
- warning: bool  # true if error_rate > 0.20

### OperatorAnalyticsItem
- operator_id: UUID
- operator_name: str
- forms_filled: int
- avg_fill_time_ms: int | None
- error_rate: float
- coaching_flag: bool  # true if error_rate significantly above average

### ComplianceScorecardResponse
- validator_coverage_pct: float
- bilingual_label_pct: float
- quality_score_avg: float
- templates_needing_attention: int
- customer_data_access_spike: bool
- computed_at: datetime

### TemplateUsageFunnelItem
- template_id: UUID
- template_name: str
- started_count: int
- draft_count: int
- submitted_count: int
- printed_count: int
- conversion_rates: dict[str, float]  # e.g., {"started_to_submitted": 0.75}

### BusiestHoursHeatmapItem
- hour: int  # 0–23
- day_of_week: int  # 0–6 (Sunday=0)
- submission_count: int
