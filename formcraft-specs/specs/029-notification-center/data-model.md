# Data Model: Notification Center

**Feature**: 029-notification-center
**Date**: 2026-05-25

---

## Overview

This feature creates two new tables (`notifications`, `notification_preferences`) and extends the organization settings JSONB. The existing `feedback_notifications` table (migration 011) is preserved for backward compatibility but no new records will be written to it — the generalized `notifications` table replaces it for all future notification routing.

---

## Existing Tables Referenced (not modified)

### feedback_notifications (migration 011 — preserved, read-only)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| recipient_user_id | UUID FK -> auth.users | |
| feedback_id | UUID FK -> feedback_submissions | Feedback-specific |
| reply_id | UUID FK -> feedback_replies | Feedback-specific |
| created_at | TIMESTAMPTZ | |
| delivered_at | TIMESTAMPTZ | |
| read_at | TIMESTAMPTZ | |

**Migration note**: Stop writing to this table. Existing records remain queryable but the new `/api/notifications` endpoints read from the new `notifications` table only.

### notification_dismissals (migration 016 — unchanged)

Operator dashboard version dismissals. Separate UX concern, not part of notification engine.

### organizations.settings JSONB (extended)

| Key | Type | Status | Used For |
|-----|------|--------|----------|
| notification_preferences | object | EXISTS (migration 027) | Org-level default preferences |

**Current structure** (migration 027):
```json
{
  "notification_preferences": {
    "email": true,
    "in_app": true
  }
}
```

**New structure** (migration 031):
```json
{
  "notification_preferences": {
    "defaults": {
      "template_submitted_for_review": { "in_app": true, "email": true },
      "template_approved": { "in_app": true, "email": true },
      "template_rejected": { "in_app": true, "email": true },
      "template_published": { "in_app": true, "email": false },
      "template_withdrawn": { "in_app": true, "email": false },
      "template_feedback_received": { "in_app": true, "email": true },
      "template_feedback_resolved": { "in_app": true, "email": false },
      "draft_expiring": { "in_app": true, "email": true },
      "system_announcement": { "in_app": true, "email": true }
    }
  }
}
```

**Migration strategy**: The migration updates existing orgs' `notification_preferences` from the flat `{email, in_app}` format to the new per-type `{defaults: {...}}` format. The old boolean values become the default for all types.

---

## New Tables

### notifications

The central notification record. One row per recipient per event.

| Field | Type | Nullable | Default | Description |
|-------|------|----------|---------|-------------|
| id | UUID PK | NOT NULL | gen_random_uuid() | Row identity |
| recipient_id | UUID FK -> auth.users | NOT NULL | | Who receives this notification |
| org_id | UUID FK -> organizations | NOT NULL | | Multi-tenant scoping |
| type | TEXT | NOT NULL | | Notification type enum (see below) |
| title_ar | TEXT | NOT NULL | | Arabic title |
| title_en | TEXT | NOT NULL | | English title |
| body_ar | TEXT | NULL | | Arabic body (optional detail) |
| body_en | TEXT | NULL | | English body (optional detail) |
| action_url | TEXT | NULL | | Deep link path (e.g., `/designer/templates/{id}`) |
| source_id | UUID | NULL | | Reference to source entity (template_id, feedback_id, etc.) |
| source_type | TEXT | NULL | | Source entity type (`template`, `feedback`, `announcement`) |
| is_announcement | BOOLEAN | NOT NULL | false | Whether this is a system announcement (pinned display) |
| read_at | TIMESTAMPTZ | NULL | | When user read the notification (NULL = unread) |
| email_status | TEXT | NOT NULL | 'pending' | Email delivery: pending, sent, failed, skipped |
| email_sent_at | TIMESTAMPTZ | NULL | | When email was sent |
| email_error | TEXT | NULL | | Last error message if email failed |
| email_retry_count | INTEGER | NOT NULL | 0 | Number of email send attempts |
| created_by | UUID FK -> auth.users | NULL | | Who triggered the event (NULL for system events) |
| created_at | TIMESTAMPTZ | NOT NULL | NOW() | When notification was created |

**Notification type enum values**:
- `template_submitted_for_review`
- `template_approved`
- `template_rejected`
- `template_published`
- `template_withdrawn`
- `template_feedback_received`
- `template_feedback_resolved`
- `draft_expiring`
- `system_announcement`

**Indexes**:

| Index | Columns | Condition | Purpose |
|-------|---------|-----------|---------|
| idx_notifications_recipient_unread | (recipient_id, created_at DESC) | WHERE read_at IS NULL | Unread count + bell dropdown |
| idx_notifications_recipient_time | (recipient_id, created_at DESC) | | Full history listing |
| idx_notifications_org | (org_id, created_at DESC) | | Org-scoped admin queries |
| idx_notifications_email_pending | (email_status, created_at) | WHERE email_status = 'pending' | Email queue processing |

**RLS policies**:
- SELECT: `recipient_id = auth.uid()` OR user is admin in same org
- INSERT: Service role only (backend creates notifications)
- UPDATE: `recipient_id = auth.uid()` (mark as read) OR service role (email status updates)
- DELETE: None (notifications are never deleted)

### notification_preferences

Per-user, per-type channel preferences. Missing rows fall back to org defaults.

| Field | Type | Nullable | Default | Description |
|-------|------|----------|---------|-------------|
| id | UUID PK | NOT NULL | gen_random_uuid() | Row identity |
| user_id | UUID FK -> auth.users | NOT NULL | | Preference owner |
| org_id | UUID FK -> organizations | NOT NULL | | Multi-tenant scoping |
| notification_type | TEXT | NOT NULL | | Which notification type |
| in_app_enabled | BOOLEAN | NOT NULL | true | Receive in-app notifications |
| email_enabled | BOOLEAN | NOT NULL | true | Receive email notifications |
| created_at | TIMESTAMPTZ | NOT NULL | NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL | NOW() | |

**Constraints**:
- UNIQUE(user_id, org_id, notification_type) — one preference per user per type per org

**Indexes**:

| Index | Columns | Purpose |
|-------|---------|---------|
| idx_prefs_user_org | (user_id, org_id) | Fetch all user preferences |
| idx_prefs_user_type | (user_id, notification_type) | Lookup during notification creation |

**RLS policies**:
- SELECT: `user_id = auth.uid()` OR admin in same org
- INSERT: `user_id = auth.uid()` OR admin (for org defaults setup)
- UPDATE: `user_id = auth.uid()`
- DELETE: `user_id = auth.uid()`

---

## Migration: 031_notification_center.sql

**Sequence**: Runs after 030_approval_workflow.sql

**Operations**:
1. CREATE TABLE `notifications` with all fields, defaults, and foreign keys
2. CREATE indexes on `notifications`
3. ENABLE RLS on `notifications` + create policies
4. CREATE TABLE `notification_preferences` with unique constraint
5. CREATE indexes on `notification_preferences`
6. ENABLE RLS on `notification_preferences` + create policies
7. UPDATE `organizations.settings` to migrate `notification_preferences` from flat to per-type format

---

## Entity Relationships

```text
auth.users (1) ----< (N) notifications (recipient_id)
organizations (1) ----< (N) notifications (org_id)
auth.users (1) ----< (N) notification_preferences (user_id)
organizations (1) ----< (N) notification_preferences (org_id)

notifications.source_id --> templates.id (when source_type = 'template')
notifications.source_id --> feedback_submissions.id (when source_type = 'feedback')
notifications.created_by --> auth.users.id (event actor)
```

---

## Query Patterns

### Unread count (polling — every 30s)
```sql
SELECT COUNT(*) FROM notifications
WHERE recipient_id = :user_id AND org_id = :org_id AND read_at IS NULL;
```
Uses `idx_notifications_recipient_unread`. Expected <5ms.

### Bell dropdown (20 most recent)
```sql
SELECT id, type, title_ar, title_en, body_ar, body_en, action_url,
       is_announcement, read_at, created_at
FROM notifications
WHERE recipient_id = :user_id AND org_id = :org_id
ORDER BY is_announcement DESC, created_at DESC
LIMIT 20;
```
Announcements pinned to top via `is_announcement DESC`.

### Mark as read
```sql
UPDATE notifications SET read_at = NOW()
WHERE id = :notification_id AND recipient_id = :user_id;
```

### Mark all as read
```sql
UPDATE notifications SET read_at = NOW()
WHERE recipient_id = :user_id AND org_id = :org_id AND read_at IS NULL;
```

### Full history with filters
```sql
SELECT * FROM notifications
WHERE recipient_id = :user_id AND org_id = :org_id
  AND (:type IS NULL OR type = :type)
  AND (:read_status IS NULL OR (read_at IS NULL) = (:read_status = 'unread'))
  AND (:date_from IS NULL OR created_at >= :date_from)
  AND (:date_to IS NULL OR created_at <= :date_to)
ORDER BY created_at DESC
LIMIT :page_size OFFSET :offset;
```

### Bulk notification creation (batch insert)
```sql
INSERT INTO notifications (recipient_id, org_id, type, title_ar, title_en, body_ar, body_en, action_url, source_id, source_type, is_announcement, email_status, created_by)
VALUES (:r1, :org, :type, ...), (:r2, :org, :type, ...), ...;
```
Batch insert for multi-recipient events. Target: 500 rows in <3s.

### Preference lookup (during notification creation)
```sql
SELECT in_app_enabled, email_enabled FROM notification_preferences
WHERE user_id = :user_id AND org_id = :org_id AND notification_type = :type;
```
Returns NULL if no preference row exists — caller falls back to org defaults.

### Email queue processing
```sql
SELECT * FROM notifications
WHERE email_status = 'pending' AND email_retry_count < 3
ORDER BY created_at ASC
LIMIT 50;
```
