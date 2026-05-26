# Implementation Plan: Batch OCR Onboarding

**Branch**: `045-batch-ocr-onboarding` | **Date**: 2026-05-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `formcraft-specs/specs/045-batch-ocr-onboarding/spec.md`

## Summary

Add an admin-facing OCR onboarding workflow for legacy form libraries. Admins create a batch of up to 200 scanned forms, each item is validated and processed with the existing single-form OCR pipeline, reviewers triage confidence-ranked results, explicitly bulk-accept high-confidence items, handle duplicate/failed items, and convert accepted results into draft templates with source and review metadata.

## Technical Context

**Language/Version**: Python 3.12 backend; TypeScript / Angular 19 frontend
**Primary Dependencies**: FastAPI, Pydantic, Supabase PostgreSQL/Auth/Storage/RLS, existing OCR services (`AzureOCRClient`, `FieldClassifier`, `BoundingBoxConverter`), Angular Material, ngx-translate, RxJS
**Storage**: Supabase PostgreSQL plus Storage; add OCR onboarding batch/item/detection/decision tables and links to existing templates/pages/elements/form_detections/audit_logs
**Testing**: pytest backend unit/integration tests; Angular component/service tests where available
**Target Platform**: Web application (admin/reviewer browser UI plus FastAPI backend)
**Project Type**: SPA + REST API
**Performance Goals**: Accept and persist a 200-form batch in one request; list dashboard summaries under 2s for 200 items; process item state transitions without blocking other items; bulk accept 100 high-confidence items under 5s excluding provider OCR latency
**Constraints**: Reviewer confirmation required before draft template creation; no automatic template creation from OCR confidence alone; item-level retry without whole-batch re-upload; Arabic/English i18n and RTL/LTR layout; RLS and audit events for batch, review, retry, and conversion actions
**Scale/Scope**: First implementation guarantees 200 forms per batch and uses existing OCR extraction/classification rather than a new provider workflow

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Arabic-first/RTL-native: PASS. UI tasks include ngx-translate keys and RTL/LTR dashboard/review validation.
- Pixel-perfect print fidelity: PASS. Draft templates keep detected coordinates from the existing OCR coordinate conversion path; no print reflow changes are introduced.
- AI suggestion, never auto-apply: PASS WITH APPROVED SPEC SCOPE. F045 is an approved OCR feature spec and requires explicit reviewer accept/bulk accept before any template conversion.
- Deterministic over probabilistic: PASS. Confidence supports triage only; deterministic validators still override conflicting field suggestions during template review.
- Test-first development: PASS. Tasks place backend contract/service tests before implementation.
- Normalized data model: PASS. New batch/item/decision entities are normalized with migrations and audit fields.
- Translation-key architecture: PASS. No hardcoded user-facing strings in frontend templates.
- Security and auditability: PASS. Admin/designer/reviewer authorization, RLS, and audit logging are explicit.
- Simplicity/YAGNI: PASS. Reuses existing OCR services and avoids a general-purpose automation engine.

## Project Structure

### Documentation (this feature)

```text
formcraft-specs/specs/045-batch-ocr-onboarding/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api.md
└── tasks.md
```

### Source Code (repository root)

```text
formcraft-backend/
├── app/
│   ├── api/routes/ocr_onboarding.py
│   ├── schemas/ocr_onboarding.py
│   ├── services/ocr_onboarding_service.py
│   └── main.py
├── migrations/042_batch_ocr_onboarding.sql
└── tests/
    ├── integration/test_ocr_onboarding_routes.py
    └── unit/test_ocr_onboarding_service.py

formcraft-frontend/
└── src/app/
    ├── core/services/ocr-onboarding.service.ts
    ├── features/admin/ocr-onboarding/
    │   ├── ocr-onboarding.module.ts
    │   ├── ocr-onboarding-routing.module.ts
    │   ├── ocr-batch-list.component.*
    │   ├── ocr-batch-detail.component.*
    │   └── ocr-batch-create.component.*
    ├── features/admin/admin.module.ts
    └── src/assets/i18n/{ar,en}.json
```

**Structure Decision**: Use the existing backend/frontend split and existing admin feature module. Backend owns batch lifecycle, item state transitions, retry, duplicate marking, and draft conversion orchestration. Frontend provides admin list/detail/create/review screens backed by translation keys.

## Phase 0: Research

See [research.md](./research.md). All open implementation decisions are resolved.

## Phase 1: Design & Contracts

See [data-model.md](./data-model.md), [contracts/api.md](./contracts/api.md), and [quickstart.md](./quickstart.md).

## Post-Design Constitution Check

- Explicit human acceptance remains the conversion gate for high-confidence items.
- New tables are normalized and covered by RLS migration policy stubs.
- API contracts include authenticated admin/designer/reviewer access and audit-triggering state changes.
- Frontend tasks require translation keys and RTL/LTR-compatible Material layouts.

No constitution violations remain.

## Complexity Tracking

No constitution violations require justification.
