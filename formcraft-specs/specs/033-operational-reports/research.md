# Research: Operational Report Engine

## Decision 1: Excel Generation Library

**Decision**: openpyxl
**Rationale**: Pure Python, supports .xlsx format, handles RTL text, cell styling, charts, and large datasets via write-only mode. Already common in enterprise Python projects. No binary dependencies.
**Alternatives considered**:
- xlsxwriter: Faster write performance but no read capability; openpyxl's write-only mode is comparable for large exports.
- pandas + openpyxl: Adds pandas dependency just for export; overkill when we already build data via SQL.

## Decision 2: PDF Report Generation

**Decision**: WeasyPrint (already in stack)
**Rationale**: Constitution locks WeasyPrint for PDF rendering. Reports use HTML/CSS templates rendered to PDF. RTL support via CSS `direction: rtl`. Charts rendered as inline SVG or pre-rendered PNG.
**Alternatives considered**:
- ReportLab: Lower-level, more control but doesn't align with existing WeasyPrint investment.
- wkhtmltopdf: External binary, deprecated upstream.

## Decision 3: Report Scheduling

**Decision**: APScheduler with PostgreSQL job store
**Rationale**: Lightweight, embeds in FastAPI process, supports cron-style schedules (daily/weekly/monthly). PostgreSQL job store ensures schedules survive restarts and work across multiple workers. No external service dependency.
**Alternatives considered**:
- Celery Beat: Heavyweight; requires Redis/RabbitMQ broker. Overkill for report scheduling.
- pg_cron (PostgreSQL extension): Supabase Cloud may not support custom extensions. Less flexible for dynamic schedule CRUD.
- External scheduler (Cloud Scheduler, etc.): Ties to specific cloud provider; Bunny Containers may not have native scheduler.

## Decision 4: Email Delivery

**Decision**: Resend API (HTTP-based email delivery)
**Rationale**: Simple REST API, no SMTP configuration needed. Supports attachments (report files). Already used in FormCraft for invitation emails. Transactional email with delivery tracking.
**Alternatives considered**:
- SMTP direct: Requires SMTP server management, connection pooling, retry logic.
- SendGrid/Mailgun: Viable but Resend already integrated in the platform.

## Decision 5: Large Dataset Handling Strategy

**Decision**: Server-side pagination for UI display + streaming/chunked generation for exports
**Rationale**: Transaction register UI uses cursor-based pagination (keyset pagination on `created_at` + `id`). Export generation streams rows to file without loading all into memory. Reports > 100K rows use async generation with progress tracking via polling endpoint.
**Alternatives considered**:
- Client-side pagination: Not feasible for 10K+ rows.
- Background job queue (Celery): Overkill; async endpoint with in-process task + status polling suffices for report generation.

## Decision 6: Cross-Template Custom Report Query Engine

**Decision**: Dynamic SQL query builder with field-type alignment
**Rationale**: Custom reports select multiple templates and align fields by designer-assigned type tags (amount, date, customer, text). The query engine:
1. Collects selected templates' element definitions
2. Groups elements by type tag across templates
3. Builds a UNION-style query extracting `field_data->>'{field_key}'` from each template's submissions
4. Applies selected aggregations (SUM, COUNT, AVG, GROUP BY)

This approach leverages PostgreSQL's JSON operators on the existing `field_data` JSONB column without requiring schema changes.
**Alternatives considered**:
- Materialized views per template: Rigid, requires migration per template change.
- Pre-computed aggregation tables: Adds write complexity to submission flow.

## Decision 7: Chart Rendering for PDF Export

**Decision**: Server-side chart generation via matplotlib (Python) rendered as SVG, embedded in WeasyPrint HTML
**Rationale**: Charts in PDF reports need to be server-rendered (no browser). Matplotlib produces clean SVG output. WeasyPrint renders inline SVG. Frontend charts use Chart.js independently.
**Alternatives considered**:
- Puppeteer/Playwright headless rendering: Heavy dependency, slow startup. Inappropriate for containerized backend.
- Chart.js server-side (chartjs-node-canvas): Requires Node.js; we're Python-only backend.

## Decision 8: Amount Field Identification

**Decision**: Element `field_type_tag` column on template elements
**Rationale**: Per clarification, designers tag fields as "amount" type during template design. This is stored as a `field_type_tag` enum value on the `elements` table. Report engine filters `WHERE field_type_tag = 'amount'` to identify summable fields. No heuristics or naming conventions needed.
**Alternatives considered**:
- Convention-based detection: Fragile, depends on field naming.
- Separate configuration table: Over-engineered; a column on elements is sufficient.
