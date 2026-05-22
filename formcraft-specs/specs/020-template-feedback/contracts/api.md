# API Contracts: Template Feedback

**Date**: 2026-05-17

## Endpoints

### `POST /api/templates/:id/feedback`

Submit feedback on a template.

**Auth**: Operator, Branch Manager, Admin  
**Request**:
```json
{
  "template_version": 2,
  "page_number": 1,
  "element_key": "national_id",
  "category": "bug",
  "text": "The label is confusing — should say National ID Number instead of just ID"
}
```

**Response 201**:
```json
{
  "id": "uuid",
  "template_id": "uuid",
  "template_version": 2,
  "page_number": 1,
  "element_key": "national_id",
  "category": "bug",
  "text": "The label is confusing — should say National ID Number instead of just ID",
  "status": "open",
  "submitted_by": "uuid",
  "created_at": "2026-05-17T10:00:00Z"
}
```

**Errors**: 422 (validation), 409 (duplicate debounce), 404 (template not found)

---

### `GET /api/templates/:id/feedback`

List feedback for a template.

**Auth**: Designer, Admin, Branch Manager  
**Query Params**:
- `version` (int, optional — filter by specific version)
- `status` (string: "open" | "resolved", optional)
- `category` (string, optional)
- `page_number` (int, optional)
- `page` (int, default 1)
- `page_size` (int, default 50)

**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "template_version": 2,
      "page_number": 1,
      "element_key": "national_id",
      "category": "bug",
      "text": "The label is confusing...",
      "status": "open",
      "submitted_by": { "id": "uuid", "name": "Ahmed Mohamed" },
      "resolved_by": null,
      "resolved_at": null,
      "resolution_note": null,
      "created_at": "2026-05-17T10:00:00Z"
    }
  ],
  "total": 5,
  "open_count": 3,
  "resolved_count": 2,
  "page": 1,
  "page_size": 50
}
```

---

### `POST /api/templates/:id/feedback/:feedback_id/resolve`

Resolve a feedback item.

**Auth**: Designer, Admin, Branch Manager  
**Request**:
```json
{
  "resolution_note": "Fixed in version 3 — label updated to National ID Number"
}
```

**Response 200**:
```json
{
  "id": "uuid",
  "status": "resolved",
  "resolved_by": { "id": "uuid", "name": "Sara Ahmed" },
  "resolved_at": "2026-05-17T12:00:00Z",
  "resolution_note": "Fixed in version 3 — label updated to National ID Number"
}
```

**Errors**: 404, 409 "Already resolved"

---

### `GET /api/templates/:id/feedback/summary`

Get feedback summary (for template card badge).

**Auth**: Designer, Admin, Branch Manager  
**Response 200**:
```json
{
  "template_id": "uuid",
  "total": 5,
  "open_count": 3,
  "resolved_count": 2,
  "by_category": { "bug": 2, "suggestion": 2, "question": 1 }
}
```

---

### `GET /api/admin/template-feedback`

Admin overview of all template feedback.

**Auth**: Admin, Branch Manager  
**Query Params**:
- `status` (optional)
- `date_from`, `date_to` (optional, ISO dates)
- `page`, `page_size`

**Response 200**:
```json
{
  "items": [
    {
      "template_id": "uuid",
      "template_name": "KYC Form",
      "latest_version": 3,
      "open_count": 4,
      "resolved_count": 8,
      "last_feedback_at": "2026-05-17T10:00:00Z"
    }
  ],
  "total": 12,
  "page": 1,
  "page_size": 50
}
```

---

### `GET /api/admin/template-feedback/export`

Export feedback as CSV.

**Auth**: Admin  
**Query Params**: same filters as list endpoint  
**Response 200**: `Content-Type: text/csv`

CSV columns: template_name, version, page, element, category, text, status, submitted_by, submitted_at, resolved_by, resolved_at

## Error Response Format

Standard FormCraft format:
```json
{
  "detail": "Human-readable error message",
  "errors": [{ "field": "text", "message": "Feedback must be at least 10 characters" }]
}
```
