# Quickstart: Enhanced Analytics Dashboard

**Feature**: 040-enhanced-analytics
**Date**: 2026-05-26

## Prerequisites

- F027 (analytics-reporting) is deployed and operational
- Supabase migration `f040_analytics_tables.sql` has been applied
- Materialized view `mv_template_usage_funnel` has been created and indexed
- Backend services are running (`formcraft-backend`)
- Frontend is built and served (`formcraft-frontend`)

## Setup

### 1. Apply Database Migration

```bash
supabase db push --migration-file migrations/f040_analytics_tables.sql
```

This creates:
- `field_analytics` table
- `operator_analytics` table
- `compliance_scorecard_cache` table
- `analytics_aggregation_log` table
- `mv_template_usage_funnel` materialized view
- RLS policies on all new tables

### 2. Schedule Materialized View Refresh

Add a cron job or scheduled function to refresh the materialized view every 15 minutes:

```sql
SELECT cron.schedule('refresh_template_funnel', '*/15 * * * *', $$
  REFRESH MATERIALIZED VIEW CONCURRENTLY mv_template_usage_funnel;
  INSERT INTO analytics_aggregation_log (view_name, refresh_type, started_at, completed_at, duration_ms, row_count, status)
  VALUES ('mv_template_usage_funnel', 'full', now(), now(), 0, (SELECT COUNT(*) FROM mv_template_usage_funnel), 'success');
$$);
```

### 3. Seed Initial Analytics Data (optional)

For existing submissions, backfill the analytics tables:

```bash
cd formcraft-backend
python -m scripts.backfill_analytics --org-id <your-org-id> --from-date 2026-01-01
```

## API Smoke Tests

### Test 1: Field Analytics

```bash
curl -s "http://localhost:8000/api/analytics/fields?template_id=<template-id>" \
  -H "Authorization: Bearer <jwt-token>" | jq .
```

Expected: JSON with `fields` array containing error rates and fill times.

### Test 2: Operator Analytics

```bash
curl -s "http://localhost:8000/api/analytics/operators?period_type=week" \
  -H "Authorization: Bearer <jwt-token>" | jq .
```

Expected: JSON with `operators` array and `org_average_error_rate`.

### Test 3: Compliance Scorecard

```bash
curl -s "http://localhost:8000/api/analytics/compliance" \
  -H "Authorization: Bearer <jwt-token>" | jq .
```

Expected: JSON with `validator_coverage_pct`, `bilingual_label_pct`, `quality_score_avg`.

### Test 4: Template Usage Funnel

```bash
curl -s "http://localhost:8000/api/analytics/templates/usage?template_id=<template-id>" \
  -H "Authorization: Bearer <jwt-token>" | jq .
```

Expected: JSON with `funnel` object containing started, draft, submitted, printed counts.

### Test 5: Busiest Hours Heatmap

```bash
curl -s "http://localhost:8000/api/analytics/operators/busiest-hours?from=2026-05-01&to=2026-05-26" \
  -H "Authorization: Bearer <jwt-token>" | jq .
```

Expected: JSON with `heatmap` array of hour/day/submission_count.

### Test 6: Export CSV

```bash
curl -s -X POST "http://localhost:8000/api/analytics/export" \
  -H "Authorization: Bearer <jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{"report_type":"field_analytics","template_id":"<template-id>","format":"csv"}' | jq .
```

Expected: JSON with `download_url` pointing to a generated CSV file.

## Frontend Navigation

1. Log in as org admin
2. Navigate to `/admin/analytics/fields` — field-level analytics
3. Navigate to `/admin/analytics/operators` — operator performance
4. Navigate to `/admin/analytics/compliance` — compliance scorecard
5. Navigate to `/admin/analytics/templates` — template usage funnel

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Analytics data is stale | Materialized view not refreshed | Check `analytics_aggregation_log` for failed refreshes |
| Field timing shows "N/A" | Telemetry not enabled | Enable per-template telemetry toggle in template settings |
| Compliance scorecard is slow | Cache expired | First request after cache expiry computes on-demand; subsequent requests are fast |
| Export fails with 500 | Storage bucket missing | Ensure Supabase Storage bucket `exports` exists with appropriate RLS |
| Empty operator list | No submissions in period | Adjust date range or wait for submissions |

## Performance Validation

Verify the following performance targets:

1. Field analytics for 50 fields / 10k submissions loads in <5s
2. Operator analytics for 100 operators loads in <3s
3. Compliance scorecard for 500+ templates loads in <10s

Use the browser DevTools Network tab or backend logs (structured latency metrics) to confirm.
