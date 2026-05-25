# Feature Specification: Data Export & Integration

**Feature Branch**: `032-data-export-integration`  
**Created**: 2026-05-25  
**Status**: Draft  
**Vision Reference**: AC-07

## User Scenarios & Testing

### User Story 1 - Submission Data Export (Priority: P1)

As an org admin, I need to export submission data filtered by template, date range, department, branch, operator, and status in CSV, Excel, or JSON format so I can integrate with external systems and generate custom reports.

**Why this priority**: Most requested enterprise feature — organizations need data out of FormCraft for compliance, reporting, and integration with existing business systems.

**Independent Test**: Navigate to `/admin/export`, select filters, choose format, download file with correct data.

**Acceptance Scenarios**:

1. **Given** admin navigates to `/admin/export`, **When** they select a template and date range, **Then** a preview shows matching submission count and estimated file size.
2. **Given** admin selects CSV format with "flattened" scope, **When** export is generated, **Then** each form field becomes a column header with field values as rows.
3. **Given** admin selects JSON format with "nested" scope, **When** export is generated, **Then** each submission is a JSON object preserving the original field_data structure.
4. **Given** admin configures a recurring export (weekly CSV to email), **When** the schedule triggers, **Then** the export is generated and emailed to the configured recipients.

---

### User Story 2 - Template Export & Import Packages (Priority: P2)

As a designer or admin, I need to export a template as a `.formcraft` package and import it into another organization or environment so I can promote templates between dev/staging/production or share between departments.

**Why this priority**: Enables template portability — critical for multi-environment deployments and cross-department sharing.

**Independent Test**: Export a template as .formcraft package, import into a different org context, verify all elements and validators preserved.

**Acceptance Scenarios**:

1. **Given** a published template exists, **When** admin clicks "Export Package", **Then** a .formcraft file is downloaded containing template definition, pages, elements, validators, and reference data bindings.
2. **Given** admin has a .formcraft file, **When** they click "Import Template" and upload the file, **Then** a new draft template is created with all elements, validators, and bindings intact.
3. **Given** the imported template references a reference data list that doesn't exist in the target org, **When** import completes, **Then** a warning shows which bindings need remapping.

---

### User Story 3 - Webhook Configuration (Priority: P3)

As an org admin, I need to configure webhook endpoints that fire on key events (form submitted, form printed, template published, batch completed) so external systems can react to FormCraft events in real time.

**Why this priority**: Enables event-driven integration without polling — essential for enterprise workflows.

**Independent Test**: Configure a webhook URL for "on_form_submitted", submit a form, verify webhook fires with correct payload.

**Acceptance Scenarios**:

1. **Given** admin navigates to `/admin/integrations/webhooks`, **When** they click "Add Webhook", **Then** a form shows: event type dropdown, URL, optional secret (for HMAC signature), and test button.
2. **Given** a webhook is configured for "on_form_submitted", **When** an operator submits a form, **Then** a POST request is sent to the webhook URL with submission data within 30 seconds.
3. **Given** a webhook delivery fails, **When** the system retries (3 attempts with exponential backoff), **Then** each attempt is logged with response code and the admin can view delivery history.
4. **Given** admin clicks "Test Webhook", **When** a test payload is sent, **Then** the response status and body are shown inline.

---

### User Story 4 - API Key Management (Priority: P4)

As an org admin, I need to generate and manage API keys scoped to my organization so external systems can programmatically access FormCraft data via authenticated API calls.

**Why this priority**: Foundation for all programmatic integrations — required before external systems can consume data.

**Independent Test**: Generate an API key, use it to call the submissions API, verify scoped access.

**Acceptance Scenarios**:

1. **Given** admin navigates to `/admin/integrations/api-keys`, **When** they click "Generate Key", **Then** a new key is created with a name, scope selection, and the key is shown once (copy to clipboard).
2. **Given** an API key exists, **When** an external system uses it in an Authorization header, **Then** API calls are scoped to that organization's data only.
3. **Given** admin wants to revoke a key, **When** they click "Revoke" and confirm, **Then** the key is immediately invalidated and all subsequent API calls with it return 401.

---

### Edge Cases

- What happens when a webhook endpoint is unreachable for more than 24 hours?
- How does template import handle version conflicts with existing templates?
- What happens when a recurring export has no matching data for the period?
- How does the system handle API key rotation without downtime?

## Requirements

### Functional Requirements

- **FR-001**: System MUST support submission data export in CSV, Excel (.xlsx), and JSON formats.
- **FR-002**: Exports MUST be filterable by template, date range, department, branch, operator, and status.
- **FR-003**: System MUST support both flattened (one column per field) and nested (original JSON structure) export scopes.
- **FR-004**: System MUST support recurring scheduled exports (daily/weekly) via email or SFTP.
- **FR-005**: System MUST support template export as .formcraft packages containing all template components.
- **FR-006**: System MUST support template import from .formcraft packages with binding conflict detection.
- **FR-007**: System MUST support webhook configuration for key events with retry logic (3 attempts, exponential backoff).
- **FR-008**: System MUST support API key generation, scoping, and revocation for programmatic access.
- **FR-009**: All webhook deliveries MUST be logged with status, response code, and timestamp.
- **FR-010**: All export and integration actions MUST be recorded in the audit log.

### Key Entities

- **Export Job**: Scheduled or one-time export configuration with filters, format, scope, and delivery method.
- **Webhook Configuration**: Event type, URL, secret, retry settings, delivery log.
- **API Key**: Name, hashed key, organization scope, creation date, last used, revoked status.
- **Template Package**: Serialized bundle of template, pages, elements, validators, and reference data bindings.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Submission exports for up to 10,000 records complete within 30 seconds.
- **SC-002**: Template packages preserve 100% of element properties, validators, and bindings on round-trip export/import.
- **SC-003**: Webhooks fire within 30 seconds of the triggering event.
- **SC-004**: 95% of webhook deliveries succeed on first attempt (to healthy endpoints).
- **SC-005**: API key operations (generate, revoke) take effect immediately with zero propagation delay.
