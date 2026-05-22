# Quickstart: Feedback Dashboard Search & Labels

**Branch**: `012-feedback-dashboard-search`  
**Depends on**: Feature 011 (`001-customer-feedback`) fully applied

## Prerequisites

- Feature 011 migration (`008_create_feedback_submissions.sql`) already applied
- Backend `.venv` active with all dependencies installed
- Supabase local dev running (`supabase start`)
- Angular dev server running

## 1. Apply the migration

```bash
cd formcraft-backend
supabase db push
# Applies 009_create_feedback_labels.sql
```

## 2. Start the backend

```bash
cd formcraft-backend
.venv/bin/uvicorn app.main:app --reload
```

New routes available:
- `GET  /api/admin/feedback?search=keyword&label_ids=uuid1,uuid2`  (extended)
- `GET  /api/admin/labels`
- `POST /api/admin/labels`
- `PATCH /api/admin/labels/{id}`
- `DELETE /api/admin/labels/{id}`
- `PUT  /api/admin/feedback/{id}/labels`

## 3. Start the frontend

```bash
cd formcraft-frontend
npm start
```

Navigate to `/admin/feedback` as an admin user. You will see:
- A search bar at the top of the dashboard (debounced, fires 300–500 ms after typing stops)
- Filter controls: Status chips, Submitter autocomplete, Date range pickers, Label multi-select
- "Manage Labels" button in the toolbar → opens the label management modal
- A Labels column on each submission row

## Running Tests

```bash
# Backend unit tests
cd formcraft-backend
.venv/bin/pytest tests/unit/feedback/test_label_service.py -v

# Backend integration tests
.venv/bin/pytest tests/integration/feedback/test_admin_label_route.py -v
```

## Key Files

| File | Purpose |
|------|---------|
| `formcraft-backend/supabase/migrations/009_create_feedback_labels.sql` | DB migration |
| `formcraft-backend/app/schemas/label.py` | Pydantic label models |
| `formcraft-backend/app/services/feedback/service.py` | Extended list_feedback + label CRUD methods |
| `formcraft-backend/app/api/routes/admin.py` | Extended admin routes (search, labels, assignment) |
| `formcraft-frontend/src/app/features/feedback/services/feedback-filter-state.service.ts` | Session filter state |
| `formcraft-frontend/src/app/features/feedback/components/label-manager/` | Label management modal |
| `formcraft-frontend/src/app/features/feedback/components/feedback-admin/` | Extended admin dashboard |
