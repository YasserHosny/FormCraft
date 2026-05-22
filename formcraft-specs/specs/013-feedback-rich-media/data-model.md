# Data Model: Feedback Rich Media

**Branch**: `013-feedback-rich-media` | **Phase**: 1

---

## New Table: `feedback_images`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | Unique identifier |
| `feedback_id` | `UUID` | NOT NULL, FK → `feedback_submissions(id) ON DELETE CASCADE` | Owning submission |
| `storage_path` | `TEXT` | NOT NULL | Supabase Storage path (e.g. `feedback/{user_id}/{uuid}.jpg`) |
| `display_order` | `SMALLINT` | NOT NULL, default `0` | Client-assigned 0-based position; rendered ASC |
| `uploaded_at` | `TIMESTAMPTZ` | NOT NULL, default `NOW()` | Server insert timestamp |

**Constraint**: Max 5 images per submission enforced at the service layer (counted before INSERT).

**Indexes**:
- `(feedback_id, display_order ASC)` — primary lookup: all images for a submission in display order

**RLS Policies**:
- INSERT: `auth.uid() = (SELECT user_id FROM feedback_submissions WHERE id = feedback_id)` — submitter inserts their own images via two-step upload
- SELECT: admin role (via profiles JOIN)
- DELETE: admin role or owner (for abort/cleanup path)

---

## Modified: `feedback_submissions` (feature 011)

| Change | Column | Direction |
|--------|--------|-----------|
| DROP | `image_url` | Replaced by `feedback_images` relation |
| ADD | `video_url` | `TEXT NULLABLE` — Supabase Storage path for an attached video |

> **Migration note**: Any existing rows with `image_url` set are migrated to a `feedback_images` row with `display_order = 0` before the column is dropped. Production deployments with real data must run the backfill step.

The `audio_url` column is unchanged.

---

## Relationships

```
auth.users (existing)
    │
    └── feedback_submissions (modified: DROP image_url, ADD video_url)
            │
            ├── feedback_images (new)          ← up to 5 rows per submission
            ├── audio_url → storage.objects    (existing, unchanged)
            ├── video_url → storage.objects    (new nullable column)
            └── feedback_submission_labels     (from feature 012)
                    └── feedback_labels        (from feature 012)
```

---

## Supabase Storage: `feedback` Bucket (updated)

| Setting | Previous Value | New Value |
|---------|---------------|-----------|
| File size limit | 10 MB | **100 MB** |
| Allowed MIME types (additions) | — | `video/mp4`, `video/webm` |

All existing MIME types (`image/jpeg`, `image/png`, `image/webp`, `audio/mpeg`, `audio/mp4`, `audio/wav`, `audio/webm`) remain.

> **Note**: The 5 MB per-image and 10 MB per-audio limits are enforced client-side; the bucket limit is a hard backstop against API bypass.

**Storage path patterns**:
- Images: `feedback/{user_id}/{uuid}.{ext}` (unchanged path format)
- Audio: `feedback/{user_id}/{uuid}.{ext}` (unchanged)
- Video: `feedback/{user_id}/{uuid}.{ext}` (new; same path namespace)

---

## Migration File

`010_extend_feedback_rich_media.sql`

```sql
-- ============================================================
-- Feature 013: Feedback Rich Media
-- Depends on: 008_create_feedback_submissions.sql (feature 011)
-- ============================================================

-- 1. Create feedback_images table
CREATE TABLE feedback_images (
    id            UUID       PRIMARY KEY DEFAULT gen_random_uuid(),
    feedback_id   UUID       NOT NULL REFERENCES feedback_submissions(id) ON DELETE CASCADE,
    storage_path  TEXT       NOT NULL,
    display_order SMALLINT   NOT NULL DEFAULT 0,
    uploaded_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_feedback_images_submission
    ON feedback_images (feedback_id, display_order ASC);

-- RLS
ALTER TABLE feedback_images ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Submitters can insert own feedback images"
    ON feedback_images FOR INSERT
    WITH CHECK (
        auth.uid() = (
            SELECT user_id FROM feedback_submissions WHERE id = feedback_id
        )
    );

CREATE POLICY "Admins can select feedback images"
    ON feedback_images FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid() AND profiles.role = 'admin'
        )
    );

CREATE POLICY "Owners and admins can delete feedback images"
    ON feedback_images FOR DELETE
    USING (
        auth.uid() = (
            SELECT user_id FROM feedback_submissions WHERE id = feedback_id
        )
        OR EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid() AND profiles.role = 'admin'
        )
    );

-- 2. Add video_url to feedback_submissions
ALTER TABLE feedback_submissions ADD COLUMN video_url TEXT;

-- 3. Backfill: migrate existing image_url rows to feedback_images
INSERT INTO feedback_images (feedback_id, storage_path, display_order, uploaded_at)
SELECT id, image_url, 0, submitted_at
FROM feedback_submissions
WHERE image_url IS NOT NULL;

-- 4. Drop the now-replaced image_url column
ALTER TABLE feedback_submissions DROP COLUMN image_url;
```

---

## Service-Layer Validation Rules

| Rule | Enforcement |
|------|-------------|
| Max 5 images per submission | `FeedbackService.submit_feedback()`: count existing `feedback_images` rows for `feedback_id` before INSERT |
| Audio / video mutual exclusion | `FeedbackSubmitRequest` Pydantic `@model_validator`: raises 422 if both `audio_url` and `video_url` are non-null |
| Video MIME type | Client-side `File.type` check + Supabase bucket MIME allowlist |
| Video size ≤ 100 MB | Client-side `File.size` check |
| Image MIME + size (each) | Client-side checks; Supabase bucket MIME allowlist for JPEG/PNG/WEBP |
