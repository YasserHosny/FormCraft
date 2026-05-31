# Contract: Draft Concurrency Detection (F052)

**Date**: 2026-06-01

## Protocol

```
LOAD: component.draftUpdatedAt = response.updated_at

SAVE (update):
  call DraftService.updateDraft(draftId, fieldValues)
  on response:
    if new Date(response.updated_at) > new Date(draftUpdatedAt)
      → show toast: translate('DESK.FILL.DRAFT_CONCURRENT_MODIFIED')
    component.draftUpdatedAt = response.updated_at  // always update
```

## Semantics

- **Last-write-wins**: save always proceeds, warning is informational only
- **No locking**: no backend lock record or ETag required
- **Backend**: `DraftResponse.updated_at` auto-maintained by Supabase
- **Scope**: applies to `updateDraft()` only — `saveDraft()` (new draft) has no concurrency
