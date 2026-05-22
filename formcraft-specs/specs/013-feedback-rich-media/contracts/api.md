# API Contracts: Feedback Rich Media

**Branch**: `013-feedback-rich-media` | **Phase**: 1

All endpoints require `Authorization: Bearer <JWT>`. Upload and submit endpoints are for authenticated users; admin endpoints require `role = 'admin'`.

---

## 1. Upload an Image (new — replaces single-image pattern from feature 011)

```
POST /api/feedback/upload/image
```

**Auth**: Authenticated user

**Request**: `multipart/form-data`

| Field | Type | Constraints |
|-------|------|-------------|
| `file` | binary | JPEG, PNG, or WEBP; max 5 MB |

**Response 200**:
```json
{
  "storage_path": "feedback/{user_id}/{uuid}.jpg"
}
```

**Error responses**:
| Code | Reason |
|------|--------|
| 400 | Unsupported MIME type or file exceeds 5 MB |
| 401 | Unauthenticated |
| 429 | Rate limit exceeded |

> **Note**: This endpoint is called once per image. For a 5-image submission, the client calls it up to 5 times sequentially, collecting `storage_path` values to include in the submit body.

---

## 2. Delete a Staged Image (new — abort / cleanup)

```
DELETE /api/feedback/upload/image
```

**Auth**: Authenticated user (must be the file owner)

**Request body** (`application/json`):
```json
{
  "storage_path": "feedback/{user_id}/{uuid}.jpg"
}
```

**Response 204**: No content

**Error responses**:
| Code | Reason |
|------|--------|
| 400 | `storage_path` missing or malformed |
| 403 | Path does not belong to the authenticated user |
| 404 | File not found in storage |

---

## 3. Upload a Video

```
POST /api/feedback/upload/video
```

**Auth**: Authenticated user

**Request**: `multipart/form-data`

| Field | Type | Constraints |
|-------|------|-------------|
| `file` | binary | `video/mp4` or `video/webm`; max 100 MB |

**Response 200**:
```json
{
  "storage_path": "feedback/{user_id}/{uuid}.mp4"
}
```

**Error responses**:
| Code | Reason |
|------|--------|
| 400 | Unsupported MIME type or file exceeds 100 MB |
| 401 | Unauthenticated |
| 429 | Rate limit exceeded |

---

## 4. Delete a Staged Video (abort / cleanup)

```
DELETE /api/feedback/upload/video
```

**Auth**: Authenticated user (must be the file owner)

**Request body** (`application/json`):
```json
{
  "storage_path": "feedback/{user_id}/{uuid}.mp4"
}
```

**Response 204**: No content

**Error responses**:
| Code | Reason |
|------|--------|
| 400 | `storage_path` missing or malformed |
| 403 | Path does not belong to the authenticated user |
| 404 | File not found in storage |

---

## 5. Submit Feedback (modified from feature 011)

```
POST /api/feedback
```

**Auth**: Authenticated user (30-second cooldown from feature 011 unchanged)

**Request body** (`application/json`) — changes from feature 011 in **bold**:

```json
{
  "page_url": "https://app.example.com/dashboard",
  "text_content": "The chart tooltip overlaps the axis label in dark mode",
  "image_paths": ["feedback/{user_id}/abc.jpg", "feedback/{user_id}/def.png"],
  "audio_url": null,
  "video_url": null
}
```

| Field | Type | Constraints |
|-------|------|-------------|
| `page_url` | string | Required; max 2048 chars |
| `text_content` | string | Required; 1–2000 chars |
| `image_paths` | `list[string]` \| null | **NEW** — replaces `image_url`; max 5 paths; each must be a valid `feedback/{user_id}/` path |
| `audio_url` | string \| null | Nullable; Supabase Storage path (feature 011 unchanged) |
| `video_url` | string \| null | **NEW** — nullable; Supabase Storage path |

**Mutual exclusion**: `audio_url` and `video_url` MUST NOT both be non-null (422 if violated).

**Response 201**:
```json
{
  "id": "uuid",
  "submitted_at": "2026-05-07T14:32:00Z",
  "images": [
    { "id": "uuid", "storage_path": "feedback/{user_id}/abc.jpg", "display_order": 0 },
    { "id": "uuid", "storage_path": "feedback/{user_id}/def.png", "display_order": 1 }
  ],
  "audio_url": null,
  "video_url": null
}
```

**Error responses**:
| Code | Reason |
|------|--------|
| 400 | More than 5 `image_paths`; path not owned by user |
| 422 | Both `audio_url` and `video_url` non-null; validation failure |
| 429 | Cooldown active (< 30 s since last submission) |

---

## 6. Get Admin Feedback List (modified from feature 011)

```
GET /api/admin/feedback
```

**Auth**: Admin

No new query parameters added by this feature. The response shape changes.

**Response 200** — `FeedbackAdminItem` changes from feature 011:

```json
{
  "results": [
    {
      "id": "uuid",
      "page_url": "...",
      "text_content": "...",
      "images": [
        { "id": "uuid", "storage_url": "https://signed-url", "display_order": 0 },
        { "id": "uuid", "storage_url": "https://signed-url", "display_order": 1 }
      ],
      "audio_url": null,
      "video_url": "https://signed-url-for-video",
      "submitted_at": "2026-05-07T14:32:00Z",
      "status": "new",
      "submitter_display_name": "Ahmed Hassan",
      "labels": []
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

| Field | Change |
|-------|--------|
| `image_url` | **REMOVED** — replaced by `images` array |
| `images` | **NEW** — `list[FeedbackImageResponse]` — each item has `{ id, storage_url (signed, 1-hour expiry), display_order }` |
| `video_url` | **NEW** — signed URL (1-hour expiry) or null |

> Signed URLs are generated server-side for all `images[*].storage_url` and `video_url` values (1-hour expiry, same pattern as feature 011 audio signed URLs).

---

## Schemas Reference

### `FeedbackImageSubmitItem` ← used in submit response (raw path)

```json
{
  "id": "uuid",
  "storage_path": "feedback/{user_id}/{uuid}.jpg",
  "display_order": 0
}
```

> **Note**: The client already holds the file and its object URL. Returning the raw `storage_path` is sufficient for confirmation. No signing is performed at submit time.

### `FeedbackImageResponse` ← used in admin list response (signed URL)

```json
{
  "id": "uuid",
  "storage_url": "string (signed URL, 1-hour expiry)",
  "display_order": 0
}
```

### `FeedbackSubmitRequest` (updated)

```json
{
  "page_url": "string",
  "text_content": "string",
  "image_paths": ["string"] | null,
  "audio_url": "string | null",
  "video_url": "string | null"
}
```

### `FeedbackSubmitResponse` (updated)

```json
{
  "id": "uuid",
  "submitted_at": "datetime",
  "images": ["FeedbackImageSubmitItem"],
  "audio_url": "string | null",
  "video_url": "string | null"
}
```
