# Implementation Plan: Template Marketplace

**Branch**: `035-template-marketplace-codex` | **Date**: 2026-05-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `formcraft-specs/specs/035-template-marketplace/spec.md`

## Summary

Build a curated template marketplace where authenticated org admins can browse approved listings, preview read-only canvas/PDF samples, import free or premium templates as immutable org-local drafts, publish their own approved templates for FormCraft review, and submit verified ratings after import. The implementation extends the existing normalized template/page/element model with marketplace listing, import, review, and transaction tables, adds FastAPI routes/services and Pydantic schemas, and adds Angular marketplace/admin publishing screens using Angular Material and translation keys.

## Technical Context

**Language/Version**: Python 3.12 backend; TypeScript / Angular 19 frontend
**Primary Dependencies**: FastAPI, Pydantic, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, ngx-translate, RxJS, existing template/PDF/reference-data services
**Storage**: Supabase PostgreSQL with versioned migration for marketplace listing/import/review/transaction tables and RLS policies
**Testing**: pytest unit/contract/integration tests for backend; Angular component/service tests where frontend test harness exists
**Target Platform**: Bunny-hosted web application with FastAPI backend and Angular frontend
**Project Type**: Polyrepo web application inside `formcraft-backend/`, `formcraft-frontend/`, and `formcraft-specs/`
**Performance Goals**: Marketplace search/filter returns within 2 seconds for 1,000+ listings; premium purchase/import finishes within 30 seconds; import preserves 100% of supported elements, validators, and layout
**Constraints**: JWT authentication on all marketplace endpoints; Admin role required for publish/import/review moderation operations; RLS prevents cross-org source template leakage; UI must be RTL-native with zero hardcoded user-facing strings
**Scale/Scope**: 1,000+ public listings, org-scoped publisher/consumer workflows, one verified review per importing org per listing, MVP payment adapter without live gateway dependency

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Arabic-first RTL: PASS. Marketplace UI uses Angular Material, `dir="auto"` where mixed names/descriptions appear, and translation keys for all user-facing text.
- Pixel-perfect print fidelity: PASS. Imports clone normalized page/element mm coordinates unchanged; previews use existing read-only canvas/PDF surfaces rather than changing PDF rendering.
- AI suggestion never auto-apply: PASS. No AI workflows are introduced.
- Deterministic validators: PASS. Validator cloning strips org-owned identifiers and preserves only supported deterministic validators; unsupported dependencies are disabled with warnings.
- Test-first development: PASS. Tasks include backend contract/integration/unit tests before implementation.
- Normalized data model: PASS. Marketplace entities are separate normalized tables with `created_at`, `updated_at`, and actor/audit fields.
- Translation-key architecture: PASS. Frontend tasks include i18n keys and no hardcoded UI strings.
- Security and auditability: PASS. Endpoints require JWT/RBAC, DB RLS, and audit log entries for publish, review, import, purchase, refund, and suspension actions.
- Simplicity and YAGNI: PASS. MVP uses a pluggable payment adapter and internal transaction states, not a live gateway integration.

## Project Structure

### Documentation (this feature)

```text
formcraft-specs/specs/035-template-marketplace/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── marketplace-api.md
└── tasks.md
```

### Source Code (repository root)

```text
formcraft-backend/
├── migrations/
│   └── 037_template_marketplace.sql
├── app/
│   ├── api/routes/marketplace.py
│   ├── schemas/marketplace.py
│   └── services/marketplace_service.py
└── tests/
    ├── integration/test_marketplace_routes.py
    └── unit/test_marketplace_service.py

formcraft-frontend/
└── src/app/
    ├── app-routing.module.ts
    ├── core/services/marketplace.service.ts
    ├── features/marketplace/
    │   ├── marketplace.module.ts
    │   ├── marketplace-routing.module.ts
    │   ├── browse/
    │   ├── detail/
    │   ├── publish/
    │   └── review/
    ├── shared/models/marketplace.models.ts
    └── assets/i18n/
        ├── ar.json
        └── en.json
```

**Structure Decision**: Use the established backend route/schema/service split and add a lazy-loaded Angular feature module at `/marketplace`. Admin publishing lives inside the marketplace module because the workflow starts from a template and shares listing metadata models with browse/import.

## Phase 0: Research

See [research.md](./research.md). Decisions resolve payment scope, cross-org cloning, marketplace update semantics, refund behavior, suspension behavior, search/indexing, and review verification.

## Phase 1: Design And Contracts

See [data-model.md](./data-model.md), [contracts/marketplace-api.md](./contracts/marketplace-api.md), and [quickstart.md](./quickstart.md). The API exposes browse/detail/import/publish/review/moderation endpoints and uses normalized marketplace entities with audit logging.

## Post-Design Constitution Check

- PASS: The data model remains normalized and migration-backed.
- PASS: API contracts require JWT/RBAC, org scoping, and audit events.
- PASS: UI plan includes translation keys and RTL/LTR verification.
- PASS: Payment integration is intentionally adapter-based for MVP simplicity.
- PASS: Tests are planned before implementation for every endpoint and critical service branch.

## Complexity Tracking

No constitution violations require justification.
