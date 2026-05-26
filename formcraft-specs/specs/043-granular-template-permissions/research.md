# Research: Granular Template Permissions

## Decision: Deterministic allow/deny evaluator in backend service

**Rationale**: The permission model must explain decisions, audit denials, and enforce consistently across APIs. A backend service can be shared by template, Desk, export, report, and admin routes and produces a single diagnostic shape.

**Alternatives considered**: Route-local role checks were simpler but would duplicate logic and miss direct links. Database-only RLS is still needed as a guardrail, but it cannot provide rich diagnostics without application-level context.

## Decision: Explicit deny overrides all inherited grants

**Rationale**: Sensitive regulated templates need a predictable safety-first rule. This also aligns with the clarification applied to the spec.

**Alternatives considered**: Most-specific rule wins was more flexible but harder to explain and test. Allow-over-deny is unsafe for compliance use cases.

## Decision: Imported templates default to admin-only until assigned

**Rationale**: Marketplace or environment imports may not map to local departments, branches, or roles. Admin-only default prevents accidental exposure.

**Alternatives considered**: Default inherited organization-wide access would be convenient but violates least privilege.

## Decision: Store policies, grants, custom roles, assignments, and decisions in normalized Supabase tables

**Rationale**: The constitution requires normalized models and versioned migrations. Normalized tables support RLS policies, auditing, and future frontend management screens.

**Alternatives considered**: JSON policy blobs on templates would be fast to prototype but harder to query, audit, and enforce with RLS.

## Decision: Reuse existing AuditLogger and add access-specific events

**Rationale**: The project already has an audit trail service. Adding `template_permission.*` and `template_access.denied` events keeps evidence centralized.

**Alternatives considered**: A separate access log table remains useful for analytics, but not as a replacement for audit events.
