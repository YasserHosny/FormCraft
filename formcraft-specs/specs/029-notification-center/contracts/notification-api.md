# API Contract: Notification Center

**Base path**: `/api`
**Auth**: Required (Bearer token)

---

## Existing Endpoints (migrated)

### GET /api/notifications

Previously served by `feedback.py` user_router reading from `feedback_notifications`. Now served by new `notifications.py` router reading from `notifications` table.

**Role gate**: Any authenticated user

**Query params**:

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| type | string | no | null | Filter by notification type |
| status | string | no | null | Filter: `read`, `unread`, or null (all) |
| date_from | ISO 8601 | no | null | Start date filter |
| date_to | ISO 8601 | no | null | End date filter |
| page | integer | no | 1 | Page number |
| page_size | integer | no | 20 | Items per page (max 50) |

**Response 200**:
```json
{
  "notifications": [
    {
      "id": "uuid",
      "type": "template_approved",
      "title_ar": "تمت الموافقة على النموذج",
      "title_en": "Template approved",
      "body_ar": "تمت الموافقة على نموذج \"فتح حساب\" بواسطة أحمد",
      "body_en": "Template \"Account Opening\" approved by Ahmed",
      "action_url": "/designer/templates/uuid",
      "source_id": "uuid",
      "source_type": "template",
      "is_announcement": false,
      "read_at": null,
      "created_by": "uuid",
      "created_at": "2026-05-25T10:30:00Z"
    }
  ],
  "total": 45,
  "page": 1,
  "page_size": 20
}
```

**Scoping**: Returns only notifications where `recipient_id = current_user` and `org_id = current_org`.

---

## New Endpoints

### GET /api/notifications/unread-count

Lightweight endpoint for bell icon badge polling (every 30s).

**Role gate**: Any authenticated user

**Response 200**:
```json
{
  "unread_count": 3
}
```

**Performance**: <50ms target. Uses `idx_notifications_recipient_unread` index.

---

### PATCH /api/notifications/{notification_id}/read

Mark a single notification as read.

**Role gate**: Any authenticated user (must be recipient)

**Response 200**:
```json
{
  "id": "uuid",
  "read_at": "2026-05-25T11:00:00Z"
}
```

**Error responses**:

| Status | When |
|--------|------|
| 404 | Notification not found or not owned by current user |

---

### POST /api/notifications/read-all

Mark all unread notifications as read for the current user.

**Role gate**: Any authenticated user

**Response 200**:
```json
{
  "marked_count": 5
}
```

---

### GET /api/notifications/preferences

Get current user's notification preferences. Returns merged view: user overrides + org defaults for types without user override.

**Role gate**: Any authenticated user

**Response 200**:
```json
{
  "preferences": [
    {
      "notification_type": "template_submitted_for_review",
      "in_app_enabled": true,
      "email_enabled": true,
      "is_default": true
    },
    {
      "notification_type": "template_approved",
      "in_app_enabled": true,
      "email_enabled": false,
      "is_default": false
    },
    {
      "notification_type": "template_rejected",
      "in_app_enabled": true,
      "email_enabled": true,
      "is_default": false
    },
    {
      "notification_type": "template_published",
      "in_app_enabled": true,
      "email_enabled": false,
      "is_default": true
    },
    {
      "notification_type": "template_withdrawn",
      "in_app_enabled": true,
      "email_enabled": false,
      "is_default": true
    },
    {
      "notification_type": "template_feedback_received",
      "in_app_enabled": true,
      "email_enabled": true,
      "is_default": true
    },
    {
      "notification_type": "template_feedback_resolved",
      "in_app_enabled": true,
      "email_enabled": false,
      "is_default": true
    },
    {
      "notification_type": "draft_expiring",
      "in_app_enabled": true,
      "email_enabled": true,
      "is_default": true
    },
    {
      "notification_type": "system_announcement",
      "in_app_enabled": true,
      "email_enabled": true,
      "is_default": true
    }
  ]
}
```

**Notes**:
- `is_default: true` means no user override exists — value comes from org defaults
- `is_default: false` means user has explicitly set this preference

---

### PATCH /api/notifications/preferences

Update one or more notification preferences for the current user. Creates preference rows if they don't exist (upsert).

**Role gate**: Any authenticated user

**Body**:
```json
{
  "preferences": [
    {
      "notification_type": "template_approved",
      "in_app_enabled": true,
      "email_enabled": false
    },
    {
      "notification_type": "template_rejected",
      "in_app_enabled": true,
      "email_enabled": true
    }
  ]
}
```

**Response 200**:
```json
{
  "updated": 2
}
```

**Error responses**:

| Status | When |
|--------|------|
| 422 | Invalid notification_type value |

---

### POST /api/admin/announcements

Create and send a system announcement to targeted users.

**Role gate**: admin only

**Body**:
```json
{
  "title_ar": "صيانة مجدولة",
  "title_en": "Scheduled Maintenance",
  "body_ar": "ستكون الخدمة غير متاحة يوم الجمعة من 2-4 صباحاً",
  "body_en": "Service will be unavailable Friday 2-4 AM",
  "target_audience": "all",
  "target_role": null,
  "target_department_id": null
}
```

**Body fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title_ar | string | yes | Arabic title |
| title_en | string | yes | English title |
| body_ar | string | no | Arabic body |
| body_en | string | no | English body |
| target_audience | string | yes | `all`, `role`, `department` |
| target_role | string | conditional | Required when target_audience = `role`. Values: `admin`, `branch_manager`, `designer`, `operator` |
| target_department_id | UUID | conditional | Required when target_audience = `department` |

**Response 201**:
```json
{
  "announcement_id": "uuid",
  "recipients_count": 42,
  "created_at": "2026-05-25T09:00:00Z"
}
```

**Behavior**: Creates one `notifications` row per recipient with `type = 'system_announcement'` and `is_announcement = true`. Email notifications queued for recipients with email enabled for `system_announcement` type.

**Error responses**:

| Status | When |
|--------|------|
| 403 | Non-admin user |
| 422 | target_audience = 'role' but target_role missing |
| 422 | target_audience = 'department' but target_department_id missing |

---

### GET /api/notifications/unsubscribe

Email unsubscribe endpoint. Linked from email footer. Disables email for specific notification type.

**Auth**: Token-based (signed URL token in query param, not Bearer)

**Query params**:

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| token | string | yes | Signed JWT containing user_id, org_id, notification_type |

**Response 200**: HTML page confirming unsubscription.

**Response 400**: Invalid or expired token.

**Behavior**: Sets `email_enabled = false` for the user+type in `notification_preferences` (creates row if missing). Does not affect in_app channel.

---

## Internal API (not exposed via REST)

### NotificationService.create_notifications()

Called internally by template_service.transition_status() and reply_service.create_reply().

**Input**:
```python
async def create_notifications(
    org_id: str,
    event_type: str,          # NotificationType enum value
    title_ar: str,
    title_en: str,
    body_ar: str | None,
    body_en: str | None,
    action_url: str | None,
    source_id: str | None,
    source_type: str | None,
    recipient_ids: list[str],  # Pre-resolved list of user IDs
    created_by: str | None,
    background_tasks: BackgroundTasks,
) -> int:  # Returns count of notifications created
```

**Behavior**:
1. For each recipient_id, check notification_preferences (user-level, then org defaults)
2. Skip if both in_app and email disabled for this type
3. Batch insert notification rows (email_status = 'skipped' if email disabled, 'pending' if enabled)
4. Queue email sending as background task for 'pending' rows
5. Return count of created notifications
