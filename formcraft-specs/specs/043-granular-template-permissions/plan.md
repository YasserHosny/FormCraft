# Implementation Plan: Granular Template Permissions

**Branch**: `043-granular-template-permissions` | **Date**: 2026-05-26 | **Spec**: `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-specs/specs/043-granular-template-permissions/spec.md`
**Input**: Feature specification from `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-specs/specs/043-granular-template-permissions/spec.md`

## Summary

Add organization-scoped custom template roles, access policies, explicit allow/deny grants, and access diagnostics so template actions can be authorized by role, department, branch, user, lifecycle state, and imported-template policy status. The implementation adds normalized Supabase tables, a deterministic FastAPI permission service, admin API contracts, and focused backend tests. Frontend wiring is intentionally deferred to avoid conflicting with parallel F044 work and current unrelated UI edits.

## Technical Context

**Language/Version**: Python 3.12 backend; TypeScript / Angular 19 frontend remains unchanged for this increment  
**Primary Dependencies**: FastAPI, Pydantic, Supabase PostgreSQL/Auth/RLS/Storage, existing AuditLogger  
**Storage**: Supabase PostgreSQL with versioned SQL migration in `formcraft-backend/migrations/041_granular_template_permissions.sql`  
**Testing**: pytest unit and integration tests under `formcraft-backend/tests/`  
**Target Platform**: FormCraft backend API on Linux containers  
**Project Type**: Web application backend feature with future Angular admin UI integration  
**Performance Goals**: Access checks complete with deterministic query fan-out and support revocation visibility within 60 seconds  
**Constraints**: Explicit deny overrides inherited grants; imported templates without local policies are admin-only; no hardcoded UI strings added; no PDF/canvas changes  
**Scale/Scope**: Organization-scoped roles and grants for templates used across branches, departments, Desk, Studio, Admin, reports, exports, and direct API access

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Arabic-first/RTL: Backend returns localized name fields and message keys; no new UI templates in this increment.
- Pixel-perfect print fidelity: No print canvas or PDF layout changes.
- AI suggestion limits: No AI or OCR behavior added.
- Deterministic over probabilistic: Permission evaluation is rule-based and deterministic.
- Test-first development: Unit and integration tests are included for service and API contracts.
- Normalized data model: New entities use normalized tables with org-scoped foreign keys and audit timestamps.
- Translation-key architecture: API exposes stable labels/message keys for future Angular translations; no hardcoded UI templates added.
- Security and auditability: Requires Supabase JWT profile, org admin role for policy management, deny audit events, and RLS-ready tables.
- Simplicity and YAGNI: Backend permission engine and contracts only; no broad workflow engine or unrelated UI refactor.

## Project Structure

### Documentation (this feature)

```text
formcraft-specs/specs/043-granular-template-permissions/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── template-permissions-api.md
└── tasks.md
```

### Source Code (repository root)

```text
formcraft-backend/
├── app/
│   ├── api/routes/template_permissions.py
│   ├── main.py
│   ├── schemas/template_permissions.py
│   └── services/template_permission_service.py
├── migrations/041_granular_template_permissions.sql
└── tests/
    ├── integration/test_template_permissions_route.py
    └── unit/test_template_permission_service.py
```

**Structure Decision**: Implement F043 as a backend API and database capability first, using existing FastAPI route/service/schema layers. Frontend screens can consume the contracts later without changing permission semantics.

## Complexity Tracking

No constitution violations require justification.
