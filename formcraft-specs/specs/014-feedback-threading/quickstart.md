# Quickstart: Feedback Threading & Replies

**Branch**: `014-feedback-threading`  
**Depends on**: Feature 011 (`001-customer-feedback`) fully applied — `feedback_submissions` table, admin dashboard, and widget must exist

## Prerequisites

- Feature 011 migration (`008_create_feedback_submissions.sql`) already applied
- Backend `.venv` active with all dependencies installed
- Supabase local dev running (`supabase start`)
- Angular dev server running
- Supabase Realtime enabled for local dev (enabled by default in `supabase start`)

## 1. Apply the migration

```bash
cd formcraft-backend
supabase db push
# Applies 011_create_feedback_replies.sql:
#   - ADD COLUMN reply_count, has_unread_user_reply to feedback_submissions
#   - CREATE feedback_replies table with RLS
#   - CREATE feedback_notifications table with RLS
```

## 2. Enable Supabase Realtime for new tables

In Supabase Dashboard → Database → Replication → Tables:
- Enable `feedback_replies` (INSERT events)
- Enable `feedback_notifications` (INSERT events)

Or via `supabase/config.toml` if using local config:
```toml
[realtime]
enabled = true
```

## 3. Start the backend

```bash
cd formcraft-backend
.venv/bin/uvicorn app.main:app --reload
```

New / modified routes available:
- `GET  /api/my-feedback`                          (NEW — user's submission history)
- `GET  /api/feedback/{id}/replies`                (NEW — thread for own submission)
- `POST /api/feedback/{id}/replies`                (NEW — user posts follow-up)
- `GET  /api/notifications`                        (NEW — fetch + deliver queued notifications)
- `PATCH /api/notifications/{id}/read`             (NEW — mark notification read)
- `GET  /api/admin/feedback/{id}/replies`          (NEW — admin reads any thread)
- `POST /api/admin/feedback/{id}/replies`          (NEW — admin posts reply)
- `PATCH /api/admin/feedback/{id}/read`            (NEW — admin clears unread flag on expand)

## 4. Start the frontend

```bash
cd formcraft-frontend
npm start
```

- Navigate to `/my-feedback` as an authenticated user — see submission history
- Expand a submission — see thread and reply input; live replies appear via Supabase Realtime
- Navigate to `/admin/feedback` as admin — expand a submission — see thread panel; reply; unread badge clears automatically on expand

## Running Tests

```bash
# Backend unit tests
cd formcraft-backend
.venv/bin/pytest tests/unit/feedback/test_reply_service.py -v

# Backend integration tests
.venv/bin/pytest tests/integration/feedback/test_reply_routes.py -v
```

## Key Files

| File | Purpose |
|------|---------|
| `formcraft-backend/supabase/migrations/011_create_feedback_replies.sql` | DB migration |
| `formcraft-backend/app/schemas/reply.py` | Pydantic models |
| `formcraft-backend/app/services/feedback/reply_service.py` | Business logic (replies, notifications, my-feedback) |
| `formcraft-backend/app/api/routes/feedback.py` | User-facing endpoints |
| `formcraft-backend/app/api/routes/admin.py` | Admin endpoints (modified) |
| `formcraft-frontend/src/app/features/feedback/services/feedback-realtime.service.ts` | Supabase Realtime channel manager |
| `formcraft-frontend/src/app/features/my-feedback/` | My Feedback page module |
| `formcraft-frontend/src/app/shared/components/thread/` | Shared ThreadComponent |

## Verifying Realtime

Open two browser windows — one as admin, one as a regular user on `/my-feedback`.

1. Admin posts a reply in the dashboard.
2. Regular user's open thread should update within 1 second (SC-001 / SC-002).
3. If not updating: check browser console for Supabase Realtime connection errors; verify the tables are enabled for replication in Supabase config.
