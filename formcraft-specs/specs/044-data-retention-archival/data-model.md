# Data Model: Data Retention and Archival

## New Tables

### retention_policies

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PRIMARY KEY DEFAULT gen_random_uuid() | |
| org_id | uuid | NOT NULL, FK → organizations.id | Tenant scope |
| name | jsonb | NOT NULL | i18n object: `{ "ar": "...", "en": "..." }` |
| data_class | varchar(64) | NOT NULL | Enum: submission, customer_profile, audit_log, generated_pdf, export_file, portal_session, report_archive |
| scope_json | jsonb | NOT NULL DEFAULT '{}' | Filter object: `{ "template_category_id": "...", "branch_id": "...", "department_id": "..." }` |
| action | varchar(32) | NOT NULL | Enum: archive, purge, mask, retain |
| period_days | integer | NOT NULL | Retention period in days |
| legal_basis | varchar(128) | | e.g. "GDPR Article 5", "Saudi SAMA CBK 42" |
| approval_required | boolean | NOT NULL DEFAULT true | |
| effective_date | timestamptz | NOT NULL DEFAULT now() | |
| created_by | uuid | NOT NULL, FK → profiles.id | |
| created_at | timestamptz | NOT NULL DEFAULT now() | |
| updated_at | timestamptz | NOT NULL DEFAULT now() | |

**Indexes**: org_id + data_class (unique where active), effective_date
**RLS**: `org_id = auth.jwt() -> 'org_id'`

### retention_jobs

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PRIMARY KEY DEFAULT gen_random_uuid() | |
| policy_id | uuid | NOT NULL, FK → retention_policies.id | |
| status | varchar(32) | NOT NULL DEFAULT 'pending' | Enum: pending, running, paused, completed, failed |
| started_at | timestamptz | | |
| completed_at | timestamptz | | |
| batch_size | integer | NOT NULL DEFAULT 1000 | |
| checkpoint_cursor | varchar(255) | | Last processed id or composite cursor |
| evaluated_count | integer | NOT NULL DEFAULT 0 | |
| actioned_count | integer | NOT NULL DEFAULT 0 | |
| error_count | integer | NOT NULL DEFAULT 0 | |
| error_log | jsonb | NOT NULL DEFAULT '[]' | Array of {batch, error, timestamp} |
| skipped_records | jsonb | NOT NULL DEFAULT '[]' | Array of {record_id, reason, hold_id} |
| manifest_id | uuid | FK → archive_manifests.id | |
| resumed_from_job_id | uuid | FK → retention_jobs.id | Self-reference for resume chain |
| created_at | timestamptz | NOT NULL DEFAULT now() | |
| updated_at | timestamptz | NOT NULL DEFAULT now() | |

**Indexes**: policy_id + status, status + created_at
**RLS**: `org_id` resolved via JOIN to retention_policies

### legal_holds

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PRIMARY KEY DEFAULT gen_random_uuid() | |
| org_id | uuid | NOT NULL, FK → organizations.id | |
| hold_type | varchar(64) | NOT NULL | Enum: investigation, dispute, regulatory |
| scope_type | varchar(64) | NOT NULL | Enum: submission, customer, template, export, audit_evidence |
| scope_id | uuid | NOT NULL | Record UUID being held |
| reason | text | NOT NULL | Human-readable reason |
| expiry_date | timestamptz | | Optional automatic expiry |
| created_by | uuid | NOT NULL, FK → profiles.id | |
| created_at | timestamptz | NOT NULL DEFAULT now() | |
| updated_at | timestamptz | NOT NULL DEFAULT now() | |

**Indexes**: org_id + scope_type + scope_id (unique where no expiry or expiry > now), hold_type
**RLS**: `org_id = auth.jwt() -> 'org_id'`

### archive_manifests

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PRIMARY KEY DEFAULT gen_random_uuid() | |
| job_id | uuid | NOT NULL, FK → retention_jobs.id | |
| record_count | integer | NOT NULL | |
| schema_location | varchar(255) | NOT NULL | e.g. "archive_schema.form_submissions" |
| cold_storage_uri | text | | Supabase Storage path |
| sha256_hash | varchar(64) | NOT NULL | Hex-encoded SHA-256 |
| integrity_status | varchar(32) | NOT NULL DEFAULT 'verified' | Enum: verified, failed, pending |
| restore_conditions | jsonb | NOT NULL DEFAULT '{}' | Policy constraints for restore |
| created_at | timestamptz | NOT NULL DEFAULT now() | |

**Indexes**: job_id (unique), sha256_hash
**RLS**: `org_id` resolved via JOIN to retention_jobs → retention_policies

### privacy_requests

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PRIMARY KEY DEFAULT gen_random_uuid() | |
| org_id | uuid | NOT NULL, FK → organizations.id | |
| request_type | varchar(64) | NOT NULL | Enum: export, delete, mask, restrict |
| scope_type | varchar(64) | NOT NULL | Enum: customer, submission |
| scope_id | uuid | NOT NULL | |
| status | varchar(32) | NOT NULL DEFAULT 'pending' | Enum: pending, approved, rejected, completed, failed |
| conflict_hold_id | uuid | FK → legal_holds.id | Set if a legal hold blocks the request |
| resolution | jsonb | | { "action_taken": "mask", "reason": "..." } |
| created_by | uuid | NOT NULL, FK → profiles.id | |
| created_at | timestamptz | NOT NULL DEFAULT now() | |
| updated_at | timestamptz | NOT NULL DEFAULT now() | |

**Indexes**: org_id + status, scope_type + scope_id
**RLS**: `org_id = auth.jwt() -> 'org_id'`

## Archive Schema

Create a new PostgreSQL schema `archive` with shadow tables for each data class that supports archiving:

- `archive.form_submissions` (mirror of `form_submissions` with added `archived_at`, `original_id`, `manifest_id`)
- `archive.customer_profiles` (mirror of customer profiles with same additions)
- `archive.generated_pdfs` (metadata only; blobs moved to Supabase Storage)
- `archive.export_files` (metadata only)
- `archive.portal_sessions` (metadata only)

All archive tables have:
- `original_id` uuid (the id in the operational table)
- `archived_at` timestamptz DEFAULT now()
- `manifest_id` uuid FK → archive_manifests.id
- RLS policies identical to operational tables

## State Transitions

### Retention Job
```
pending -> running (on scheduler trigger)
running -> paused (admin action or error threshold)
running -> completed (all batches processed)
running -> failed (unrecoverable error)
paused -> running (resume)
paused -> failed (max resume attempts exceeded)
```

### Privacy Request
```
pending -> approved (admin review, no conflict)
pending -> rejected (admin review)
approved -> completed (action executed successfully)
approved -> failed (execution error)
```

## Relationships

```
retention_policies ||--o{ retention_jobs : "triggers"
retention_jobs ||--o| archive_manifests : "produces"
retention_jobs ||--o{ retention_jobs : "resumed_from"
legal_holds ||--o| privacy_requests : "blocks"
organizations ||--o{ retention_policies : "owns"
organizations ||--o{ legal_holds : "owns"
organizations ||--o{ privacy_requests : "owns"
profiles ||--o{ retention_policies : "created_by"
profiles ||--o{ legal_holds : "created_by"
profiles ||--o{ privacy_requests : "created_by"
```
