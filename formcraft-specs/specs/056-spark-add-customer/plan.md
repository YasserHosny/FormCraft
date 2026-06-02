# Implementation Plan: Spark Theme — Add Customer

**Branch**: `056-spark-add-customer` | **Date**: 2026-06-02 | **Spec**: [spec.md](spec.md)

## Summary

Replace the `SparkFeatureBridgeComponent` placeholder at `/ui/desk/customers/new` with a fully native Spark Add Customer form. The form is a single new Angular standalone component that reuses the existing `CustomerService` for data persistence. No backend changes are required. The implementation is frontend-only: one new component, one route swap, translation keys, and RTL-safe layout.

---

## Technical Context

**Language/Version**: TypeScript / Angular 19 (standalone components)  
**Primary Dependencies**: Angular Material, ngx-translate, RxJS, Angular Reactive Forms, `CustomerService` (existing, `providedIn: 'root'`)  
**Storage**: N/A — uses existing Supabase-backed REST API via `CustomerService`  
**Testing**: Angular `TestBed`, Jasmine/Karma (project standard)  
**Target Platform**: Web browser — Angular SPA served from Bunny Magic Containers  
**Project Type**: Web application (Angular SPA, Spark theme sub-feature)  
**Performance Goals**: Form renders in under 1 second; operator completes full Add Customer flow in under 60 seconds (SC-001)  
**Constraints**: RTL/Arabic-first layout required (Constitution I); zero hardcoded UI strings — all via i18n keys (Constitution VII); TDD mandatory (Constitution V)  
**Scale/Scope**: Single form page (~1 new component, ~1 route change)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arabic-First RTL-Native | **MUST COMPLY** | All form inputs must carry `dir="auto"`. Arabic Name field is right-to-left by default. Full RTL layout test required before merge. |
| II. Pixel-Perfect Print Fidelity | N/A | No PDF output in this feature. |
| III. AI Suggestion, Never Auto-Apply | N/A | No AI involvement. |
| IV. Deterministic Over Probabilistic | N/A | No AI suggestions to override. |
| V. Test-First Development | **MUST COMPLY** | Component spec file and test cases written before implementation. Red-Green-Refactor enforced. |
| VI. Normalized Data Model | **COMPLIANT** | Uses existing `Customer` entity and `CustomerCreate` interface — no schema changes. |
| VII. Translation-Key Architecture | **MUST COMPLY** | All labels, placeholders, error messages, and button text must be i18n keys. No hardcoded strings in template. |
| VIII. Security and Auditability | **COMPLIANT** | `RoleGuard` already guards the route. No RBAC changes needed. |
| IX. Simplicity and YAGNI | **COMPLIANT** | No custom fields (deferred), no unsaved-changes dialog, no extra abstractions. |

**Gate Result**: PASS — no violations. Proceed to Phase 0.

---

## Project Structure

### Documentation (this feature)

```text
formcraft-specs/specs/056-spark-add-customer/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/           ← Phase 1 output
└── tasks.md             ← Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
formcraft-frontend/src/app/features/ui-redesign/
├── desk/
│   ├── add-customer.component.ts          ← NEW (standalone component)
│   ├── add-customer.component.html        ← NEW
│   ├── add-customer.component.scss        ← NEW
│   └── add-customer.component.spec.ts     ← NEW (written first — TDD)
└── ui-redesign.routes.ts                  ← MODIFY: swap SparkFeatureBridgeComponent → AddCustomerComponent

formcraft-frontend/src/assets/i18n/
├── ar.json                                ← MODIFY: add new translation keys
└── en.json                                ← MODIFY: add new translation keys
```

**Structure Decision**: Spark theme desk features all live in `features/ui-redesign/desk/`. The new component follows the identical pattern of `customers.component.ts` already present there. No new directories needed.

---

## Phase 0: Research

*All NEEDS CLARIFICATION items were resolved during `/speckit.clarify`. No open unknowns.*

See [research.md](research.md) for full decisions.

---

## Phase 1: Design & Contracts

See [data-model.md](data-model.md) for entity definitions.  
See [contracts/](contracts/) for interface contracts.  
See [quickstart.md](quickstart.md) for local dev setup.

---

## Complexity Tracking

*No constitution violations — this section is intentionally empty.*
