# Data Model: Batch Operations & Print Queue

## Existing Entities Used

### Template

Source table: `templates`

Relevant fields:
- `id` UUID primary key
- `org_id` UUID
- `name` text
- `status` text
- `version` integer
- `created_by` UUID
- `updated_at` timestamptz

F036 usage:
- Batch jobs and schedules reference a published template.
- Column mapping targets template field `key` values extracted from the template's pages/elements.
- Validation reuses template rules and element validators.

### Page and Element

Source tables: `pages`, `elements`

F036 usage:
- Template field keys are derived from elements with `control_type != 'static'`.
- Validation rules (required, format, min/max, regex, conditions) are read from element config.
- PDF rendering reuses the existing render pipeline for the pinned template version.

### Form Submission

Source table: `form_submissions`

F036 extension:
- Add `batch_job_id` UUID nullable, references `batch_jobs(id)` on delete set null.
- Add `batch_generated` boolean not null default false.

F036 usage:
- Each successfully generated PDF is logged as a form submission with `batch_generated = true` and `batch_job_id` set.
- Submissions respect existing org-scoped RLS and audit logging.
- Batch-generated submissions appear in standard submission history and reports.

### Organization and Org Settings

Source tables: `organizations`, `org_settings`

F036 usage:
- Batch jobs and schedules are org-scoped.
- `max_batch_size` is read from org settings and enforced at job creation.

### Profile

Source table: `profiles`

F036 usage:
- `created_by` references the operator/admin who created the batch job or schedule.

## New Entity: Batch Job

Source table: `batch_jobs`

Fields:
- `id` UUID primary key, default `gen_random_uuid()`
- `org_id` UUID not null, references `organizations(id)` on delete cascade
- `template_id` UUID not null, references `templates(id)`
- `template_version` integer not null
- `created_by` UUID not null, references `profiles(id)`
- `name` text not null
- `status` text not null default `queued`, allowed values `queued`, `running`, `completed`, `failed`, `cancelled`
- `data_source_type` text not null, allowed values `csv`, `xlsx`, `clipboard`
- `data_source_id` UUID nullable, references `batch_data_sources(id)` on delete set null
- `column_mapping` JSONB not null default `{}`::jsonb
  - shape: `{ "csv_column_name": "template_field_key", ... }`
- `row_count` integer not null default 0
- `success_count` integer not null default 0
- `fail_count` integer not null default 0
- `progress` integer not null default 0
  - number of PDFs generated so far
- `duplicate_strategy` text not null default `warn`, allowed values `warn`, `skip`, `include`
- `duplicate_count` integer not null default 0
- `download_format` text not null default `zip`, allowed values `zip`, `merged_pdf`, `printer_queue`
- `printer_profile_id` UUID nullable, references `printer_profiles(id)`
- `scheduled_job_id` UUID nullable, references `batch_schedules(id)` on delete set null
  - populated when the job was triggered by a schedule
- `started_at` timestamptz nullable
- `completed_at` timestamptz nullable
- `cancelled_at` timestamptz nullable
- `cancelled_by` UUID nullable, references `profiles(id)`
- `error_summary` text nullable
- `created_at` timestamptz not null default `now()`
- `updated_at` timestamptz not null default `now()`

Validation rules:
- `(org_id, name)` is not unique; names are user-provided and may repeat.
- `status` transitions:
  - `queued -> running`
  - `running -> completed | failed | cancelled`
  - no other transitions allowed
- `template_id` must reference a published template at creation time.
- `printer_profile_id` is required when `download_format = printer_queue`.
- `progress <= row_count` always.

State transitions:

```text
queued -> running -> completed
queued -> running -> failed
queued -> running -> cancelled
```

Indexes:
- `idx_batch_jobs_org_status` on `batch_jobs(org_id, status, updated_at)`
- `idx_batch_jobs_template` on `batch_jobs(template_id)`
- `idx_batch_jobs_created_by` on `batch_jobs(created_by)`

RLS:
- `batch_jobs` ENABLE ROW LEVEL SECURITY
- Policy: `batch_jobs_org_isolation` — ALL operations scoped to `current_setting('app.current_org_id')::UUID`

## New Entity: Batch Data Source

Source table: `batch_data_sources`

Fields:
- `id` UUID primary key, default `gen_random_uuid()`
- `org_id` UUID not null, references `organizations(id)` on delete cascade
- `file_name` text not null
- `storage_path` text not null
  - Supabase Storage path (org-scoped private bucket)
- `mime_type` text not null
  - allowed: `text/csv`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- `file_size_bytes` integer not null
  - must be `<= 10 * 1024 * 1024` (10 MB)
- `encoding` text nullable
  - detected encoding (UTF-8, Windows-1256, etc.)
- `column_headers` JSONB not null default `[]`::jsonb
  - ordered array of header strings
- `checksum` text not null
  - SHA-256 of file contents
- `created_by` UUID not null, references `profiles(id)`
- `created_at` timestamptz not null default `now()`
- `updated_at` timestamptz not null default `now()`

Validation rules:
- `mime_type` and `file_name` extension must match whitelist (.csv, .xlsx).
- `file_size_bytes` must not exceed 10 MB.
- Auto-purged by cleanup job 30 days after `created_at` if the linked batch job is completed/failed/cancelled.

Indexes:
- `idx_batch_data_sources_org` on `batch_data_sources(org_id, created_at)`

RLS:
- `batch_data_sources` ENABLE ROW LEVEL SECURITY
- Policy: `batch_data_sources_org_isolation` — ALL operations scoped to `current_setting('app.current_org_id')::UUID`

## New Entity: Batch Schedule

Source table: `batch_schedules`

Fields:
- `id` UUID primary key, default `gen_random_uuid()`
- `org_id` UUID not null, references `organizations(id)` on delete cascade
- `template_id` UUID not null, references `templates(id)`
- `created_by` UUID not null, references `profiles(id)`
- `name` text not null
- `enabled` boolean not null default false
- `data_source_type` text not null, allowed value `api`
- `api_endpoint` text not null
- `api_auth_type` text not null, allowed values `api_key`, `bearer_token`
- `api_auth_credential` text not null
  - encrypted storage of key/token
- `api_headers` JSONB not null default `{}`::jsonb
- `cron_expression` text not null
  - validated as a valid 5-field cron expression
- `notification_recipients` JSONB not null default `[]`::jsonb
  - array of `{ mode: "email", address: "..." }`
- `column_mapping` JSONB not null default `{}`::jsonb
  - same shape as batch job mapping; may be pre-configured
- `download_format` text not null default `zip`, allowed values `zip`, `merged_pdf`, `printer_queue`
- `printer_profile_id` UUID nullable, references `printer_profiles(id)`
- `max_rows_per_run` integer not null default 1000
- `last_run_at` timestamptz nullable
- `last_run_status` text nullable, allowed values `success`, `failed`, `cancelled`
- `last_run_job_id` UUID nullable, references `batch_jobs(id)` on delete set null
- `next_run_at` timestamptz nullable
- `failure_count` integer not null default 0
- `created_at` timestamptz not null default `now()`
- `updated_at` timestamptz not null default `now()`

Validation rules:
- `template_id` must reference a published template.
- `api_auth_credential` must be encrypted at rest.
- `cron_expression` is validated by APScheduler's `CronTrigger` parser.
- `next_run_at` is computed from `cron_expression` and updated after each run.
- `failure_count` is reset to 0 on a successful run.

State transitions:

```text
disabled -> enabled
enabled -> disabled
```

Indexes:
- `idx_batch_schedules_org_enabled` on `batch_schedules(org_id, enabled)`
- `idx_batch_schedules_next_run` on `batch_schedules(next_run_at)` where `enabled = true`

RLS:
- `batch_schedules` ENABLE ROW LEVEL SECURITY
- Policy: `batch_schedules_org_isolation` — ALL operations scoped to `current_setting('app.current_org_id')::UUID`

## New Entity: Batch Error

Source table: `batch_errors`

Fields:
- `id` UUID primary key, default `gen_random_uuid()`
- `org_id` UUID not null, references `organizations(id)` on delete cascade
- `batch_job_id` UUID not null, references `batch_jobs(id)` on delete cascade
- `row_number` integer not null
  - 1-based index into the original data source
- `field_key` text nullable
  - nullable for row-level errors (e.g., duplicate row)
- `error_type` text not null, allowed values `validation`, `generation`, `mapping`, `duplicate`, `template_changed`
- `error_message` text not null
- `created_at` timestamptz not null default `now()`

Validation rules:
- `row_number >= 1`.
- Errors are immutable after creation.

Indexes:
- `idx_batch_errors_job` on `batch_errors(batch_job_id, row_number)`
- `idx_batch_errors_type` on `batch_errors(batch_job_id, error_type)`

RLS:
- `batch_errors` ENABLE ROW LEVEL SECURITY
- Policy: `batch_errors_org_isolation` — ALL operations scoped to `current_setting('app.current_org_id')::UUID`

## Cleanup and Retention

- **Batch Data Sources**: A periodic cleanup task (nightly APScheduler job) deletes Supabase Storage objects and `batch_data_sources` rows where `created_at < now() - interval '30 days'` and the linked `batch_job.status` is in (`completed`, `failed`, `cancelled`).
- **Batch Errors**: No automatic deletion in v1; operators download and clear manually if needed. Large error sets may be purged in a future housekeeping feature.
- **Batch Jobs**: Soft-delete is not used; jobs remain for audit. Admins can delete completed jobs explicitly, which cascades to errors.

## Derived Views

No materialized views are required for v1. Queue dashboard queries use indexed filters on `batch_jobs(org_id, status, updated_at)`. Future scale may justify a `batch_jobs_summary` materialized view if org-level job volume exceeds 10,000 active rows.
