# Digital Signatures API Contract

## Admin / Operator Endpoints (JWT Required)

### `GET /api/digital-signatures/workflows`

**Auth**: Admin or Designer

List signature workflows for the current organization.

**Query Parameters**:
- `template_id` (uuid, optional)
- `is_active` (boolean, optional)
- `page` (int, default 1)
- `page_size` (int, default 20)

**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "template_id": "uuid",
      "name": "Customer Approval Workflow",
      "is_ordered": true,
      "expiration_days": 7,
      "decline_policy": "stop",
      "require_all_signers": true,
      "is_active": true,
      "created_at": "2026-05-26T12:00:00Z",
      "updated_at": "2026-05-26T12:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

### `POST /api/digital-signatures/workflows`

**Auth**: Admin or Designer

Create a new signature workflow.

**Request Body**:
```json
{
  "template_id": "uuid",
  "name": "Customer Approval Workflow",
  "is_ordered": true,
  "expiration_days": 7,
  "decline_policy": "stop",
  "require_all_signers": true
}
```

**Response 201**: Created workflow object.
**Response 409**: Active workflow already exists for this template.

### `PATCH /api/digital-signatures/workflows/{workflow_id}`

**Auth**: Admin or Designer

Update a workflow. Only name, expiration_days, decline_policy, and is_active are mutable after creation.

**Response 200**: Updated workflow object.

### `POST /api/digital-signatures/requests`

**Auth**: Operator, Admin, or Designer

Create a signature request for a submission.

**Request Body**:
```json
{
  "workflow_id": "uuid",
  "submission_id": "uuid",
  "signers": [
    {
      "signer_type": "internal",
      "profile_id": "uuid",
      "name": "Manager Name",
      "order_index": 0
    },
    {
      "signer_type": "external",
      "email": "customer@example.com",
      "name": "Customer Name",
      "order_index": 1
    }
  ]
}
```

**Response 201**: Created request object with `id`, `status: "draft"`, and `expires_at`.
**Response 422**: Workflow not active, submission not found, or invalid signer configuration.

### `POST /api/digital-signatures/requests/{request_id}/send`

**Auth**: Operator, Admin, or Designer

Send invitations to all pending signers. Transitions request from `draft` to `sent`.

**Response 200**: Request with updated status.
**Response 409**: Request not in `draft` state.

### `GET /api/digital-signatures/requests`

**Auth**: Operator, Admin, or Designer

List signature requests for the organization.

**Query Parameters**:
- `status` (string, optional)
- `submission_id` (uuid, optional)
- `page` (int, default 1)
- `page_size` (int, default 20)

**Response 200**: Paginated list of requests with recipient summaries.

### `GET /api/digital-signatures/requests/{request_id}`

**Auth**: Operator, Admin, Designer, or signer recipient

Get full request details including recipients and events.

**Response 200**:
```json
{
  "id": "uuid",
  "status": "in_progress",
  "current_signer_index": 1,
  "expires_at": "2026-06-02T12:00:00Z",
  "recipients": [
    {
      "id": "uuid",
      "signer_type": "internal",
      "name": "Manager Name",
      "status": "signed",
      "signed_at": "2026-05-26T13:00:00Z"
    },
    {
      "id": "uuid",
      "signer_type": "external",
      "email": "customer@example.com",
      "name": "Customer Name",
      "status": "invited"
    }
  ],
  "events": [
    {
      "event_type": "invited",
      "created_at": "2026-05-26T12:00:00Z"
    }
  ]
}
```

### `POST /api/digital-signatures/requests/{request_id}/cancel`

**Auth**: Operator, Admin, or Designer

Cancel a pending signature request.

**Request Body**:
```json
{
  "reason": "Customer requested cancellation"
}
```

**Response 200**: Updated request with `status: "canceled"`.

### `POST /api/digital-signatures/requests/{request_id}/resend/{recipient_id}`

**Auth**: Operator, Admin, or Designer

Resend invitation to a specific recipient.

**Response 200**: Updated recipient with new token and expiration.

### `GET /api/digital-signatures/evidence/{request_id}`

**Auth**: Admin, Designer, Operator, or Viewer

Retrieve the signed evidence package.

**Response 200**:
```json
{
  "id": "uuid",
  "document_hash": "sha256:abc123...",
  "hash_algorithm": "sha256",
  "original_pdf_path": "signed/original-uuid.pdf",
  "sealed_pdf_path": "signed/sealed-uuid.pdf",
  "signer_snapshot": [...],
  "event_summary": [...],
  "integrity_status": "valid",
  "verified_at": "2026-05-26T14:00:00Z",
  "created_at": "2026-05-26T14:00:00Z"
}
```

### `POST /api/digital-signatures/evidence/{request_id}/verify`

**Auth**: Admin, Designer, Operator, or Viewer

Re-verify document integrity by recomputing the hash and comparing.

**Response 200**:
```json
{
  "integrity_status": "valid",
  "verified_at": "2026-05-26T14:05:00Z",
  "message": "Document hash matches expected value."
}
```

## Public Signer Endpoints (Token Required)

### `GET /api/sign/{token}`

**Auth**: None; validated via opaque `token` path parameter.

Load signer-facing signature request page metadata.

**Response 200**:
```json
{
  "request_id": "uuid",
  "template_name": "Loan Application",
  "organization_name": "Example Org",
  "signer_name": "Customer Name",
  "status": "invited",
  "requires_otp": true,
  "document_url": "https://.../original.pdf",
  "expires_at": "2026-06-02T12:00:00Z"
}
```
**Response 404**: Invalid or expired token.
**Response 410**: Request expired or canceled.

### `POST /api/sign/{token}/otp/send`

**Auth**: None; token validated.

Send email OTP to external signer.

**Response 202**: OTP send accepted.
**Response 429**: Too many OTP requests.

### `POST /api/sign/{token}/otp/verify`

**Auth**: None; token validated.

Verify external signer OTP.

**Request Body**:
```json
{
  "otp": "123456"
}
```

**Response 200**: Verification success; signer status becomes `verified`.
**Response 400**: Invalid or expired OTP.

### `POST /api/sign/{token}/authenticate`

**Auth**: None; token validated.

Internal signer password re-authentication.

**Request Body**:
```json
{
  "password": "current_password"
}
```

**Response 200**: Authentication success; signer status becomes `verified`.
**Response 401**: Invalid password.

### `POST /api/sign/{token}/sign`

**Auth**: None; token validated; signer must be `verified`.

Record the signer's digital signature.

**Request Body**:
```json
{
  "consent": true,
  "ip_address": "192.0.2.1",
  "user_agent": "Mozilla/5.0..."
}
```

**Response 200**: Signature recorded; status becomes `signed`. If ordered and this was the last signer, request transitions to `signed` then `sealed`.
**Response 409**: Signer not in `verified` state.

### `POST /api/sign/{token}/decline`

**Auth**: None; token validated.

Decline the signature request.

**Request Body**:
```json
{
  "reason": "I do not agree to the terms"
}
```

**Response 200**: Decline recorded; status becomes `declined`. Request behavior depends on workflow `decline_policy`.

## Error Responses

All endpoints return standard FastAPI error shapes:

- `400`: Validation error
- `401`: Missing or invalid JWT (admin/operator endpoints) or token (public endpoints)
- `403`: Insufficient role permissions
- `404`: Resource not found
- `409`: Conflict (wrong state, duplicate workflow, etc.)
- `422`: Unprocessable entity
- `429`: Rate limited
- `503`: Service unavailable (email OTP provider down)
