# Implementation Plan: Digital Signatures

**Branch**: `046-digital-signatures` | **Date**: 2026-05-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `formcraft-specs/specs/046-digital-signatures/spec.md`

## Summary

Build an in-house digital signature workflow for FormCraft submissions and template approvals. Organizations enable signature workflows on selected templates; operators initiate signature requests with internal and external signers; signers verify identity (password for internal users, email OTP for external recipients) and apply legally traceable digital signatures. The system preserves signed PDF evidence, SHA-256 document hashes, and a complete auditable event timeline. Backend extends existing submission/approval/PDF infrastructure with new normalized signature tables, FastAPI routes, Pydantic schemas, and services. Frontend adds an Angular signature management module with signer configuration, request tracking, and evidence verification views, using Angular Material and translation keys.

## Technical Context

**Language/Version**: Python 3.12 backend; TypeScript / Angular 19 frontend  
**Primary Dependencies**: FastAPI, Pydantic, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, ngx-translate, RxJS, existing submission/approval/PDF/notification/email services, WeasyPrint for signed PDF generation  
**Storage**: Supabase PostgreSQL with versioned migration for signature workflow/request/recipient/event/evidence tables and RLS policies; signed PDFs stored in Supabase Storage  
**Testing**: pytest unit/contract/integration tests for backend; Angular component/service tests where frontend test harness exists  
**Target Platform**: Bunny-hosted web application with FastAPI backend and Angular SPA frontend  
**Performance Goals**: Signature request creation under 5 seconds; signer invitation email delivery within 30 seconds; evidence verification query returns within 2 seconds  
**Constraints**: JWT authentication on all admin/operator endpoints; public signer endpoints use opaque signature-request tokens (not JWT); RLS prevents cross-org signature data leakage; UI must be RTL-native with zero hardcoded user-facing strings; max 10 signers per request; default 7-day expiration; AES-256 encryption for evidence at rest; 7-year audit retention  
**Scale/Scope**: Per-organization signature workflows for selected templates and submissions; ordered and parallel multi-signer support; internal and external signer types; in-house signing without external provider dependency  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate Result | Plan Response |
|-----------|-------------|---------------|
| I. Arabic-First, RTL-Native | PASS | Signature UI uses Angular Material, `dir="auto"` for mixed signer names, and translation keys for all user-facing text. Signer-facing pages default to Arabic with English fallback. |
| II. Pixel-Perfect Print Fidelity | PASS | Signed PDFs reuse the existing WeasyPrint renderer with a signature overlay layer; original mm canvas coordinates are preserved unchanged. |
| III. AI Suggestion, Never Auto-Apply | PASS | No AI workflows are introduced. |
| IV. Deterministic Over Probabilistic | PASS | Signature state transitions, OTP generation, hash verification, and expiration checks are deterministic service rules. |
| V. Test-First Development | PASS WITH TASK REQUIREMENT | Tasks must create failing contract/unit tests for request creation, signer invitation, identity verification, signing, decline, expiration, evidence verification, and idempotency before implementation. |
| VI. Normalized Data Model | PASS | New signature entities are normalized tables with `created_at`, `updated_at`, and actor/audit fields; evidence is stored as JSONB with structured schema. |
| VII. Translation-Key Architecture | PASS WITH TASK REQUIREMENT | Frontend tasks include i18n keys for all admin, operator, and signer-facing strings. |
| VIII. Security and Auditability | PASS | Admin/operator endpoints require JWT/RBAC; public signer endpoints use opaque tokens; DB RLS prevents cross-org access; audit logs record all lifecycle events; evidence encrypted at rest. |
| IX. Simplicity and YAGNI | PASS | In-house signing without external provider dependency. Scope excludes advanced PKI, blockchain anchoring, third-party eIDAS providers, and advanced certificate management. |

No blocking gate failures.

## Project Structure

### Documentation (this feature)

```text
formcraft-specs/specs/046-digital-signatures/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── digital-signatures-api.md
└── tasks.md
```

### Source Code (repository root)

```text
formcraft-backend/
├── migrations/
│   └── 046_digital_signatures.sql
├── app/
│   ├── api/routes/
│   │   └── digital_signatures.py          # signature workflow, request, recipient, evidence admin/operator endpoints
│   ├── schemas/
│   │   └── digital_signature.py           # request, recipient, event, evidence DTOs
│   └── services/
│       ├── digital_signature_service.py   # core orchestration: create request, invite signers, process sign/decline
│       ├── signer_identity_service.py     # internal password re-auth, external email OTP generation/verification
│       ├── signature_evidence_service.py  # evidence package creation, hash verification, PDF sealing
│       └── signature_token_service.py     # opaque token generation/validation for public signer endpoints
└── tests/
    ├── unit/
    │   ├── test_digital_signature_service.py
    │   ├── test_signer_identity_service.py
    │   ├── test_signature_evidence_service.py
    │   └── test_signature_token_service.py
    └── integration/
        └── test_digital_signature_routes.py

formcraft-frontend/
└── src/app/
    ├── core/services/
    │   └── digital-signature.service.ts
    ├── features/digital-signatures/
    │   ├── digital-signatures.module.ts
    │   ├── digital-signatures-routing.module.ts
    │   ├── workflow-config/               # admin configures template-level signature workflows
    │   ├── request-list/                  # operator views and manages signature requests
    │   ├── request-detail/                # timeline, resend, cancel, signer status
    │   ├── signer-portal/                 # public signer-facing page (token-protected)
    │   └── evidence-viewer/               # compliance/audit views evidence package
    ├── features/admin/
    │   └── signature-settings/            # org-level signature enablement and defaults
    └── assets/i18n/
        ├── ar.json
        └── en.json
```

**Structure Decision**: Use the established backend route/schema/service split. Add a dedicated Angular `digital-signatures` feature module for admin workflow configuration and operator request management. The public signer portal lives inside the same module but uses token-based routing separate from authenticated app navigation. Evidence viewer is shared between operator and admin roles.

## Complexity Tracking

No constitution violations require justification.

## Phase 0: Research

See [research.md](./research.md). Decisions resolve in-house vs external provider, identity verification mechanism, evidence storage format, PDF sealing approach, token security model, and expiration/cleanup strategy.

## Phase 1: Design And Contracts

See [data-model.md](./data-model.md), [contracts/digital-signatures-api.md](./contracts/digital-signatures-api.md), and [quickstart.md](./quickstart.md). The API exposes workflow configuration, request creation, signer invitation, public signer actions (view/verify/sign/decline), evidence retrieval, and admin/operator management endpoints.

## Post-Design Constitution Check

- PASS: The data model remains normalized and migration-backed.
- PASS: API contracts require JWT/RBAC for admin/operator routes and opaque tokens for public signer routes.
- PASS: UI plan includes translation keys and RTL/LTR verification.
- PASS: Evidence handling uses structured JSONB and AES-256 encryption at rest.
- PASS: Tests are planned before implementation for every endpoint and critical service branch.
