# Implementation Plan: Template Governance

**Branch**: `031-template-governance` | **Date**: 2026-05-25 | **Spec**: [spec.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/031-template-governance/spec.md)
**Input**: Feature specification from `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-specs/specs/031-template-governance/spec.md`

## Summary

Extend the existing F28 approval workflow into a full Admin Console governance area. The implementation adds `/admin/templates` for all-status template oversight and bulk actions, enhances the existing review queue with a read-only canvas review context and lifecycle-aware element comments, and adds a compliance dashboard that computes quality scores from template/page/element data on read. Backend work stays within FastAPI + Supabase, reusing `TemplateService.transition_status()` for approvals/rejections and existing audit logging patterns for all governance actions.

## Technical Context

**Language/Version**: Python 3.12 backend; TypeScript / Angular 19 frontend  
**Primary Dependencies**: FastAPI, Supabase PostgreSQL/Auth/RLS, Angular Material, ngx-translate, Konva.js canvas preview, RxJS  
**Storage**: Supabase PostgreSQL; extend existing `templates`, `pages`, `elements`, `template_reviews`, `audit_logs`, `form_submissions`, `profiles`, `departments` data  
**Testing**: `pytest` for backend unit/integration tests; Angular build and focused component/service tests where present  
**Target Platform**: Web application deployed as Angular frontend + FastAPI backend on existing container infrastructure  
**Project Type**: Enterprise web application with API backend and Angular frontend  
**Performance Goals**: `/admin/templates` initial query under 3s; compliance dashboard for 500+ templates under 5s; filtered review context under 3s  
**Constraints**: Preserve org isolation via Supabase RLS and `org_id`; no new reviewer role; no stored quality score; all governance actions audited; Arabic/English UI with RTL/LTR support  
**Scale/Scope**: Org-scoped governance for hundreds of templates, multiple departments/designers, and review comments per submitted template

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution source: `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-specs/CONSTITUTION.md`.

Spec-kit canonical constitution path `.specify/memory/constitution.md` is synchronized with `formcraft-specs/CONSTITUTION.md` and must remain synchronized before future plan, task, analyze, or implementation commands.

| Principle | Gate Result | Plan Response |
|-----------|-------------|---------------|
| I. Arabic-First, RTL-Native | PASS | Admin templates, review workspace, comments, and compliance dashboard must use translation keys, RTL/LTR mirroring, and `dir="auto"` for mixed text/comment inputs. |
| II. Pixel-Perfect Print Fidelity | PASS | Review canvas is read-only and does not alter print/PDF coordinates. All comment pins use mm coordinates and do not affect PDF output. |
| III. AI Suggestion, Never Auto-Apply | PASS | No AI suggestions or auto-application are introduced. |
| IV. Deterministic Over Probabilistic | PASS | Compliance scoring and validator-impact checks are deterministic from existing element metadata and validator keys. |
| V. Test-First Development | PASS WITH TASK REQUIREMENT | Tasks must create failing backend contract/unit tests before implementation for all new endpoints and compliance formula logic. |
| VI. Normalized Data Model | PASS | New review comments and validator change events are normalized tables with migrations, foreign keys, `created_at`, `updated_at`, and `created_by`. |
| VII. Translation-Key Architecture | PASS WITH TASK REQUIREMENT | No hardcoded UI strings; Angular components must add `en.json`/`ar.json` keys and use runtime translations. |
| VIII. Security and Auditability | PASS | Admin-only endpoints, Supabase RLS, org scoping, authenticated access, and audit events are required for all governance actions. |
| IX. Simplicity and YAGNI | JUSTIFIED EXCEPTIONS | The constitution warns against version diffing UI and bulk automation, but this approved F31 spec explicitly requires version diff context and bulk governance actions. Scope is limited to admin governance only; no general automation engine or unrelated diff UI is added. |

No blocking gate failures. Complexity exceptions are documented below.

## Project Structure

### Documentation (this feature)

```text
/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-specs/specs/031-template-governance/
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
│   │   │   ├── admin_templates.py        # new governance list, bulk actions, compliance endpoints
│   │   │   ├── review_queue.py           # extend with review context/comment endpoints
│   │   │   └── templates.py              # designer-visible comment resolution endpoint if needed
│   │   ├── schemas/
│   │   │   ├── admin_templates.py        # new request/response DTOs
│   │   │   └── review_queue.py           # extend comment/review context DTOs
│   │   └── services/
│   │       ├── template_governance_service.py
│   │       ├── compliance_service.py
│   │       └── review_queue_service.py   # extend existing F28 service
│   ├── migrations/
│   │   └── 032_template_governance.sql
│   └── tests/
│       ├── unit/
│       │   └── test_compliance_service.py
│       └── integration/
│           └── test_template_governance_routes.py
└── formcraft-frontend/
    └── src/app/
        ├── core/services/
        │   ├── template-governance.service.ts
        │   └── review-queue.service.ts       # extend existing API client
        ├── features/admin/
        │   ├── template-governance/
        │   │   ├── template-governance.component.ts
        │   │   ├── template-governance.component.html
        │   │   └── template-governance.component.scss
        │   ├── review-workspace/
        │   │   ├── review-workspace.component.ts
        │   │   ├── review-workspace.component.html
        │   │   └── review-workspace.component.scss
        │   └── compliance-dashboard/
        │       ├── compliance-dashboard.component.ts
        │       ├── compliance-dashboard.component.html
        │       └── compliance-dashboard.component.scss
        └── shared/models/
            └── governance.models.ts
```

**Structure Decision**: Use the existing two-project web app layout (`formcraft-backend`, `formcraft-frontend`). Add a dedicated backend governance service for all-status template oversight and a compliance service for computed metrics, while extending `ReviewQueueService` instead of replacing F28. On the frontend, add admin route components under `features/admin` and reuse existing `ReviewQueueService`, `TemplateService`, status badge, and designer canvas patterns.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Version diffing UI/context | F31 FR-005 requires showing version diff while reviewing updated templates. Existing `TemplateService.compute_diff` will be reused to keep scope narrow. | Omitting diff would fail the approved spec and weaken review decisions. |
| Bulk governance actions | F31 FR-002 requires bulk archive, reassignment, and category changes. This is constrained to admin-selected templates and not a general automation system. | Single-template-only actions would fail the approved spec and keep admin governance inefficient. |

## Phase 0: Research

See [research.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/031-template-governance/research.md).

## Phase 1: Design & Contracts

See [data-model.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/031-template-governance/data-model.md), [contracts/openapi.yaml](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/031-template-governance/contracts/openapi.yaml), and [quickstart.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/031-template-governance/quickstart.md).

## Constitution Check - Post Design

Post-design check remains acceptable. The design preserves the existing F28 lifecycle service, keeps org-scoped data access, computes quality metrics on read as required, and introduces normalized persistence only where lifecycle and auditability require it. The two YAGNI exceptions remain bounded to approved F31 requirements: review diff context and selected-template bulk governance actions.
