# API Contracts: Feedback Threading & Replies

**Branch**: `014-feedback-threading` | **Phase**: 1

All endpoints require `Authorization: Bearer <JWT>`. Admin endpoints require `role = 'admin'`.

---

## User-Facing Endpoints

### 1. List Own Submissions ("My Feedback")

```
GET /api/my-feedback
```

**Auth**: Authenticated user

**Query parameters**:

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Items per page |

**Response 200**:
```json
{
  "results": [
    {
      "id": "uuid",
      "page_url": "https://...",
      "text_content": "...",
      "status": "new",
      "submitted_at": "2026-05-07T12:00:00Z",
      "reply_count": 2,
      "has_unread_admin_reply": true
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

> `has_unread_admin_reply` is `true` when the user has at least one notification with `read_at IS NULL` for this submission.

---

### 2. Get Thread Replies (user — own submission only)

```
GET /api/feedback/{id}/replies
```

**Auth**: Authenticated user (must own the submission → 403 otherwise)

**Query parameters**:

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | 20 | Max replies to return |
| `before_id` | UUID \| null | — | Cursor — return replies created before this reply ID (for "Load earlier messages") |

**Response 200**:
```json
{
  "replies": [
    {
      "id": "uuid",
      "author_role": "admin",
      "author_name": "Support Team",
      "text_content": "Thanks for reporting this!",
      "created_at": "2026-05-08T09:00:00Z"
    }
  ],
  "has_earlier": true
}
```

**Error responses**:
| Code | Reason |
|------|--------|
| 403 | Submission does not belong to authenticated user |
| 404 | Submission not found |

---

### 3. Post User Follow-Up Reply

```
POST /api/feedback/{id}/replies
```

**Auth**: Authenticated user (must own the submission)

**Request body** (`application/json`):
```json
{
  "text_content": "Thanks, can you clarify the timeline?"
}
```

| Field | Type | Constraints |
|-------|------|-------------|
| `text_content` | string | Required; 1–2000 chars |

**Response 201**:
```json
{
  "id": "uuid",
  "author_role": "user",
  "author_name": "Ahmed Hassan",
  "text_content": "Thanks, can you clarify the timeline?",
  "created_at": "2026-05-08T10:00:00Z"
}
```

**Side effects** (service layer):
- `feedback_submissions.reply_count += 1`
- `feedback_submissions.has_unread_user_reply = TRUE`

**Error responses**:
| Code | Reason |
|------|--------|
| 400 | `text_content` empty or exceeds 2000 chars |
| 403 | Submission does not belong to authenticated user |
| 404 | Submission not found |

---

### 4. List Notifications

```
GET /api/notifications
```

**Auth**: Authenticated user

**Behaviour**: Returns all notifications where `recipient_user_id = auth.uid()`. Sets `delivered_at = NOW()` on all rows where `delivered_at IS NULL` in the same request (atomic mark-as-delivered). Used on app init to surface queued notifications (SC-004).

**Response 200**:
```json
{
  "notifications": [
    {
      "id": "uuid",
      "feedback_id": "uuid",
      "reply_id": "uuid",
      "created_at": "2026-05-08T09:00:00Z",
      "delivered_at": "2026-05-08T10:05:00Z",
      "read_at": null
    }
  ],
  "unread_count": 1
}
```

---

### 5. Mark Notification as Read

```
PATCH /api/notifications/{id}/read
```

**Auth**: Authenticated user (must own the notification)

**Request body**: none

**Response 204**: No content

**Side effect**: Sets `feedback_notifications.read_at = NOW()`.

**Error responses**:
| Code | Reason |
|------|--------|
| 403 | Notification does not belong to authenticated user |
| 404 | Notification not found |

---

## Admin Endpoints

### 6. Get Thread Replies (admin — any submission)

```
GET /api/admin/feedback/{id}/replies
```

**Auth**: Admin

**Query parameters**: same as endpoint 2 (`limit`, `before_id`)

**Response 200**: same shape as endpoint 2; `has_unread_user_reply` state visible via parent submission object (from existing `GET /api/admin/feedback`).

---

### 7. Post Admin Reply

```
POST /api/admin/feedback/{id}/replies
```

**Auth**: Admin

**Request body** (`application/json`):
```json
{
  "text_content": "We've deployed a fix for this issue."
}
```

**Response 201**: same shape as endpoint 3 (`author_role: "admin"`).

**Side effects** (service layer):
- `feedback_submissions.reply_count += 1`
- INSERT into `feedback_notifications(recipient_user_id, feedback_id, reply_id)` for the submission's `user_id`

**Error responses**:
| Code | Reason |
|------|--------|
| 400 | `text_content` empty or exceeds 2000 chars |
| 404 | Submission not found |

---

### 8. Clear Unread Indicator (auto-called on thread expand)

```
PATCH /api/admin/feedback/{id}/read
```

**Auth**: Admin

**Request body**: none

**Response 204**: No content

**Side effect**: Sets `feedback_submissions.has_unread_user_reply = FALSE`.

**Error responses**:
| Code | Reason |
|------|--------|
| 404 | Submission not found |

> This endpoint is called automatically by the frontend the moment the admin expands a submission thread panel (FR-015). No explicit user gesture required.

---

## Schemas Reference

### `ReplyResponse`
```json
{
  "id": "uuid",
  "author_role": "admin | user",
  "author_name": "string",
  "text_content": "string",
  "created_at": "datetime"
}
```

### `ReplyCreateRequest`
```json
{
  "text_content": "string (1–2000 chars)"
}
```

### `MyFeedbackItem`
```json
{
  "id": "uuid",
  "page_url": "string",
  "text_content": "string",
  "status": "new | reviewed | resolved",
  "submitted_at": "datetime",
  "reply_count": 0,
  "has_unread_admin_reply": false
}
```

### `NotificationResponse`
```json
{
  "id": "uuid",
  "feedback_id": "uuid",
  "reply_id": "uuid",
  "created_at": "datetime",
  "delivered_at": "datetime | null",
  "read_at": "datetime | null"
}
```

## Supabase Realtime Events (Angular client-side only)

| Channel | Event | Filter | Consumer |
|---------|-------|--------|----------|
| `thread:{feedback_id}` | `postgres_changes INSERT` | `table=feedback_replies&filter=feedback_id=eq.{id}` | Active thread panel — appends new reply live |
| `notifications:{user_id}` | `postgres_changes INSERT` | `table=feedback_notifications&filter=recipient_user_id=eq.{uid}` | Global notification badge — increments unread count |
