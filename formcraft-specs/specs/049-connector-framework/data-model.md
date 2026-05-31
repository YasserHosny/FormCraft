# Feature 049: Data Model Design

## Overview
This document details the database schema for webhook infrastructure, API key management, and connector configuration.

---

## Database Schema

### api_keys Table
```sql
CREATE TABLE api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  key_hash VARCHAR(64) NOT NULL UNIQUE,  -- Hash of key_secret (HMAC-SHA256)
  scopes TEXT[] DEFAULT '{"read"}',      -- Granted scopes: read, write, admin
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by UUID NOT NULL REFERENCES profiles(id),
  last_used_at TIMESTAMP,                -- Track last API call using this key
  expires_at TIMESTAMP,                  -- Optional expiration
  is_active BOOLEAN DEFAULT true,        -- Can revoke without deleting
  deleted_at TIMESTAMP,                  -- Soft delete (revocation)
  
  UNIQUE(org_id, name),
  CHECK (array_length(scopes, 1) > 0),
  CHECK (char_length(name) > 0 AND char_length(name) <= 255)
);

-- Indexes for performance
CREATE INDEX idx_api_keys_org_id ON api_keys(org_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_api_keys_created_by ON api_keys(created_by);
CREATE INDEX idx_api_keys_expires_at ON api_keys(expires_at) WHERE is_active = true;
```

### webhooks Table
```sql
CREATE TABLE webhooks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  event_type VARCHAR(50) NOT NULL,       -- form_submitted, form_printed, template_published, batch_completed
  endpoint_url VARCHAR(2048) NOT NULL,   -- HTTPS URL for webhook delivery
  custom_headers JSONB DEFAULT '{}',     -- {"Authorization": "Bearer xxx"} (header values, not secrets)
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by UUID NOT NULL REFERENCES profiles(id),
  updated_by UUID NOT NULL REFERENCES profiles(id),
  last_triggered_at TIMESTAMP,           -- Last time event was queued for delivery
  deleted_at TIMESTAMP,                  -- Soft delete
  
  UNIQUE(org_id, endpoint_url, event_type),
  CHECK (event_type IN ('form_submitted', 'form_printed', 'template_published', 'batch_completed')),
  CHECK (char_length(endpoint_url) > 0 AND endpoint_url LIKE 'https://%')
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
  resource_id UUID NOT NULL,             -- ID of resource that triggered event (submission, template, etc.)
  
  -- Request details
  url VARCHAR(2048) NOT NULL,
  method VARCHAR(10) DEFAULT 'POST',
  
  -- Attempt tracking
  attempt_number SMALLINT DEFAULT 1,     -- 1, 2, or 3
  
  -- Response details
  status_code SMALLINT,
  response_body TEXT,                    -- Truncated response (first 1000 chars)
  error_message TEXT,                    -- Network error, timeout, etc.
  
  -- Timing
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  sent_at TIMESTAMP,                     -- When attempt was made
  next_retry_at TIMESTAMP,               -- When next retry will be attempted
  completed_at TIMESTAMP,                -- When delivery succeeded or failed permanently
  
  -- Status tracking
  status VARCHAR(20) DEFAULT 'pending',  -- pending, sent, failed, success
  
  CHECK (status IN ('pending', 'sent', 'failed', 'success')),
  CHECK (attempt_number BETWEEN 1 AND 3)
);

CREATE INDEX idx_webhook_deliveries_webhook_id ON webhook_deliveries(webhook_id);
CREATE INDEX idx_webhook_deliveries_org_id ON webhook_deliveries(org_id);
CREATE INDEX idx_webhook_deliveries_status_retry ON webhook_deliveries(status, next_retry_at) 
  WHERE status = 'pending' AND next_retry_at <= CURRENT_TIMESTAMP;
CREATE INDEX idx_webhook_deliveries_created_at ON webhook_deliveries(created_at);
```

### connectors Table
```sql
CREATE TABLE connectors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  connector_type VARCHAR(50) NOT NULL,   -- dms, email, crm, banking, custom
  name VARCHAR(255) NOT NULL,
  
  -- Connector configuration (encrypted at rest for sensitive data)
  config JSONB NOT NULL,
  -- Example DMS: {"type": "sharepoint", "site_url": "...", "folder_path": "/Forms"}
  -- Example Email: {"to_recipients": ["admin@..."], "include_pdf": true}
  -- Example CRM: {"system": "salesforce", "instance_url": "..."}
  
  -- Webhook binding
  webhook_id UUID REFERENCES webhooks(id) ON DELETE SET NULL,
  
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by UUID NOT NULL REFERENCES profiles(id),
  updated_by UUID NOT NULL REFERENCES profiles(id),
  last_sync_at TIMESTAMP,                -- Last successful execution
  error_message TEXT,                    -- Most recent error (for status UI)
  deleted_at TIMESTAMP,
  
  UNIQUE(org_id, connector_type, name)
);

CREATE INDEX idx_connectors_org_id_active ON connectors(org_id, is_active) WHERE deleted_at IS NULL;
CREATE INDEX idx_connectors_type ON connectors(connector_type) WHERE is_active = true;
CREATE INDEX idx_connectors_webhook_id ON connectors(webhook_id) WHERE webhook_id IS NOT NULL;
```

### connector_field_mappings Table (for CRM, Banking connectors)
```sql
CREATE TABLE connector_field_mappings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  connector_id UUID NOT NULL REFERENCES connectors(id) ON DELETE CASCADE,
  formcraft_field_id UUID NOT NULL REFERENCES elements(id) ON DELETE CASCADE,
  external_field_key VARCHAR(255) NOT NULL,  -- Target field in external system
  transformation VARCHAR(255),           -- Optional expression or lookup
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE(connector_id, formcraft_field_id)
);

CREATE INDEX idx_connector_field_mappings_connector_id ON connector_field_mappings(connector_id);
CREATE INDEX idx_connector_field_mappings_field_id ON connector_field_mappings(formcraft_field_id);
```

---

## Row-Level Security (RLS) Policies

### Enable RLS on Tables
```sql
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhooks ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhook_deliveries ENABLE ROW LEVEL SECURITY;
ALTER TABLE connectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE connector_field_mappings ENABLE ROW LEVEL SECURITY;
```

### API Keys RLS
```sql
-- Users can read api_keys only for their org
CREATE POLICY api_keys_read ON api_keys FOR SELECT 
  USING (org_id = auth.jwt_claim('org_id')::uuid);

-- Users can create keys for their org
CREATE POLICY api_keys_insert ON api_keys FOR INSERT 
  WITH CHECK (org_id = auth.jwt_claim('org_id')::uuid);

-- Users can update keys for their org
CREATE POLICY api_keys_update ON api_keys FOR UPDATE 
  USING (org_id = auth.jwt_claim('org_id')::uuid)
  WITH CHECK (org_id = auth.jwt_claim('org_id')::uuid);

-- Users can delete keys for their org
CREATE POLICY api_keys_delete ON api_keys FOR DELETE 
  USING (org_id = auth.jwt_claim('org_id')::uuid);
```

### Webhooks RLS
```sql
CREATE POLICY webhooks_read ON webhooks FOR SELECT 
  USING (org_id = auth.jwt_claim('org_id')::uuid);

CREATE POLICY webhooks_write ON webhooks FOR INSERT 
  WITH CHECK (org_id = auth.jwt_claim('org_id')::uuid);

CREATE POLICY webhooks_update ON webhooks FOR UPDATE 
  USING (org_id = auth.jwt_claim('org_id')::uuid)
  WITH CHECK (org_id = auth.jwt_claim('org_id')::uuid);

CREATE POLICY webhooks_delete ON webhooks FOR DELETE 
  USING (org_id = auth.jwt_claim('org_id')::uuid);
```

### Webhook Deliveries RLS
```sql
CREATE POLICY webhook_deliveries_read ON webhook_deliveries FOR SELECT 
  USING (org_id = auth.jwt_claim('org_id')::uuid);

-- System-only insert (via webhook dispatcher)
CREATE POLICY webhook_deliveries_insert ON webhook_deliveries FOR INSERT 
  WITH CHECK (org_id = auth.jwt_claim('org_id')::uuid);
```

### Connectors RLS
```sql
CREATE POLICY connectors_all ON connectors FOR ALL 
  USING (org_id = auth.jwt_claim('org_id')::uuid)
  WITH CHECK (org_id = auth.jwt_claim('org_id')::uuid);
```

---

## Migration Strategy

### Migration 1: Create Webhook Infrastructure Tables
```sql
-- File: migrations/001_create_webhook_infrastructure.sql

-- Create all webhook-related tables
CREATE TABLE api_keys ( ... );
CREATE TABLE webhooks ( ... );
CREATE TABLE webhook_deliveries ( ... );
CREATE TABLE connectors ( ... );
CREATE TABLE connector_field_mappings ( ... );

-- Create all indexes
CREATE INDEX ... ;

-- Enable RLS and create policies
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
-- ... (all RLS policies)
```

### Migration 2: Add webhook_secret Column (for Signature Verification)
```sql
-- File: migrations/002_add_webhook_secret.sql

ALTER TABLE webhooks ADD COLUMN webhook_secret VARCHAR(128) NOT NULL DEFAULT gen_random_uuid()::text;
```

### Rollback Strategy
```sql
-- Rollback Migration 2
ALTER TABLE webhooks DROP COLUMN webhook_secret;

-- Rollback Migration 1
DROP TABLE connector_field_mappings;
DROP TABLE connectors;
DROP TABLE webhook_deliveries;
DROP TABLE webhooks;
DROP TABLE api_keys;
```

---

## Example Data

```sql
-- Create API key
INSERT INTO api_keys (org_id, name, key_hash, scopes, created_by)
VALUES (
  'org-123',
  'Integration API Key',
  'sha256_hash_of_secret',
  ARRAY['read', 'write'],
  'user-456'
);

-- Create webhook
INSERT INTO webhooks (org_id, name, event_type, endpoint_url, created_by, updated_by)
VALUES (
  'org-123',
  'DMS Archive Webhook',
  'form_printed',
  'https://dms.company.com/api/webhook/formcraft',
  'user-456',
  'user-456'
);

-- Create DMS connector
INSERT INTO connectors (org_id, connector_type, name, config, webhook_id, created_by, updated_by)
VALUES (
  'org-123',
  'dms',
  'SharePoint Archive',
  '{
    "type": "sharepoint",
    "site_url": "https://company.sharepoint.com/sites/forms",
    "folder_path": "/Shared Documents/FormCraft/Archived"
  }'::jsonb,
  'webhook-id-above',
  'user-456',
  'user-456'
);

-- Create field mapping (CRM connector)
INSERT INTO connector_field_mappings (connector_id, formcraft_field_id, external_field_key)
VALUES (
  'connector-id',
  'elem-customer-name',
  'salesforce.Account.Name'
);
```

---

## Performance Considerations

### Query Optimization

1. **List webhooks for org** (with pagination):
   ```sql
   SELECT * FROM webhooks 
   WHERE org_id = $1 AND deleted_at IS NULL 
   ORDER BY created_at DESC 
   LIMIT 20 OFFSET $2;
   ```
   **Index used**: `idx_webhooks_org_id_active`

2. **Find pending deliveries for retry**:
   ```sql
   SELECT * FROM webhook_deliveries 
   WHERE status = 'pending' AND next_retry_at <= CURRENT_TIMESTAMP
   ORDER BY next_retry_at ASC
   LIMIT 100;
   ```
   **Index used**: `idx_webhook_deliveries_status_retry`

3. **Get delivery history for webhook**:
   ```sql
   SELECT * FROM webhook_deliveries 
   WHERE webhook_id = $1 
   ORDER BY created_at DESC 
   LIMIT 50;
   ```
   **Index used**: `idx_webhook_deliveries_webhook_id`

### Caching Strategy
- **Webhook configs**: Cache in memory per org, invalidate on CRUD
- **API key validation**: Cache in memory, invalidate on regenerate/revoke
- **Connector configs**: Cache in memory, invalidate on update

---

## Audit Logging

### Events to Log
```
API_KEY_CREATED:
  - API key ID, name, scopes
  
API_KEY_REGENERATED:
  - API key ID, old_secret_hash, new_secret_hash
  
API_KEY_REVOKED:
  - API key ID, reason
  
WEBHOOK_CREATED:
  - Webhook ID, endpoint, event_type
  
WEBHOOK_UPDATED:
  - Webhook ID, changed_fields (before/after)
  
WEBHOOK_DELETED:
  - Webhook ID
  
WEBHOOK_DELIVERY_SUCCESS:
  - Webhook ID, resource ID, HTTP status, response time
  
WEBHOOK_DELIVERY_FAILED:
  - Webhook ID, resource ID, error message, attempt number
  
CONNECTOR_CREATED:
  - Connector ID, type, name
  
CONNECTOR_UPDATED:
  - Connector ID, changed_fields
  
CONNECTOR_DELETED:
  - Connector ID
```

All audit logs should include: org_id, user_id, timestamp, and should never contain secrets or sensitive data.

---

## Security Considerations

### Credential Storage
- API key secrets: hashed with HMAC-SHA256 (cannot be recovered)
- Connector credentials (passwords, tokens): encrypted at rest using organization-specific encryption key
- Never log credentials (log only success/failure)

### Data Isolation
- RLS policies strictly enforce org_id matching on all queries
- Webhook payloads always include org_id (verify on receipt)
- Cross-org queries impossible via database constraints

### Signature Verification
- Webhook payloads signed with HMAC-SHA256
- Signature includes: payload + webhook_secret
- External systems verify signature before processing payload
- Prevents tampering and ensures authenticity

---

## Monitoring & Observability

### Key Metrics
- **API keys**: Total per org, active vs revoked, expiration date distribution
- **Webhooks**: Total per org, by event type, success rate, latency
- **Deliveries**: Pending count, success/failure ratio, retry count distribution
- **Connectors**: Active by type, error rate, last sync time

### Alerts
- Webhook delivery success rate < 95%
- API key regenerated unexpectedly
- Cross-org access attempts
- Connector credentials invalid
- Delivery queue depth > 1000

---

## Testing Strategy

### Unit Tests
- API key hashing and verification
- HMAC-SHA256 signature generation
- RLS policy isolation
- Webhook retry backoff calculation

### Integration Tests
- Create API key → use to authenticate request → verify scopes enforced
- Create webhook → trigger event → verify delivery attempt
- Update webhook → verify new config is used
- Connector field mapping → verify transform applied

### E2E Tests
- Full workflow: form submission → webhook delivery → external system updated
- Cross-org isolation: Org A cannot access Org B's webhooks
- Security: signature verification prevents tampering
