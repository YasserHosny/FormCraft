# Research: Analytics & Reporting Dashboard

**Feature**: 027-analytics-reporting
**Date**: 2026-05-24

---

## R1: Live Aggregation Query Performance on PostgreSQL

**Decision**: Use PostgreSQL aggregate queries (`COUNT`, `GROUP BY`, date-based grouping) directly on the `submissions` table with existing indexes.

**Rationale**: The `submissions` table already has indexes on `org_id`, `operator_id`, `template_id`, and `created_at DESC`. For organizations with up to 100K submissions, PostgreSQL handles aggregation queries efficiently (sub-second for most GROUP BY queries on indexed columns). No materialized views or pre-aggregation needed at this scale.

**Alternatives considered**:
- Materialized views refreshed on a schedule — rejected because adds complexity (refresh jobs, stale data) without performance need at 100K scale.
- Separate analytics database / data warehouse — rejected as massive over-engineering for current scale.
- In-memory caching (Redis) — not needed; PostgreSQL query caching sufficient. Can add later if needed.

**Performance mitigation**: Use `date_trunc()` for time-series grouping, limit result sets with pagination, add composite indexes if specific queries are slow during testing.

---

## R2: Charting Library for Angular 19

**Decision**: Use `ng2-charts` (Angular wrapper for Chart.js) for frontend chart rendering.

**Rationale**: Chart.js is the most widely used charting library, lightweight (~60KB gzip), supports all needed chart types (line, bar, doughnut), handles RTL layout, and has excellent Angular integration via `ng2-charts`. The project already uses Angular Material which integrates well.

**Alternatives considered**:
- D3.js — rejected as too low-level for standard charts; requires significant custom code for basic line/bar charts.
- Apache ECharts — powerful but heavier (200KB+), better suited for complex interactive dashboards beyond current scope.
- Highcharts — requires commercial license for enterprise use.

---

## R3: PDF Report Generation

**Decision**: Use the existing WeasyPrint-based PDF engine (`app/services/pdf/`) to render analytics reports as PDF.

**Rationale**: The project already has a working PDF rendering pipeline via WeasyPrint. Analytics PDF reports follow the same pattern: render HTML template → convert to PDF. Reuses existing infrastructure without adding new dependencies.

**Approach**: Create an HTML template for each report type, populate with data, render via WeasyPrint. Include chart images as base64-encoded PNGs (Chart.js can export canvas to image on frontend, send to backend for PDF embedding).

---

## R4: CSV Export Encoding

**Decision**: UTF-8 with BOM (`\xEF\xBB\xBF` prefix) for Arabic compatibility.

**Rationale**: Arabic text in CSV files must use UTF-8 with BOM to display correctly in Microsoft Excel (the primary tool enterprise customers use to open CSV files). Without BOM, Excel defaults to ANSI encoding and corrupts Arabic characters.

**Implementation**: Prepend BOM bytes to CSV output stream. Use Python's `csv` module with `utf-8-sig` encoding.

---

## R5: Role-Based Data Scoping Strategy

**Decision**: Implement scoping at the service layer using the authenticated user's profile (org_id, department_id, branch_id, role).

**Rationale**: Consistent with existing FormCraft patterns (e.g., `submission_service.py` uses `org_id` from `current_user`). The service layer applies WHERE clauses based on role:
- `org_admin` / `admin`: `WHERE org_id = :org_id` (all org data)
- `branch_manager`: `WHERE org_id = :org_id AND s.branch_id IN (SELECT id FROM branches WHERE department_id = :dept_id)` (department-scoped via branch→department join, since submissions has branch_id not department_id)
- `operator`: `WHERE operator_id = :user_id` (own data only)

RLS policies on the `submissions` table provide a second layer of defense at the database level.

---

## R6: Date Range Handling

**Decision**: Use ISO 8601 date strings (`YYYY-MM-DD`) for API parameters with preset aliases.

**Rationale**: Standard format, timezone-agnostic at the day level, easy to parse in both Python and TypeScript.

**Presets**: `today`, `this_week`, `this_month`, `this_quarter`, `this_year`, `last_7_days`, `last_30_days`, `custom` (with `date_from` + `date_to` params).

**Period comparison**: For trend charts, automatically compute the comparison period (e.g., "this month" compares to "last month" with same day count).
