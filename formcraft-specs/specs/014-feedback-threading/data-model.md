# Data Model: Feedback Threading & Replies

**Branch**: `014-feedback-threading` | **Phase**: 1

---

## New Table: `feedback_replies`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | Unique identifier |
| `feedback_id` | `UUID` | NOT NULL, FK → `feedback_submissions(id) ON DELETE CASCADE` | Owning submission |
| `author_id` | `UUID` | NOT NULL, FK → `auth.users(id) ON DELETE CASCADE` | Reply author |
| `author_role` | `TEXT` | NOT NULL, CHECK IN `('admin', 'user')` | Role at time of posting |
| `text_content` | `TEXT` | NOT NULL, CHECK `char_length BETWEEN 1 AND 2000` | Reply body |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `NOW()` | Post timestamp |

> No `read_at` column — per-reply read tracking is out of scope for v1 (see research.md Decision 3). Admin unread state lives on `feedback_submissions.has_unread_user_reply`; user notification state lives on `feedback_notifications.read_at`.

**Indexes**:
- `(feedback_id, created_at DESC)` — primary thread fetch + cursor pagination (`before_id`)

**RLS Policies**:
- INSERT: `auth.uid() = author_id` AND (`author_role = 'admin'` requires admin profile OR `author_role = 'user'` requires `feedback_submissions.user_id = auth.uid()`)
- SELECT: `auth.uid() = (SELECT user_id FROM feedback_submissions WHERE id = feedback_id)` OR admin role via profiles JOIN

---

## New Table: `feedback_notifications`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | Unique identifier |
| `recipient_user_id` | `UUID` | NOT NULL, FK → `auth.users(id) ON DELETE CASCADE` | Notification recipient (the submitter) |
| `feedback_id` | `UUID` | NOT NULL, FK → `feedback_submissions(id) ON DELETE CASCADE` | Related submission |
| `reply_id` | `UUID` | NOT NULL, FK → `feedback_replies(id) ON DELETE CASCADE` | Triggering reply |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `NOW()` | When notification was created |
| `delivered_at` | `TIMESTAMPTZ` | NULLABLE | Set when the notification is fetched by the recipient's client (first GET /api/notifications call after creation) |
| `read_at` | `TIMESTAMPTZ` | NULLABLE | Set when the user clicks/taps the notification link |

**Indexes**:
- `(recipient_user_id, delivered_at)` — fetch undelivered notifications on login
- `(recipient_user_id, created_at DESC)` — notification badge count

**RLS Policies**:
- INSERT: admin role (notifications created by server-side service, not by the user)
- SELECT: `auth.uid() = recipient_user_id` OR admin role
- UPDATE (`delivered_at`, `read_at`): `auth.uid() = recipient_user_id`

---

## Modified: `feedback_submissions` (feature 011)

| Change | Column | Type | Default | Description |
|--------|--------|------|---------|-------------|
| ADD | `reply_count` | `INT` | `0` NOT NULL | Denormalised count of replies — updated by service layer on each INSERT/DELETE |
| ADD | `has_unread_user_reply` | `BOOLEAN` | `FALSE` NOT NULL | Set `TRUE` when a user posts a follow-up; cleared `FALSE` when admin expands the thread |

No existing columns are removed or renamed.

---

## Relationships

```
auth.users (existing)
    │
    ├── feedback_submissions (modified: ADD reply_count, has_unread_user_reply)
    │       │
    │       ├── feedback_replies (new)          ← N replies per submission
    │       │       └── author_id → auth.users
    │       │
    │       ├── feedback_notifications (new)    ← N notifications per submission
    │       │       ├── recipient_user_id → auth.users
    │       │       └── reply_id → feedback_replies
    │       │
    │       ├── feedback_images                 (from feature 013)
    │       └── feedback_submission_labels      (from feature 012)
    └── profiles (existing)
```

---

## Migration File

`011_create_feedback_replies.sql`

```sql
-- ============================================================
-- Feature 014: Feedback Threading & Replies
-- Depends on: 008_create_feedback_submissions.sql (feature 011)
-- ============================================================

-- 1. Add denormalised columns to feedback_submissions
ALTER TABLE feedback_submissions
    ADD COLUMN reply_count          INT     NOT NULL DEFAULT 0,
    ADD COLUMN has_unread_user_reply BOOLEAN NOT NULL DEFAULT FALSE;

-- 2. Create feedback_replies table
CREATE TABLE feedback_replies (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    feedback_id   UUID        NOT NULL REFERENCES feedback_submissions(id) ON DELETE CASCADE,
    author_id     UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    author_role   TEXT        NOT NULL CHECK (author_role IN ('admin', 'user')),
    text_content  TEXT        NOT NULL CHECK (char_length(text_content) BETWEEN 1 AND 2000),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_feedback_replies_thread
    ON feedback_replies (feedback_id, created_at DESC);

-- RLS
ALTER TABLE feedback_replies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authors can insert own replies"
    ON feedback_replies FOR INSERT
    WITH CHECK (auth.uid() = author_id);

CREATE POLICY "Submitters and admins can select replies"
    ON feedback_replies FOR SELECT
    USING (
        auth.uid() = (
            SELECT user_id FROM feedback_submissions WHERE id = feedback_id
        )
        OR EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid() AND profiles.role = 'admin'
        )
    );

-- 3. Create feedback_notifications table
CREATE TABLE feedback_notifications (
    id                 UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_user_id  UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    feedback_id        UUID        NOT NULL REFERENCES feedback_submissions(id) ON DELETE CASCADE,
    reply_id           UUID        NOT NULL REFERENCES feedback_replies(id) ON DELETE CASCADE,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    delivered_at       TIMESTAMPTZ,
    read_at            TIMESTAMPTZ
);

CREATE INDEX idx_notifications_undelivered
    ON feedback_notifications (recipient_user_id, delivered_at)
    WHERE delivered_at IS NULL;

CREATE INDEX idx_notifications_user_time
    ON feedback_notifications (recipient_user_id, created_at DESC);

-- RLS
ALTER TABLE feedback_notifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Admins can insert notifications"
    ON feedback_notifications FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid() AND profiles.role = 'admin'
        )
    );

CREATE POLICY "Recipients and admins can select notifications"
    ON feedback_notifications FOR SELECT
    USING (
        auth.uid() = recipient_user_id
        OR EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid() AND profiles.role = 'admin'
        )
    );

CREATE POLICY "Recipients can update own notifications"
    ON feedback_notifications FOR UPDATE
    USING (auth.uid() = recipient_user_id)
    WITH CHECK (auth.uid() = recipient_user_id);
```

---

## Service-Layer State Transition Rules

| Event | Service action on `feedback_submissions` |
|-------|------------------------------------------|
| User posts follow-up reply | `reply_count += 1`, `has_unread_user_reply = TRUE` |
| Admin posts reply | `reply_count += 1` (only); also INSERT into `feedback_notifications` for the submitter |
| Admin expands thread (PATCH /read) | `has_unread_user_reply = FALSE` |
