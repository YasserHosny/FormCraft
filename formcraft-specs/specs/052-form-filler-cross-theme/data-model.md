# Data Model: Form Filler Cross-Theme (F052)

**Date**: 2026-06-01 | **Branch**: `052-form-filler-cross-theme`

No new database tables or migrations required. Feature operates entirely on existing backend entities.

## Draft Entity (Extended)

```typescript
// Existing interface in formcraft-frontend/src/app/features/desk/services/draft.service.ts
interface DraftResponse {
  id: string;
  template_id: string;
  template_version: number;  // compare to FillTemplate.version for mismatch
  operator_id: string;
  org_id: string;
  field_values: Record<string, any>;
  completion_percent: number;
  name: string | null;
  expires_at: string;        // check: new Date(expires_at) < new Date() → expired
  created_at: string;
  updated_at: string;        // used for optimistic concurrency detection
}

// State transitions (F052 clarification 2026-06-01):
// in_progress → submitted   (on SubmissionService.submit() success)
// in_progress → deleted     (explicit operator action)
// in_progress → expired     (client: expires_at < now; backend: 30-day inactivity)
```

## Component State (New Fields)

```typescript
// Add to FormFillerComponent:
draftUpdatedAt: string | null = null;  // last known draft.updated_at from backend
submitting = false;
savingDraft = false;
showRetryBanner = false;
submissionError: string | null = null;
tafqeetValues: Record<string, string> = {};  // P2: tafqeet display values
```

## I18n Keys (New — add to ar.json and en.json)

Namespace: `DESK.FILL.*`

| Key | Arabic | English |
|-----|--------|---------|
| `DESK.FILL.DRAFT_SAVED` | تم حفظ المسودة بنجاح | Draft saved successfully |
| `DESK.FILL.DRAFT_SAVE_FAILED` | فشل حفظ المسودة | Failed to save draft |
| `DESK.FILL.DRAFT_LOAD_FAILED` | فشل تحميل المسودة | Failed to load draft |
| `DESK.FILL.SUBMIT_SUCCESS` | تم إرسال النموذج برقم مرجعي {{ref}} | Form submitted — reference {{ref}} |
| `DESK.FILL.SUBMIT_FAILED` | فشل إرسال النموذج | Form submission failed |
| `DESK.FILL.SUBMIT_RETRY_EXHAUSTED` | تعذّر الإرسال بعد 3 محاولات | Submission failed after 3 attempts |
| `DESK.FILL.DRAFT_CONCURRENT_MODIFIED` | تم تعديل هذه المسودة في جلسة أخرى | This draft was modified in another session |
| `DESK.FILL.DRAFT_EXPIRED` | انتهت صلاحية هذه المسودة | This draft has expired |
| `DESK.FILL.REQUIRED_FIELDS_MISSING` | يرجى ملء جميع الحقول المطلوبة | Please fill all required fields |
| `DESK.FILL.TEMPLATE_VERSION_MISMATCH` | تحديث قالب متاح | Template update available |
| `DESK.FILL.TEMPLATE_LOAD_FAILED` | فشل تحميل النموذج | Failed to load template |
| `DESK.FILL.NO_TEMPLATE_ID` | لم يتم تحديد نموذج | No template specified |
| `DESK.FILL.PAGE_LABEL` | صفحة {{number}} | Page {{number}} |
| `DESK.FILL.RETRY` | إعادة المحاولة | Retry |
| `DESK.FILL.SAVE_AS_DRAFT` | حفظ كمسودة | Save as Draft |
