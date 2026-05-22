# API Contract: Form Filler

## New Endpoint: `GET /api/desk/fill/:templateId`

Returns the full template structure (pages + elements) for form filling. Only returns published templates. This is a separate endpoint from `GET /api/templates/:id` (which is available to designers/admins and returns drafts too). The desk endpoint enforces a security boundary: desk-mode users can only load published templates, preventing accidental exposure of draft template data to operators.

### Response (200 OK)

```json
{
  "id": "uuid",
  "name": "KYC Form",
  "version": 3,
  "language": "ar",
  "country": "EG",
  "pages": [
    {
      "id": "page-uuid",
      "sort_order": 0,
      "width_mm": 210,
      "height_mm": 297,
      "elements": [
        {
          "id": "elem-uuid",
          "key": "customer_name",
          "type": "text",
          "label_ar": "اسم العميل",
          "label_en": "Customer Name",
          "required": true,
          "direction": "rtl",
          "sort_order": 0,
          "validation": {},
          "formatting": {}
        },
        {
          "id": "elem-uuid-2",
          "key": "amount",
          "type": "currency",
          "label_ar": "المبلغ",
          "label_en": "Amount",
          "required": true,
          "direction": "ltr",
          "sort_order": 1,
          "validation": { "min": 0, "max": 9999999 },
          "formatting": { "currency": "EGP", "decimals": 2 }
        },
        {
          "id": "elem-uuid-3",
          "key": "amount_words",
          "type": "tafqeet",
          "label_ar": "المبلغ كتابةً",
          "label_en": "Amount in Words",
          "required": false,
          "direction": "rtl",
          "sort_order": 2,
          "validation": {},
          "formatting": { "sourceElementKey": "amount", "language": "ar", "currency": "EGP" }
        }
      ]
    }
  ]
}
```

### Error Responses

| Status | Condition | Body |
|--------|-----------|------|
| 404 | Template not found or not published | `{ "detail": "Template not found or not published" }` |

---

## New Endpoint: `POST /api/submissions`

Creates a submission record after successful form fill + print.

### Request

```json
{
  "template_id": "uuid",
  "template_version": 3,
  "field_values": {
    "customer_name": "أحمد محمد",
    "amount": 1500.25,
    "national_id": "12345678901234"
  }
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| template_id | UUID | yes | Must be published |
| template_version | int | yes | Must match current published version |
| field_values | object | yes | Keys = element.key, values = entered data |

### Response (201 Created)

```json
{
  "id": "submission-uuid",
  "reference_number": "FC-2026-05-0042",
  "template_id": "uuid",
  "template_version": 3,
  "operator_id": "user-uuid",
  "created_at": "2026-05-16T10:30:00Z"
}
```

### Error Responses

| Status | Condition | Body |
|--------|-----------|------|
| 404 | Template not found / not published | `{ "detail": "Template not found or not published" }` |
| 422 | Validation errors in field_values | `{ "detail": "Validation failed", "errors": [{"field": "national_id", "message": "Must be 14 digits"}] }` |
| 422 | Version mismatch | `{ "detail": "Template version mismatch. Current: 4, submitted: 3" }` |

---

## New Endpoint: `POST /api/desk/drafts`

Creates a new draft.

### Request

```json
{
  "template_id": "uuid",
  "template_version": 3,
  "field_values": { "customer_name": "أحمد" },
  "name": "KYC Form - أحمد"
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| template_id | UUID | yes | — |
| template_version | int | yes | — |
| field_values | object | yes | Partial values |
| name | string | no | Auto-generated if not provided |

### Response (201 Created)

```json
{
  "id": "draft-uuid",
  "template_id": "uuid",
  "template_version": 3,
  "field_values": { "customer_name": "أحمد" },
  "completion_percent": 10,
  "name": "KYC Form - أحمد",
  "expires_at": "2026-05-23T10:30:00Z",
  "created_at": "2026-05-16T10:30:00Z",
  "updated_at": "2026-05-16T10:30:00Z"
}
```

---

## New Endpoint: `PATCH /api/desk/drafts/:draftId`

Updates an existing draft (manual save or auto-save).

### Request

```json
{
  "field_values": { "customer_name": "أحمد محمد", "amount": 1500.25 },
  "name": "KYC Form - أحمد محمد"
}
```

### Response (200 OK)

Same shape as POST response with updated values.

---

## New Endpoint: `GET /api/desk/drafts/:draftId`

Retrieves a specific draft for resuming.

### Response (200 OK)

```json
{
  "id": "draft-uuid",
  "template_id": "uuid",
  "template_version": 3,
  "field_values": { "customer_name": "أحمد" },
  "completion_percent": 10,
  "name": "KYC Form - أحمد",
  "expires_at": "2026-05-23T10:30:00Z",
  "created_at": "2026-05-16T10:30:00Z",
  "updated_at": "2026-05-16T10:30:00Z"
}
```

### Error Responses

| Status | Condition | Body |
|--------|-----------|------|
| 404 | Draft not found or not owned by user | `{ "detail": "Draft not found" }` |
| 410 | Draft expired | `{ "detail": "Draft has expired" }` |

---

## New Endpoint: `DELETE /api/desk/drafts/:draftId`

Deletes a draft.

### Response (204 No Content)

---

## New Endpoint: `GET /api/validators/:country`

Returns validation patterns for a specific country (used by frontend to run client-side validation).

### Response (200 OK)

```json
{
  "country": "EG",
  "validators": [
    {
      "field_type": "national_id",
      "pattern": "^\\d{14}$",
      "error_ar": "الرقم القومي يجب أن يكون 14 رقماً",
      "error_en": "National ID must be 14 digits"
    },
    {
      "field_type": "phone",
      "pattern": "^(\\+20|0)1[0125]\\d{8}$",
      "error_ar": "رقم الهاتف غير صحيح",
      "error_en": "Invalid phone number"
    }
  ]
}
```

---

## Modified Endpoint: `POST /api/pdf/render/:templateId`

Extended to accept field_values for filled PDF generation.

### New Request Body (optional)

```json
{
  "field_values": {
    "customer_name": "أحمد محمد",
    "amount": 1500.25
  }
}
```

When `field_values` is provided, elements render with the operator's data. When omitted, existing behavior (empty/placeholder) is preserved for backward compatibility.

### Response

Unchanged — returns PDF as StreamingResponse.

---

## Authentication & Authorization

All endpoints require:
- Valid JWT token (AuthGuard)
- User role must have access to `/desk` mode
- All queries scoped by org_id via Supabase RLS
- Submissions and drafts are per-operator (RLS enforced)

The `POST /api/submissions` endpoint additionally:
- Re-validates all field_values server-side before creating the submission
- Generates reference_number atomically via PostgreSQL sequence
- Logs FORM_SUBMITTED audit event
