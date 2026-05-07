# API Contracts: Customer Feedback

**Branch**: `001-customer-feedback` | **Phase**: 1

All endpoints require a valid JWT in the `Authorization: Bearer <token>` header unless noted.

---

## POST `/api/feedback/upload/image`

Upload an image attachment before submitting feedback.

**Auth**: Any authenticated user  
**Content-Type**: `multipart/form-data`

**Request**:
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `file` | binary | yes | JPEG/PNG/WEBP, max 5 MB |

**Response 200**:
```json
{ "url": "feedback/uuid/uuid.jpg" }
```

**Error responses**:
| Status | Condition |
|--------|-----------|
| 400 | Unsupported MIME type |
| 413 | File exceeds 5 MB |
| 401 | Missing or invalid token |

---

## POST `/api/feedback/upload/audio`

Upload an audio attachment (pre-recorded file or live recording blob).

**Auth**: Any authenticated user  
**Content-Type**: `multipart/form-data`

**Request**:
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `file` | binary | yes | MP3/M4A/WAV/WebM, max 10 MB |

**Response 200**:
```json
{ "url": "feedback/uuid/uuid.mp3" }
```

**Error responses**:
| Status | Condition |
|--------|-----------|
| 400 | Unsupported MIME type |
| 413 | File exceeds 10 MB |
| 401 | Missing or invalid token |

---

## DELETE `/api/feedback/upload`

Remove an orphaned file from storage when submission is aborted after a successful upload.

**Auth**: Any authenticated user (may only delete their own paths)  
**Content-Type**: `application/json`

**Request body**:
```json
{ "url": "feedback/uuid/uuid.jpg" }
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `url` | string | yes | storage path returned by a prior upload call |

**Response 204**: No content

**Error responses**:
| Status | Condition |
|--------|-----------|
| 400 | Path does not belong to the authenticated user |
| 401 | Missing or invalid token |
| 404 | Path not found in storage |

---

## POST `/api/feedback`

Submit a feedback entry.

**Auth**: Any authenticated user

**Request body**:
```json
{
  "page_url":     "https://app.formcraft.io/designer/template-id",
  "text_content": "The PDF export button is missing on mobile.",
  "image_url":    "feedback/uuid/uuid.jpg",
  "audio_url":    null
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `page_url` | string | yes | valid URL, max 2048 chars |
| `text_content` | string | yes | 1–2000 characters |
| `image_url` | string\|null | no | storage path from upload endpoint |
| `audio_url` | string\|null | no | storage path from upload endpoint |

**Response 201**:
```json
{
  "id": "uuid",
  "submitted_at": "2026-05-07T10:00:00Z",
  "status": "new"
}
```

**Error responses**:
| Status | Condition |
|--------|-----------|
| 400 | `text_content` empty or > 2000 chars |
| 401 | Missing or invalid token |
| 422 | Validation failure (invalid URL, bad field) |
| 429 | Cooldown active — less than 30 seconds since last submission |

---

## GET `/api/admin/feedback`

List all feedback submissions (paginated).

**Auth**: ADMIN role required

**Query parameters**:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number (1-based) |
| `limit` | int | 50 | Items per page (max 200) |
| `status` | string | — | Filter by status: `new`, `reviewed`, `resolved` |
| `user_id` | UUID | — | Filter by submitter |
| `date_from` | ISO date | — | Submissions on or after this date |
| `date_to` | ISO date | — | Submissions on or before this date |

**Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "page_url": "https://...",
      "text_content": "The PDF export button...",
      "image_url": "feedback/uuid/uuid.jpg",
      "image_signed_url": "https://supabase.storage/.../signed?token=...",
      "audio_url": "feedback/uuid/uuid.mp3",
      "audio_signed_url": "https://supabase.storage/.../signed?token=...",
      "submitted_at": "2026-05-07T10:00:00Z",
      "status": "new",
      "submitter_display_name": "Ahmed Hassan"
    }
  ],
  "total": 142,
  "page": 1,
  "limit": 50
}
```

**Error responses**:
| Status | Condition |
|--------|-----------|
| 401 | Missing or invalid token |
| 403 | Non-admin role |

---

## PATCH `/api/admin/feedback/{id}`

Update the status of a feedback submission.

**Auth**: ADMIN role required

**Request body**:
```json
{ "status": "reviewed" }
```

| Field | Allowed values |
|-------|----------------|
| `status` | `new`, `reviewed`, `resolved` |

**Response 200**:
```json
{ "id": "uuid", "status": "reviewed" }
```

**Error responses**:
| Status | Condition |
|--------|-----------|
| 400 | Invalid status value |
| 401 | Missing or invalid token |
| 403 | Non-admin role |
| 404 | Feedback ID not found |
