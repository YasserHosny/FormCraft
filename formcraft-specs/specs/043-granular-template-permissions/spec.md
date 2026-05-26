# Feature Specification: Granular Template Permissions

**Feature Branch**: `043-granular-template-permissions`  
**Created**: 2026-05-26  
**Status**: Draft  
**Input**: User description: "Granular template permissions and custom roles: org admins define role capabilities and per-template or department-scoped access so designers, reviewers, operators, and branch teams only see, edit, approve, fill, print, or export the templates they are authorized to use."

## Clarifications

### Session 2026-05-26

- Q: Which rule wins when a user has both an inherited grant and an explicit restriction for the same template action? -> A: Explicit deny overrides grants.
- Q: What access should imported templates have when no local policy matches? -> A: Admin-only until assigned.
- Q: How quickly must revoked grants and deactivated custom roles stop authorizing active users? -> A: Within 60 seconds.
- Q: What must access diagnostics expose for support and audit review? -> A: Final decision with matched grants, restrictions, role sources, scope matches, and stale-cache status.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Restrict Template Visibility and Actions (Priority: P1)

An org admin grants template access by role, department, branch, or named user so each team sees only the templates and actions relevant to its work.

**Why this priority**: Multi-branch enterprises need stronger boundaries than broad roles to prevent unauthorized use of regulated forms.

**Independent Test**: Can be tested by creating scoped grants for a template and verifying users outside the scope cannot see or act on it from Studio, Desk, Admin, reports, or exports.

**Acceptance Scenarios**:

1. **Given** a template is restricted to one branch, **When** an operator from another branch opens Form Desk, **Then** the template is not visible and cannot be accessed directly.
2. **Given** a designer has edit but not publish permission, **When** they finish changes, **Then** they can save a draft but cannot publish or bypass review.
3. **Given** a user has a department grant and an explicit deny on a sensitive template, **When** they try the denied action, **Then** the explicit deny wins and the action is blocked.

---

### User Story 2 - Define Custom Role Capabilities (Priority: P2)

An org admin creates custom roles such as "Cheque Reviewer" or "Branch Print Supervisor" with explicit template capabilities.

**Why this priority**: Banks and ministries often have job functions that do not fit the default admin, designer, reviewer, operator, and viewer roles.

**Independent Test**: Can be tested by assigning a custom role to a user and confirming each allowed and denied capability behaves as configured.

**Acceptance Scenarios**:

1. **Given** a custom role allows review but not design, **When** the user opens FormCraft, **Then** they can access assigned review queues but not edit template layouts.
2. **Given** a custom role is deactivated, **When** assigned users next act, **Then** they lose the role's capabilities and receive a clear access message.
3. **Given** an assigned custom role is deactivated, **When** the same user retries an allowed template action within 60 seconds, **Then** the action is denied unless another active grant permits it.

---

### User Story 3 - Audit and Troubleshoot Access (Priority: P3)

An admin reviews why a user can or cannot access a template and exports evidence for compliance review.

**Why this priority**: Access decisions must be explainable when a user is blocked, overexposed, or audited.

**Independent Test**: Can be tested by selecting a user-template pair and confirming the system explains the grants, inherited rules, restrictions, and final decision.

**Acceptance Scenarios**:

1. **Given** a user reports a missing form, **When** an admin checks access diagnostics, **Then** the system shows whether role, branch, department, lifecycle state, or explicit denial caused the result.
2. **Given** access is changed on a sensitive template, **When** the change is saved, **Then** the audit log records who changed it, what changed, and who is affected.

### Edge Cases

- A user changes branch while a draft, review, or batch job is open.
- A reviewer loses permission while a review is in progress.
- A template is imported from the marketplace or another environment with no matching local access policy.
- Imported templates with no matching local access policy are visible only to org admins until an admin assigns a policy.
- Public portal access differs from internal Desk access.
- Cached template lists must update promptly after grants are revoked.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow authorized admins to create template access policies by role, custom role, department, branch, user, and lifecycle state.
- **FR-002**: System MUST support distinct capabilities for view, edit, clone, import, export, submit for review, review, publish, fill, print, reprint, and report.
- **FR-003**: System MUST enforce access consistently across Design Studio, Form Desk, Admin Console, Platform Console support views, exports, reports, APIs, and direct links.
- **FR-004**: System MUST support explicit deny rules that override inherited grants for sensitive templates.
- **FR-005**: System MUST allow admins to create, update, deactivate, and assign custom roles with named capability sets.
- **FR-006**: System MUST show access diagnostics explaining the final access decision for a user and template, including matched grants, restrictions, role sources, scope matches, and stale-cache status.
- **FR-007**: System MUST record all policy, grant, custom role, and access-denied events in the audit trail.
- **FR-008**: System MUST prevent policy edits that leave a published template with no accountable owner or reviewer when review is required.
- **FR-009**: System MUST provide Arabic and English labels for custom roles, permission names, and access messages.
- **FR-010**: System MUST treat imported templates without matching local access policy as admin-only until an authorized admin assigns a local policy.

### Key Entities

- **Custom Role**: Organization-defined capability set with localized name, status, and assignment rules.
- **Template Access Policy**: Rules governing which users or groups may perform actions on a template or category.
- **Template Access Grant**: Explicit permission assignment to a role, department, branch, user, or group.
- **Template Restriction**: Explicit denial or additional condition such as lifecycle state or branch-only visibility.
- **Access Decision Record**: Explainable outcome for a user, template, action, and time.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Admins can restrict a sensitive template to one branch and verify the result in under 5 minutes.
- **SC-002**: Unauthorized users are blocked from restricted template actions in 100% of tested entry points.
- **SC-003**: Access diagnostics explain allow or deny decisions for 95% of support cases without engineering assistance.
- **SC-004**: Permission changes take effect for active users within 60 seconds.
- **SC-005**: Audit exports contain complete evidence for every permission change and denied sensitive action.
