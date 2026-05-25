# Data Model: Data Export & Integration

## Existing Entities Used

### Template

Source table: `templates`

Relevant fields:
- `id` UUID primary key
- `org_id` UUID
- `name` text
- `status` text
- `version` integer
- `lineage_id` UUID
- `created_by` UUID
- `department_id` UUID nullable
- `category` text nullable
- `updated_at` timestamptz

F32 usage:
- Template package export reads template/page/element/rule metadata.
- Package import creates a new draft template or a new version when lineage/name matches.
- Webhook event `template_published` fires from existing publish transition.

### Template Page

Source table: `pages`

Relevant fields:
- `id` UUID primary key
- `template_id` UUID
- `width_mm`, `height_mm`
- `background_asset`
- `sort_order`

F32 usage:
- Included in `.formcraft` package with exact mm dimensions and background references.

### Template Element

Source table: `elements`

Relevant fields:
- `id` UUID primary key
- `page_id` UUID
- `type` text
- `key` text
- `label_ar`, `label_en` text nullable
- `validation` JSONB nullable
- `conditions`/visibility metadata if present in applied migrations
- `x_mm`, `y_mm`, `width_mm`, `height_mm`

F32 usage:
- Flattened export uses element `key` as stable column name.
- Template package includes element metadata and validator/condition configuration.
- Import remapping preserves field keys unless conflicts require review.

### Form Submission

Source table: `form_submissions`

Relevant fields:
- `id` UUID primary key
- `org_id` UUID
- `template_id` UUID
- `template_version` integer
- `operator_id` UUID
- `branch_id` UUID nullable
- `department_id` UUID nullable, if available through template/operator joins
- `status` text
- `field_data` JSONB
- `created_at` timestamptz
- `updated_at` timestamptz

F32 usage:
- Filtered one-time and recurring submission exports.
- Webhook event `form_submitted`.
- Print-related event `form_printed` may derive from existing print/audit flow.

## New Entity: Export Request

Source table: `export_requests`

Fields:
- `id` UUID primary key, default `gen_random_uuid()`
- `org_id` UUID not null, references `organizations(id)`
- `requested_by` UUID not null, references `profiles(id)`
- `schedule_id` UUID nullable, references `export_schedules(id)` on delete set null
- `dataset` text not null, allowed value `submissions` for F32
- `filters` JSONB not null
- `format` text not null, allowed values `csv`, `xlsx`, `json`
- `scope` text not null, allowed values `flattened`, `structured`
- `matching_count` integer not null default 0
- `status` text not null, allowed values `previewed`, `completed`, `rejected`, `failed`
- `rejection_reason` text nullable
- `file_name` text nullable
- `file_size_bytes` bigint nullable
- `completed_at` timestamptz nullable
- `created_by` UUID not null, references `profiles(id)`
- `created_at` timestamptz not null default `now()`
- `updated_at` timestamptz not null default `now()`

Validation rules:
- `matching_count` and estimated file size must be under configured limits before direct download generation.
- Oversized one-time exports create a rejected request record or preview response with rejection metadata.
- `filters` must be org-scoped and may include template, date range, department, branch, operator, and status.

## New Entity: Export Schedule

Source table: `export_schedules`

Fields:
- `id` UUID primary key, default `gen_random_uuid()`
- `org_id` UUID not null, references `organizations(id)`
- `name` text not null
- `created_by` UUID not null, references `profiles(id)`
- `dataset` text not null, allowed value `submissions`
- `filters` JSONB not null
- `format` text not null, allowed values `csv`, `xlsx`, `json`
- `scope` text not null, allowed values `flattened`, `structured`
- `frequency` text not null, allowed values `daily`, `weekly`
- `email_recipients` text[] not null
- `no_data_behavior` text not null default `send_empty_file`, allowed values `send_empty_file`, `send_notice`
- `status` text not null default `active`, allowed values `active`, `paused`, `disabled`
- `next_run_at` timestamptz not null
- `last_run_at` timestamptz nullable
- `created_at` timestamptz not null default `now()`
- `updated_at` timestamptz not null default `now()`

Validation rules:
- Only org admins can create/update/delete schedules.
- Email recipients must be non-empty for active schedules.
- SFTP/file-transfer destinations are not valid in F32.

State transitions:

```text
active <-> paused
active -> disabled
paused -> disabled
```

## New Entity: Export Delivery

Source table: `export_deliveries`

Fields:
- `id` UUID primary key, default `gen_random_uuid()`
- `org_id` UUID not null, references `organizations(id)`
- `schedule_id` UUID not null, references `export_schedules(id)` on delete cascade
- `export_request_id` UUID nullable, references `export_requests(id)` on delete set null
- `email_recipients` text[] not null
- `status` text not null, allowed values `queued`, `sent`, `failed`
- `attempt_count` integer not null default 0
- `failure_reason` text nullable
- `sent_at` timestamptz nullable
- `created_by` UUID nullable, references `profiles(id)`
- `created_at` timestamptz not null default `now()`
- `updated_at` timestamptz not null default `now()`

Validation rules:
- Delivery records are created only for recurring export schedules.
- Delivery summaries never expose generated file contents.

## New Entity: Integration Credential

Source table: `integration_credentials`

Fields:
- `id` UUID primary key, default `gen_random_uuid()`
- `org_id` UUID not null, references `organizations(id)`
- `name` text not null
- `key_hash` text not null
- `key_prefix` text not null
- `scopes` text[] not null
- `status` text not null default `active`, allowed values `active`, `revoked`, `expired`
- `expires_at` timestamptz nullable
- `last_used_at` timestamptz nullable
- `revoked_at` timestamptz nullable
- `revoked_by` UUID nullable, references `profiles(id)`
- `created_by` UUID not null, references `profiles(id)`
- `created_at` timestamptz not null default `now()`
- `updated_at` timestamptz not null default `now()`

Validation rules:
- Secret value is shown once and never stored in plaintext.
- Revoked credentials stop granting access immediately.
- Scopes are explicit and org-scoped.

State transitions:

```text
active -> revoked
active -> expired
```

## New Entity: Webhook Subscription

Source table: `webhook_subscriptions`

Fields:
- `id` UUID primary key, default `gen_random_uuid()`
- `org_id` UUID not null, references `organizations(id)`
- `name` text not null
- `event_type` text not null, allowed values `form_submitted`, `form_printed`, `template_published`, `batch_completed`
- `target_url` text not null
- `signing_secret_hash` text not null
- `signing_secret_prefix` text nullable
- `status` text not null default `active`, allowed values `active`, `paused`, `disabled`
- `created_by` UUID not null, references `profiles(id)`
- `created_at` timestamptz not null default `now()`
- `updated_at` timestamptz not null default `now()`

Validation rules:
- Active subscriptions require a signing secret.
- Only HTTPS URLs are valid outside local/dev test environments.
- Each delivery is signed using the active subscription secret.

State transitions:

```text
active <-> paused
active -> disabled
paused -> disabled
```

## New Entity: Webhook Delivery

Source table: `webhook_deliveries`

Fields:
- `id` UUID primary key, default `gen_random_uuid()`
- `org_id` UUID not null, references `organizations(id)`
- `subscription_id` UUID not null, references `webhook_subscriptions(id)` on delete cascade
- `event_type` text not null
- `event_id` UUID not null
- `payload_preview` JSONB not null
- `signature_header` text not null
- `status` text not null, allowed values `queued`, `delivered`, `failed`
- `attempt_count` integer not null default 0
- `next_retry_at` timestamptz nullable
- `last_response_code` integer nullable
- `last_response_body_preview` text nullable
- `delivered_at` timestamptz nullable
- `created_by` UUID nullable, references `profiles(id)`
- `created_at` timestamptz not null default `now()`
- `updated_at` timestamptz not null default `now()`

Validation rules:
- `payload_preview` stores the full webhook payload and is visible only to authorized org admins.
- Failed deliveries retry up to three attempts with exponential backoff.
- Delivery status becomes `failed` after the third failed attempt.

State transitions:

```text
queued -> delivered
queued -> failed
failed -> queued   # only while retry attempts remain
```

## Computed/Packaged Model: Template Package

Not stored as a table by default.

Fields in `.formcraft` bundle:
- `package_version`
- `exported_at`
- `source_org_id`
- `source_template_id`
- `template_lineage_id`
- `template`
- `pages`
- `elements`
- `validators`
- `conditions`
- `reference_bindings`
- `checksum`

Validation rules:
- Unsupported future package versions are rejected.
- Checksum mismatch rejects import.
- Matching lineage or template name creates a new version of the existing template.
- No match creates a new draft template.
- Missing departments, branches, reference lists, or validators produce import review warnings/remapping before use.

## Migration Sketch

```sql
CREATE TABLE IF NOT EXISTS export_requests (...);
CREATE TABLE IF NOT EXISTS export_schedules (...);
CREATE TABLE IF NOT EXISTS export_deliveries (...);
CREATE TABLE IF NOT EXISTS integration_credentials (...);
CREATE TABLE IF NOT EXISTS webhook_subscriptions (...);
CREATE TABLE IF NOT EXISTS webhook_deliveries (...);

ALTER TABLE export_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE export_schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE export_deliveries ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhook_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhook_deliveries ENABLE ROW LEVEL SECURITY;

CREATE INDEX idx_export_requests_org_created ON export_requests(org_id, created_at DESC);
CREATE INDEX idx_export_schedules_org_status_next_run ON export_schedules(org_id, status, next_run_at);
CREATE INDEX idx_export_deliveries_schedule_created ON export_deliveries(schedule_id, created_at DESC);
CREATE INDEX idx_integration_credentials_org_status ON integration_credentials(org_id, status);
CREATE INDEX idx_webhook_subscriptions_org_event_status ON webhook_subscriptions(org_id, event_type, status);
CREATE INDEX idx_webhook_deliveries_subscription_created ON webhook_deliveries(subscription_id, created_at DESC);
CREATE INDEX idx_webhook_deliveries_retry ON webhook_deliveries(status, next_retry_at);
```
