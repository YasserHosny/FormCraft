# API Contract: Operator Dashboard

## New Endpoint: `GET /api/desk/dashboard`

### Request

Query parameters:

| Param | Type | Required | Default | Values | Notes |
|-------|------|----------|---------|--------|-------|
| search | string | no | null | any string | ILIKE match on template name + description |
| category | string | no | null | any category string | Exact match on template.category |
| country | string | no | null | "EG", "SA", "AE" | Exact match on template.country |
| language | string | no | null | "ar", "en" | Exact match on template.language |
| page | int | no | 1 | >= 1 | Pagination for templates grid |
| limit | int | no | 20 | 1-100 | Items per page for templates grid |

### Response (200 OK)

```json
{
  "templates": {
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "KYC Form",
        "description": "Know Your Customer onboarding form",
        "category": "banking",
        "status": "published",
        "version": 3,
        "language": "ar",
        "country": "EG",
        "updated_at": "2026-05-16T10:00:00Z",
        "is_pinned": true
      }
    ],
    "total": 45,
    "page": 1,
    "limit": 20
  },
  "recent": [
    {
      "template_id": "550e8400-e29b-41d4-a716-446655440000",
      "template_name": "KYC Form",
      "category": "banking",
      "version": 3,
      "last_used_at": "2026-05-16T09:30:00Z"
    }
  ],
  "pinned": [
    {
      "template_id": "550e8400-e29b-41d4-a716-446655440000",
      "template_name": "KYC Form",
      "category": "banking",
      "version": 3,
      "is_published": true,
      "pinned_at": "2026-05-10T08:00:00Z"
    }
  ],
  "drafts": [],
  "notifications": [
    {
      "id": "generated-uuid",
      "template_id": "550e8400-e29b-41d4-a716-446655440000",
      "template_name": "KYC Form",
      "old_version": 2,
      "new_version": 3,
      "updated_at": "2026-05-16T08:00:00Z"
    }
  ]
}
```

**Notes**:
- `templates.items[].is_pinned`: Boolean indicating if the current user has pinned this template. Enables the pin toggle on template cards.
- `recent`: Maximum 10 items. Empty array if operator has no submission history.
- `pinned`: All of the operator's pinned templates. `is_published` is false if the template was unpublished after pinning.
- `drafts`: Empty array until the drafts table exists (Form Filler feature). Future shape: `{ draft_id, template_id, template_name, completion_percent, last_modified, expires_at }`.
- `notifications`: Derived from templates where current version > last version the operator used, excluding dismissed notifications.
- `notifications[].id`: A deterministic composite identifier in the format `{template_id}:{new_version}` (e.g., `550e8400-e29b-41d4-a716-446655440000:3`). Used as the `:notificationId` path param for dismissal. The backend parses this to extract template_id and version for the dismissal record.

---

## New Endpoint: `POST /api/desk/pins`

### Request

```json
{
  "template_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| template_id | UUID | yes | Must reference a published template in the operator's org |

### Response (201 Created)

```json
{
  "id": "pin-uuid",
  "template_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-05-16T10:00:00Z"
}
```

### Error Responses

| Status | Condition | Body |
|--------|-----------|------|
| 409 Conflict | Template already pinned | `{ "detail": "Template already pinned" }` |
| 422 Unprocessable | Pin limit (20) exceeded | `{ "detail": "Maximum 20 pinned templates allowed" }` |
| 404 Not Found | Template doesn't exist or not published | `{ "detail": "Template not found" }` |

---

## New Endpoint: `DELETE /api/desk/pins/:templateId`

### Response (204 No Content)

No body.

### Error Responses

| Status | Condition | Body |
|--------|-----------|------|
| 404 Not Found | Pin doesn't exist | `{ "detail": "Pin not found" }` |

---

## New Endpoint: `POST /api/desk/notifications/:notificationId/dismiss`

### Request

No body. The `notificationId` is the deterministic ID from the dashboard response (e.g., `template_id:version`).

### Response (204 No Content)

No body. Creates a row in `notification_dismissals`.

### Error Responses

| Status | Condition | Body |
|--------|-----------|------|
| 404 Not Found | Notification ID invalid | `{ "detail": "Notification not found" }` |

---

## Authentication & Authorization

All endpoints require:
- Valid JWT token (AuthGuard)
- User role must have access to `/desk` mode (operator, designer, admin, viewer)
- All queries scoped by org_id via Supabase RLS

No additional role guards — all desk-mode users can access the dashboard.
