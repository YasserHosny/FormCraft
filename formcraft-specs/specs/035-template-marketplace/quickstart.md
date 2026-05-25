# Quickstart: Template Marketplace

## Prerequisites

- Backend dependencies installed from `formcraft-backend/requirements.txt`
- Frontend dependencies installed in `formcraft-frontend/`
- Supabase database available with existing FormCraft migrations applied
- An admin user with an organization and at least one published template

## Backend Validation

1. Apply the migration:

   ```bash
   cd formcraft-backend
   supabase db push
   ```

2. Run backend tests:

   ```bash
   cd formcraft-backend
   pytest tests/unit/test_marketplace_service.py tests/integration/test_marketplace_routes.py
   ```

3. Start the API:

   ```bash
   cd formcraft-backend
   uvicorn app.main:app --reload
   ```

4. Verify browse endpoint with an admin token:

   ```bash
   curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/marketplace/listings?page=1&page_size=24"
   ```

## Frontend Validation

1. Start the Angular app:

   ```bash
   cd formcraft-frontend
   npm start
   ```

2. Navigate to `/marketplace`.

3. Verify in RTL and LTR:

   - Listings grid loads with translated labels.
   - Search and filters update the list.
   - Listing detail opens with read-only canvas/PDF preview.
   - Free listing import creates a draft template.
   - Premium listing purchase creates a transaction before import.
   - Publish flow submits a published template for review.
   - Verified importer can submit one rating/review.

## Critical Scenarios

- Imported templates remain unchanged after publisher updates a listing.
- Reference-data dependencies require remapping before activation.
- Unsupported validators/custom fields are disabled with warnings.
- Suspended publisher listings disappear from marketplace browse and cannot be imported.
- Audit logs are created for publish, approve/reject, purchase, import, review, refund/reversal, and suspension actions.

## Implementation Validation Notes

- Focused backend tests pass with the shared backend virtual environment:
  `../../FormCraft/formcraft-backend/.venv/bin/python -m pytest tests/unit/test_marketplace_service.py tests/integration/test_marketplace_routes.py`
- Ruff passes for new F035 backend files.
- `npm run build` was retried after `npm ci`; it remains blocked by existing non-F035 Angular errors in admin portal, reports, and public portal templates. The build log contains no remaining F035 marketplace errors after fixing the marketplace review component initialization.
