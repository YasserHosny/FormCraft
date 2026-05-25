# Feature Specification: Batch Operations & Print Queue

**Feature Branch**: `036-batch-operations`  
**Created**: 2026-05-25  
**Status**: Draft  
**Vision Reference**: FD-06

## User Scenarios & Testing

### User Story 1 - Batch Form Generation from Data Source (Priority: P1)

As an operator or admin, I need to select a template, upload a CSV/Excel data source, map columns to template fields, validate all rows, and generate batch PDFs, so I can produce hundreds of pre-filled forms (e.g., monthly statements, certificates) without manual entry.

**Why this priority**: Highest enterprise value — batch processing is the single biggest time saver for organizations producing high volumes of forms (bank statements, certificates, payroll cheques).

**Independent Test**: Navigate to `/desk/queue`, create new batch job, upload CSV, map columns, validate, generate 100 PDFs, download as ZIP.

**Acceptance Scenarios**:

1. **Given** operator navigates to `/desk/queue` and clicks "New Batch Job", **When** they select a published template, **Then** Step 2 shows data source options: CSV upload, Excel upload, clipboard paste.
2. **Given** operator uploads a CSV, **When** the column mapping step loads, **Then** a drag-drop mapper shows CSV columns on the left and template field keys on the right, with auto-mapping by header match.
3. **Given** columns are mapped, **When** validation runs, **Then** each row shows green (valid) or red (invalid with specific field errors), and a summary shows "480 valid, 20 invalid".
4. **Given** operator clicks "Generate" for valid rows, **When** the background job runs, **Then** a progress bar shows "Generated 127/480 PDFs" and each PDF is logged as an individual form_submission with batch_job_id.
5. **Given** generation completes, **When** operator clicks "Download", **Then** options show: individual PDFs as ZIP, single merged PDF, or send to network printer queue.

---

### User Story 2 - Queue Dashboard & Job Management (Priority: P2)

As an operator or admin, I need a queue dashboard showing active, completed, and failed batch jobs with progress tracking, download links, and error reports, so I can monitor batch operations and troubleshoot failures.

**Why this priority**: Operational visibility — without a dashboard, operators have no way to track or manage batch jobs.

**Independent Test**: Navigate to `/desk/queue`, see active job with progress bar, completed jobs with download links, failed job with error report.

**Acceptance Scenarios**:

1. **Given** a batch job is running, **When** operator views the queue, **Then** the active job shows: template name, row count, progress bar, estimated time remaining, cancel button.
2. **Given** a job completed successfully, **When** viewing completed jobs, **Then** each shows: template name, row count, success/fail count, timestamp, download link.
3. **Given** a job had partial failures, **When** operator clicks the failed job, **Then** an error report shows which rows failed and why (specific validation errors per row) with a "Download Error Report CSV" button.

---

### User Story 3 - Scheduled Recurring Batches (Priority: P3)

As an admin, I need to configure recurring batch jobs that pull data from an API endpoint on a schedule (cron expression), generate forms automatically, and notify on completion or failure, so routine report generation runs without manual intervention.

**Why this priority**: Automation — eliminates the daily/weekly manual batch generation burden for routine operations like statements.

**Independent Test**: Configure a weekly batch job with API data source and email notification, verify it auto-runs and notifies.

**Acceptance Scenarios**:

1. **Given** admin configures a scheduled batch, **When** they set template + API endpoint + cron schedule, **Then** the system validates the API returns data in the expected format.
2. **Given** the scheduled time arrives, **When** the system pulls data and generates PDFs, **Then** an email notification is sent to configured recipients with success/failure summary.
3. **Given** a scheduled job fails, **When** the API is unreachable, **Then** the system retries once after 15 minutes and sends a failure notification if retry also fails.

---

### Edge Cases

- What happens when a batch job is cancelled mid-generation? Partial results should be downloadable.
- How does the system handle CSV files with inconsistent encoding (UTF-8 vs Windows-1256 for Arabic)?
- What happens when the merged PDF exceeds storage limits?
- How does the system handle a batch referencing a template that gets unpublished mid-job?
- What happens when two operators start batch jobs for the same template simultaneously?

## Requirements

### Functional Requirements

- **FR-001**: System MUST support batch form generation from CSV, Excel (.xlsx), and clipboard paste data sources.
- **FR-002**: System MUST provide a column mapping UI with auto-mapping by header match and drag-drop manual mapping.
- **FR-003**: System MUST validate all rows against template rules before generation, showing per-row, per-field errors.
- **FR-004**: Batch generation MUST run as background jobs with real-time progress tracking.
- **FR-005**: System MUST support download as individual PDFs (ZIP), merged single PDF, or send to printer queue.
- **FR-006**: Each batch-generated PDF MUST be logged as an individual form_submission with batch_job_id reference.
- **FR-007**: System MUST provide a queue dashboard showing active, completed, and failed jobs.
- **FR-008**: Failed jobs MUST provide downloadable error reports with per-row failure details.
- **FR-009**: System MUST support scheduled recurring batch jobs with cron expressions and API data sources.
- **FR-010**: System MUST send email notifications on batch job completion or failure.
- **FR-011**: System MUST respect org-level max_batch_size setting.
- **FR-012**: Batch jobs MUST be cancellable with partial results preserved.

### Key Entities

- **Batch Job**: Template reference, data source type, column mapping, status (queued/running/completed/failed/cancelled), progress, row count, success count, fail count, created_by, timestamps.
- **Batch Schedule**: Template reference, data source (API endpoint + auth), cron expression, notification recipients, last run status, next run time.
- **Batch Error**: Job reference, row number, field key, error type, error message.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Batch generation of 500 PDFs completes within 5 minutes.
- **SC-002**: Column auto-mapping correctly maps 80%+ of columns for well-named CSV headers.
- **SC-003**: Validation of 1,000 rows completes within 10 seconds.
- **SC-004**: Queue dashboard updates progress in real-time (within 2 seconds of each PDF generated).
- **SC-005**: Scheduled batch jobs execute within 5 minutes of their configured time.
