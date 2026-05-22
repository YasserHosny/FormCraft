# API Contracts: Feedback Dashboard Search & Labels

**Branch**: `012-feedback-dashboard-search` | **Phase**: 1

All endpoints require a valid JWT in the `Authorization: Bearer <token>` header. All label and search endpoints require the ADMIN role.

---

## GET `/api/admin/feedback` *(extended from feature 011)*

List feedback submissions with optional search and label filtering added to existing filters.

**Auth**: ADMIN role required

**New query parameters** (added to existing `page`, `limit`, `status`, `user_id`, `date_from`, `date_to`):

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `search` | string | — | Debounced keyword; ILIKE match against `text_content` |
| `label_ids` | UUID[] | — | Comma-separated label UUIDs; OR logic — returns submissions carrying any one |

**Response 200** *(extended)*:
```json
{
  "data": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "page_url": "https://...",
      "text_content": "The export button...",
      "image_url": "feedback/uuid/uuid.jpg",
      "image_signed_url": "https://...",
      "audio_url": null,
      "audio_signed_url": null,
      "submitted_at": "2026-05-07T10:00:00Z",
      "status": "new",
      "submitter_display_name": "Ahmed Hassan",
      "labels": [
        { "id": "uuid", "name": "Bug Report", "colour": "red" }
      ]
    }
  ],
  "total": 142,
  "page": 1,
  "limit": 50
}
```

**New field**: `labels` — array of label objects assigned to the submission (empty array if none).

---

## GET `/api/admin/feedback/submitters`

Return the list of users who have submitted at least one feedback entry. Used to populate the submitter autocomplete filter in the admin dashboard.

**Auth**: ADMIN role required

**Response 200**:
```json
[
  { "user_id": "uuid", "display_name": "Ahmed Hassan" },
  { "user_id": "uuid", "display_name": "Sara K." }
]
```

Results are ordered alphabetically by `display_name`. Display name is resolved from `profiles.display_name`, falling back to `profiles.email`.

**Error responses**:
| Status | Condition |
|--------|-----------|
| 401 | Missing or invalid token |
| 403 | Non-admin role |

---

## GET `/api/admin/labels`

List all feedback labels.

**Auth**: ADMIN role required

**Response 200**:
```json
[
  { "id": "uuid", "name": "Bug Report", "colour": "red", "created_at": "2026-05-07T09:00:00Z" }
]
```

**Error responses**:
| Status | Condition |
|--------|-----------|
| 401 | Missing or invalid token |
| 403 | Non-admin role |

---

## POST `/api/admin/labels`

Create a new label.

**Auth**: ADMIN role required

**Request body**:
```json
{ "name": "Bug Report", "colour": "red" }
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `name` | string | yes | 1–50 characters, must be unique |
| `colour` | string | no | One of: red, orange, yellow, green, teal, blue, purple, pink, grey, brown |

**Response 201**:
```json
{ "id": "uuid", "name": "Bug Report", "colour": "red", "created_at": "2026-05-07T09:00:00Z" }
```

**Error responses**:
| Status | Condition |
|--------|-----------|
| 400 | Name empty, > 50 chars, or invalid colour value |
| 409 | Label name already exists |
| 401 | Missing or invalid token |
| 403 | Non-admin role |

---

## PATCH `/api/admin/labels/{id}`

Update a label's name or colour.

**Auth**: ADMIN role required

**Request body** *(all fields optional; at least one required)*:
```json
{ "name": "UI Bug", "colour": "orange" }
```

**Response 200**:
```json
{ "id": "uuid", "name": "UI Bug", "colour": "orange", "created_at": "2026-05-07T09:00:00Z" }
```

**Error responses**:
| Status | Condition |
|--------|-----------|
| 400 | Invalid colour value or name constraints violated |
| 404 | Label not found |
| 409 | New name conflicts with an existing label |
| 401 | Missing or invalid token |
| 403 | Non-admin role |

---

## DELETE `/api/admin/labels/{id}`

Delete a label and remove it from all submissions.

**Auth**: ADMIN role required

**Response 204**: No content

**Error responses**:
| Status | Condition |
|--------|-----------|
| 404 | Label not found |
| 401 | Missing or invalid token |
| 403 | Non-admin role |

---

## PUT `/api/admin/feedback/{id}/labels`

Replace the full label set on a submission (idempotent assignment).

**Auth**: ADMIN role required

**Request body**:
```json
{ "label_ids": ["uuid-1", "uuid-2"] }
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `label_ids` | UUID[] | yes | 0–5 items; empty array clears all labels |

**Response 200**:
```json
{
  "feedback_id": "uuid",
  "labels": [
    { "id": "uuid-1", "name": "Bug Report", "colour": "red" },
    { "id": "uuid-2", "name": "Mobile", "colour": "blue" }
  ]
}
```

**Error responses**:
| Status | Condition |
|--------|-----------|
| 400 | More than 5 label IDs supplied |
| 404 | Feedback submission or one of the label IDs not found |
| 401 | Missing or invalid token |
| 403 | Non-admin role |
