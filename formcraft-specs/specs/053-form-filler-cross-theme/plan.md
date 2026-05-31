# Implementation Plan: Form Filler Cross-Theme (F053)

**Branch**: `053-form-filler-cross-theme` | **Date**: 2026-06-01 | **Spec**: [spec.md](./spec.md)
**Input**: Complete the Form Filler feature across both classic desk (`/desk/fill/:templateId`) and new theme (`/ui/desk/fill/:templateId`) with real data binding, conditional logic, signature field, draft management, submission confirmation, and cross-cutting quality gates.

---

## Summary

The classic desk `FillComponent` is largely complete (634 lines). The new-theme `FormFillerComponent` is a partial stub (261 lines) missing conditional logic, tafqeet, signature field, i18n, draft version checks, ngOnDestroy auto-save, error summary, and a dedicated submission-confirmation screen. This plan focuses on completing the new-theme component to full parity, adding `DraftService.listDrafts()`, creating `SubmissionConfirmedComponent`, and verifying the classic desk against all spec requirements.

---

## Technical Context

**Language/Version**: TypeScript / Angular 19 (frontend), Python 3.12 / FastAPI (backend)
**Primary Dependencies**: Angular Material, Angular Reactive Forms, ngx-translate, RxJS, `ConditionEngineService`, `ValidationService`, `FillerTafqeetService`, `AutoFillService`, `DraftService`, `SubmissionService`, `SignaturePadComponent`, `RoleGuard` — all `providedIn: 'root'` or standalone, no new dependencies
**Storage**: Supabase PostgreSQL — `drafts` table (018_drafts.sql), `submissions` table (017_submissions.sql); no schema changes required
**Testing**: Angular/Karma (unit + component tests); pytest (backend contract tests)
**Target Platform**: Web browser (desktop + mobile)
**Project Type**: Web application — Angular 19 frontend + FastAPI backend (polyrepo)
**Performance Goals**: SC-003 validation ≤ 300ms; SC-004 condition visibility ≤ 200ms; SC-007 draft auto-save ≤ 2s background; SC-008 submission response ≤ 3s
**Constraints**: Zero hardcoded mock data; RTL-first; all i18n keys via ngx-translate; RoleGuard already applied to all form-filler routes
**Scale/Scope**: Up to 100 fields per template; operators fill multiple forms per day; single-user draft ownership (no concurrent editing)

---

## Constitution Check

| Principle | Status | Notes |
|---|---|---|
| I. Arabic-First RTL-Native | REQUIRED | All new strings must use ngx-translate keys; RTL layout verified; signature pad label uses `dir="auto"` |
| II. Pixel-Perfect Print Fidelity | N/A | Form filling does not affect PDF layout |
| III. AI Suggestion Never Auto-Apply | N/A | No AI in form filling |
| IV. Deterministic Over Probabilistic | REQUIRED | `ValidationService.getValidatorFn(element)` must be called for every field; country validators take precedence |
| V. Test-First Development | REQUIRED | All new components and service methods require tests written first |
| VI. Normalized Data Model | PASS | No schema changes; existing normalized tables used |
| VII. Translation-Key Architecture | REQUIRED | Remove all hardcoded Arabic strings from `FormFillerComponent` (new-theme); use translate keys |
| VIII. Security and Auditability | PASS | `RoleGuard` already on both routes; backend `AuditLogger` fires on draft-save and submission |
| IX. Simplicity and YAGNI | REQUIRED | No new services; reuse all existing `providedIn: 'root'` services |

**No violations. Gate passed.**

---

## Project Structure

### Documentation (this feature)
```text
formcraft-specs/specs/053-form-filler-cross-theme/
├── spec.md               ✓ (clarified 2026-06-01)
├── plan.md               ✓ (this file)
├── research.md           ✓ (generated 2026-06-01)
├── data-model.md         ✓ (generated 2026-06-01)
├── contracts/
│   └── api-contracts.md  ✓ (generated 2026-06-01)
└── tasks.md              (Phase 2 output — /speckit.tasks)
```

### Source Code — Frontend
```text
formcraft-frontend/src/app/
├── features/
│   ├── desk/
│   │   ├── services/
│   │   │   ├── form-filler.service.ts       MODIFY — extend TemplateElement interface
│   │   │   ├── draft.service.ts             MODIFY — add listDrafts() method
│   │   │   └── submission.service.ts        VERIFY — confirm SubmissionResponse shape
│   │   ├── components/
│   │   │   ├── signature-pad/
│   │   │   │   └── signature-pad.component.ts  VERIFY (no changes expected)
│   │   │   └── draft-list/
│   │   │       └── draft-list.component.ts  MODIFY — accept draft[] input, use listDrafts
│   │   └── fill/
│   │       └── fill.component.ts            VERIFY against spec (classic desk)
│   └── ui-redesign/
│       └── desk/
│           ├── form-filler.component.ts     MODIFY — primary implementation target
│           ├── form-filler.component.html   MODIFY — add condition/tafqeet/signature rendering
│           ├── form-filler.component.scss   MODIFY — signature pad + error summary styles
│           ├── submission-confirmed.component.ts   CREATE — new confirmation screen
│           └── dashboard.component.ts       VERIFY — ensure My Drafts panel wired
└── core/
    └── i18n/
        └── assets/i18n/
            ├── ar.json                      MODIFY — add missing form-filler keys
            └── en.json                      MODIFY — add missing form-filler keys
```

### Source Code — Backend
```text
formcraft-backend/app/
├── api/routes/
│   └── drafts.py                            VERIFY — ensure GET /desk/drafts list endpoint exists
└── services/
    └── draft_service.py                     VERIFY — list_drafts() method
```

---

## Implementation Phases

### Phase 1 — Interface & Service Foundations
*Goal: fix the data contracts that all components depend on*

1. **Extend `TemplateElement` interface** (`form-filler.service.ts`):
   - Add `options`, `visible_when`, `required_when`, `tafqeet_enabled` to the interface
   - Verify backend `/desk/fill/{templateId}` already returns these fields (they are stored on the Element entity)

2. **Add `DraftService.listDrafts()`** (`draft.service.ts`):
   - `GET /desk/drafts` → `Observable<DraftResponse[]>`
   - Backend route must be verified/added in `drafts.py`

3. **Verify `SubmissionService.submit()`** shape matches `SubmissionResponse` contract

### Phase 2 — New-Theme FormFillerComponent Completion
*Goal: bring new-theme from stub to full spec parity*

4. **Wire `ConditionEngineService`**:
   - Call `conditionEngineService.initialize(flatElements, formGroup)` after `buildFormFromTemplate()`
   - Subscribe to `visibilityChanged$` → update `visibleKeys: Set<string>`
   - Subscribe to `requiredChanged$` → update `requiredKeys: Set<string>`
   - Filter submission payload to visible keys only

5. **Wire `FillerTafqeetService`**:
   - For each element with `tafqeet_enabled === true`, subscribe to `formGroup.get(key).valueChanges`
   - Call `tafqeetService.compute(value)` → store result in `tafqeetValues: Map<string, string>`
   - Template renders tafqeet text below the field

6. **Integrate `SignaturePadComponent`**:
   - Import `SignaturePadComponent` in standalone imports
   - Add `case 'signature'` to the field renderer template
   - On `(confirmed)` event, `formGroup.get(element.key).setValue(base64PngString)`
   - On `(cleared)` event, `formGroup.get(element.key).setValue(null)`

7. **Add Error Summary Panel**:
   - Collect all touched invalid controls with their labels
   - Render as a Material card above the submit button, only when form is submitted-and-invalid

8. **Fix i18n — remove hardcoded strings**:
   - Replace all hardcoded Arabic snackbar messages with `translate.instant('desk.form_filler.*')` keys
   - Replace hardcoded section titles with `translate.instant('desk.page_number', { n: pageIndex + 1 })`
   - Add all keys to `ar.json` and `en.json`

9. **Add `ngOnDestroy` auto-save**:
   - Call `saveDraft()` in `ngOnDestroy()` if form is dirty and not submitted

10. **Add draft version mismatch dialog**:
    - After `loadDraft()`, compare `draft.template_version` with `template.version`
    - If mismatch, open `MatDialog` with `VersionWarningComponent` (already exists in classic desk)

11. **Fix post-submission navigation**:
    - Navigate to `/ui/desk/submission-confirmed` with Router `state` containing `{ referenceNumber, templateName, submittedAt }`
    - Remove 2-second `setTimeout`

### Phase 3 — Submission Confirmed Screen
*Goal: dedicated confirmation screen for new-theme*

12. **Create `SubmissionConfirmedComponent`**:
    - Route: `/ui/desk/submission-confirmed` (lazy-loaded standalone, guarded by `RoleGuard ['admin', 'branch_manager', 'operator']`)
    - Reads `router.getCurrentNavigation().extras.state` for `SubmissionConfirmedState`
    - Displays: reference number (large, prominent), template name, submission timestamp
    - CTA: "Back to Desk" → `router.navigate(['/ui/desk'])`
    - Edge case: if state is null (direct navigation), redirect to `/ui/desk`

### Phase 4 — Customer Auto-Fill (P2)
*Goal: complete the customer picker flow in new-theme*

13. **Complete `openCustomerPicker()` in new-theme**:
    - Open a `MatDialog` with a search-and-select component
    - On selection, call `CustomerService.getAutoFillData(customerId, templateId)`
    - Call `AutoFillService.executeAutoFill(mappings, formGroup)` with the result

### Phase 5 — Classic Desk Verification
*Goal: confirm classic FillComponent satisfies all P1 spec requirements*

14. **Audit `FillComponent` against FR-001 to FR-038**:
    - Check: ConditionEngine wired ✓ (import present)
    - Check: tafqeet wired ✓ (import present)
    - Check: SignaturePadComponent used for signature fields
    - Check: version mismatch dialog (`VersionWarningComponent` import)
    - Check: ngOnDestroy draft save
    - Check: submission payload uses `visibleKeys` filter
    - Check: i18n compliance (no hardcoded strings)
    - Document any gaps and fix

### Phase 6 — My Drafts Panel in New-Theme Dashboard
*Goal: surface DraftListComponent in the new-theme shell*

15. **Wire draft list in new-theme `DashboardComponent`**:
    - Call `DraftService.listDrafts()` on init
    - Pass to `DraftListComponent` or equivalent inline panel
    - Confirm `DraftListComponent.openDraft()` uses `/ui/desk/fill/:templateId?draftId=:id` for new-theme context

---

## Complexity Tracking

No constitution violations. No complexity justification required.

---

## Constitution Check (Post-Design)

All constitution principles maintained:
- **I (RTL)**: All new components use `dir="auto"` where needed; all strings use translate keys
- **IV (Deterministic validators)**: `ValidationService.getValidatorFn(element)` called for every field
- **V (Test-First)**: Tests written before implementation in each phase
- **VII (Translation keys)**: No hardcoded strings in any new or modified component
- **VIII (Security/Audit)**: `RoleGuard` on new route; backend audit logging already in place
- **IX (YAGNI)**: Zero new services; all reuse existing `providedIn: 'root'` infrastructure

**Gate: PASSED**
