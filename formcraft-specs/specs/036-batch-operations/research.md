# Research: Batch Operations & Print Queue

## Decision: Background Job Execution Model

Use an in-process async generation loop with polling-based status updates for on-demand batch jobs, and APScheduler for recurring scheduled batches.

**Rationale**: The project already uses APScheduler for report schedules, so recurring batch schedules reuse the same scheduler infrastructure. On-demand batch jobs are triggered via HTTP and run asynchronously in a background task loop (asyncio) within the FastAPI process, writing progress back to PostgreSQL. Operators poll the job status endpoint. This avoids introducing Celery/RQ infrastructure while meeting the 500 PDF / 5 minute target.

**Alternatives considered**:
- Celery with Redis broker: rejected because it adds new infrastructure (Redis, workers) not present in the project stack.
- Synchronous generation: rejected because HTTP timeouts would fail for batches > ~20 PDFs.
- APScheduler for on-demand jobs: rejected because APScheduler is better suited to cron-based recurring tasks; on-demand jobs need immediate start and granular progress tracking that is simpler with a direct async loop.

## Decision: Data Source Parsing Strategy

Use Python's built-in `csv` module for CSV and `openpyxl` for `.xlsx`. Clipboard paste is parsed as tab-separated or comma-separated via the same CSV parser.

**Rationale**: `openpyxl` is already a project dependency (used in reports and data export). The `csv` module requires no additional dependency. Both support streaming reads, which keeps memory bounded for 10 MB files. Clipboard paste is normalized to a string buffer and fed through `csv.DictReader`.

**Alternatives considered**:
- `pandas`: rejected because it is a heavy dependency and not already in the project; streaming with `csv`/`openpyxl` is sufficient.
- `xlrd` for `.xls`: rejected because the spec limits uploads to `.xlsx` and `.csv`.

## Decision: File Upload Storage

Store uploaded data sources temporarily in Supabase Storage (org-scoped private bucket) for the duration of processing, then delete after job completion or the 30-day retention deadline. Do not store raw uploads in the database.

**Rationale**: Supabase Storage is already used in the project. Keeping large CSV/XLSX out of PostgreSQL rows avoids table bloat. The `batch_data_sources` table stores metadata (path, MIME type, size, checksum) and a reference to the storage path.

**Alternatives considered**:
- Store file contents as BYTEA in PostgreSQL: rejected because it bloats the database and complicates backups.
- Store on local filesystem: rejected because containers are ephemeral; Supabase Storage is the project's chosen persistence layer.

## Decision: ZIP Generation

Generate ZIP archives on-the-fly using Python's `zipfile` module with streaming response. For merged single PDF, use `pypdf` or WeasyPrint multi-page document.

**Rationale**: Python `zipfile` is in the standard library and supports streaming writes to an HTTP response. For merged PDF, the existing WeasyPrint renderer can produce a multi-page HTML document, or individual PDFs can be concatenated with `pypdf` if already available.

**Alternatives considered**:
- Pre-generate ZIP and store in Supabase Storage: rejected because it doubles storage usage; on-demand generation is acceptable since downloads happen after completion.
- Use `pypdf` for merging if not present: deferred; WeasyPrint multi-page HTML is the primary path.

## Decision: Duplicate Detection

Detect exact duplicate rows during validation by hashing the mapped-column values of each row. Flag duplicates with a warning; operator chooses skip or include.

**Rationale**: Simple, deterministic, and fast. Hashing (MD5/SHA256 of normalized JSON array) avoids O(n²) string comparisons. The operator decision is stored per job so the choice is auditable.

**Alternatives considered**:
- Fuzzy duplicate detection: rejected as over-engineered for v1; exact match covers the common case of literal repeated rows.
- Always skip duplicates silently: rejected because the operator needs visibility into data quality.

## Decision: Column Auto-Mapping

Auto-map CSV/Excel columns to template fields by normalizing headers (lowercase, strip spaces, underscore replace) and matching against template field `key` values using substring similarity.

**Rationale**: The success criterion targets 80%+ accuracy for well-named headers. Normalization + simple key matching is fast and predictable. No machine learning or fuzzy logic is required.

**Alternatives considered**:
- AI-powered header matching: rejected by constitution (deterministic over probabilistic) and YAGNI.
- Manual mapping only: rejected because it would fail the SC-002 target.

## Decision: Scheduled API Authentication

Support API key (custom header) and Bearer token for scheduled batch API data sources. Store credentials encrypted in the `batch_schedules` table using the project's existing encryption pattern.

**Rationale**: The clarification specifies these two methods for v1. OAuth 2.0 is deferred. Encrypting credentials at rest satisfies the security principle.

**Alternatives considered**:
- OAuth 2.0 in v1: rejected because it adds flows (redirect, refresh tokens) not justified by initial scope.
- Plaintext credential storage: rejected for security.

## Decision: Progress Tracking

Track batch job progress by updating a `progress` counter (generated count) and `status` in PostgreSQL after every N PDFs (e.g., every 10) to reduce write load while keeping polling updates within 2 seconds.

**Rationale**: Writing after every single PDF would create unnecessary database load for large batches. Batching progress writes (every 10 PDFs) balances accuracy and performance.

**Alternatives considered**:
- WebSocket/SSE real-time push: rejected because the project does not currently use WebSockets, and polling is sufficient for the 2-second update target.
- Write every single PDF: rejected because it adds ~500 writes for a 500-PDF batch.

## Decision: Error Report Format

Error reports are downloadable as CSV with columns: `row_number`, `field_key`, `error_type`, `error_message`. For validation-time errors, the report is generated immediately. For generation-time errors, the report is appended as rows fail.

**Rationale**: CSV is universally consumable, sortable in Excel, and easy to generate. Reusing the existing CSV export pattern keeps the stack consistent.

**Alternatives considered**:
- XLSX error report: deferred; CSV satisfies the requirement with less code.
- JSON error report: rejected because operators typically review errors in spreadsheet tools.
