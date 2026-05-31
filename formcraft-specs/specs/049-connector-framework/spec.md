# Feature 049: Connector Framework

## Overview
A pluggable integration framework that enables FormCraft to securely connect to external enterprise systems (banking, CRM, document management, email, etc.) via webhooks, REST APIs, and pre-built connectors. Admins configure integrations without code, triggering automated workflows on form submission, printing, template publishing, and batch completion.

## Objective
Enable FormCraft submissions to seamlessly integrate with downstream systems — automatically archiving PDFs to document management, syncing customer data to CRM, triggering bank workflows, sending notifications — all without custom development.

## Constitution Scope (Principle IX — YAGNI)

This feature is **explicitly scoped to four pre-built connectors and four event types** to avoid violating Principle IX (Simplicity and YAGNI), which forbids a "general-purpose bulk automation engine".

**In Scope (Phase 1):**
- 4 event types only: `form_submitted`, `form_printed`, `template_published`, `batch_completed`
- 4 pre-built connectors only: DMS, Email, CRM, Banking
- HTTPS webhooks to admin-configured URLs (org-bounded)

**Out of Scope (REMOVED from this spec):**
- Connector marketplace (was FR-8) — deferred until ≥3 customer requests document a need
- Custom connector builder UI — admins use raw webhooks only in Phase 1
- A/B testing across connector configurations
- Custom JSON/XML payload templating (only one canonical payload schema per event type)
- Webhook batching (was Phase 5)

Any future extension MUST be filed as a separate spec amendment.

## User Stories

### US-1: Configure API Keys & Webhooks (Org Admin)
**As an** Org Admin  
**I want to** generate API keys scoped to my organization and configure webhook endpoints  
**So that** external systems can receive FormCraft events in real-time

**Acceptance Criteria:**
- Admin can navigate to `/admin/integrations/api-keys` page
- Can generate API keys with unique identifiers and secrets
- Each key shows creation date, last used date, and scopes (read, write, admin)
- Can revoke/regenerate keys immediately
- Webhook endpoints can be configured for: form_submitted, form_printed, template_published, batch_completed
- Admin can test webhooks before activating (send sample payload)
- Webhook delivery logs show success/failure history

### US-2: Auto-Archive Submissions to Document Management (System Integration)
**As a** System Integration  
**I want to** receive webhook events when forms are printed  
**So that** PDFs can be automatically archived to the organization's document management system

**Acceptance Criteria:**
- on_form_printed webhook includes: submission ID, template ID, PDF URL, metadata
- DMS connector validates credentials and tests connection before saving
- Failed archive attempts trigger retry with exponential backoff (1s, 5s, 30s)
- Admin can see delivery status and re-trigger failed deliveries

### US-3: Sync Customer Data to CRM (System Integration)
**As a** System Integration  
**I want to** receive submission events and extract customer data  
**So that** customer profiles in FormCraft can be kept in sync with the organization's CRM

**Acceptance Criteria:**
- on_form_submitted webhook includes all form field data (flattened JSON)
- Webhook payload includes operator information and submission timestamp
- CRM connector supports field mapping (FormCraft field → CRM field)
- Can upsert (create or update) customer records based on matching key

### US-4: Trigger Backend Workflows (System Integration)
**As a** System Integration  
**I want to** receive form submission events  
**So that** backend workflows can be triggered automatically (approval routing, fund transfers, etc.)

**Acceptance Criteria:**
- on_form_submitted webhook delivers complete submission payload immediately
- Includes all form data, operator context, and submission metadata
- Custom header support for authentication (API key in header, Bearer token, etc.)

### US-5: Manage Multiple Integrations (Org Admin)
**As an** Org Admin  
**I want to** manage multiple pre-built and custom connectors  
**So that** FormCraft integrates with all my organization's systems

**Acceptance Criteria:**
- Integration management dashboard at `/admin/integrations/connectors`
- List all active, pending, and failed integrations
- For each connector: status, event type, target system, last sync time
- Can enable/disable connectors without reconfiguration
- Can delete connector and disable further delivery

---

## Functional Requirements

### FR-1: API Key Management
- Admins can generate organization-scoped API keys
- Each key has: unique `key_id`, secret `key_secret`, scopes, created_at, last_used_at, expires_at (optional)
- Key display: show full secret only on creation (not retrievable later)
- Regenerate key: creates new secret, invalidates old one
- Revoke key: immediately stops accepting requests
- Audit log: track all API key operations

### FR-2: Webhook Infrastructure
- Support events: `form_submitted`, `form_printed`, `template_published`, `batch_completed`
- Admin configures: event type + endpoint URL + HTTP method (POST) + custom headers
- Webhook payload includes: event type, timestamp, resource ID, resource data, org context
- Retry logic: 3 attempts with exponential backoff (1s, 5s, 30s)
- Webhook logs: record attempt timestamp, HTTP status, response body (truncated)
- Test webhook: send sample payload to verify endpoint responds 2xx
- Header filtering: no sensitive data in logs (only safe headers stored)

### FR-3: Pre-Built Connectors (Phase 1)
Support initial connectors with field mapping and credential management:
- **Document Management** (DMS/ECM): Archive PDF to document system (Sharepoint, OneDrive, file server)
- **Email**: Send submission PDF or summary email to stakeholders
- **CRM**: Upsert customer records based on form data with field mapping
- **Banking System**: Send transaction data (amount, beneficiary, account) for processing
- Each connector: status UI, field mapper, test connection, error handling

### FR-4: Custom Webhook Support (scope-limited)
- Organizations can configure custom HTTPS endpoints (HTTPS only — HTTP rejected at validation)
- Admin provides: endpoint URL, custom headers (for auth, stored encrypted), HTTP method (POST only in Phase 1)
- Payload schema is **fixed** per event type (no custom templating in Phase 1 — see Constitution Scope)
- Endpoint is accepted only after one successful test delivery (`POST /admin/integrations/webhooks/:id/test` returns 2xx)

### FR-5: Field Mapping (CRM/Banking connectors only)
- For CRM and Banking connectors, admins map FormCraft element IDs → external field keys via `connector_field_mappings` table
- Mapping is a simple 1:1 key mapping; no expressions, no transformations in Phase 1
- DMS and Email connectors do not require field mapping (they consume the canonical event payload)

### FR-6: Security & Compliance
- API keys: scoped to organization (never cross-org); stored as bcrypt/HMAC-SHA256 hash; plaintext returned only on `POST` and `regenerate` responses
- Webhooks: HTTPS required (HTTP rejected at creation time with 400)
- Signature verification: webhook payloads signed with `webhook_secret` (HMAC-SHA256) sent in `X-FormCraft-Signature` header
- Header values for `custom_headers` are encrypted at rest using the organization's KMS data-encryption key (DEK) and decrypted only inside the dispatcher worker. Audit logs and the admin UI display header names only — values are masked as `●●●●●` and not retrievable after creation.
- Connector credentials (DMS tokens, CRM OAuth refresh tokens, banking API keys) follow the same encryption rule as `custom_headers`.
- Rate limiting (enforced via Supabase row-level throttling): API keys ≤ 1000 req/min/org; webhook test endpoint ≤ 10 req/min/webhook; outbound dispatcher ≤ 100 req/min/endpoint.
- Audit trail: webhook deliveries log status code + first 1KB of response body + timestamps; payload bodies are NOT logged (only the event_type + resource_id are recorded).
- Banking connector: any outbound payload containing PAN/account numbers must mask all but last-4 digits before logging; no full PAN is ever persisted in `webhook_deliveries.response_body`.

### FR-7: Monitoring, Alerting & Debugging
- Webhook delivery logs: searchable, filterable by status, event type, date range; retained 30 days then archived
- Failed delivery alerts: when an endpoint records ≥ 2 consecutive failures, send an in-app notification + email to the webhook's `created_by` user (uses the existing F-NOTIFY infrastructure — no new alerting subsystem)
- Retry dashboard: manually trigger retry for failed webhooks via `POST .../deliveries/:id/retry`
- Delivery metrics: rolling 24h success rate, P50/P95 latency, payload size — exposed via `GET /admin/integrations/webhooks/:id/metrics`
- Sample payloads: admin can view the last 10 successful and last 10 failed payloads per webhook (sensitive fields redacted)

### FR-8: Async Dispatch Queue (Supabase-native)
- Webhook events are persisted as rows in `webhook_deliveries` with `status='pending'` and `next_retry_at=NOW()`
- A FastAPI background worker (single instance per environment in Phase 1) polls `SELECT ... FROM webhook_deliveries WHERE status='pending' AND next_retry_at <= NOW() FOR UPDATE SKIP LOCKED LIMIT 100` every 2 seconds
- No external message queue is introduced (consistent with Constitution technology constraints — Supabase only). If throughput exceeds 1000 deliveries/min the team must amend this spec before adding a real MQ.
- Workers update row status to `sent` / `success` / `failed` and set `next_retry_at` for retries (1s, 5s, 30s backoff). After attempt #3, status becomes `failed` permanently.

---

## Data Model

### api_keys Table
```sql
CREATE TABLE api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  key_hash VARCHAR(64) NOT NULL UNIQUE,
  -- Store hash of key_secret (not the secret itself)
  scopes TEXT[] DEFAULT '{"read"}',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by UUID NOT NULL REFERENCES profiles(id),
  last_used_at TIMESTAMP,
  expires_at TIMESTAMP,
  is_active BOOLEAN DEFAULT true,
  deleted_at TIMESTAMP,
  
  CHECK (array_length(scopes, 1) > 0)
);

CREATE INDEX idx_api_keys_org_id ON api_keys(org_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_api_keys_created_by ON api_keys(created_by);
```

### webhooks Table
```sql
CREATE TABLE webhooks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  event_type VARCHAR(50) NOT NULL, -- form_submitted, form_printed, template_published, batch_completed
  endpoint_url VARCHAR(2048) NOT NULL,
  custom_headers JSONB DEFAULT '{}',
  -- Stored as {"Authorization": "Bearer xxx", "X-Custom": "value"} (keys only, no secrets)
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by UUID NOT NULL REFERENCES profiles(id),
  updated_by UUID NOT NULL REFERENCES profiles(id),
  last_triggered_at TIMESTAMP,
  deleted_at TIMESTAMP,
  
  UNIQUE(org_id, endpoint_url, event_type),
  CHECK (event_type IN ('form_submitted', 'form_printed', 'template_published', 'batch_completed')),
  CHECK (char_length(endpoint_url) > 0)
);

CREATE INDEX idx_webhooks_org_id_active ON webhooks(org_id, is_active) WHERE deleted_at IS NULL;
CREATE INDEX idx_webhooks_event_type ON webhooks(event_type) WHERE is_active = true;
```

### webhook_deliveries Table
```sql
CREATE TABLE webhook_deliveries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  webhook_id UUID NOT NULL REFERENCES webhooks(id) ON DELETE CASCADE,
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  event_type VARCHAR(50) NOT NULL,
  resource_id UUID NOT NULL,
  attempt_number SMALLINT DEFAULT 1,
  
  -- Request details
  url VARCHAR(2048) NOT NULL,
  method VARCHAR(10) DEFAULT 'POST',
  
  -- Response details
  status_code SMALLINT,
  response_body TEXT,
  error_message TEXT,
  
  -- Timing
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  sent_at TIMESTAMP,
  next_retry_at TIMESTAMP,
  completed_at TIMESTAMP,
  
  -- Status tracking
  status VARCHAR(20) DEFAULT 'pending', -- pending, sent, failed, success
  
  CHECK (status IN ('pending', 'sent', 'failed', 'success'))
);

CREATE INDEX idx_webhook_deliveries_webhook_id ON webhook_deliveries(webhook_id);
CREATE INDEX idx_webhook_deliveries_org_id ON webhook_deliveries(org_id);
CREATE INDEX idx_webhook_deliveries_status_next_retry ON webhook_deliveries(status, next_retry_at) 
  WHERE status = 'pending';
CREATE INDEX idx_webhook_deliveries_created_at ON webhook_deliveries(created_at);
```

### connectors Table (Pre-built Connectors)
```sql
CREATE TABLE connectors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  connector_type VARCHAR(50) NOT NULL, -- dms, email, crm, banking, custom
  name VARCHAR(255) NOT NULL,
  
  -- Connector configuration (connector-specific settings)
  config JSONB NOT NULL,
  -- Example DMS: {"type": "sharepoint", "site_url": "...", "folder_path": "/Forms"}
  -- Example Email: {"to_recipients": ["admin@..."], "include_pdf": true}
  -- Example CRM: {"system": "salesforce", "field_mappings": {...}}
  
  -- Webhook binding
  webhook_id UUID REFERENCES webhooks(id) ON DELETE SET NULL,
  
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by UUID NOT NULL REFERENCES profiles(id),
  updated_by UUID NOT NULL REFERENCES profiles(id),
  last_sync_at TIMESTAMP,
  error_message TEXT,
  deleted_at TIMESTAMP
);

CREATE INDEX idx_connectors_org_id ON connectors(org_id) WHERE is_active = true;
CREATE INDEX idx_connectors_type ON connectors(connector_type);
```

### connector_field_mappings Table (for CRM, Banking connectors)
```sql
CREATE TABLE connector_field_mappings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  connector_id UUID NOT NULL REFERENCES connectors(id) ON DELETE CASCADE,
  formcraft_field_id UUID NOT NULL REFERENCES elements(id) ON DELETE CASCADE,
  external_field_key VARCHAR(255) NOT NULL,
  -- formcraft_field_id: the element being mapped
  -- external_field_key: the target field in external system (e.g., "CRM.customer_name")
  
  transformation VARCHAR(255), -- Optional expression or lookup
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_connector_field_mappings_connector_id ON connector_field_mappings(connector_id);
```

---

## API Endpoints

### API Key Management
- `POST /admin/integrations/api-keys` — Create new API key
- `GET /admin/integrations/api-keys` — List org's API keys (with usage stats)
- `GET /admin/integrations/api-keys/:id` — Get API key details
- `PUT /admin/integrations/api-keys/:id` — Update API key (name, scopes, expiry)
- `POST /admin/integrations/api-keys/:id/regenerate` — Create new secret for key
- `DELETE /admin/integrations/api-keys/:id` — Revoke API key

### Webhook Management
- `POST /admin/integrations/webhooks` — Create webhook endpoint
- `GET /admin/integrations/webhooks` — List org's webhooks
- `GET /admin/integrations/webhooks/:id` — Get webhook details
- `PUT /admin/integrations/webhooks/:id` — Update webhook
- `POST /admin/integrations/webhooks/:id/test` — Send test payload to endpoint
- `DELETE /admin/integrations/webhooks/:id` — Delete webhook

### Webhook Delivery Log
- `GET /admin/integrations/webhooks/:id/deliveries` — List delivery attempts (paginated)
- `GET /admin/integrations/webhooks/:id/deliveries/:deliveryId` — Get delivery details
- `POST /admin/integrations/webhooks/:id/deliveries/:deliveryId/retry` — Manually retry failed delivery
- `DELETE /admin/integrations/webhooks/:id/deliveries/:deliveryId` — Clear log entry

### Connectors (Pre-built)
- `POST /admin/integrations/connectors` — Create connector configuration
- `GET /admin/integrations/connectors` — List org's connectors
- `GET /admin/integrations/connectors/:id` — Get connector details
- `PUT /admin/integrations/connectors/:id` — Update connector config
- `POST /admin/integrations/connectors/:id/test` — Test connector connection
- `DELETE /admin/integrations/connectors/:id` — Delete connector
- `POST /admin/integrations/connectors/:id/field-mappings` — Add field mapping (CRM, Banking)
- `GET /admin/integrations/connectors/:id/field-mappings` — List field mappings
- `DELETE /admin/integrations/connectors/:id/field-mappings/:mappingId` — Remove mapping

### Internal Dispatcher (not exposed publicly)
- The webhook dispatcher is a backend worker; there is no public `/webhooks/...` ingress endpoint in Phase 1.
- All event triggers originate inside FastAPI (form submission, print, publish, batch handlers) and enqueue rows in `webhook_deliveries`.

### Webhook Metrics
- `GET /admin/integrations/webhooks/:id/metrics` — Returns 24h rolling success rate, P50/P95 latency, payload count (see FR-7)

---

## Acceptance Criteria

1. **API Key Security**
   - API keys are hashed in database (not reversible)
   - Key secret shown only once on creation
   - Key can be revoked immediately, stopping all authenticated requests
   - All API key operations logged to audit trail

2. **Webhook Delivery**
   - Webhooks reliably deliver with 3 retry attempts
   - Exponential backoff: 1s, 5s, 30s between retries
   - Payload includes org context (org_id, org_name) and event data
   - Failed delivery doesn't block form operations (async, non-blocking)

3. **Data Security**
   - Webhook payloads signed with HMAC-SHA256, sent in `X-FormCraft-Signature` header
   - HTTPS required (HTTP rejected at creation with 400)
   - Custom header VALUES are stored encrypted at rest (KMS DEK per org); only header NAMES are displayed in admin UI; values are masked as `●●●●●` after creation and never retrievable in cleartext
   - Audit logs and `webhook_deliveries.response_body` never contain request payload bodies; banking responses mask PAN/account numbers to last-4 digits

4. **Admin Experience**
   - Webhook configuration in < 5 minutes
   - Test webhook before activation (admin sends test, sees response)
   - Clear error messages when webhook fails
   - Can retry failed deliveries from UI
   - Can disable webhook without losing configuration

5. **Integration Reliability**
   - Webhook delivery logs retained for 30 days
   - Can search/filter logs by status, event type, date range
   - Metrics dashboard shows webhook success rate
   - Failed delivery alerts sent to admin after 2 consecutive failures

6. **Pre-built Connectors**
   - DMS connector: validates credentials, tests folder write access
   - Email connector: supports multiple recipients, HTML templates
   - CRM connector: field mapping UI, test sync
   - All connectors show status (active, error, pending) on dashboard

---

## Implementation Phases

### Phase 1: API Keys & Webhook Infrastructure (Backend)
- Create api_keys, webhooks, webhook_deliveries tables
- RLS policies for org-scoped access
- API endpoints for CRUD operations
- Webhook dispatcher (background job that sends events)
- Retry logic with exponential backoff
- Webhook signature verification (HMAC-SHA256)
- Audit logging for all operations

### Phase 2: Webhook Admin UI (Frontend)
- Build `/admin/integrations/api-keys` page
- Build `/admin/integrations/webhooks` page
- Test webhook UI (send sample event)
- Webhook delivery log viewer (search, filter, retry)
- Copy-to-clipboard for API key and webhook URL

### Phase 3: Event Triggering (Integration with Form Desk)
- Trigger webhook on form submission (form_submitted event)
- Trigger webhook on form print (form_printed event)
- Include PDF URL in event payload
- Trigger webhook on template publish (template_published event)
- Trigger webhook on batch completion (batch_completed event)
- Ensure webhooks don't block user operations

### Phase 4: Pre-Built Connectors (Backend + UI)
- DMS Connector: SharePoint, OneDrive, file server integration
- Email Connector: send PDF to recipients
- CRM Connector: field mapper, upsert customer records
- Banking Connector: send transaction data to core banking
- Connector configuration UI with field mappings
- Connector test/validation endpoints

### Phase 5: Advanced Features & Refinement
- Custom webhook templates (JSON/XML)
- Connector marketplace / extensibility
- Performance optimization (webhook batching)
- Monitoring dashboard (success rates, latency)
- Documentation and examples

---

## Dependencies

- Organizations table (existing) — org_id foreign key
- Elements table (existing) — for field mappings
- Profiles table (existing) — for user audit
- Audit logs table (existing) — audit logging
- Form submission data flow (existing) — to trigger webhooks
- PDF generation (existing) — to include PDF URL in webhook

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Webhook delivery failures block form operations | High | Webhooks are async, separate queue; form submission completes immediately |
| Endpoint receiving webhook is slow/unavailable | Medium | Exponential backoff prevents spam; retry attempts stop after 3 fails |
| Sensitive data leaked in webhook payload | Critical | Admin controls payload content; signature prevents tampering; HTTPS required |
| API key compromise | Critical | Keys are hashed; can be revoked immediately; rate limiting per key |
| Webhook signature verification bypassed | High | HMAC-SHA256; keys stored securely; verification required on all events |
| Cross-org data leakage via webhooks | Critical | RLS policies on webhooks; org_id isolation in queries; audit logging |

---

## Testing Strategy

- **Unit**: API key generation/revocation, webhook dispatch logic, retry backoff
- **Integration**: Create webhook → trigger event → verify delivery → check logs
- **E2E**: Admin creates webhook → submit form → webhook receives event → data syncs to external system
- **Security**: Cross-org access prevention, signature verification, header redaction
- **Performance**: Webhook delivery under 5s for 100 concurrent deliveries

---

## Success Metrics

- Webhook delivery success rate > 99% (for healthy endpoints)
- API key generation < 5 seconds
- Webhook configuration < 10 minutes (including test)
- Delivery log search < 500ms
- No form submission delays due to webhook processing
- 0 cross-org data leakage incidents
- 100% audit trail completeness for integration operations

---

## Next Steps (Post-Phase 5)

1. **Monitor production** webhook delivery rates and latencies
2. **Gather user feedback** on pre-built connector coverage
3. **Plan Phase 2 enhancements**:
   - Connector marketplace for third-party vendors
   - Webhook batching for high-volume submissions
   - Intelligent retry (circuit breaker pattern)
   - Multi-destination routing (same event to multiple endpoints)
