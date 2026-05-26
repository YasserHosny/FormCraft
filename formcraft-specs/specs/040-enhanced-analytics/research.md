# Research: Enhanced Analytics Dashboard

**Feature**: 040-enhanced-analytics
**Date**: 2026-05-26

## Decisions

### 1. Aggregation Strategy: Materialized Views vs Real-Time Queries

**Decision**: Use PostgreSQL materialized views refreshed every 15 minutes for all analytics except compliance scorecards.

**Rationale**: F027 uses live aggregation queries against existing tables. F040 performance targets (5s for 10k submissions, 3s for 100 operators) require pre-aggregation. PostgreSQL materialized views provide a native, RLS-compatible solution without introducing additional infrastructure (Redis, ClickHouse, etc.). Compliance scorecards use on-demand computation with 24h caching because they involve complex cross-table joins (templates, elements, validators) that are harder to maintain as materialized views.

**Alternatives considered**:
- Real-time queries with heavy indexing: Rejected — would not meet 5s target for field-level analytics across 10k submissions.
- RedisTimeSeries / ClickHouse: Rejected — adds infrastructure complexity; constitution favors simplicity and YAGNI.
- Application-level caching: Rejected — harder to invalidate consistently than database-level materialized views.

### 2. Data Retention: Hot vs Archive

**Decision**: 90 days hot retention in detail tables, daily rollup aggregates archived for 1 year.

**Rationale**: Field-level analytics at submission granularity generates significant data volume. 90 days covers typical operational reporting needs (monthly/quarterly reviews). Annual compliance audits require historical trends, so daily aggregates provide sufficient granularity at lower storage cost.

**Alternatives considered**:
- Infinite retention: Rejected — storage cost and query degradation.
- 30 days hot only: Rejected — insufficient for quarterly operational reviews.

### 3. Charting Library

**Decision**: Use Chart.js via ng2-charts (already in project per AGENTS.md).

**Rationale**: Project already uses ng2-charts/Chart.js for F033 operational reports. Consistency reduces learning curve and bundle size. Chart.js supports all required visualizations: bar charts (error rates), line charts (version adoption), heatmaps (busiest hours via matrix plugin), and funnel charts (via custom stacked bar or chartjs-plugin-funnel).

**Alternatives considered**:
- D3.js: Rejected — steeper learning curve, more code for standard charts.
- ApexCharts: Rejected — not already in project; would increase bundle size.

### 4. Export Formats

**Decision**: CSV for tabular data, PNG for chart images, PDF for full reports.

**Rationale**: CSV is universally importable into Excel/Google Sheets for further analysis. PNG captures chart visualizations for presentations. PDF full reports use existing WeasyPrint infrastructure for printable, RTL-safe output.

**Alternatives considered**:
- Excel (.xlsx): Rejected — openpyxl is already in project but CSV is simpler and sufficient for analytics export; can add .xlsx later if requested.
- SVG export: Rejected — PNG is more universally usable in presentations and documents.

### 5. Integration with F027

**Decision**: Extend existing F027 analytics infrastructure rather than creating a parallel system.

**Rationale**: F027 already defines submission volume, branch breakdown, template usage, and operator productivity queries. F040 adds deeper metrics (field-level, compliance scorecards, completion funnels). Reusing the same `/api/analytics/*` route prefix and existing RLS patterns maintains consistency.

**Alternatives considered**:
- Separate `/api/v2/analytics` namespace: Rejected — unnecessary versioning for additive features.
- Completely independent analytics service: Rejected — violates YAGNI; no need for separate deployment unit.

### 6. Compliance Scorecard Computation

**Decision**: Compute compliance scorecards on-demand with 24-hour result caching in a dedicated `compliance_scorecard_cache` table.

**Rationale**: Compliance metrics require scanning templates, elements, and validators across the entire org — expensive to keep in a materialized view. A computed-on-demand approach with caching balances freshness and performance. The cache table provides simple invalidation (truncate on demand, TTL-based refresh).

**Alternatives considered**:
- Materialized view for compliance: Rejected — would refresh unnecessarily frequently; most compliance checks change slowly (template edits).
- Real-time computation without cache: Rejected — would not meet 10s target for 500+ templates.
