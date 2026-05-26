# Feature Specification: Data Retention and Archival

**Feature Branch**: `044-data-retention-archival`  
**Created**: 2026-05-26  
**Status**: Draft  
**Input**: User description: "Data retention and archival policies: compliance admins configure retention periods for submissions, customer profiles, audit logs, generated PDFs, and portal sessions; the system previews impact, archives or purges eligible data, supports legal holds, and records compliance evidence."

## Clarifications

### Session 2026-05-26

- Q: Where are archived records stored — same database, separate schema, or external object storage? → A: In a dedicated archive schema within the same PostgreSQL database, with optional cold export of large blobs (generated PDFs, exports) to Supabase Storage.
- Q: What scheduling and batching approach should retention jobs use? → A: Background scheduled jobs via APScheduler with configurable batch sizes of 1,000 records and idempotent execution.
- Q: Should archive manifests and purge evidence include cryptographic integrity checks? → A: Yes, SHA-256 hashes for all archive manifests and purge evidence records.
- Q: Should retention evidence reuse the existing audit_logs table or create a separate compliance table? → A: Extend the existing audit_logs table with compliance-specific event types (retention_job_started, retention_job_completed, record_archived, record_purged, legal_hold_applied, legal_hold_released).
- Q: What is the failure recovery model for interrupted retention jobs? → A: Partial commit with resume capability; each batch is committed independently and job progress is checkpointed in the retention_job record.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure Retention Policies (Priority: P1)

A compliance admin defines retention periods for operational data classes and previews which records will be archived, purged, or retained.

**Why this priority**: Regulated organizations need predictable data lifecycle controls before storing customer and submission data at scale.

**Independent Test**: Can be tested by creating a policy in a sandbox organization and confirming the preview identifies eligible records without changing data.

**Acceptance Scenarios**:

1. **Given** a compliance admin creates a submission retention policy, **When** they preview the policy, **Then** the system shows counts, date ranges, affected forms, and blocked records.
2. **Given** a policy would purge data still required by audit minimums, **When** the admin saves it, **Then** the system blocks or requires an approved exception.

---

### User Story 2 - Archive and Purge Eligible Data (Priority: P2)

The system runs approved retention jobs that archive records where required, purge records where allowed, and preserve evidence of the outcome.

**Why this priority**: Manual deletion is risky and does not scale across submissions, customer profiles, generated PDFs, exports, and portal sessions.

**Independent Test**: Can be tested by running a retention job against eligible sample records and confirming archive manifests, purge results, and audit events match the preview.

**Acceptance Scenarios**:

1. **Given** records are eligible for archival, **When** a retention job runs, **Then** records are moved to the configured archive state and an archive manifest is created.
2. **Given** records are eligible for purge, **When** a purge job completes, **Then** the data is no longer accessible from operational views and evidence remains in compliance logs.

---

### User Story 3 - Apply Legal Holds and Privacy Requests (Priority: P3)

A compliance admin places a legal hold or handles a customer privacy request without accidentally destroying required evidence.

**Why this priority**: Retention must support disputes, investigations, and customer rights while preserving immutable audit obligations.

**Independent Test**: Can be tested by placing a legal hold on a customer or submission and confirming retention jobs skip held records and report the reason.

**Acceptance Scenarios**:

1. **Given** a submission is under legal hold, **When** it reaches its purge date, **Then** the system retains it and records the hold as the reason.
2. **Given** a customer deletion request conflicts with a legal hold, **When** the request is reviewed, **Then** the system shows the conflict and permits only allowed masking or deferral.

### Edge Cases

- A retention policy is shortened retroactively and affects many old records.
- Archive storage fails after some records are marked for archival.
- A customer profile is merged after one profile is under legal hold.
- Generated PDFs, export files, and report archives reference purged submissions.
- Audit logs have longer minimum retention than the records they describe.
- A retention job is interrupted mid-batch; on resume it must not re-process already-committed batches.
- A legal hold is placed on a record while a retention job is actively processing the same batch.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow authorized compliance admins to define retention policies by organization, data class, template category, branch, and legal basis.
- **FR-002**: System MUST provide a non-destructive preview showing affected counts, examples, blocked records, and downstream references before policy activation.
- **FR-003**: System MUST support archive, purge, mask, and retain actions according to policy.
- **FR-004**: System MUST support legal holds that prevent purge or masking of specified submissions, customers, templates, exports, or audit evidence.
- **FR-005**: System MUST record retention job status, skipped records, errors, approvals, and final outcomes.
- **FR-006**: System MUST preserve immutable audit evidence for retention actions even when operational records are purged.
- **FR-007**: System MUST allow authorized users to search archive manifests and restore archived records when policy permits.
- **FR-008**: System MUST identify references from reports, exports, notifications, portal sessions, and generated PDFs before purge and block the purge if unresolved references remain.
- **FR-009**: System MUST provide Arabic and English policy names, notices, admin messages, and evidence summaries.
- **FR-010**: System MUST execute retention jobs in background batches of up to 1,000 records with checkpointed progress and idempotent resume.
- **FR-011**: System MUST compute and store SHA-256 hashes for every archive manifest and purge evidence record.
- **FR-012**: Archived operational records MUST remain in a dedicated PostgreSQL archive schema; large binary artifacts (PDFs, exports) MAY be moved to Supabase Storage cold tier.

### Key Entities

- **Retention Policy**: Data lifecycle rule with scope, period, action (archive | purge | mask | retain), approval state, effective date, and legal basis.
- **Retention Job**: Execution instance with status (pending | running | paused | completed | failed), batch size, checkpoint cursor, evaluated count, actioned count, error count, and resumed_from_job_id.
- **Legal Hold**: Compliance block with hold type (investigation | dispute | regulatory), scope (submission | customer | template | export | audit_evidence), reference ID, expiry date (optional), and creating admin.
- **Archive Manifest**: Evidence package with manifest ID, SHA-256 hash, record count, archive schema location, cold storage URI (optional), integrity status, creation timestamp, and restore conditions.
- **Privacy Request**: Customer or admin request to export, delete, mask, or restrict personal data; may conflict with legal holds.

### Data Model Additions

- **retention_policies** table: id, org_id, name (i18n), data_class, scope_json, action, period_days, legal_basis, approval_required, effective_date, created_by, created_at, updated_at.
- **retention_jobs** table: id, policy_id, status, started_at, completed_at, batch_size, checkpoint_cursor, evaluated_count, actioned_count, error_count, error_log, manifest_id, resumed_from_job_id.
- **legal_holds** table: id, org_id, hold_type, scope_type, scope_id, reason, expiry_date, created_by, created_at, updated_at.
- **archive_manifests** table: id, job_id, record_count, schema_location, cold_storage_uri, sha256_hash, integrity_status, created_at.
- **retention_job_audit** view/table extension: compliance event types written to existing audit_logs table.

## Non-Functional / Quality Attributes

- **NF-001 Performance**: Preview queries for 100,000 records must complete in < 2 minutes using indexed date-range scans.
- **NF-002 Scalability**: Retention jobs must not block operational reads; use batch cursors and low-priority background workers.
- **NF-003 Reliability**: Interrupted jobs must be resumable without data loss; each batch committed atomically.
- **NF-004 Observability**: Retention job progress emitted as structured logs with job_id, batch_number, and checkpoint_cursor.
- **NF-005 Security**: Archive schema must enforce RLS identical to operational tables; cold storage objects must be encrypted at rest.
- **NF-006 Compliance**: All retention evidence must remain queryable for the maximum audit retention period (7 years default).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Compliance admins can preview the impact of a retention policy in under 2 minutes for 100,000 records.
- **SC-002**: 100% of retention jobs produce an auditable manifest or failure report.
- **SC-003**: Records under legal hold are skipped by purge jobs in all tested scenarios.
- **SC-004**: Purged records are removed from operational search, history, reports, and exports while retention evidence remains available.
- **SC-005**: Admins can answer "why was this record retained, archived, or purged?" from compliance views without database access.
- **SC-006**: Resume of an interrupted retention job processes only uncommitted batches, verified by checkpoint cursor equality.
- **SC-007**: SHA-256 manifest hashes verify successfully on 100% of archive restore operations.
