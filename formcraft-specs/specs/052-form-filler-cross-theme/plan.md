# Implementation Plan: Form Filler Cross-Theme (F052)

**Branch**: `052-form-filler-cross-theme` | **Date**: 2026-06-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/formcraft-specs/specs/052-form-filler-cross-theme/spec.md`

## Summary

Complete the new-theme `FormFillerComponent` (`ui-redesign/desk/form-filler.component.ts`) — a standalone Angular 19 component that already has a service-injection skeleton but is missing: `syncHiddenControls()` wiring, submission retry, optimistic draft concurrency detection, draft expiry handling, template-version mismatch dialog, visible-field-aware validation guard, i18n key replacement, and error summary panel. The classic desk `FillComponent` continues unchanged; this plan targets only the new-theme component and its i18n assets.

## Technical Context

**Language/Version**: TypeScript 5.4 (Angular 19) — frontend only. No new backend work required.
**Primary Dependencies**: Angular Material, RxJS, ngx-translate, ReactiveFormsModule, Angular Router
**Storage**: Supabase PostgreSQL — accessed through existing REST services (no schema changes)
**Testing**: Karma + Jasmine (Angular component spec), existing `form-filler.component.spec.ts`
**Target Platform**: Modern desktop browser (Chrome/Firefox/Safari); RTL + LTR
**Project Type**: Web application — standalone Angular component completing an in-progress skeleton
**Performance Goals**: Validation ≤ 300ms post-blur; condition evaluation ≤ 200ms; auto-save ≤ 2s non-blocking; submission round-trip ≤ 3s (incl. up to 3 retries at 7s total)
**Constraints**: RTL-first layout, `dir="auto"` on text inputs, zero hardcoded strings, no new API endpoints, no new backend migrations
**Scale/Scope**: Single form filler view; up to 50 fields per template; concurrent multi-tab session scenario handled via last-write-wins + stale-read toast

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arabic-First, RTL-Native | ✅ PASS | `dir="auto"` required on all text inputs; `label_ar`/`label_en` bindings use `currentLanguage` |
| II. Pixel-Perfect Print Fidelity | ✅ N/A | Print delegated to classic desk — no PDF in this component |
| III. AI Suggestion, Never Auto-Apply | ✅ N/A | No AI in form filler |
| IV. Deterministic Over Probabilistic | ✅ PASS | `ValidationService.getValidatorFn()` provides deterministic validators |
| V. Test-First Development | ⚠️ REQUIRED | `form-filler.component.spec.ts` exists; must extend with failing tests before each gap |
| VI. Normalized Data Model | ✅ PASS | Draft uses `updated_at` from backend — no embedded doc changes |
| VII. Translation-Key Architecture | ⚠️ REQUIRED | Hardcoded Arabic strings must be replaced with i18n keys before merge |
| VIII. Security & Auditability | ✅ PASS | `RoleGuard` with `['admin', 'branch_manager', 'operator']` already applied on route |
| IX. Simplicity & YAGNI | ✅ PASS | P2 features deferred; no new services or modules |

**Gate result**: PASS with two mandatory pre-implementation actions (Principles V and VII).

## Project Structure

### Documentation (this feature)

```text
formcraft-specs/specs/052-form-filler-cross-theme/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   ├── form-filler-component.contract.md
│   └── draft-service-concurrency.contract.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (affected files)

```text
formcraft-frontend/src/app/features/ui-redesign/desk/
├── form-filler.component.ts        ← Primary implementation target
├── form-filler.component.html      ← Template (dir="auto", i18n keys, retry banner)
├── form-filler.component.scss      ← RTL layout adjustments if needed
└── form-filler.component.spec.ts   ← Tests extended before each task

formcraft-frontend/src/assets/i18n/
├── ar.json                         ← Add DESK.FILL.* keys (Arabic)
└── en.json                         ← Add DESK.FILL.* keys (English)
```

**Structure Decision**: Single standalone component extending the existing skeleton. No new services, no new modules.

## Phase 0 Findings

See [research.md](research.md) for full research output.

**Key resolved unknowns:**

| Unknown | Decision | Rationale |
|---------|----------|-----------|
| Route guard scope | `RoleGuard` already applied; roles `['admin', 'branch_manager', 'operator']` | Discovered in `ui-redesign.routes.ts` — no change needed |
| Optimistic concurrency detection | Compare `DraftResponse.updated_at` on load vs. server response on save | `DraftResponse` already exposes `updated_at` |
| Submission retry | RxJS `retry({ count: 3, delay })` with 1s/2s/4s delays | Standard RxJS 7 pattern |
| Condition engine wiring | Already added by parallel F053 work; `syncHiddenControls()` still missing | Remaining gap: disable/enable controls on visibility change |
| Hidden-field exclusion | `ctrl.disable()` → Angular's `formGroup.value` auto-excludes | Angular canonical pattern |
| I18n replacement | `DESK.FILL.*` namespace in `ar.json`/`en.json` | Matches existing namespace pattern |

## Phase 1 Artifacts

See [data-model.md](data-model.md), [contracts/](contracts/), and [quickstart.md](quickstart.md).
