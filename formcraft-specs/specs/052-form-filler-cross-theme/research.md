# Research: Form Filler Cross-Theme (F052)

**Date**: 2026-06-01 | **Branch**: `052-form-filler-cross-theme`

## Existing Implementation Gaps (as of 2026-06-01)

Audit of `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`:

| Gap | Spec Ref | Already Done by F053? |
|-----|----------|-----------------------|
| `ConditionEngineService.initialize()` call | FR-013/014 | ✅ Done |
| `visibilityChanged$` subscription | FR-013 | ✅ Done |
| `requiredChanged$` subscription | FR-014 | ✅ Done |
| `hasUnsavedChanges` tracking | FR-017 | ✅ Done |
| `ngOnDestroy` auto-saves draft | FR-017 | ✅ Done |
| Template version mismatch check | FR-020 | ✅ Done (snackbar) |
| `syncHiddenControls()` method | FR-015 | ❌ Missing |
| Controls not disabled on hide | FR-015 | ❌ Missing |
| Submission retry (3x backoff) | FR-047 | ❌ Missing |
| `draftUpdatedAt` concurrency detection | FR-046 | ❌ Missing |
| Draft expiry check (`expires_at`) | Clarification 2026-06-01 | ❌ Missing |
| Error summary panel | FR-012 | ❌ Missing |
| Hardcoded `templateName`/`templateCode` defaults | FR-033 | ❌ Missing |
| Hardcoded `صفحة ${n}` section labels | Constitution VII | ❌ Missing |
| Hardcoded snackbar strings (Arabic) | Constitution VII | ❌ Missing |
| `getTemplate()` missing `takeUntil` | Best practice | ❌ Missing |
| `formGroup.valid` ignores hidden fields | FR-011/015 | ❌ Missing |
| Version mismatch uses snackbar, not dialog | FR-020 | ❌ Missing (should use VersionWarningComponent) |
| Route guard applied | FR-042 | ✅ Done in routes file |
| Persistent error banner on retry exhaustion | FR-047 | ❌ Missing |

## Key Decisions

### Route Guard
**Decision**: `RoleGuard` with `['admin', 'branch_manager', 'operator']` already on `/ui/desk/fill/:templateId`.  
**Rationale**: Confirmed in `formcraft-frontend/src/app/features/ui-redesign/ui-redesign.routes.ts` — no change needed.

### Hidden-Field Exclusion
**Decision**: `ctrl.disable({ emitEvent: false })` for invisible fields; `ctrl.enable()` for visible.  
**Rationale**: Angular's `formGroup.value` auto-excludes disabled controls. Canonical pattern. Matches FR-015.

### Submission Retry
**Decision**: `retry({ count: 3, delay: (_, i) => timer(Math.pow(2, i-1) * 1000) })` from RxJS 7.  
**Rationale**: Angular 19 ships RxJS 7. No extra deps. 1s/2s/4s = max 7s total.

### Optimistic Concurrency
**Decision**: Store `draftUpdatedAt` from load. On save response, if `response.updated_at > draftUpdatedAt` → toast.  
**Rationale**: `DraftResponse.updated_at` already available. No new endpoint. Last-write-wins.

### Draft Expiry
**Decision**: Check `new Date(draft.expires_at) < new Date()` on load → redirect to `/ui/desk`.  
**Rationale**: `DraftResponse.expires_at` available. Soft expiry — frontend must enforce.

### Version Mismatch Dialog
**Decision**: Replace snackbar with `VersionWarningComponent` dialog (already used by classic desk).  
**Rationale**: `VersionWarningComponent` exists at `features/desk/components/version-warning/`. Reuse over duplication.

### I18n Namespace
**Decision**: `DESK.FILL.*` namespace in `ar.json` / `en.json`.  
**Rationale**: Matches existing `DESK.*` namespace in the project.
