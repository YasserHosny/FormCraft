# UI/API Contract: New-Theme Admin Pages

This contract documents frontend expectations for F055. Backend API behavior remains unchanged.

## Routes

| Route | Component | Guard | Redirect behavior |
|-------|-----------|-------|-------------------|
| `/ui/admin/export` | Spark 3 Export page | `RoleGuard`, `roles: ['admin']` | Non-admin users redirect to `/ui/dashboard` |
| `/ui/admin/portal` | Spark 3 Portal page | `RoleGuard`, `roles: ['admin']` | Non-admin users redirect to `/ui/dashboard` |
| `/ui/admin/integrations` | Spark 3 Integrations page | `RoleGuard`, `roles: ['admin']` | Non-admin users redirect to `/ui/dashboard` |

Toolbar tab routes must point to these `/ui/admin/*` routes, not `/admin/*` classic routes.

## Export Page Service Contract

### Preview

- Service: `DataExportService.preview(request: ExportPreviewRequest)`
- Existing endpoint wrapped by service: `POST /admin/export/preview`
- Request: `ExportPreviewRequest`
- Success response: `ExportPreviewResponse`
- UI obligations:
  - Show loading while pending.
  - Show matching count and warnings on success.
  - Disable Download when `can_download=false` or matching count exceeds 50,000 records.
  - Show translated inline error and retry affordance on failure.

### Download

- Service: `DataExportService.download(request: ExportPreviewRequest)`
- Existing endpoint wrapped by service: `POST /admin/export/download`
- Response: `Blob`
- UI obligations:
  - Trigger browser download as `submissions.<format>`.
  - Disable duplicate clicks while pending.
  - Refresh history after successful download.

### History

- Service: `DataExportService.listHistory(page, pageSize)`
- Existing endpoint wrapped by service: `GET /admin/export/history`
- UI obligations:
  - Show paginated history rows.
  - Render translated empty state when `items` is empty.

## Portal Page Service Contract

### Template List

- Service: `PortalService.listPortalTemplates()`
- Existing endpoint wrapped by service: `GET /admin/portal/templates`
- UI obligations:
  - Render selectable template/configuration rows.
  - Show portal-enabled indicator per row.
  - Render translated empty, loading, and error states.

### Template Configuration

- Service: `PortalService.updatePortalTemplate(templateId, config)`
- Existing endpoint wrapped by service: `PATCH /admin/portal/templates/{templateId}`
- UI obligations:
  - Allow editing fields defined in `PortalConfiguration`.
  - Hide OTP mode controls when OTP/verification is disabled.
  - Show public URL as copyable text when present.
  - Render `public_qr_svg` when supplied; otherwise generate QR client-side using the existing classic-page approach.
  - Show translated success notification on save success.
  - Show translated inline validation/server error on save failure.

### Analytics

- Service: `PortalService.getPortalAnalytics(templateId)`
- Existing endpoint wrapped by service: `GET /admin/portal/analytics`
- UI obligations:
  - Render submission count, OTP sent/failure counts, rate-limit hits, and email-confirmation failures when available.
  - Analytics failure must not block configuration editing.

## Integrations Page Service Contract

### Credentials

- Service: `IntegrationService.listCredentials()`
- Existing endpoint wrapped by service: `GET /admin/integrations/credentials`
- Service: `IntegrationService.revokeCredential(credentialId)`
- Existing endpoint wrapped by service: `PATCH /admin/integrations/credentials/{credentialId}/revoke`
- UI obligations:
  - Display existing credentials with name, key prefix, scopes, status, timestamps.
  - Enable Revoke only for active credentials.
  - Refresh list after revoke.
  - Do not render create-credential flow in F055.

### Webhooks

- Service: `IntegrationService.listWebhooks()`
- Existing endpoint wrapped by service: `GET /admin/integrations/webhooks`
- Service: `IntegrationService.updateWebhook(webhookId, updates)`
- Existing endpoint wrapped by service: `PATCH /admin/integrations/webhooks/{webhookId}`
- UI obligations:
  - Display existing webhooks with name, event type, target URL, status, timestamps.
  - Toggle active <-> paused for active/paused webhooks.
  - Do not enable toggling disabled webhooks.
  - Do not render create-webhook flow in F055.

## Translation Contract

All visible text for the three pages must be represented in both:

- `formcraft-frontend/src/assets/i18n/en.json`
- `formcraft-frontend/src/assets/i18n/ar.json`

Required key groups:

- `adminExport.*`
- `adminPortal.*`
- `adminIntegrations.*`
- Any new `nav.*` labels needed by route updates

No raw user-facing English or Arabic strings should remain in templates, snackbars, confirmations, or inline errors.
