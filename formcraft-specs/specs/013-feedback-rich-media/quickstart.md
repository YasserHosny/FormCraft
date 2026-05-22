# Quickstart: Feedback Rich Media

**Branch**: `013-feedback-rich-media`  
**Depends on**: Feature 011 (`001-customer-feedback`) fully applied (migration 008 in place, widget and admin dashboard live)

## Prerequisites

- Feature 011 migration (`008_create_feedback_submissions.sql`) already applied
- Backend `.venv` active with all dependencies installed
- Supabase local dev running (`supabase start`)
- Angular dev server running

## 1. Apply the migration

```bash
cd formcraft-backend
supabase db push
# Applies 010_extend_feedback_rich_media.sql
# Creates feedback_images table, adds video_url, backfills image_url → feedback_images, drops image_url
```

## 2. Update Supabase Storage bucket

In Supabase Dashboard → Storage → `feedback` bucket → Settings:
- **File size limit**: set to `100` MB
- **Allowed MIME types**: add `video/mp4`, `video/webm`

Or via Supabase CLI (if using `storage.config.toml`):
```toml
[storage.buckets.feedback]
file_size_limit = "100MiB"
allowed_mime_types = [
  "image/jpeg", "image/png", "image/webp",
  "audio/mpeg", "audio/mp4", "audio/wav", "audio/webm",
  "video/mp4", "video/webm"
]
```

## 3. Start the backend

```bash
cd formcraft-backend
.venv/bin/uvicorn app.main:app --reload
```

New / modified routes available:
- `POST /api/feedback/upload/image`   (extended — was single-image, now called per-image)
- `DELETE /api/feedback/upload/image` (unchanged contract)
- `POST /api/feedback/upload/video`   (NEW)
- `DELETE /api/feedback/upload/video` (NEW)
- `POST /api/feedback`                (modified — `image_paths[]` + `video_url`)
- `GET  /api/admin/feedback`          (modified — `images[]` array + `video_url` in response)

## 4. Start the frontend

```bash
cd formcraft-frontend
npm start
```

Open the feedback widget (FAB button). You will see:
- A thumbnail grid for up to 5 images with individual remove buttons
- A "5 images maximum" message when the limit is reached
- A video section with Record / Upload controls (Record hidden in unsupported browsers)
- 2-minute elapsed timer during recording
- Audio and video sections disable each other with explanatory messages

Navigate to `/admin/feedback` as an admin user to see:
- Multi-thumbnail grid in expanded submission rows
- Inline `<video>` player for video submissions

## Running Tests

```bash
# Backend unit tests
cd formcraft-backend
.venv/bin/pytest tests/unit/feedback/test_rich_media_service.py -v

# Backend integration tests
.venv/bin/pytest tests/integration/feedback/test_rich_media_routes.py -v
```

## Key Files

| File | Purpose |
|------|---------|
| `formcraft-backend/supabase/migrations/010_extend_feedback_rich_media.sql` | DB migration |
| `formcraft-backend/app/schemas/feedback.py` | Updated Pydantic models (FeedbackSubmitRequest, FeedbackImageResponse) |
| `formcraft-backend/app/services/feedback/service.py` | upload_image, upload_video, delete_upload, updated submit_feedback + list_feedback |
| `formcraft-backend/app/api/routes/feedback.py` | New upload/delete image+video endpoints |
| `formcraft-frontend/src/app/features/feedback/services/video-recorder.service.ts` | VideoRecorderService (MediaRecorder lifecycle) |
| `formcraft-frontend/src/app/features/feedback/components/feedback-widget/` | Updated widget with multi-image and video support |
