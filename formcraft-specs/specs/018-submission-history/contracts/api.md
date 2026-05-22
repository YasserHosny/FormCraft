# API Contract: Submission History & Reprint

## Extended Endpoint: `GET /api/submissions`

List submissions with search, filtering, and pagination.

### Request Query Parameters

| Param | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| search | string | no | null | Matches reference_number (exact) or template name (ILIKE) |
| template_id | UUID | no | null | Filter by specific template |
| status | string | no | null | Filter: 'printed', 'submitted' |
| date_from | date | no | null | ISO 8601 date (inclusive) |
| date_to | date | no | null | ISO 8601 date (inclusive) |
| page | int | no | 1 | >= 1 |
| limit | int | no | 25 | 25, 50, or 100 |
| sort_by | string | no | 'created_at' | 'created_at', 'reference_number', 'template_name' |
| sort_dir | string | no | 'desc' | 'asc' or 'desc' |
| scope | string | no | 'own' | 'own' (operator's submissions) or 'org' (all org submissions — admin/branch_manager only; ignored for operators) |

### Response (200 OK)

```json
{
  "items": [
    {
      "id": "submission-uuid",
      "reference_number": "FC-2026-05-0042",
      "template_id": "template-uuid",
      "template_name": "KYC Form",
      "template_version": 3,
      "status": "printed",
      "created_at": "2026-05-16T10:30:00Z",
      "key_summary": ["أحمد محمد", "12345678901234", "1500.25"]
    }
  ],
  "total": 156,
  "page": 1,
  "limit": 25
}
```

**Notes**:
- `key_summary`: First 3 non-empty field values from the submission, ordered by the template's element sort_order. Computed at serialization time.

---

## New Endpoint: `GET /api/submissions/:submissionId`

Returns full submission detail.

### Response (200 OK)

```json
{
  "id": "submission-uuid",
  "reference_number": "FC-2026-05-0042",
  "template_id": "template-uuid",
  "template_name": "KYC Form",
  "template_version": 3,
  "status": "printed",
  "operator_id": "user-uuid",
  "operator_name": "أحمد محمد",
  "org_id": "org-uuid",
  "field_values": {
    "customer_name": "محمد علي",
    "national_id": "12345678901234",
    "amount": 1500.25,
    "amount_words": "ألف وخمسمائة جنيه مصري وخمسة وعشرون قرشاً"
  },
  "created_at": "2026-05-16T10:30:00Z"
}
```

### Error Responses

| Status | Condition | Body |
|--------|-----------|------|
| 404 | Submission not found or not in user's org | `{ "detail": "Submission not found" }` |

---

## New Endpoint: `POST /api/submissions/:submissionId/reprint`

Generates a reprint PDF with watermark. Logs audit event.

### Request

No body required.

### Response (200 OK)

Returns PDF as `StreamingResponse` with `Content-Type: application/pdf`.

The PDF includes:
- All field values rendered at original positions
- Diagonal "REPRINT" watermark (20% opacity, rotated 45deg)
- Footer: "Reprint of FC-2026-05-0042 | Originally printed: 2026-05-16 | Reprinted: 2026-05-17"

### Side Effects

- Audit log entry: `{ action: "FORM_REPRINTED", resource_type: "submission", resource_id: submissionId, metadata: { reference_number, operator_id } }`

---

## New Endpoint: `GET /api/submissions/:submissionId/export`

Exports submission data as JSON or CSV.

### Request Query Parameters

| Param | Type | Required | Values |
|-------|------|----------|--------|
| format | string | yes | 'json' or 'csv' |

### Response (200 OK) — JSON format

```json
{
  "reference_number": "FC-2026-05-0042",
  "template_name": "KYC Form",
  "template_version": 3,
  "submitted_at": "2026-05-16T10:30:00Z",
  "operator": "أحمد محمد",
  "field_values": {
    "customer_name": "محمد علي",
    "national_id": "12345678901234",
    "amount": 1500.25
  }
}
```

Headers: `Content-Disposition: attachment; filename="FC-2026-05-0042.json"`

### Response (200 OK) — CSV format

```csv
reference_number,template_name,submitted_at,customer_name,national_id,amount
FC-2026-05-0042,KYC Form,2026-05-16T10:30:00Z,محمد علي,12345678901234,1500.25
```

Headers: `Content-Disposition: attachment; filename="FC-2026-05-0042.csv"`; `Content-Type: text/csv; charset=utf-8` with BOM for Arabic Excel compatibility.

### Side Effects

- Audit log entry: `{ action: "SUBMISSION_EXPORTED", resource_type: "submission", resource_id: submissionId, metadata: { format, reference_number } }`

---

## Authentication & Authorization

All endpoints require:
- Valid JWT token (AuthGuard)
- User must have desk-mode access
- Submissions scoped by org_id via RLS (operators see own org)
- Reprint and export are available to all desk-mode users (no additional role restriction)
