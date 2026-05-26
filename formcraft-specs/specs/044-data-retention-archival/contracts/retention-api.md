# API Contract: Retention Endpoints

## Base Path

All endpoints prefixed with `/api/retention`

## Authentication

All endpoints require Bearer JWT token in `Authorization` header.
RLS enforces `org_id` matching the authenticated user's organization.

## Endpoints

### Retention Policies

#### GET /policies

List retention policies for the current organization.

**Query Parameters**:
- `data_class` (optional): Filter by data class
- `action` (optional): Filter by action
- `page` (optional): Default 1
- `page_size` (optional): Default 20, max 100

**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": { "ar": "...", "en": "..." },
      "data_class": "submission",
      "action": "archive",
      "period_days": 365,
      "legal_basis": "Saudi SAMA CBK 42",
      "approval_required": true,
      "effective_date": "2026-01-01T00:00:00Z",
      "created_by": "uuid",
      "created_at": "2026-01-01T00:00:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

#### POST /policies

Create a new retention policy.

**Request Body**:
```json
{
  "name": { "ar": "سياسة الاحتفاظ بالطلبات", "en": "Submission Retention Policy" },
  "data_class": "submission",
  "scope_json": { "template_category_id": "uuid", "branch_id": "uuid" },
  "action": "archive",
  "period_days": 365,
  "legal_basis": "Saudi SAMA CBK 42",
  "approval_required": true,
  "effective_date": "2026-01-01T00:00:00Z"
}
```

**Response 201**: Returns created policy object.
**Response 422**: Validation error (e.g., invalid data_class).
**Response 409**: Conflicting policy exists for org + data_class + scope.

#### GET /policies/{policy_id}

Get policy details.

**Response 200**: Policy object.

#### PUT /policies/{policy_id}

Update a policy. Only allowed if no active jobs reference it.

**Request Body**: Same as POST (all fields optional for partial update).

**Response 200**: Updated policy.
**Response 409**: Active job blocks update.

#### DELETE /policies/{policy_id}

Soft-delete or disable a policy. Only allowed if no jobs exist.

**Response 204**.

#### POST /policies/{policy_id}/preview

Preview the impact of a policy without modifying data.

**Request Body**: None (uses saved policy config).

**Response 200**:
```json
{
  "affected_count": 150000,
  "date_range": { "oldest": "2023-01-01", "newest": "2025-12-31" },
  "affected_forms": ["Form A", "Form B"],
  "blocked_records": 120,
  "blocked_reason": "Legal hold or audit minimum",
  "downstream_references": {
    "reports": 12,
    "exports": 3,
    "generated_pdfs": 450
  }
}
```

### Retention Jobs

#### GET /jobs

List retention jobs.

**Query Parameters**:
- `policy_id` (optional)
- `status` (optional): pending, running, paused, completed, failed
- `page`, `page_size`

**Response 200**: Paginated list of job objects.

#### POST /jobs

Trigger a new retention job for a policy.

**Request Body**:
```json
{
  "policy_id": "uuid",
  "batch_size": 1000
}
```

**Response 201**: Created job object with status `pending`.
**Response 409**: Job already running for this policy.

#### GET /jobs/{job_id}

Get job details including progress.

**Response 200**:
```json
{
  "id": "uuid",
  "policy_id": "uuid",
  "status": "running",
  "started_at": "2026-05-26T10:00:00Z",
  "completed_at": null,
  "batch_size": 1000,
  "checkpoint_cursor": "abc123",
  "evaluated_count": 5000,
  "actioned_count": 4880,
  "error_count": 0,
  "error_log": [],
  "skipped_records": [
    { "record_id": "uuid", "reason": "legal_hold", "hold_id": "uuid" }
  ],
  "manifest_id": null,
  "resumed_from_job_id": null
}
```

#### POST /jobs/{job_id}/pause

Pause a running job.

**Response 200**: Job with status `paused`.

#### POST /jobs/{job_id}/resume

Resume a paused or failed job.

**Response 200**: Job with status `running`.

### Legal Holds

#### GET /holds

List legal holds.

**Query Parameters**:
- `scope_type`, `hold_type`, `page`, `page_size`

**Response 200**: Paginated list of holds.

#### POST /holds

Create a legal hold.

**Request Body**:
```json
{
  "hold_type": "investigation",
  "scope_type": "submission",
  "scope_id": "uuid",
  "reason": "Regulatory investigation #2026-001",
  "expiry_date": "2027-01-01T00:00:00Z"
}
```

**Response 201**: Created hold.
**Response 409**: Hold already exists for this scope.

#### DELETE /holds/{hold_id}

Release a legal hold.

**Response 204**.

### Archive Manifests

#### GET /manifests

List archive manifests.

**Query Parameters**:
- `job_id`, `integrity_status`, `page`, `page_size`

**Response 200**: Paginated list of manifests.

#### GET /manifests/{manifest_id}

Get manifest details.

**Response 200**:
```json
{
  "id": "uuid",
  "job_id": "uuid",
  "record_count": 4880,
  "schema_location": "archive.form_submissions",
  "cold_storage_uri": "storage/retention/archives/2026/05/26/uuid.tar.gz",
  "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "integrity_status": "verified",
  "restore_conditions": { "max_restore_date": "2031-05-26", "requires_approval": true },
  "created_at": "2026-05-26T12:00:00Z"
}
```

#### POST /manifests/{manifest_id}/restore

Request restoration of archived records.

**Request Body**:
```json
{
  "reason": "Customer service request #12345",
  "approval_override": false
}
```

**Response 202**: Accepted; returns restore job tracking object.
**Response 403**: Restore conditions not met (e.g., past max restore date).

### Privacy Requests

#### GET /privacy-requests

List privacy requests.

**Query Parameters**:
- `status`, `request_type`, `page`, `page_size`

**Response 200**: Paginated list.

#### POST /privacy-requests

Create a privacy request.

**Request Body**:
```json
{
  "request_type": "delete",
  "scope_type": "customer",
  "scope_id": "uuid"
}
```

**Response 201**: Created request. If conflict with legal hold, `conflict_hold_id` is populated and status remains `pending`.

#### POST /privacy-requests/{request_id}/resolve

Admin resolves a pending privacy request.

**Request Body**:
```json
{
  "status": "approved",
  "resolution": { "action_taken": "mask", "reason": "Legal hold prevents deletion; masked PII instead." }
}
```

**Response 200**: Updated request.

## Error Codes

| Code | Meaning |
|------|---------|
| `RETENTION_POLICY_CONFLICT` | Duplicate active policy for org + data_class + scope |
| `RETENTION_JOB_ACTIVE` | Cannot modify policy or start duplicate job |
| `LEGAL_HOLD_EXISTS` | Hold already active for scope |
| `RESTORE_NOT_ALLOWED` | Restore conditions violated |
| `PREVIEW_TIMEOUT` | Preview query exceeded time limit |

## Webhooks

The system emits the following webhook events (if configured per org):

- `retention.job.started`
- `retention.job.completed`
- `retention.job.failed`
- `retention.hold.created`
- `retention.hold.released`
- `retention.manifest.restored`

Payload shape for `retention.job.completed`:
```json
{
  "event": "retention.job.completed",
  "org_id": "uuid",
  "job_id": "uuid",
  "policy_id": "uuid",
  "manifest_id": "uuid",
  "actioned_count": 4880,
  "skipped_count": 120,
  "timestamp": "2026-05-26T12:00:00Z"
}
```
