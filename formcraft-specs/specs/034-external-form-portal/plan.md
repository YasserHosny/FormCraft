# Implementation Plan: External Form Portal

**Branch**: `034-external-form-portal-plan` | **Date**: 2026-05-25 | **Spec**: [spec.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/034-external-form-portal/spec.md)
**Input**: Feature specification from `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-specs/specs/034-external-form-portal/spec.md`

## Summary

Add a public, accountless form portal for EXT-01. Organizations can expose selected published templates through public URLs/QR codes, optionally gate access with admin-configured OTP modes and CAPTCHA, enforce abuse limits, and receive public submissions with pinned template versions, deterministic validation, optional PDF download/email confirmation, and audit-safe metadata. Backend work adds initial public discovery plus portal-session-token-protected public actions and admin configuration routes over Supabase; frontend work adds responsive Flow Layout public pages and an admin portal configuration area.

## Technical Context

**Language/Version**: Python 3.12 backend; TypeScript / Angular 19 frontend  
**Primary Dependencies**: FastAPI, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, ngx-translate, RxJS, Zod, Pydantic, existing validation/condition/tafqeet services, existing PDF renderer, existing notification/email infrastructure, pluggable SMS provider adapter, hCaptcha/reCAPTCHA adapter  
**Storage**: Supabase PostgreSQL; extend existing `organizations`, `org_settings`, `templates`, `pages`, `elements`, `submissions`, `profiles`, `audit_logs`; add portal configuration/session/OTP/rate-limit/public-submission metadata tables  
**Testing**: `pytest` backend unit/integration/contract tests; Angular build and focused service/component tests where present  
**Target Platform**: Public web portal and admin SPA deployed as Angular frontend + FastAPI backend on existing container infrastructure  
**Project Type**: Web application with public/API backend and Angular SPA frontend  
**Performance Goals**: Public form shell interactive within 3 seconds on mobile 4G; OTP request response recorded within 30 seconds of send attempt; 100 concurrent public submissions without user-visible degradation; hot public URLs tolerate burst traffic through rate limiting and CAPTCHA gating  
**Constraints**: Initial public form discovery is anonymous but rate-limited and scoped to enabled public forms; OTP, submit, and PDF endpoints require opaque portal-session or scoped download tokens; admin routes require admin role; public submissions pin template version at session load; OTP-gated forms fail closed when OTP providers are unavailable; rate limiting uses IP + browser/session before OTP and verified contact after OTP; audit logs store metadata plus bounded/redacted field summary only; all public UI is Arabic-first and RTL/LTR safe; no FormCraft account is created for external users  
**Scale/Scope**: Per-template public portal for organizations; initial scope covers published template access, OTP/CAPTCHA gate, public submission, optional PDF/email confirmation, and admin configuration/analytics for hundreds of public forms and bursty public traffic

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution source: `/media/yasserhosny/My Passport/Work/Projects/FormCraft/.specify/memory/constitution.md`.

| Principle | Gate Result | Plan Response |
|-----------|-------------|---------------|
| I. Arabic-First, RTL-Native | PASS | Public Flow Layout and admin portal UI must use translation keys, default Arabic, mirror RTL/LTR spacing, and use `dir="auto"` for mixed user-entered values. |
| II. Pixel-Perfect Print Fidelity | PASS | Public filling uses responsive Flow Layout only; optional PDF download reuses the existing print/PDF renderer and pinned template version without changing mm canvas coordinates. |
| III. AI Suggestion, Never Auto-Apply | PASS | No AI suggestions or auto-application are introduced. |
| IV. Deterministic Over Probabilistic | PASS | Validation, conditions, tafqeet, OTP state, CAPTCHA verification, and rate limits are deterministic service checks. |
| V. Test-First Development | PASS WITH TASK REQUIREMENT | Tasks must create failing contract/unit tests for public access, validation parity, OTP lockouts/provider outages, rate limits, and audit-safe metadata before implementation. |
| VI. Normalized Data Model | PASS | New portal config/session/OTP/rate-limit/public metadata entities are normalized with foreign keys, audit fields, and migrations; raw public payload is not duplicated in audit logs. |
| VII. Translation-Key Architecture | PASS WITH TASK REQUIREMENT | Public portal and admin UI must add `en.json`/`ar.json` keys and avoid hardcoded user-facing strings. |
| VIII. Security and Auditability | PASS | Admin configuration is RBAC-protected; initial discovery is anonymous but rate-limited, and OTP/submit/PDF public actions require opaque portal-session or scoped download tokens, OTP/CAPTCHA/rate limits, redacted audit metadata, hashed contacts/IPs, and org-scoped persistence. |
| IX. Simplicity and YAGNI | JUSTIFIED EXCEPTIONS | Anonymous initial discovery plus portal-session-token public actions, OTP, CAPTCHA, and rate limiting are explicitly required by F034. Scope excludes account creation, SSO, arbitrary public workflows, and a generic public-site builder. |

No blocking gate failures. Complexity exceptions are documented below.

## Project Structure

### Documentation (this feature)

```text
/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-specs/specs/034-external-form-portal/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
└── tasks.md             # Created by speckit-tasks, not by this plan
```

### Source Code (repository root)

```text
/media/yasserhosny/My Passport/Work/Projects/FormCraft/
├── formcraft-backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   ├── public_portal.py          # public form load, OTP, submit, PDF
│   │   │   └── admin_portal.py           # admin portal config and analytics
│   │   ├── schemas/
│   │   │   └── portal.py                 # public/admin DTOs
│   │   └── services/
│   │       ├── portal_service.py         # config lookup, token validation, session pinning, submit orchestration
│   │       ├── portal_otp_service.py     # OTP generation, verification, lockout
│   │       ├── portal_rate_limit_service.py
│   │       └── captcha_service.py        # hCaptcha/reCAPTCHA adapter
│   ├── migrations/
│   │   └── 035_external_form_portal.sql
│   └── tests/
│       ├── unit/
│       │   ├── test_portal_service.py
│       │   ├── test_portal_otp_service.py
│       │   └── test_portal_rate_limit_service.py
│       └── integration/
│           └── test_external_form_portal_routes.py
└── formcraft-frontend/
    └── src/app/
        ├── core/services/
        │   └── portal.service.ts
        ├── features/public-portal/
        │   ├── public-portal.module.ts
        │   ├── public-form-page/
        │   ├── otp-gate/
        │   └── confirmation-page/
        ├── features/admin/portal/
        │   ├── portal-admin.component.ts
        │   ├── portal-admin.component.html
        │   └── portal-admin.component.scss
        └── shared/models/
            └── portal.models.ts
```

**Structure Decision**: Use the existing backend/frontend split. Add separate public and admin backend route modules because initial public discovery is anonymous/rate-limited, subsequent public portal actions are portal-session-token protected, and admin portal routes use existing JWT/RBAC. Keep portal orchestration in focused services so validation, OTP, CAPTCHA, token validation, email confirmation, QR generation, and rate limiting remain independently testable. Add a dedicated Angular `public-portal` feature to avoid coupling accountless public pages to authenticated admin/desk routing.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Anonymous initial discovery | External users must open enabled public form links without FormCraft accounts. | Requiring login would fail EXT-01; keeping anonymity only at discovery while token-protecting subsequent actions limits the public surface. |
| OTP and CAPTCHA provider adapters | Sensitive public forms require identity/friction gates and provider failure handling. | Hardcoding one provider would make tests brittle and block future org/provider changes. |
| Portal sessions | Template version pinning and pre-OTP rate-limit keys require a durable session boundary. | Stateless submit-only access would allow mid-fill version drift and weaker abuse controls. |

## Phase 0: Research

See [research.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/034-external-form-portal/research.md).

## Phase 1: Design & Contracts

See [data-model.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/034-external-form-portal/data-model.md), [contracts/openapi.yaml](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/034-external-form-portal/contracts/openapi.yaml), and [quickstart.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/034-external-form-portal/quickstart.md).

## Constitution Check - Post Design

Post-design check remains acceptable. The design keeps public submission data normalized and org-scoped, uses deterministic validation and abuse controls, preserves PDF fidelity by reusing the existing renderer for pinned template versions, requires translation-key UI in public/admin flows, and records audit-safe redacted summaries rather than full public payloads. Anonymous access is limited to initial enabled-form discovery; OTP, submit, and PDF actions are constrained to opaque portal-session/download tokens, CAPTCHA, OTP, and rate limiting.
