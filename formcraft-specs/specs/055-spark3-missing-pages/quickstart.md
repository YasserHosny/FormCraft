# Quickstart: New-Theme Admin Pages - Export, Portal, Integration

## Preconditions

- Work on branch `055-spark3-missing-pages`.
- Do not modify backend code or unrelated feature spec paths.
- Frontend environment can authenticate as an admin and as a non-admin user.

## Verification Scenarios

1. **Admin navigation**
   - Log in as admin.
   - Open `/ui/admin/analytics`.
   - Click toolbar tabs for Export, Portal, and Integration.
   - Expected: routes are `/ui/admin/export`, `/ui/admin/portal`, and `/ui/admin/integrations`; no classic-theme redirect occurs.

2. **Role guard**
   - Log in as non-admin.
   - Navigate directly to `/ui/admin/export`, `/ui/admin/portal`, and `/ui/admin/integrations`.
   - Expected: user is redirected to `/ui/dashboard` and never sees page content.

3. **Export page**
   - Open `/ui/admin/export` as admin.
   - Set filters and format/scope.
   - Click Preview.
   - Expected: matching count, warnings, and download eligibility render.
   - If matching count is above 50,000 or backend returns `can_download=false`, Download is disabled.
   - Click Download for an eligible preview.
   - Expected: browser downloads `submissions.<format>` and history refreshes.

4. **Portal page**
   - Open `/ui/admin/portal` as admin.
   - Select a template.
   - Toggle enabled state, OTP, captcha, rate-limit fields, email confirmation, and PDF download.
   - Save.
   - Expected: success notification appears and selected/list configuration updates.
   - Force duplicate slug/server validation failure.
   - Expected: inline translated error appears and edits remain visible.

5. **Integrations page**
   - Open `/ui/admin/integrations` as admin.
   - Expected: API credential and webhook sections render.
   - Revoke an active credential.
   - Expected: status updates to revoked and revoke action disables.
   - Pause/resume a webhook.
   - Expected: status updates after save and section refreshes.

6. **Empty/loading/error states**
   - Verify each page shows translated loading indicators while requests are active.
   - Mock empty responses for history/templates/credentials/webhooks.
   - Expected: translated empty states render instead of blank tables.
   - Mock request failure.
   - Expected: translated inline error and retry action render.

7. **Arabic/RTL and English/LTR**
   - Switch to Arabic while each page is open.
   - Expected: labels and values use Arabic translation keys and layout mirrors without reload.
   - Switch back to English.
   - Expected: LTR layout and English translations render without raw keys.

## Suggested Commands

```bash
cd formcraft-frontend
npm test -- --watch=false
```

Use the project's existing frontend serve command to perform manual browser checks if not covered by automated tests.
