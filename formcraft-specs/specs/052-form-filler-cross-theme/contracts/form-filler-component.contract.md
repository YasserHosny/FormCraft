# Contract: FormFillerComponent (New Theme — F052)

**File**: `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`
**Route**: `/ui/desk/fill/:templateId` (guard: `['admin', 'branch_manager', 'operator']`)

## Route Inputs

| Source | Name | Required | Description |
|--------|------|----------|-------------|
| Route param | `templateId` | Yes | Published template ID |
| Query param | `draftId` | No | Existing draft to resume |

## `ngOnInit` Sequence

1. Extract `templateId` → if absent: `error = translate('DESK.FILL.NO_TEMPLATE_ID')`
2. `getTemplate(templateId)` → on success: build form, initialize condition engine, subscribe visibility/required
3. If `draftId`: call `loadDraft(draftId)`
4. On template load error: `error = translate('DESK.FILL.TEMPLATE_LOAD_FAILED')`

## `loadDraft(draftId)` Contract

1. Check `expires_at < now` → snackbar + navigate `/ui/desk` + return
2. Check `template_version !== template.version` → open `VersionWarningComponent` dialog
3. Store `draftUpdatedAt = draft.updated_at`
4. `formGroup.patchValue(draft.field_values)` → `loading = false`

## `submitForm()` Contract

```
Pre: isFormValid() === true, submitting === false
Retry: 3 attempts at 1s / 2s / 4s delays
Post (success): snackbar with reference_number, navigate /ui/desk after 2s
Post (exhausted): showRetryBanner = true, submissionError = translate('DESK.FILL.SUBMIT_RETRY_EXHAUSTED')
```

## `saveDraft()` Contract

```
Post (new draft success): draftId = response.id, draftUpdatedAt = response.updated_at
Post (update success): if response.updated_at > draftUpdatedAt → concurrent-modification toast
                       draftUpdatedAt = response.updated_at
Post (failure): snackbar translate('DESK.FILL.DRAFT_SAVE_FAILED')
```

## `syncHiddenControls(visibleKeys)` Contract

```
For each key in formGroup.controls:
  key NOT in visibleKeys → ctrl.disable({ emitEvent: false })
  key IN visibleKeys     → ctrl.enable({ emitEvent: false })
```

## Invariants

- `formGroup.value` (not `getRawValue()`) used for submission — excludes disabled controls
- `isFormValid()` only checks `visibleFields` keys — hidden fields never block submission
- Zero hardcoded UI strings — all via `TranslateService`
