# Research: Form Filler Cross-Theme Implementation (F053)

**Branch**: `053-form-filler-cross-theme` | **Date**: 2026-06-01

---

## Decision: Signature Field Rendering

**Decision**: Reuse existing `SignaturePadComponent` (`formcraft-frontend/src/app/features/desk/components/signature-pad/signature-pad.component.ts`)

**Rationale**: The component is already a standalone Angular component with HTML5 canvas drawing, touch/mouse event handling, clear/confirm actions, base64 PNG serialisation, required validation, and i18n (`signature.clear`, `signature.confirm`, `signature.required` keys). It must be imported by the form-field renderer — no new component needed.

**Alternatives considered**: `signature_pad` npm library (rejected — external dependency when native canvas already implemented), typed-name approach (rejected — insufficient for legal/bank documents per clarification Q1).

---

## Decision: Route Authorization

**Decision**: Reuse existing `RoleGuard` with `data: { roles: ['admin', 'branch_manager', 'operator'] }`.

**Rationale**: Both `/ui/desk/fill/:templateId` (new-theme) and `/desk/fill/:templateId` (classic) are ALREADY guarded with `RoleGuard` checking `['admin', 'branch_manager', 'operator']`. This satisfies the clarification (operators + admins). Designer read-verify mode is out of scope for this feature per YAGNI; no route changes needed.

**Alternatives considered**: New `FillerGuard` (rejected — `RoleGuard` already handles role array; duplication is prohibited by constitution), adding designer role (deferred — not requested in spec).

---

## Decision: Draft Discovery (My Drafts Panel)

**Decision**: Add `DraftService.listDrafts(templateId?: string)` method; wire `DraftListComponent` into the new-theme dashboard header.

**Rationale**: `DraftListComponent` exists in `formcraft-frontend/src/app/features/desk/components/draft-list/`. The component already navigates to `/desk/fill/{template_id}?draft={id}`. However, `DraftService` only exposes `getDraft(id)` — a `GET /desk/drafts` list endpoint must be added (or confirmed on the backend). The classic desk already shows drafts on the dashboard. New-theme dashboard needs the same panel.

**Alternatives considered**: URL-only draft resumption (rejected — per clarification Q3, operators must discover drafts without knowing raw IDs).

---

## Decision: Post-Submission Navigation

**Decision**: Create a new `SubmissionConfirmedComponent` in `formcraft-frontend/src/app/features/ui-redesign/desk/submission-confirmed.component.ts` for the new-theme flow. Route: `/ui/desk/submission-confirmed`. Classic desk uses snackbar + history redirect (already implemented).

**Rationale**: New-theme spec requires a dedicated confirmation screen (SC-015). The current implementation uses a 2-second `setTimeout → router.navigate(['/ui/desk'])`, which doesn't show the reference number prominently. A dedicated screen is needed. Public portal has a similar `ConfirmationPageComponent` but it is portal-specific and should not be reused directly.

**Alternatives considered**: Enhanced snackbar (rejected — not "prominent" per clarification Q4), reusing portal confirmation (rejected — different context, different data shape).

---

## Decision: Audit Logging

**Decision**: Backend-side audit logging only. No frontend `AuditLogService` call needed.

**Rationale**: The backend `DraftService.create_draft()` already calls `AuditLogger.log_event(action="DRAFT_SAVED", resource_type="draft")`. Backend `SubmissionService` calls `AuditLogger` on successful creation. The frontend has no direct audit access — this is intentional (audit happens server-side so it cannot be spoofed). FR-025a/b describe server-side behaviour, not a frontend service call.

**Alternatives considered**: Frontend audit client (rejected — creates two audit paths; server-side is already the authoritative trail per constitution principle VIII).

---

## Decision: ConditionEngineService Integration in New Theme

**Decision**: Call `ConditionEngineService.initialize(flatElements, formGroup)` in `buildFormFromTemplate()` and subscribe to `visibilityChanged$` / `requiredChanged$` in `ngOnInit()`.

**Rationale**: `ConditionEngineService` is `providedIn: 'root'`, already used in classic desk `FillComponent`. The new-theme component currently calls `validationService.getValidatorFn()` but never calls `conditionEngineService.initialize()`. This means all conditional logic is silently skipped.

---

## Decision: Interface Extension — TemplateElement

**Decision**: Extend `TemplateElement` in `form-filler.service.ts` to add `visible_when`, `required_when`, `tafqeet_enabled`, `options`.

**Rationale**: The current `TemplateElement` interface is missing these fields used by `ConditionEngineService` and `FillerTafqeetService`. The `options` field is also needed for select/dropdown rendering. These are fetched as part of the template payload.

---

## Decision: i18n — Remove Hardcoded Strings from New Theme Form Filler

**Decision**: Replace all hardcoded Arabic strings in `form-filler.component.ts` with `translate.instant()` or `| translate` pipe calls.

**Rationale**: Current implementation has multiple hardcoded Arabic strings: snackbar messages (`'تم حفظ المسودة بنجاح'`), section titles (`صفحة ${sectionNumber}`), shortcuts. This violates Constitution principle VII (Translation-Key Architecture).

---

## Implementation Gap Summary

| Area | Status | Gap |
|---|---|---|
| `SignaturePadComponent` | EXISTS | Needs import in field renderer |
| `ConditionEngineService` | EXISTS | Not wired in new-theme component |
| `FillerTafqeetService` | EXISTS | Not wired in new-theme component |
| `DraftService` | EXISTS | Missing `listDrafts()` method |
| `SubmissionConfirmedComponent` | MISSING | Needs creation (new-theme only) |
| `TemplateElement` interface | PARTIAL | Missing `visible_when`, `required_when`, `tafqeet_enabled`, `options` |
| New-theme form-filler i18n | PARTIAL | Multiple hardcoded Arabic strings |
| New-theme draft version check | MISSING | `template_version` mismatch warning not implemented |
| New-theme `ngOnDestroy` auto-save | MISSING | `saveDraft()` not called in `ngOnDestroy()` |
| New-theme error summary panel | MISSING | No error list component rendered |
| Classic desk | LARGELY COMPLETE | 634-line `FillComponent` — verify against spec |
| Backend routes | EXISTS | `GET /desk/drafts` list endpoint needs verification |
