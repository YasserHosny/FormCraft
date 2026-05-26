# Quickstart: Granular Template Permissions

1. Apply migration:

   ```bash
   cd /media/yasserhosny/My\ Passport/Work/Projects/FormCraft/formcraft-backend
   # Apply migrations with the project's Supabase workflow.
   ```

2. Run backend tests:

   ```bash
   cd /media/yasserhosny/My\ Passport/Work/Projects/FormCraft/formcraft-backend
   pytest tests/unit/test_template_permission_service.py tests/integration/test_template_permissions_route.py
   ```

3. Manual API smoke test:

   - Create or update a policy with `PUT /api/admin/template-permissions/templates/{template_id}/policy`.
   - Check access with `GET /api/template-permissions/templates/{template_id}/decision?capability=fill`.
   - Verify diagnostics with `GET /api/admin/template-permissions/templates/{template_id}/diagnostics?user_id={user_id}&capability=fill`.

4. Expected behavior:

   - Explicit deny grants block the action even when an inherited allow also matches.
   - Imported templates with no active policy are admin-only.
   - Deactivated custom roles stop authorizing users on the next access check.
