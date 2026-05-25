# Quickstart: Template Governance

## Prerequisites

- Backend environment configured for Supabase.
- Frontend dependencies installed in `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-frontend`.
- Existing F28 approval workflow available.
- Test users:
  - Org admin.
  - Designer with at least one draft/submitted template.
  - Optional operator/submission data for usage-impact warnings.

## Backend

1. Apply the new migration:

```bash
cd "/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-backend"
# apply migrations using the project Supabase workflow
```

2. Run backend tests:

```bash
cd "/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-backend"
pytest tests/unit/test_compliance_service.py tests/integration/test_template_governance_routes.py
```

3. Run lint:

```bash
cd "/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-backend"
ruff check .
```

## Frontend

1. Build the frontend:

```bash
cd "/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-frontend"
npm run build
```

2. Start the dev server:

```bash
cd "/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-frontend"
npm start
```

3. Open the app at:

```text
http://localhost:4200
```

## Manual Validation Flow

1. Login as an org admin.
2. Navigate to `/admin/templates`.
3. Confirm all org templates are visible across statuses with filters for status, department, designer, category, and search.
4. Select multiple templates and run "Change Category"; confirm category changes and audit log entries.
5. Select published templates and click "Bulk Archive"; confirm usage warning includes distinct operator count for current month before archiving.
6. Submit a template for review as a designer or use an existing `submitted_for_review` template.
7. Navigate to `/admin/reviews` and click "Review".
8. Confirm read-only canvas preview loads with template pages/elements.
9. Add an element-level comment on a field and request changes.
10. Login as the designer, open the rejected template, confirm the comment appears on the canvas/review panel, resolve it with a reply, and resubmit.
11. Login as admin, reopen review, confirm the prior comment shows resolved with the designer reply.
12. Open `/admin/templates/compliance`.
13. Confirm summary metrics, missing validators, missing bilingual labels, stale templates, and regulatory alerts render within target performance.

## API Smoke Checks

```bash
# Admin all-status template list
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/admin/templates?status=all&page=1&page_size=25"

# Bulk archive preview
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"template_ids":["TEMPLATE_ID"],"action":"archive","dry_run":true}' \
  "http://localhost:8000/api/admin/templates/bulk-actions"

# Review context
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/admin/review-queue/TEMPLATE_ID/review-context"

# Compliance dashboard
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/admin/templates/compliance"
```

## Expected Audit Events

- `TEMPLATE_BULK_ARCHIVED`
- `TEMPLATE_REASSIGNED`
- `TEMPLATE_CATEGORY_CHANGED`
- `TEMPLATE_REVIEW_COMMENT_CREATED`
- `TEMPLATE_REVIEW_COMMENT_RESOLVED`
- Existing F28 events for submitted/approved/rejected/published transitions remain in use.
