# Data Model: External Form Portal

## Existing Entities Used

### Organization

Source table: `organizations` and `org_settings`

F034 usage:
- Resolve public URL org slug/custom domain.
- Scope portal configuration, sessions, OTP challenges, rate-limit events, and public submissions.

### Template

Source table: `templates`

Relevant fields:
- `id` UUID primary key
- `org_id` UUID
- `name` text
- `status` text
- `version` integer
- `lineage_id` UUID nullable
- `created_by` UUID
- `updated_at` timestamptz

F034 usage:
- Only published templates can be exposed publicly.
- Portal sessions pin `template_id` and `template_version` at load time.
- Public URL slug is unique per org/template portal config.
- Public QR codes are derived from the canonical public URL and are not persisted in F034.

### Page and Element

Source tables: `pages`, `elements`, and current render/read models used by Form Desk.

F034 usage:
- Public Flow Layout renders form fields from the pinned template version.
- Validation, conditions, required logic, and tafqeet reuse existing deterministic services.
- Optional PDF download reuses existing renderer and pinned version.

### Submission

Source table: `submissions`

F034 usage:
- Public submissions are inserted through the existing submission workflow where possible.
- Public-specific metadata is stored separately with `source = public_portal` semantics.

## New Entity: Portal Configuration

Source table: `portal_configurations`

Fields:
- `id` UUID primary key, default `gen_random_uuid()`
- `org_id` UUID not null, references `organizations(id)`
- `template_id` UUID not null, references `templates(id)`
- `public_slug` text not null
- `enabled` boolean not null default false
- `verification_required` boolean not null default false
- `allowed_otp_modes` text[] not null default empty array, allowed values `sms`, `email`
- `captcha_enabled` boolean not null default false
- `captcha_provider` text nullable, allowed values `hcaptcha`, `recaptcha`
- `allow_pdf_download` boolean not null default false
- `send_email_confirmation` boolean not null default false
- `rate_limit_max` integer not null default 10
- `rate_limit_window_minutes` integer not null default 60
- `created_by` UUID not null, references `profiles(id)`
- `created_at` timestamptz not null default `now()`
- `updated_at` timestamptz not null default `now()`

Validation rules:
- `(org_id, public_slug)` must be unique.
- `(org_id, template_id)` must be unique.
- `template_id` must reference a published template before `enabled = true`.
- `allowed_otp_modes` must be non-empty when `verification_required = true`.
- `captcha_provider` is required when `captcha_enabled = true`.

State transitions:

```text
disabled -> enabled
enabled -> disabled
```

## New Entity: Portal Session

Source table: `portal_sessions`

Fields:
- `id` UUID primary key, default `gen_random_uuid()`
- `org_id` UUID not null, references `organizations(id)`
- `portal_configuration_id` UUID not null, references `portal_configurations(id)`
- `template_id` UUID not null, references `templates(id)`
- `template_version` integer not null
- `session_token_hash` text not null
- `browser_fingerprint_hash` text nullable
- `ip_hash` text not null
- `status` text not null default `started`, allowed values `started`, `otp_verified`, `submitted`, `expired`, `locked`
- `otp_verified_at` timestamptz nullable
- `verified_contact_mode` text nullable, allowed values `sms`, `email`
- `verified_contact_hash` text nullable
- `expires_at` timestamptz not null
- `created_at` timestamptz not null default `now()`
- `updated_at` timestamptz not null default `now()`

Validation rules:
- Session token is shown only to the browser; only hash is stored.
- Template version never changes after creation.
- OTP-gated submissions require `status = otp_verified`.

State transitions:

```text
started -> otp_verified
started -> locked
started -> expired
otp_verified -> submitted
otp_verified -> expired
```

## New Entity: OTP Verification

Source table: `portal_otp_verifications`

Fields:
- `id` UUID primary key, default `gen_random_uuid()`
- `org_id` UUID not null, references `organizations(id)`
- `portal_session_id` UUID not null, references `portal_sessions(id)` on delete cascade
- `contact_mode` text not null, allowed values `sms`, `email`
- `contact_hash` text not null
- `code_hash` text not null
- `status` text not null default `pending`, allowed values `pending`, `verified`, `failed`, `locked`, `expired`, `provider_failed`
- `attempt_count` integer not null default 0
- `expires_at` timestamptz not null
- `locked_until` timestamptz nullable
- `sent_at` timestamptz nullable
- `verified_at` timestamptz nullable
- `provider_error` text nullable
- `created_at` timestamptz not null default `now()`
- `updated_at` timestamptz not null default `now()`

Validation rules:
- Maximum 3 failed attempts before 15-minute lockout.
- OTP provider failure leaves the session blocked.
- Only the latest pending challenge for a session/contact is verifiable.

## New Entity: Portal Rate Limit Event

Source table: `portal_rate_limit_events`

Fields:
- `id` UUID primary key, default `gen_random_uuid()`
- `org_id` UUID not null, references `organizations(id)`
- `portal_configuration_id` UUID not null, references `portal_configurations(id)`
- `portal_session_id` UUID nullable, references `portal_sessions(id)` on delete set null
- `key_type` text not null, allowed values `pre_otp`, `verified_contact`
- `key_hash` text not null
- `event_type` text not null, allowed values `load`, `otp_send`, `submit`
- `allowed` boolean not null
- `window_start` timestamptz not null
- `created_at` timestamptz not null default `now()`

Validation rules:
- Pre-OTP key is derived from IP hash plus browser/session key.
- Post-OTP key is derived from verified contact hash.
- Events older than retention window may be purged.

## New Entity: Public Submission Metadata

Source table: `public_submission_metadata`

Fields:
- `id` UUID primary key, default `gen_random_uuid()`
- `org_id` UUID not null, references `organizations(id)`
- `submission_id` UUID not null, references `submissions(id)` on delete cascade
- `portal_configuration_id` UUID not null, references `portal_configurations(id)`
- `portal_session_id` UUID not null, references `portal_sessions(id)`
- `source` text not null default `public_portal`, allowed value `public_portal`
- `template_version` integer not null
- `verified_contact_mode` text nullable, allowed values `sms`, `email`
- `verified_contact_hash` text nullable
- `submission_ip_hash` text not null
- `captcha_verified` boolean not null default false
- `audit_field_summary` JSONB not null default `{}`::jsonb
- `pdf_download_token_hash` text nullable
- `pdf_download_expires_at` timestamptz nullable
- `email_confirmation_status` text nullable, allowed values `not_requested`, `queued`, `sent`, `failed`
- `email_confirmation_sent_at` timestamptz nullable
- `email_confirmation_failure_reason` text nullable
- `created_at` timestamptz not null default `now()`
- `updated_at` timestamptz not null default `now()`

Validation rules:
- `submission_id` is unique.
- `audit_field_summary` must be bounded/redacted and must not store full raw submitted payload.
- `template_version` must match the portal session pinned version.
- Email confirmation failure must not roll back or delete the submission.

## Derived Analytics

Portal analytics are computed from `public_submission_metadata`, `portal_rate_limit_events`, and `portal_otp_verifications` for F034. A materialized daily rollup can be added later if query cost demands it.
