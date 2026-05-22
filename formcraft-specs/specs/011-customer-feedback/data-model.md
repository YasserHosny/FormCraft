# Data Model: Customer Feedback

**Branch**: `001-customer-feedback` | **Phase**: 1

## New Table: `feedback_submissions`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | Unique identifier |
| `user_id` | `UUID` | NOT NULL, FK → `auth.users(id)` | Submitter |
| `page_url` | `TEXT` | NOT NULL | URL of page where widget was opened |
| `text_content` | `TEXT` | NOT NULL, `char_length <= 2000` | Required text message |
| `image_url` | `TEXT` | NULLABLE | Supabase Storage path for attached image |
| `audio_url` | `TEXT` | NULLABLE | Supabase Storage path for attached audio |
| `submitted_at` | `TIMESTAMPTZ` | NOT NULL, default `NOW()` | Submission timestamp |
| `status` | `TEXT` | NOT NULL, default `'new'`, CHECK IN `('new','reviewed','resolved')` | Admin review status |

**Indexes**:
- `(user_id, submitted_at DESC)` — cooldown check query
- `(submitted_at DESC)` — admin dashboard default sort
- `(status)` — admin status filter

**RLS Policies**:
- INSERT: `auth.uid() = user_id` (users submit only their own feedback)
- SELECT: `auth.jwt() ->> 'role' = 'admin'` (admin reads all; users cannot read others' feedback)
- UPDATE (status only): admin role

---

## Supabase Storage: `feedback` Bucket

| Setting | Value |
|---------|-------|
| Bucket name | `feedback` |
| Public | `false` (private) |
| File size limit | 10 MB |
| Allowed MIME types | `image/jpeg`, `image/png`, `image/webp`, `audio/mpeg`, `audio/mp4`, `audio/wav`, `audio/webm` |

**Storage path pattern**:
- Images: `feedback/{user_id}/{uuid}.{ext}`
- Audio: `feedback/{user_id}/{uuid}.{ext}`

**RLS on storage.objects**:
- INSERT: authenticated users, path prefix must equal their `user_id`
- SELECT: admin role OR owner (for signed URL generation)

---

## State Transitions: `status`

```
new → reviewed → resolved
new → resolved          (skip reviewed)
reviewed → new          (re-open)
resolved → reviewed     (re-open to reviewed)
```

---

## Relationships

```
auth.users (existing)
    │
    ├── profiles (existing) ← joined on profiles.id = feedback_submissions.user_id
    │       └── display_name / email  (used for submitter_display_name in admin API response)
    │
    └── feedback_submissions (new)
            ├── image_url → storage.objects (feedback bucket)
            └── audio_url → storage.objects (feedback bucket)
```

> **Note**: The `GET /api/admin/feedback` response includes `submitter_display_name`. This
> field is resolved by joining `feedback_submissions.user_id` → `profiles.id` and returning
> `profiles.display_name` (falling back to `profiles.email`). No new column is needed in
> `feedback_submissions`; this is a read-time JOIN in `list_feedback()` service method.

---

## Migration File

`008_create_feedback_submissions.sql`

```sql
-- Create feedback_submissions table
CREATE TABLE feedback_submissions (
    id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    page_url     TEXT        NOT NULL,
    text_content TEXT        NOT NULL CHECK (char_length(text_content) BETWEEN 1 AND 2000),
    image_url    TEXT,
    audio_url    TEXT,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status       TEXT        NOT NULL DEFAULT 'new'
                             CHECK (status IN ('new', 'reviewed', 'resolved'))
);

-- Indexes
CREATE INDEX idx_feedback_user_time ON feedback_submissions (user_id, submitted_at DESC);
CREATE INDEX idx_feedback_time      ON feedback_submissions (submitted_at DESC);
CREATE INDEX idx_feedback_status    ON feedback_submissions (status);

-- RLS
ALTER TABLE feedback_submissions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can insert own feedback"
    ON feedback_submissions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Admins can read all feedback"
    ON feedback_submissions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
              AND profiles.role = 'admin'
        )
    );

CREATE POLICY "Admins can update feedback status"
    ON feedback_submissions FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
              AND profiles.role = 'admin'
        )
    )
    WITH CHECK (true);
```
