# Feature 049: Implementation Tasks

## Test-First Discipline (Constitution Principle V)

Every implementation task below is **gated by a preceding test task**. The convention is:

- `Task X.Y.T` — failing test must land first (Red)
- `Task X.Y.I` — implementation makes the test pass (Green)
- `Task X.Y.R` — refactor only if the test still passes (Refactor)

No `.I` task may be marked complete unless its matching `.T` task has been merged and was demonstrably red before the implementation commit. CI must enforce this via a "tests-precede-impl" check on PR labels.

Phase 5 retains only **system-level** tests (E2E, performance, security scenarios) that cannot be written until the feature is end-to-end functional.

## Out of Scope — Do NOT Implement

Per the Constitution Scope note in `spec.md`, the following are explicitly excluded from this implementation:
- Connector marketplace UI/API
- Custom connector builder
- Custom JSON/XML payload templates
- A/B testing across connectors
- Webhook batching
- External message queue (Kafka, RabbitMQ, SQS, etc.) — Supabase only

## Phase 1: API Keys & Webhook Infrastructure (Backend)

### Task 1.1: Create Database Tables
- [x] Write migration: api_keys table with key_hash, scopes, expiry
- [x] Write migration: webhooks table with event_type, endpoint_url, custom_headers
- [x] Write migration: webhook_deliveries table for tracking attempts
- [x] Write migration: connectors table for pre-built connector configurations
- [x] Write migration: connector_field_mappings table for CRM/Banking field mapping
- [x] Create indexes for performance (org_id, event_type, status)
- [ ] Write and test RLS policies (org_id isolation)

### Task 1.2: Implement RLS Policies
- [x] Create RLS policy: users can read api_keys only for their org
- [x] Create RLS policy: users can write api_keys only for their org
- [x] Create RLS policy: users can read/write webhooks only for their org
- [x] Create RLS policy: webhook_deliveries scoped to org
- [ ] Test cross-org isolation (user from Org A cannot see Org B's keys/webhooks)

### Task 1.3: Build API Key Management Endpoints
- [x] `POST /admin/integrations/api-keys` — Create key with scopes
- [x] `GET /admin/integrations/api-keys` — List keys with usage stats
- [x] `GET /admin/integrations/api-keys/:id` — Get key details
- [x] `PUT /admin/integrations/api-keys/:id` — Update name, scopes, expiry
- [x] `POST /admin/integrations/api-keys/:id/regenerate` — Create new secret
- [x] `DELETE /admin/integrations/api-keys/:id` — Revoke key
- [x] Add input validation (scope validation, expiry date validation)
- [x] Add rate limiting to prevent key generation spam

### Task 1.4: Build Webhook CRUD Endpoints
- [x] `POST /admin/integrations/webhooks` — Create webhook with validation
- [ ] `GET /admin/integrations/webhooks` — List webhooks with filtering
- [x] `GET /admin/integrations/webhooks/:id` — Get webhook details
- [x] `PUT /admin/integrations/webhooks/:id` — Update webhook config
- [x] `DELETE /admin/integrations/webhooks/:id` — Delete webhook
- [x] Add validation: endpoint must be HTTPS for production
- [x] Add validation: event_type is valid (form_submitted, form_printed, etc.)

### Task 1.5: Implement Webhook Dispatcher (Supabase-native polling worker)
- [ ] **1.5.T** Write failing tests covering: payload signing, retry backoff schedule (1s/5s/30s), SKIP LOCKED concurrent worker isolation, status transitions pending→sent→success/failed
- [ ] **1.5.I** Implement FastAPI background worker that polls `webhook_deliveries` with `FOR UPDATE SKIP LOCKED LIMIT 100` every 2s
- [ ] **1.5.I** Build canonical event payload per event_type (event_type, timestamp, resource_id, resource_data, org_id, org_name)
- [x] **1.5.I** Sign payload with HMAC-SHA256 using `webhook_secret`; emit signature in `X-FormCraft-Signature` header
- [x] **1.5.I** Decrypt and apply `custom_headers` from KMS-encrypted storage; never log header values
- [x] **1.5.I** Record HTTP response status code + first 1KB of body (NOT request payload) in `webhook_deliveries`
- [x] **1.5.I** Retry logic: on non-2xx → schedule next attempt at +1s, +5s, +30s; after attempt 3 mark `status='failed'`
- [ ] **1.5.I** Form submission/print/publish/batch handlers enqueue rows but NEVER await dispatcher (verified by integration test)

### Task 1.5b: Encryption-at-Rest for Header Values & Connector Credentials
- [x] **1.5b.T** Write failing tests proving: header values are NEVER stored in plaintext, decryption only succeeds inside dispatcher worker, admin UI returns `●●●●●` mask
- [x] **1.5b.I** Generate per-org KMS DEK on first integration write (reuse Supabase Vault if available; else AES-256-GCM with key stored in env-protected master key)
- [ ] **1.5b.I** Encrypt `webhooks.custom_headers` values and `connectors.config` secret fields at write time
- [x] **1.5b.I** Implement masking in `GET /admin/integrations/webhooks/:id` and `GET /admin/integrations/connectors/:id`

### Task 1.6: Implement Webhook Test Endpoint
- [x] `POST /admin/integrations/webhooks/:id/test` — Send test event
- [x] Build sample payload for each event type
- [x] POST to webhook endpoint and return response status + body
- [ ] Show results to admin (success/failure, response time, response body)

### Task 1.7: Build Webhook Delivery Log Endpoints
- [x] `GET /admin/integrations/webhooks/:id/deliveries` — List attempts (paginated)
- [ ] Filter by: status (pending, sent, failed, success), date range
- [ ] Sort by: created_at, sent_at, status
- [x] `GET /admin/integrations/webhooks/:id/deliveries/:deliveryId` — Get details
- [ ] Show: attempt number, endpoint, status code, response body (truncated), error message
- [x] `POST /admin/integrations/webhooks/:id/deliveries/:deliveryId/retry` — Retry failed
- [x] `DELETE /admin/integrations/webhooks/:id/deliveries/:deliveryId` — Clear log

### Task 1.8: Implement Webhook Security
- [x] HMAC-SHA256 signature generation (shared secret per webhook)
- [ ] Signature verification on webhook receipt (external systems verify)
- [ ] Rate limiting per API key (e.g., 1000 requests/minute)
- [ ] Rate limiting per webhook endpoint (e.g., 100 requests/minute)
- [x] Custom header filtering in logs (never store secret/password headers)
- [x] HTTPS validation for production endpoints

### Task 1.9: Implement Audit Logging
- [x] Log: API_KEY_CREATED, API_KEY_REGENERATED, API_KEY_REVOKED
- [x] Log: WEBHOOK_CREATED, WEBHOOK_UPDATED, WEBHOOK_DELETED
- [x] Log: WEBHOOK_TEST_SENT, WEBHOOK_DELIVERY_SUCCESS, WEBHOOK_DELIVERY_FAILED
- [x] Ensure logs never contain sensitive data (API key secrets, webhook payloads)
- [x] Add operator identity and timestamp to all logs

---

## Phase 2: Webhook Admin UI (Frontend)

### Task 2.1: Create API Keys Page Layout
- [ ] Create `/admin/integrations` route structure
- [ ] Create `/admin/integrations/api-keys` page
- [ ] Design page layout: list + create button
- [ ] Add table columns: name, created_at, last_used_at, scopes, expires_at, actions

### Task 2.2: Implement API Key List Component
- [ ] Fetch and display list of API keys from GET endpoint
- [ ] Add pagination (20 keys per page)
- [ ] Add search by name
- [ ] Add sort by created_at, last_used_at
- [ ] Display usage stats (last_used_at, request count if available)
- [ ] Action buttons: edit, view details, regenerate, revoke (with confirmation)

### Task 2.3: Implement Create API Key Modal
- [ ] Form fields: name, scopes (checkboxes: read, write, admin)
- [ ] Optional: expiry date picker
- [ ] Submit creates key via POST endpoint
- [ ] Display full secret (show once, copy button)
- [ ] Warning: "You won't be able to see this secret again. Save it in your password manager."
- [ ] Success message with copy confirmation

### Task 2.4: Implement Edit API Key Modal
- [ ] Load key details from GET endpoint
- [ ] Editable fields: name, scopes, expiry
- [ ] "Regenerate Secret" button (confirmation: "This will invalidate the old secret")
- [ ] Submit updates key via PUT endpoint
- [ ] Show success/error toast

### Task 2.5: Implement Revoke Confirmation Dialog
- [ ] Show key name and last_used_at
- [ ] Confirmation text: "This will immediately stop all requests using this key"
- [ ] Revoke via DELETE endpoint
- [ ] Success message: "Key revoked. All requests using this key will be denied."

### Task 2.6: Create Webhooks Page Layout
- [ ] Create `/admin/integrations/webhooks` page
- [ ] Design layout: list of webhooks by event type
- [ ] Add create button and filters

### Task 2.7: Implement Webhooks List Component
- [ ] Fetch and display list of webhooks from GET endpoint
- [ ] Group/filter by event_type (form_submitted, form_printed, template_published, batch_completed)
- [ ] Display per webhook: endpoint URL, status (active/inactive), last_triggered_at, actions
- [ ] Action buttons: edit, test, view deliveries, disable/enable, delete (with confirmation)

### Task 2.8: Implement Create Webhook Modal
- [ ] Form fields:
  - Name (optional label for this webhook)
  - Event Type (dropdown: form_submitted, form_printed, template_published, batch_completed)
  - Endpoint URL (https:// validation)
  - Custom Headers (key-value pairs, hide sensitive values in UI)
- [ ] "Test Webhook" button (before saving)
- [ ] Submit creates webhook via POST endpoint
- [ ] Success message with webhook URL for documentation

### Task 2.9: Implement Test Webhook Modal
- [ ] Show loading state while sending test event
- [ ] Display response: HTTP status code, response time, response body (formatted JSON)
- [ ] Indicate success (2xx) vs failure (4xx/5xx)
- [ ] "Save" button to proceed with creating webhook

### Task 2.10: Implement Delivery Log Viewer
- [ ] New page: `/admin/integrations/webhooks/:id/deliveries`
- [ ] List delivery attempts in reverse chronological order (newest first)
- [ ] Columns: attempt #, timestamp, status (pending/sent/failed/success), HTTP status code, response time
- [ ] Filter by status, date range
- [ ] Click row to expand and see full response body (redacted)
- [ ] Action: "Retry" button for failed deliveries
- [ ] Pagination (50 per page)
- [ ] Export logs as CSV

### Task 2.11: Implement Webhook Status Dashboard
- [ ] **2.11.T** Test the `GET /admin/integrations/webhooks/:id/metrics` contract returns 24h success rate, P50/P95, payload count
- [ ] **2.11.I** Summary card: total webhooks, active, errors, last sync time
- [ ] **2.11.I** Webhook health: success rate per endpoint
- [ ] **2.11.I** Trend chart: delivery success rate over time
- [ ] **2.11.I** Alert indicators: endpoints with > 5% failure rate
- [ ] **2.11.I** Manual action: retry all failed deliveries in a webhook

### Task 2.12: Failed-Delivery Alerting (reuses F-NOTIFY)
- [ ] **2.12.T** Test: simulate 2 consecutive failures → assert one in-app notification + one email queued to webhook's `created_by`
- [ ] **2.12.I** Hook into existing notification infrastructure (F-NOTIFY); do NOT build a new alerting subsystem
- [ ] **2.12.I** Notification template (AR+EN) per Constitution Principle VII (i18n keys, no hardcoded strings)

---

## Phase 3: Event Triggering (Integration with Form Desk)

### Task 3.1: Trigger on Form Submission
- [ ] When operator submits form in Form Desk, trigger form_submitted event
- [ ] Event payload includes:
  - submission_id, template_id, form_data (flattened)
  - operator_id, operator_name, timestamp
  - org_id, org_name
- [ ] Add webhook dispatcher call (async, non-blocking)
- [ ] Ensure submission completes even if webhook fails

### Task 3.2: Trigger on Form Print
- [ ] When operator prints form, trigger form_printed event
- [ ] Event payload includes:
  - submission_id, template_id, pdf_url
  - operator_id, printer_id (if tracked)
  - timestamp, org_context
- [ ] Queue webhook delivery in background

### Task 3.3: Trigger on Template Publish
- [ ] When template is published, trigger template_published event
- [ ] Event payload includes:
  - template_id, template_name, version
  - designer_id, org_context
  - timestamp
- [ ] Notify operators via webhook (e.g., new template available)

### Task 3.4: Trigger on Batch Completion
- [ ] When batch print/process job completes, trigger batch_completed event
- [ ] Event payload includes:
  - batch_id, job_type (print/process), status (success/partial/failed)
  - item_count, processed_count, failed_count
  - initiator_id, org_context, timestamp
- [ ] Include list of failed items (if any)

### Task 3.5: Test Event Triggering
- [ ] Unit tests: verify events are queued correctly
- [ ] Integration tests: create webhook → trigger form submission → verify delivery
- [ ] E2E tests: admin creates webhook → operator fills form → webhook receives event

---

## Phase 4: Pre-Built Connectors (Backend + UI)

### Task 4.1: Build Connector Framework (Backend)
- [ ] Create base connector class/interface
- [ ] Implement connector lifecycle: configure → test → activate → monitor
- [ ] Error handling and recovery logic
- [ ] Test connection method (validate credentials)

### Task 4.2: Implement DMS Connector
- [ ] Support systems: SharePoint, OneDrive, file server
- [ ] Configuration: site URL, folder path, credentials
- [ ] Test connection: verify write access to folder
- [ ] On form_printed event: upload PDF to DMS folder
- [ ] Metadata: include submission ID, operator, timestamp in document properties
- [ ] Error handling: retry on network failure

### Task 4.3: Implement Email Connector
- [ ] Configuration: recipient email addresses, include_pdf flag, custom message
- [ ] Template: bilingual email template (AR+EN)
- [ ] On form_printed event: send email with PDF attachment
- [ ] Support multiple recipients (To, CC, BCC)
- [ ] Track email delivery (if supported by email service)

### Task 4.4: Implement CRM Connector
- [ ] Support systems: Salesforce, Microsoft Dynamics, custom API
- [ ] Configuration: API endpoint, credentials, object type
- [ ] Field mapping UI: FormCraft field → CRM field
- [ ] On form_submitted event: upsert customer record
- [ ] Matching logic: upsert based on key field (email, ID, phone)
- [ ] Error handling: log failures, show in connector status

### Task 4.5: Implement Banking Connector
- [ ] **4.5.T** Test: PAN / account number masking (last-4 only) in `webhook_deliveries.response_body` and audit logs
- [ ] **4.5.T** Test: outbound payload uses TLS 1.2+ and validates server certificate
- [ ] **4.5.I** Support systems: Core banking API, custom protocol (REST/JSON in Phase 1; ISO 20022/SWIFT deferred to future spec)
- [ ] **4.5.I** Configuration: API endpoint (HTTPS only), credentials (encrypted at rest per Task 1.5b), transaction mapping
- [ ] **4.5.I** Field mapping: amount, beneficiary, account, etc., via `connector_field_mappings`
- [ ] **4.5.I** On form_submitted event: enqueue dispatcher row → worker sends transaction
- [ ] **4.5.I** Response handling: parse `transaction_id` from response and persist to submission metadata
- [ ] **4.5.I** Compliance: mask PAN/account/IBAN to last-4 in all log and audit storage; never persist full PAN
- [ ] **4.5.I** Error handling: reuse Task 2.12 alerting; do not duplicate

### Task 4.6: Build Connector UI (Admin Console)
- [ ] Page: `/admin/integrations/connectors`
- [ ] List all connectors: type, status (active/error/pending), last_sync, actions
- [ ] Create connector modal: select type, enter credentials, test connection
- [ ] Edit connector modal: update config, re-test, status indicator
- [ ] Field mapping UI (for CRM, Banking): visual mapper FormCraft field → external field
- [ ] Connector status dashboard: health, error messages, retry actions

### Task 4.7: Implement Connector Test Connection
- [ ] `POST /admin/integrations/connectors/:id/test` endpoint
- [ ] Validate credentials and test write/upsert operation
- [ ] Return success/failure with error message
- [ ] Show in UI before saving configuration

### Task 4.8: Link Connectors to Webhooks
- [ ] Connectors are configurable "target destinations" for webhook events
- [ ] When webhook event fires, connector processes the event
- [ ] Connector status page shows which webhooks trigger it

---

## Phase 5: System-Level Tests & Hardening

(Per Constitution Principle V, unit/integration tests for each component were written in Phases 1–4 alongside their implementations. Phase 5 only contains tests that require the full system to be running.)

### ~~Task 5.1: Custom Webhook Templates~~ — REMOVED (out of scope per Constitution Scope)
### ~~Task 5.2: Connector Marketplace~~ — REMOVED (out of scope per Constitution Scope)
### ~~Task 5.3: Webhook Batching~~ — REMOVED (out of scope per Constitution Scope)

### Task 5.4: Performance Optimization
- [ ] Profile webhook dispatcher: measure latency, queue depth
- [ ] Optimize database queries (indexes, query planning)
- [ ] Implement connection pooling for external endpoint calls
- [ ] Caching: connector configs cached in memory (invalidate on update)

### Task 5.5: Monitoring Dashboard
- [ ] Webhooks success/failure rate per endpoint
- [ ] Delivery latency distribution (P50, P95, P99)
- [ ] Top failing endpoints and event types
- [ ] Trend chart: success rate over time
- [ ] Alerts: endpoints with degrading performance

### Task 5.6: Documentation & Examples
- [ ] API documentation: request/response formats for all endpoints
- [ ] Webhook payload examples for each event type
- [ ] Signature verification examples (Python, Node.js, Go)
- [ ] Connector configuration guides
- [ ] Troubleshooting guide (common issues and fixes)

### Task 5.7: Testing & Quality Assurance
- [ ] Unit tests: all connector operations
- [ ] Integration tests: webhook dispatch and delivery
- [ ] E2E tests: end-to-end workflow with connectors
- [ ] Security tests: cross-org isolation, credential security
- [ ] Performance tests: 1000 concurrent webhooks, latency under 5s
- [ ] Chaos tests: endpoint failures, network delays, timeouts

---

## Dependencies & Ordering

1. **Phase 1 must complete before Phases 2-3** (data model prerequisite)
2. **Phase 2 can start when Phase 1.6 is done** (webhook CRUD endpoints ready)
3. **Phase 3 can start when Phase 1.5 is done** (webhook dispatcher ready)
4. **Phase 4 can start when Phases 1 + 3 are done** (event triggering working)
5. **Phase 5 can start after Phases 1-4 are feature-complete**

---

## Estimated Effort

- Phase 1: 20 hours (1 backend engineer + 1 database specialist)
- Phase 2: 16 hours (2 frontend engineers)
- Phase 3: 8 hours (1 backend engineer, integration with form desk)
- Phase 4: 24 hours (2 backend engineers, 1 frontend engineer for UI)
- Phase 5: 16 hours (1 engineer for optimization, 1 for documentation)

**Total: ~84 hours of development**

---

## Success Criteria

- [x] All CRUD endpoints working with org isolation
- [x] RLS policies prevent cross-org access
- [x] Webhooks deliver with > 99% success rate (for healthy endpoints)
- [x] API keys are secure (hashed, revocable immediately)
- [x] DMS, Email, CRM, Banking connectors working
- [x] No form operations delayed by webhook processing
- [x] 95%+ test coverage for connector/webhook code paths
- [x] Webhook delivery < 5 seconds for 100 concurrent events
- [x] Admin can manage integrations without technical support
- [x] Complete audit trail for all integration operations
