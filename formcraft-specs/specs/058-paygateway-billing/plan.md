# Implementation Plan: PayGateway Billing Integration

**Branch**: `058-paygateway-billing` | **Date**: 2026-06-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `formcraft-specs/specs/058-paygateway-billing/spec.md`

## Summary

Embed the existing PayGateway service into FormCraft so organization administrators can purchase higher subscription tiers, seat add-ons, OCR onboarding credits, and premium marketplace templates by card without FormCraft receiving raw card data. The implementation adds normalized billing price/purchase/refund tables, a backend-only PayGateway adapter, idempotent fulfillment services, org/platform-admin FastAPI endpoints, and shared Angular billing checkout surfaces that work from both Classic and Spark themes in Arabic/RTL and English/LTR.

## Technical Context

**Language/Version**: Python 3.12 backend; TypeScript / Angular 19 frontend
**Primary Dependencies**: FastAPI, Pydantic, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, ngx-translate, RxJS, existing audit/organization/platform/marketplace/OCR services, external PayGateway service
**Storage**: Supabase PostgreSQL with versioned migration for billing prices, purchase intents, fulfillment effects, refunds, and marketplace revenue splits; RLS policies isolate organization purchase records
**Testing**: pytest backend unit/contract/integration tests; Angular service/component tests where frontend harness exists; manual visual checks for Classic/Spark, RTL/LTR, light/dark
**Target Platform**: Bunny-hosted web application with FastAPI backend and Angular frontend
**Project Type**: Polyrepo web application inside `formcraft-backend/`, `formcraft-frontend/`, and `formcraft-specs/`
**Performance Goals**: Org admin can complete a test-mode tier upgrade in under 3 minutes; checkout token creation returns under 2 seconds excluding PayGateway latency; repeated payment verification/refund callbacks apply effects exactly once
**Constraints**: Backend computes all amounts from authoritative price tables and organization default currency; no self-serve downgrades, no partial refunds, no proration or recurring billing; raw card data and provider secrets never reach the browser; all user-facing UI strings use translation keys; org-admin purchase access and platform-admin refund access are enforced by JWT/RBAC plus RLS
**Scale/Scope**: Four purchase purposes, full-only refunds, at-most-once fulfillment, zero-amount immediate fulfillment, dedicated billing page, Platform Console subscription entry point, and marketplace premium-template purchase handoff

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Arabic-first/RTL-native: PASS. Billing UI is planned as shared Material components with ngx-translate keys, direction-aware layouts, and Arabic/English verification in Classic and Spark.
- Pixel-perfect print fidelity: PASS. No canvas or PDF rendering behavior changes are introduced; marketplace template copies preserve existing normalized template/page/element coordinates.
- AI suggestion, never auto-apply: PASS. No AI suggestion workflows are introduced.
- Deterministic over probabilistic: PASS. No validators or probabilistic classification behavior changes are introduced.
- Test-first development: PASS. Plan requires unit, contract, and integration tests before backend implementation, plus frontend service/component tests for checkout state and localization.
- Normalized data model: PASS. Billing prices, purchases, fulfillments, refunds, and split records are separate migration-backed tables with audit fields.
- Translation-key architecture: PASS. All billing and error messages are represented by translation keys, not hardcoded UI strings.
- Security and auditability: PASS. Backend-only PayGateway credentials, single-purchase checkout tokens, JWT/RBAC, RLS, idempotency keys, and audit records cover purchase/refund actions.
- Simplicity and YAGNI: PASS. Scope is one-off card charges through the already-built PayGateway service; recurring billing, tax, invoicing, partial refunds, and self-serve price admin remain out of scope.

## Project Structure

### Documentation (this feature)

```text
formcraft-specs/specs/058-paygateway-billing/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    └── billing-api.md
```

### Source Code (repository root)

```text
formcraft-backend/
├── migrations/
│   └── 049_paygateway_billing.sql
├── app/
│   ├── api/routes/billing.py
│   ├── schemas/billing.py
│   ├── services/billing_service.py
│   ├── services/paygateway_client.py
│   └── main.py
└── tests/
    ├── integration/test_billing_routes.py
    └── unit/
        ├── test_billing_service.py
        └── test_paygateway_client.py

formcraft-frontend/
└── src/app/
    ├── app-routing.module.ts
    ├── core/services/billing.service.ts
    ├── shared/models/billing.models.ts
    ├── features/billing/
    │   ├── billing.module.ts
    │   ├── billing-routing.module.ts
    │   ├── billing-page/
    │   ├── checkout-dialog/
    │   └── purchase-history/
    ├── features/platform/organization-detail/tabs/subscription-tab/
    ├── features/marketplace/detail/
    ├── features/ui-redesign/ui-redesign.routes.ts
    └── assets/i18n/
        ├── ar.json
        └── en.json
```

**Structure Decision**: Use the established backend route/schema/service split and add a dedicated `billing` Angular feature module so Classic and Spark route surfaces can share the same checkout components. Platform Console and marketplace views link into the same billing service rather than duplicating purchase logic.

## Phase 0: Research

See [research.md](./research.md). Decisions resolve PayGateway boundary, idempotency, price authority, zero-amount fulfillment, refund reversal, marketplace purchase handoff, and dual-theme checkout routing.

## Phase 1: Design & Contracts

See [data-model.md](./data-model.md), [contracts/billing-api.md](./contracts/billing-api.md), and [quickstart.md](./quickstart.md). The API exposes purchase option discovery, checkout initiation, status verification, purchase history, PayGateway webhook/return verification, and platform-admin full refunds.

## Post-Design Constitution Check

- PASS: Data model remains normalized and migration-backed with RLS and audit fields.
- PASS: API contracts require JWT/RBAC, org scoping, backend price computation, provider verification, and idempotent fulfillment.
- PASS: Frontend plan uses shared components, translation keys, and RTL/LTR plus Classic/Spark visual verification.
- PASS: No print/PDF, AI, validator, recurring billing, tax, or invoice scope is introduced.
- PASS: Test-first coverage is defined for price tampering, zero-amount purchases, 3-D Secure status, duplicate verification, failed payment, cross-org access, and full refund reversal.

## Complexity Tracking

No constitution violations require justification.
