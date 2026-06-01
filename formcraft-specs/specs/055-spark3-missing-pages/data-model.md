# Data Model: New-Theme Admin Pages - Export, Portal, Integration

No backend database changes are introduced. The frontend consumes existing service DTOs from:

- `formcraft-frontend/src/app/shared/models/integration.models.ts`
- `formcraft-frontend/src/app/shared/models/portal.models.ts`

## Export Filter

**Source type**: `ExportPreviewRequest.filters`

**Fields**:

- `template_id`: optional UUID string
- `date_from`: optional ISO/date string
- `date_to`: optional ISO/date string
- `branch_id`: optional UUID string
- `operator_id`: optional UUID string
- `status`: optional string
- `format`: `csv` | `xlsx` | `json`
- `scope`: `flattened` | `structured`

**Validation rules**:

- Empty filters are omitted from the request payload.
- Download remains disabled until a successful preview indicates the export can be downloaded.
- Counts above 50,000 records are presented as oversized and not downloadable.

## Export Preview

**Source type**: `ExportPreviewResponse`

**Fields**:

- `matching_count`: non-negative integer
- `estimated_file_size_bytes`: optional non-negative integer or null
- `can_download`: boolean
- `rejection_reason`: optional string or null
- `warnings`: string array

## Export Record

**Source type**: `ExportRequestRecord`

**Fields**:

- `id`: UUID
- `dataset`: `submissions`
- `format`: `csv` | `xlsx` | `json`
- `scope`: `flattened` | `structured`
- `status`: `previewed` | `completed` | `rejected` | `failed`
- `matching_count`: non-negative integer
- `rejection_reason`: optional string or null
- `created_at`: timestamp string

## Portal Configuration

**Source type**: `PortalConfiguration`

**Fields**:

- `template_id`: UUID
- `public_slug`: non-empty string
- `public_url`: string
- `public_qr_svg`: SVG string or null
- `enabled`: boolean
- `verification_required`: boolean
- `allowed_otp_modes`: array of `sms` | `email`
- `captcha_enabled`: boolean
- `captcha_provider`: `hcaptcha` | `recaptcha` | null
- `allow_pdf_download`: boolean
- `send_email_confirmation`: boolean
- `rate_limit_max`: positive integer
- `rate_limit_window_minutes`: positive integer

## Portal Analytics

**Source type**: `PortalAnalyticsResponse`

**Fields**:

- `submission_count`: integer
- `otp_sent_count`: integer
- `otp_failure_count`: integer
- `rate_limited_count`: integer
- `email_confirmation_failure_count`: integer

## API Credential

**Source type**: `IntegrationCredential`

**Fields**:

- `id`: UUID
- `name`: string
- `key_prefix`: string
- `scopes`: array of supported integration scopes
- `status`: `active` | `revoked` | `expired`
- `expires_at`: optional timestamp or null
- `last_used_at`: optional timestamp or null
- `created_at`: timestamp string

**Allowed UI operations**:

- Revoke active credentials.
- Display revoked/expired credentials without enabled revoke action.
- Creating credentials is out of scope.

## Webhook Subscription

**Source type**: `WebhookSubscription`

**Fields**:

- `id`: UUID
- `name`: string
- `event_type`: `form_submitted` | `form_printed` | `template_published` | `batch_completed`
- `target_url`: URL string
- `signing_secret_prefix`: optional string or null
- `status`: `active` | `paused` | `disabled`
- `created_at`: timestamp string

**Allowed UI operations**:

- Toggle active webhooks to paused.
- Toggle paused webhooks to active.
- Display disabled webhooks without enabled toggle.
- Creating webhooks is out of scope.
