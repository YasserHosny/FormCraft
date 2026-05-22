# Quickstart: Customer Feedback Feature

**Branch**: `001-customer-feedback`

## Running Locally

### Prerequisites
- Backend `.venv` active with all dependencies installed
- Supabase local dev running (`supabase start`)
- Angular dev server running

### 1. Apply the migration

```bash
cd formcraft-backend
supabase db push
# Applies 008_create_feedback_submissions.sql
```

### 2. Create the feedback storage bucket

In Supabase dashboard (or via CLI):
```bash
supabase storage create feedback --public=false
```

### 3. Start the backend

```bash
cd formcraft-backend
.venv/bin/uvicorn app.main:app --reload
```

New routes available:
- `POST /api/feedback/upload/image`
- `POST /api/feedback/upload/audio`
- `POST /api/feedback`
- `GET  /api/admin/feedback`
- `PATCH /api/admin/feedback/{id}`

### 4. Start the frontend

```bash
cd formcraft-frontend
npm start
```

The feedback widget (floating button) will appear in the bottom-right corner of all authenticated pages.

Admin dashboard: navigate to `/admin/feedback` while logged in as an admin user.

## Running Tests

```bash
# Backend unit tests
cd formcraft-backend
.venv/bin/pytest tests/unit/feedback/ -v

# Backend integration tests
.venv/bin/pytest tests/integration/feedback/ -v
```

## Key Files

| File | Purpose |
|------|---------|
| `formcraft-backend/supabase/migrations/008_create_feedback_submissions.sql` | DB migration |
| `formcraft-backend/app/api/routes/feedback.py` | Submit + upload endpoints |
| `formcraft-backend/app/api/routes/admin.py` | Admin list + status-update endpoints (extended) |
| `formcraft-backend/app/schemas/feedback.py` | Pydantic request/response models |
| `formcraft-backend/app/services/feedback/service.py` | Business logic, cooldown, storage upload |
| `formcraft-frontend/src/app/features/feedback/` | Feedback widget + admin dashboard |
| `formcraft-frontend/src/app/features/feedback/services/feedback.service.ts` | API calls |
| `formcraft-frontend/src/app/features/feedback/components/feedback-widget/` | Floating widget |
| `formcraft-frontend/src/app/features/feedback/components/feedback-admin/` | Admin dashboard |
