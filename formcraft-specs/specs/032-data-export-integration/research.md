# Research: Data Export & Integration

## Decision: Use Direct Downloads For One-Time Submission Exports

**Rationale**: The clarified spec requires direct download only. The export service will preview matching count, reject oversized requests before generation, and stream CSV/workbook/JSON responses for allowed exports. This avoids introducing a generic background export queue for one-time requests.

**Alternatives considered**:
- Background job for every one-time export. Rejected because the user selected direct download only.
- Hybrid small-direct/large-background export. Rejected because oversized exports must be rejected and narrowed by filters.

## Decision: Store Export History For Requests, Schedules, And Email Deliveries

**Rationale**: The spec requires export history showing actor, filters, format, status, delivery summary, and failure/completion times. A normalized export request/schedule/delivery model supports auditability without storing generated files permanently unless implementation chooses short-lived file storage for email attachments.

**Alternatives considered**:
- Rely only on audit logs. Rejected because admins need operational export status/history and retry/failure details.
- Store all generated exports indefinitely. Rejected because it increases sensitive data retention; history can record metadata while direct downloads stream immediately.

## Decision: Recurring Exports Are Email-Only In F32

**Rationale**: Clarification narrowed recurring delivery to email only, with SFTP/file-transfer deferred. This reuses the notification/email infrastructure direction from F29 and keeps the first export integration phase operationally small.

**Alternatives considered**:
- Include SFTP/file-transfer destinations. Rejected by clarification and would add credential, connectivity, and network failure complexity.
- Save schedules without delivery. Rejected because scheduled exports must actually deliver to recipients.

## Decision: Spreadsheet Export Uses Safe Field-Key Columns And Formula Escaping

**Rationale**: Flattened exports need one column per form field key. CSV/workbook cells must preserve Arabic/mixed text and neutralize values that spreadsheet tools could interpret as formulas. Field keys remain stable machine-readable headers; labels can be included in metadata or workbook secondary sheet later if needed.

**Alternatives considered**:
- Use localized labels as primary headers. Rejected because duplicate/missing labels and language switching make downstream integration unstable.
- Export raw field JSON only. Rejected because spreadsheet users need flattened columns.

## Decision: `.formcraft` Package Is A Versioned JSON Bundle

**Rationale**: Template portability needs a deterministic, inspectable bundle of template, pages, elements, validators, conditions, and reference-binding metadata. A manifest with package schema version, source org metadata, template lineage, and checksums lets import validate compatibility and reject corrupted/unsupported packages before any partial creation.

**Alternatives considered**:
- Zip package with multiple files. Rejected initially because a single JSON bundle is simpler to validate and move.
- Database dump-style export. Rejected because it risks leaking org-specific IDs and violates portability/remapping needs.

## Decision: Matching Package Imports Create New Template Versions

**Rationale**: Clarification selected new-version behavior when lineage or template name matches an existing template. Imports must not replace the currently published version; instead they create a new draft/version record that follows existing template versioning semantics.

**Alternatives considered**:
- Always import as a new draft. Rejected by clarification.
- Reject all name/lineage conflicts. Rejected because environment promotion needs controlled version updates.

## Decision: API Integration Credentials Are Hashed And Scoped

**Rationale**: The secret is shown once and must be revocable immediately. Store only a hash/fingerprint plus metadata, scopes, expiry, last-used time, and revoked state. Request authentication resolves credential to org/scopes before permitting integration access.

**Alternatives considered**:
- Store reversible plaintext credentials. Rejected for security.
- Use ordinary user JWTs for integrations. Rejected because external system credentials need independent scope, expiry, and revocation.

## Decision: Webhook Deliveries Require HMAC Signatures

**Rationale**: The spec requires every active webhook to have a signing secret and every delivery to include a verifiable signature. HMAC over timestamp + payload with a per-subscription secret is a common deterministic pattern that lets receivers verify origin and detect tampering.

**Alternatives considered**:
- Optional secrets. Rejected by clarification.
- URL-only webhooks. Rejected because payloads can include sensitive submission data.

## Decision: Store Full Webhook Payload Previews With Admin-Only Access

**Rationale**: Clarification requires full payload previews in delivery logs for admins. To reduce blast radius, delivery logs remain org-scoped, admin-only, and audited when viewed if implementation supports read auditing.

**Alternatives considered**:
- Redacted previews only. Rejected by clarification.
- Metadata-only logs. Rejected because admins need full troubleshooting context.

## Decision: Hook Webhooks Into Existing Domain Events Without A General Automation Engine

**Rationale**: F32 events are limited to form submitted, form printed, template published, and batch completed. Services that already perform these actions can enqueue or dispatch webhook deliveries through `WebhookService`, preserving simple, explicit integration points.

**Alternatives considered**:
- General event bus/automation engine. Rejected by the constitution and out-of-scope for F32.
- Polling external systems. Rejected because AC-07 calls for webhooks and no polling.
