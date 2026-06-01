# API Contracts: Form Filler Cross-Theme (F053)

**Branch**: `053-form-filler-cross-theme` | **Date**: 2026-06-01

---

## GET /desk/fill/{templateId}

**Response** `200 FillTemplate`:
```json
{
  "id": "uuid",
  "name": "string",
  "version": 1,
  "language": "ar|en",
  "country": "EG|SA|AE",
  "is_deprecated": false,
  "pages": [
    {
      "id": "uuid",
      "sort_order": 1,
      "width_mm": 210,
      "height_mm": 297,
      "elements": [
        {
          "id": "uuid",
          "key": "account_type",
          "type": "select",
          "label_ar": "نوع الحساب",
          "label_en": "Account Type",
          "required": true,
          "direction": "rtl",
          "sort_order": 1,
          "options": [
            { "value": "individual", "label_ar": "فردي", "label_en": "Individual" },
            { "value": "corporate", "label_ar": "شركة", "label_en": "Corporate" }
          ],
          "visible_when": null,
          "required_when": null,
          "tafqeet_enabled": false,
          "validation": null,
          "formatting": null
        }
      ]
    }
  ]
}
```
**Errors**: `404` template not found · `403` not published/forbidden

---

## GET /desk/drafts

**Query params**: none (returns all drafts for `auth.uid()`)

**Response** `200 DraftResponse[]`:
```json
[
  {
    "id": "uuid",
    "template_id": "uuid",
    "template_version": 1,
    "operator_id": "uuid",
    "org_id": "uuid",
    "field_values": {},
    "completion_percent": 42,
    "name": "Draft name or null",
    "expires_at": "2026-06-08T...",
    "created_at": "...",
    "updated_at": "..."
  }
]
```

---

## POST /desk/submissions/{templateId}

**Request body**:
```json
{
  "template_version": 1,
  "field_values": { "account_type": "individual", "name_ar": "أحمد محمد" }
}
```

**Response** `201 SubmissionResponse`:
```json
{
  "id": "uuid",
  "reference_number": "ORG-000042",
  "template_id": "uuid",
  "template_version": 1,
  "created_at": "..."
}
```

**Errors**: `422` validation failure with `{ "errors": [{ "field": "key", "message": "..." }] }` · `409` duplicate submission

---

## GET /desk/customers/search?q={query}

**Response** `200 Customer[]`:
```json
[
  {
    "id": "uuid",
    "name_ar": "أحمد محمد علي",
    "name_en": "Ahmed Mohamed Ali",
    "phone": "+201234567890",
    "national_id": "30001012345678",
    "email": "ahmed@example.com"
  }
]
```

---

## GET /desk/customers/{customerId}/auto-fill?template_id={templateId}

**Response** `200 AutoFillMapping`:
```json
{
  "mappings": {
    "customer_name_ar": "أحمد محمد علي",
    "national_id": "30001012345678",
    "phone": "+201234567890"
  }
}
```
