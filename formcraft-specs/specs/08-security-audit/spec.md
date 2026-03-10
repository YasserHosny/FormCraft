# Feature Specification: Security & Audit Logging

**Feature Branch**: `08-security-audit`
**Created**: 2026-02-21
**Status**: Draft
**Input**: FormCraft PRD Phase 6 – Security & Logging

## User Scenarios & Testing

### User Story 1 - Audit Trail for Template Operations (Priority: P1)

Every template CRUD operation (create, update, delete, publish, version) is logged to an audit trail with the acting user, timestamp, action type, and before/after snapshot of changed fields.

**Why this priority**: Audit trail is a constitutional requirement (Principle VIII) and essential for enterprise compliance.

**Independent Test**: Can be tested by performing template operations and querying the audit log to verify entries.

**Acceptance Scenarios**:

1. **Given** a Designer creates a template, **When** the operation completes, **Then** an audit entry is logged with action "template.create", user_id, template_id, and timestamp.
2. **Given** a Designer updates element positions, **When** the operation completes, **Then** an audit entry captures the changed fields with before/after values.
3. **Given** an Admin publishes a template, **When** the status changes, **Then** an audit entry is logged with action "template.publish" and the status transition (Draft → Published).
4. **Given** an Admin deletes a template, **When** the operation completes, **Then** an audit entry is logged with action "template.delete" and a snapshot of the deleted template.

---

### User Story 2 - AI Suggestion Audit Logging (Priority: P1)

Every AI suggestion request, response, and user decision (accept/dismiss) is logged. This enables tracking AI accuracy and usage patterns.

**Why this priority**: AI behavior must be traceable for compliance and model tuning.

**Independent Test**: Can be tested by triggering AI suggestions and verifying all three events (request, response, decision) are logged.

**Acceptance Scenarios**:

1. **Given** a Designer triggers an AI suggestion, **When** the request is sent, **Then** an audit entry logs the request payload (label, language, country).
2. **Given** the AI returns a suggestion, **When** the response is received, **Then** an audit entry logs the response payload (controlType, confidence, validation).
3. **Given** the Designer accepts a suggestion, **When** they click Accept, **Then** an audit entry logs action "ai.suggestion.accepted" with the element_id and applied changes.
4. **Given** the Designer dismisses a suggestion, **When** they click Dismiss, **Then** an audit entry logs action "ai.suggestion.dismissed" with the element_id.

---

### User Story 3 - Authentication Event Logging (Priority: P1)

All authentication events are logged: successful login, failed login, logout, token refresh, password change, role change.

**Why this priority**: Security events are critical for detecting unauthorized access attempts.

**Independent Test**: Can be tested by performing auth actions and querying the audit log.

**Acceptance Scenarios**:

1. **Given** a user logs in successfully, **When** the JWT is issued, **Then** an audit entry logs action "auth.login.success" with user_id and IP address.
2. **Given** a failed login attempt, **When** the authentication fails, **Then** an audit entry logs action "auth.login.failed" with the attempted email and IP address.
3. **Given** an Admin changes a user's role, **When** the role is updated, **Then** an audit entry logs action "user.role.changed" with the old and new roles.

---

### User Story 4 - Supabase Row-Level Security (Priority: P1)

RLS policies enforce that users can only access data they are authorized to see. Designers see their own templates and published templates. Operators see published templates only. Viewers see published templates only. Admins see all templates.

**Why this priority**: Database-level security prevents data leaks even if API middleware is bypassed.

**Independent Test**: Can be tested by querying Supabase directly with different user tokens and verifying row visibility.

**Acceptance Scenarios**:

1. **Given** a Designer with user_id "A", **When** they query templates, **Then** they see their own drafts and all published templates (not other users' drafts).
2. **Given** a Viewer, **When** they query templates, **Then** they see only published templates.
3. **Given** an Admin, **When** they query templates, **Then** they see all templates including all users' drafts.

---

### User Story 5 - API Security Hardening (Priority: P2)

The API implements rate limiting, input sanitization, CORS configuration, and security headers.

**Why this priority**: Security hardening prevents abuse but is secondary to core audit functionality.

**Independent Test**: Can be tested by sending rapid requests and verifying rate limit responses, and by inspecting response headers.

**Acceptance Scenarios**:

1. **Given** a client sends 100 requests per minute to `/api/ai/suggest-control`, **When** the rate limit (30/min) is exceeded, **Then** subsequent requests return 429 Too Many Requests.
2. **Given** CORS is configured, **When** a request comes from an unauthorized origin, **Then** the browser blocks the request (preflight fails).
3. **Given** any API response, **When** headers are inspected, **Then** they include `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`.

---

### Edge Cases

- What happens when the audit log table is full? → Audit logs are append-only with no hard limit; old entries can be archived via scheduled job (not in Phase 1).
- What happens when audit logging fails? → The primary operation still completes; logging failure is reported to error monitoring but does not block the user action.
- What happens with bulk operations (e.g., importing 20 fields)? → Each field operation gets its own audit entry (not batched).

## Requirements

### Functional Requirements

- **FR-001**: System MUST log all template CRUD operations to the `audit_logs` table.
- **FR-002**: System MUST log all AI suggestion events (request, response, accept, dismiss).
- **FR-003**: System MUST log all authentication events (login success, login failure, logout, token refresh, role change).
- **FR-004**: Each audit entry MUST include: id, user_id, action (string), resource_type, resource_id, metadata (JSONB), ip_address, timestamp.
- **FR-005**: Audit log metadata MUST include before/after snapshots for update operations.
- **FR-006**: Audit log writes MUST be non-blocking (async) — they must not slow down the primary operation.
- **FR-007**: System MUST implement Supabase RLS policies aligned with the four roles.
- **FR-008**: RLS policies: Admins SELECT/INSERT/UPDATE/DELETE all; Designers SELECT own + published, INSERT/UPDATE/DELETE own; Operators SELECT published only; Viewers SELECT published only.
- **FR-009**: System MUST implement rate limiting on the AI suggestion endpoint (30 requests/minute per user).
- **FR-010**: System MUST configure CORS to allow only `formcraft.iron-sys.com` and localhost (development).
- **FR-011**: System MUST set security headers: X-Content-Type-Options, X-Frame-Options, Strict-Transport-Security, Content-Security-Policy.
- **FR-012**: System MUST sanitize all user inputs to prevent SQL injection and XSS (handled by Pydantic validation + Supabase parameterized queries).
- **FR-013**: Audit log failures MUST NOT block primary operations.
- **FR-014**: System MUST provide `GET /api/admin/audit-logs` endpoint for Admins to query audit entries with filters (date range, action type, user_id).

### Key Entities

- **AuditLog**: id (UUID), user_id (FK), action (string), resource_type (string), resource_id (UUID, nullable), metadata (JSONB), ip_address (string), created_at (timestamp).
- **RLS Policy Set**: Supabase migration defining policies per table per role.

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of template operations produce audit entries (verified by integration tests).
- **SC-002**: 100% of AI suggestion events are logged (verified by integration tests).
- **SC-003**: Audit log writes add less than 5ms overhead to the primary operation (async).
- **SC-004**: RLS policies correctly restrict data access for all four roles (verified by direct Supabase queries in tests).
- **SC-005**: Rate limiting correctly throttles excessive AI suggestion requests.
