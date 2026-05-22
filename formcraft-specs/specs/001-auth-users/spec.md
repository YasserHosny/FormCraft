# Feature Specification: Authentication & User Management

**Feature Branch**: `01-auth-users`
**Created**: 2026-02-21
**Status**: Draft
**Input**: FormCraft PRD Phase 1.1 – User Management

## User Scenarios & Testing

### User Story 1 - Admin Creates User Accounts (Priority: P1)

An Admin can create new user accounts with assigned roles. The system supports four roles: Admin, Designer, Operator, Viewer. Each role determines feature access.

**Why this priority**: Without user management, no other feature can enforce access control.

**Independent Test**: Can be fully tested by creating users via API and verifying JWT tokens contain correct role claims.

**Acceptance Scenarios**:

1. **Given** the system has no users, **When** the first Admin account is created via Supabase seed, **Then** the Admin can log in and access the admin panel.
2. **Given** an Admin is logged in, **When** they create a new user with role "Designer", **Then** the user receives credentials and can log in with Designer permissions.
3. **Given** an Admin is logged in, **When** they attempt to create a user with an already-registered email, **Then** the system returns a 409 Conflict error.

---

### User Story 2 - User Logs In with JWT (Priority: P1)

A registered user can log in with email and password. The system returns a JWT access token and a refresh token. The JWT contains the user's role claim.

**Why this priority**: JWT authentication is the foundation for all protected API calls.

**Independent Test**: Can be tested by sending login credentials and verifying the returned JWT structure and claims.

**Acceptance Scenarios**:

1. **Given** a registered user with email "designer@example.com", **When** they submit correct credentials, **Then** they receive a JWT with `role: "designer"` claim and a refresh token.
2. **Given** a registered user, **When** they submit an incorrect password, **Then** the system returns 401 Unauthorized with no token.
3. **Given** a valid JWT that has expired, **When** the user sends a refresh token request, **Then** a new JWT is issued without requiring re-login.

---

### User Story 3 - Role-Based Access Control (Priority: P1)

Each API endpoint enforces role-based access. Admin has full access. Designer can create/edit templates. Operator can fill forms and export PDFs. Viewer can only view published templates.

**Why this priority**: RBAC prevents unauthorized actions across the entire application.

**Independent Test**: Can be tested by calling protected endpoints with different role JWTs and verifying 200 vs 403 responses.

**Acceptance Scenarios**:

1. **Given** a user with role "Viewer", **When** they attempt to create a template, **Then** the API returns 403 Forbidden.
2. **Given** a user with role "Designer", **When** they attempt to create a template, **Then** the API returns 201 Created.
3. **Given** a user with role "Operator", **When** they attempt to delete a template, **Then** the API returns 403 Forbidden.
4. **Given** a user with role "Admin", **When** they attempt to change another user's role, **Then** the API returns 200 OK and the role is updated.

---

### User Story 4 - User Language Preference (Priority: P2)

Each user has a stored language preference (Arabic or English). The preference is loaded on login and determines the UI language and direction.

**Why this priority**: Language preference personalizes the experience but is not blocking for core auth.

**Independent Test**: Can be tested by setting language preference via API and verifying it persists across sessions.

**Acceptance Scenarios**:

1. **Given** a user with language preference "ar", **When** they log in, **Then** the UI loads in Arabic with RTL direction.
2. **Given** a user with no language preference set, **When** they log in, **Then** the system defaults to Arabic ("ar").
3. **Given** a logged-in user, **When** they change language to "en", **Then** the preference is saved and the UI switches to English LTR.

---

### Edge Cases

- What happens when a JWT is tampered with? → Supabase Auth rejects it; API returns 401.
- What happens when an Admin deletes their own account? → System prevents self-deletion if they are the last Admin.
- What happens when Supabase Auth is temporarily unavailable? → API returns 503 Service Unavailable with retry-after header.
- What happens with concurrent role changes? → Last write wins; audit log captures both changes.

## Requirements

### Functional Requirements

- **FR-001**: System MUST authenticate users via email/password through Supabase Auth.
- **FR-002**: System MUST issue JWT access tokens containing user ID and role claim.
- **FR-003**: System MUST support token refresh via Supabase refresh tokens.
- **FR-004**: System MUST enforce four roles: Admin, Designer, Operator, Viewer.
- **FR-005**: System MUST allow Admins to create, update, and deactivate user accounts.
- **FR-006**: System MUST store user language preference ("ar" or "en") in the users profile table.
- **FR-007**: System MUST default new users to Arabic ("ar") language preference.
- **FR-008**: System MUST enforce role-based access on every API endpoint via middleware.
- **FR-009**: System MUST log all authentication events (login, logout, failed attempts) to the audit trail.
- **FR-010**: System MUST prevent deletion of the last Admin account.
- **FR-011**: System MUST enforce Supabase Row-Level Security (RLS) policies aligned with application roles.

### Key Entities

- **User**: id (UUID), email, role (enum: admin/designer/operator/viewer), language (enum: ar/en), is_active (boolean), created_at, updated_at, created_by
- **AuditLog**: id, user_id, action (enum), resource_type, resource_id, metadata (JSONB), timestamp
- **Role Permission Matrix**: Defined as RLS policies + API middleware guards, not as a separate table.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can register and log in within 3 seconds end-to-end.
- **SC-002**: JWT validation adds less than 10ms overhead per API request.
- **SC-003**: 100% of protected endpoints return 403 for unauthorized roles (verified by contract tests).
- **SC-004**: All authentication events are captured in the audit log with zero data loss.
- **SC-005**: Language preference persists correctly across logout/login cycles.
