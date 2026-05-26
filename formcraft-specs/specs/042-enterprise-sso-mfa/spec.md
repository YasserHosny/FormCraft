# Feature Specification: Enterprise SSO and MFA

**Feature Branch**: `042-enterprise-sso-mfa`  
**Created**: 2026-05-26  
**Status**: Draft  
**Input**: User description: "Enterprise SSO and MFA for FormCraft organizations: admins configure SAML or OIDC identity providers, enforce domain-based login, require MFA for sensitive roles, map identity groups to FormCraft roles and departments, and review sign-in/audit events for Arabic-first enterprise deployments."

## Clarifications

### Session 2026-05-26

- Q: Which MFA methods should be supported in the initial release? → A: TOTP (authenticator app) and SMS/Email OTP for MVP; WebAuthn deferred to a later iteration.
- Q: Should SAML/OIDC integration be built in-house or via an external identity service? → A: In-house integration using standard Python libraries (`python-saml`, `authlib`) to preserve full audit trails and Arabic localization control.
- Q: What are the default session timeout and idle timeout values? → A: Default absolute session lifetime is 8 hours; default idle timeout is 30 minutes.
- Q: What is the organization's fallback policy when a user's identity groups no longer match any active mapping? → A: Fallback to no role/department access with an admin notification; the account is not locked.
- Q: How should identity provider secrets and signing certificates be stored? → A: Encrypt at rest using AES-256 and store in the existing PostgreSQL database.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure Enterprise Sign-In (Priority: P1)

An organization IT admin configures a corporate identity provider so employees sign in to FormCraft using the organization's existing identity system.

**Why this priority**: Enterprise banks and government organizations commonly require centralized identity before allowing production rollout.

**Independent Test**: Can be tested by configuring a test identity provider, assigning a verified domain, and confirming users can authenticate through the configured provider.

**Acceptance Scenarios**:

1. **Given** an org admin with identity settings access, **When** they add a valid SAML or OIDC provider and verify the login domain, **Then** the organization can route matching users to corporate sign-in.
2. **Given** provider metadata is invalid or expired, **When** the admin attempts to save it, **Then** the system rejects the configuration with a clear reason and leaves existing sign-in unchanged.

---

### User Story 2 - Enforce MFA and Session Policy (Priority: P2)

An org admin requires MFA and stricter session controls for sensitive users such as admins, reviewers, and platform-support accounts.

**Why this priority**: Privileged access to templates, customer data, exports, and platform settings must be protected beyond a password.

**Independent Test**: Can be tested by enabling MFA for a role, signing in as a user in that role, and verifying the user must complete enrollment or challenge before accessing protected areas.

**Acceptance Scenarios**:

1. **Given** MFA is required for admins, **When** an admin signs in without an enrolled method, **Then** they are guided through enrollment before entering FormCraft.
2. **Given** an active session exceeds the configured timeout or concurrent session limit, **When** the user next acts, **Then** the system requires re-authentication and records the session event.

---

### User Story 3 - Map Identity Groups to FormCraft Access (Priority: P3)

An IT admin maps corporate groups to FormCraft roles, departments, and branches so access is assigned automatically during sign-in.

**Why this priority**: Large organizations cannot manually maintain every user assignment as employees move between branches or departments.

**Independent Test**: Can be tested by signing in a test user with mapped identity groups and confirming their FormCraft profile receives the expected role and org scope.

**Acceptance Scenarios**:

1. **Given** a group mapping exists for branch operators, **When** a new matching employee signs in, **Then** the user is provisioned with the configured role, department, branch, and default language.
2. **Given** a user's identity groups no longer match any active mapping, **When** they sign in, **Then** access is withheld or reduced according to the organization's fallback policy.

### Edge Cases

- Identity provider metadata expires, changes signing certificates, or becomes unreachable during sign-in.
- The same email address exists in more than one organization.
- A platform admin is locked out by an organization IP allowlist or broken SSO configuration.
- A user loses their MFA device and needs recovery without bypassing audit controls.
- SAML/OIDC clock skew causes assertions to appear expired or not yet valid.
- A user's identity groups no longer match any active mapping; fallback policy strips role/department access and notifies admins without locking the account.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow authorized organization admins to configure one or more SAML or OIDC identity providers for their organization.
- **FR-002**: System MUST support verified domain routing so users are directed to the correct organization sign-in experience.
- **FR-003**: System MUST validate provider configuration before activation and preserve the last working configuration if validation fails.
- **FR-004**: System MUST allow admins to require MFA by role, platform-admin flag, department, branch, or all users.
- **FR-005**: Users MUST be able to enroll, challenge, reset, and recover TOTP (authenticator app) and SMS/Email OTP methods through auditable workflows.
- **FR-006**: System MUST allow admins to configure session timeout, idle timeout, concurrent session limits, and trusted IP ranges. Default absolute session lifetime is 8 hours; default idle timeout is 30 minutes.
- **FR-007**: System MUST support just-in-time provisioning rules that map identity groups or claims to FormCraft roles, departments, branches, and language preference. If no mapping matches, fallback to stripped access with an admin alert.
- **FR-008**: System MUST prevent SSO/MFA policy changes from disabling all administrative access for an organization.
- **FR-009**: System MUST record sign-in attempts, MFA events, provider changes, session revocations, and policy changes in the audit trail.
- **FR-010**: System MUST provide localized Arabic and English sign-in, MFA, error, and recovery messages.

### Key Entities

- **Identity Provider**: Organization sign-in configuration, verified domains, provider type, status, metadata health, and activation history.
- **Auth Policy**: MFA, session, IP, and fallback access rules that apply to users or user groups.
- **Identity Mapping**: Relationship between identity provider claims and FormCraft roles, departments, branches, and preferences.
- **MFA Enrollment**: User-owned authentication method (TOTP or SMS/Email OTP), enrollment state, recovery state, and last challenge result.
- **Session Event**: Auditable record of sign-in, sign-out, revocation, timeout, failed challenge, and policy enforcement.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An org admin can configure and test a valid identity provider in under 20 minutes without support assistance.
- **SC-002**: 95% of SSO users with valid corporate credentials can complete sign-in and reach their permitted default mode on the first attempt.
- **SC-003**: 100% of privileged users subject to MFA are challenged before accessing admin, platform, export, or approval actions.
- **SC-004**: Identity policy changes are visible in audit history within 1 minute of the action.
- **SC-005**: Broken provider configuration can be detected and rolled back without locking out all organization admins.
