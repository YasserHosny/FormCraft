# Implementation Plan: Enterprise SSO and MFA

**Branch**: `042-enterprise-sso-mfa` | **Date**: 2026-05-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/042-enterprise-sso-mfa/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement enterprise SSO (SAML 2.0 and OIDC) and MFA (TOTP and SMS/Email OTP) for FormCraft organizations. Admins configure identity providers, enforce domain-based routing, require MFA for privileged roles, map identity groups to FormCraft roles/departments/branches, and audit all sign-in and policy events. The solution preserves Arabic-first RTL localization and full auditability.

## Technical Context

**Language/Version**: Python 3.12, TypeScript / Angular 19  
**Primary Dependencies**: FastAPI, `python-saml`, `authlib`, `pyotp`, `cryptography`, Angular Material, `ngx-translate`  
**Storage**: Supabase PostgreSQL  
**Testing**: pytest (backend), Angular TestBed / Karma (frontend)  
**Target Platform**: Bunny Magic Containers (Linux server + modern browser)  
**Project Type**: web-service + web-app  
**Performance Goals**: SSO login redirect < 2s, MFA challenge verify < 500ms  
**Constraints**: <200ms p95 for MFA verify; Arabic/English i18n; RTL-first UI; AES-256 encryption for IdP secrets  
**Scale/Scope**: Up to 10 identity providers per org; 100 concurrent SSO sessions per org; MFA enrollment per user limited to 2 active methods  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arabic-First, RTL-Native | PASS | All new auth UI components must be RTL-tested; i18n keys for Arabic and English sign-in/MFA/recovery flows. |
| II. Pixel-Perfect Print Fidelity | N/A | No PDF output in this feature. |
| III. AI Suggestion, Never Auto-Apply | PASS | No AI involvement. |
| IV. Deterministic Over Probabilistic | PASS | Deterministic validators only. |
| V. Test-First Development | PASS | TDD enforced: contract tests for SSO/OIDC endpoints, unit tests for MFA/encryption services. |
| VI. Normalized Data Model | PASS | New entities (Identity Provider, Auth Policy, Identity Mapping, MFA Enrollment, Session Event) are normalized with FKs and audit fields. |
| VII. Translation-Key Architecture | PASS | All UI strings via i18n keys; language preference stored per user. |
| VIII. Security and Auditability | PASS | JWT via Supabase Auth extended with MFA step-up; RLS policies for new tables; full audit trail for sign-in, MFA, provider, policy events. |
| IX. Simplicity and YAGNI | **VIOLATION — Justified** | Principle IX lists "No SSO" as a Phase-1 guardrail. F042 is an explicitly approved feature spec in `formcraft-specs/specs/042-enterprise-sso-mfa/`, satisfying the constitution's governance rule that "Features are added only when specified in an approved spec." This is treated as an approved exception, analogous to the F31 bulk-governance exception. Complexity is bounded to the spec scope (SAML/OIDC + TOTP/SMS-Email OTP). No general-purpose identity abstraction beyond the specified flows. |

## Project Structure

### Documentation (this feature)

```text
specs/042-enterprise-sso-mfa/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
formcraft-backend/
├── app/
│   ├── models/
│   │   └── identity.py          # IdP, AuthPolicy, IdentityMapping, MfaEnrollment, SessionEvent
│   ├── services/
│   │   ├── sso_service.py       # SAML/OIDC orchestration, metadata validation
│   │   ├── mfa_service.py       # TOTP / SMS-Email OTP enrollment, challenge, verify
│   │   ├── session_service.py   # Session timeout, idle timeout, concurrent limit enforcement
│   │   └── crypto_service.py    # AES-256 encryption/decryption for IdP secrets
│   ├── api/v1/
│   │   ├── sso.py               # SSO endpoints (SAML ACS, OIDC callback, metadata)
│   │   ├── mfa.py               # MFA enrollment, challenge, verify, recovery
│   │   └── auth_policy.py       # Policy CRUD and org-level defaults
│   ├── core/
│   │   └── config.py            # SSO/MFA settings, encryption key config
│   └── tests/
│       ├── unit/
│       │   ├── test_sso_service.py
│       │   ├── test_mfa_service.py
│       │   └── test_crypto_service.py
│       └── integration/
│           └── test_sso_flows.py

formcraft-frontend/
├── src/app/
│   ├── features/
│   │   ├── sso/
│   │   │   ├── components/
│   │   │   │   ├── idp-config/
│   │   │   │   ├── domain-verify/
│   │   │   │   └── sso-signin/
│   │   │   └── sso.module.ts
│   │   └── mfa/
│   │       ├── components/
│   │       │   ├── enroll/
│   │       │   ├── challenge/
│   │       │   └── recovery/
│   │       └── mfa.module.ts
│   ├── core/
│   │   ├── services/
│   │   │   ├── sso.service.ts
│   │   │   └── mfa.service.ts
│   │   └── guards/
│   │       └── mfa.guard.ts
│   └── shared/
│       └── components/
│           └── mfa-status/
```

**Structure Decision**: Option 2 (Web application) — existing `formcraft-backend/` and `formcraft-frontend/` polyrepo layout. Feature code is scoped to new modules/routes within the existing structure to minimize cross-cutting changes.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Principle IX — SSO | Explicitly approved in F042 spec; enterprise banks and government customers require centralized identity before production rollout. | Using only Supabase native auth would force orgs to manage a second credential set, violating the primary user goal and acceptance criteria. |
| MFA service addition | Spec requires TOTP and SMS/Email OTP for privileged roles. | Relying solely on Supabase MFA would limit method choice and prevent org-level policy enforcement by role/department. |

## Design Decisions

### Identity Provider Integration
- **SAML**: Use `python-saml` (OneLogin) for SAML 2.0 Service Provider flows. XML metadata parsed and validated before storage.
- **OIDC**: Use `authlib` for OIDC RP flows. Discovery document fetched and cached with TTL.
- **Secrets**: IdP certificates, client secrets, and signing keys encrypted with AES-256-GCM using a per-organization key derived from a master key plus org UUID.

### MFA
- **TOTP**: `pyotp` with RFC 6238 compliance. QR codes rendered via `qrcode` library; frontend uses `angularx-qrcode`.
- **SMS/Email OTP**: 6-digit codes, 5-minute expiry. Backend generates via `secrets`; delivery reuses existing notification/email infrastructure.
- **Enrollment**: Self-service enrollment with mandatory verification before activation. Max 2 active methods per user.

### Session Management
- Extend existing JWT/session layer. Add `mfa_verified` claim to JWT after successful challenge.
- Session timeout and idle timeout enforced via middleware that checks `last_activity_at` against policy.
- Concurrent session limits tracked in PostgreSQL; oldest sessions revoked on limit breach.

### Just-in-Time Provisioning
- Identity Mapping table stores claim-to-role/department/branch rules.
- On SSO sign-in, claims are evaluated in priority order; first match wins.
- Unmatched users fall back to no role/department with an admin alert (as clarified).

### Audit
- All events write to `audit_logs` (existing table) via existing audit service with new event types: `sso_signin`, `mfa_enroll`, `mfa_challenge`, `mfa_verify`, `idp_change`, `policy_change`, `session_revoke`.

## Architecture Notes

- **No new auth server**: SSO/MFA are built into the existing FastAPI backend, not a separate identity server.
- **Supabase Auth still primary**: SSO federates into Supabase Auth by linking/external identity; local users remain in Supabase. This preserves existing RLS and JWT infrastructure.
- **Feature flags**: New SSO/MFA UI routes are guarded by a feature-check service that verifies the org has SSO enabled.
