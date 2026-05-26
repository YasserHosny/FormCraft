# Research: Data Retention and Archival

## Decisions

### Archive Storage Location
- **Decision**: Use a dedicated PostgreSQL archive schema within the same database instance.
- **Rationale**: Keeps referential integrity, allows SQL queries for compliance views, and avoids introducing a second database technology. Large blobs (PDFs, exports) exported to Supabase Storage cold tier to avoid bloating the primary database.
- **Alternatives considered**: Separate read-replica (overkill for v1), S3-style object storage for all data (loses relational query capability).

### Job Scheduling
- **Decision**: APScheduler with a dedicated `RetentionJobExecutor` that processes one job at a time per organization.
- **Rationale**: APScheduler is already used in the project (033-operational-reports). Sequential per-organization processing prevents resource contention across tenants.
- **Alternatives considered**: Celery + Redis (adds infrastructure), cron scripts (no checkpoint/resume), async background tasks (harder to observe and resume).

### Batch Size and Checkpointing
- **Decision**: Default batch size 1,000 records. Checkpoint stored as a cursor (last processed `id` or `created_at` + `id`) in `retention_jobs.checkpoint_cursor`.
- **Rationale**: 1,000 is a balance between transaction size and memory usage. Cursor-based checkpointing is idempotent and avoids OFFSET performance degradation.
- **Alternatives considered**: Timestamp-only cursors (risk duplicates if clock precision issues), full offset/limit (slow at scale).

### Audit Evidence Integration
- **Decision**: Extend existing `audit_logs` table with compliance-specific event types.
- **Rationale**: Leverages existing audit infrastructure, RLS policies, and query patterns. Avoids schema duplication.
- **Alternatives considered**: Separate `compliance_audit` table (rejected due to YAGNI — audit_logs already handles structured events).

### Hashing for Integrity
- **Decision**: SHA-256 computed over a canonical JSON representation of the archive manifest or purge evidence record.
- **Rationale**: SHA-256 is widely supported, fast enough for manifests, and satisfies audit integrity requirements. Canonical JSON ensures deterministic hashing regardless of key ordering.
- **Alternatives considered**: MD5 (insufficient for compliance), HMAC (requires secret management; not needed for integrity alone).

### Legal Hold Detection During Job Execution
- **Decision**: Query `legal_holds` table at the start of each batch; skip records with active holds. Record skip reason in job error_log/skipped_records JSONB.
- **Rationale**: Holds may be created while a job runs; per-batch detection is safer than pre-computing a skip list at job start.
- **Alternatives considered**: Pre-computed skip list (risk stale data if holds added mid-job).

### Preview Query Strategy
- **Decision**: Use `COUNT(*) OVER()` + limited sample SELECTs with indexed date-range filters. Run in a read-only transaction.
- **Rationale**: Non-destructive and fast. `OVER()` provides total count without a second query. Read-only transaction ensures no accidental writes.
- **Alternatives considered**: Materialized preview tables (too much overhead for a preview feature).

### Frontend Architecture
- **Decision**: Angular feature module under `features/admin/retention` using Angular Material tables, paginators, and dialogs. RxJS streams for polling job status.
- **Rationale**: Aligns with existing admin UI patterns (departments, users, reports). Reuses shared components where possible.
- **Alternatives considered**: Standalone component-only Angular architecture (inconsistent with existing modules).
