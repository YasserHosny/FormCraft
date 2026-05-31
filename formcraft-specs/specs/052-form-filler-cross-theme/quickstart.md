# Quickstart: Form Filler Cross-Theme (F052)

**Date**: 2026-06-01

## What This Feature Does

Completes the new-theme `FormFillerComponent` at `/ui/desk/fill/:templateId`. The classic desk `/desk/fill/:templateId` is unchanged.

## Affected Files

| File | Change |
|------|--------|
| `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` | Main implementation |
| `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.html` | dir="auto", retry banner, error summary |
| `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.spec.ts` | TDD tests (write first) |
| `formcraft-frontend/src/assets/i18n/ar.json` | DESK.FILL.* keys |
| `formcraft-frontend/src/assets/i18n/en.json` | DESK.FILL.* keys |

**No backend changes. No new services. No new modules.**

## Key Patterns

### Hidden Controls Sync
```typescript
private syncHiddenControls(visibleKeys: Set<string>): void {
  Object.keys(this.formGroup.controls).forEach(key => {
    const ctrl = this.formGroup.get(key)!;
    visibleKeys.has(key)
      ? ctrl.enable({ emitEvent: false })
      : ctrl.disable({ emitEvent: false });
  });
}
```

### Visible-Fields Validation Guard
```typescript
private isFormValid(): boolean {
  return Array.from(this.visibleFields).every(key => !this.formGroup.get(key)?.invalid);
}
```

### Submission Retry
```typescript
import { retry, timer } from 'rxjs';

this.submissionService.submit(...).pipe(
  retry({ count: 3, delay: (_, i) => timer(Math.pow(2, i - 1) * 1000) }),
  takeUntil(this.destroy$)
).subscribe({ next: onSuccess, error: onExhausted });
```

### Optimistic Concurrency
```typescript
// On draft load:
this.draftUpdatedAt = draft.updated_at;

// On save response:
if (new Date(response.updated_at) > new Date(this.draftUpdatedAt!)) {
  this.snackBar.open(this.translate.instant('DESK.FILL.DRAFT_CONCURRENT_MODIFIED'), '', { duration: 4000 });
}
this.draftUpdatedAt = response.updated_at;
```

## Running Tests
```bash
cd formcraft-frontend
ng test --include=form-filler.component.spec.ts
```

## Manual Test Checklist
- [ ] Template name/version from API (no hardcoded defaults)
- [ ] Section labels use i18n (no hardcoded Arabic)
- [ ] Hidden field excluded from submission payload
- [ ] Submit with missing visible required field → blocked + inline error
- [ ] 3 retry attempts on submit failure → persistent banner with Retry + Save as Draft
- [ ] Draft expiry → redirect to /ui/desk with toast
- [ ] Concurrent draft save → warning toast
- [ ] Version mismatch → VersionWarningComponent dialog
- [ ] All snackbar messages translated (AR + EN)
- [ ] Text inputs have dir="auto"
