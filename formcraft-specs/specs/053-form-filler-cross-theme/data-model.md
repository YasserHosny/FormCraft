# Data Model: Form Filler Cross-Theme (F053)

**Branch**: `053-form-filler-cross-theme` | **Date**: 2026-06-01

---

## Existing Tables (no schema changes needed)

### `drafts`
```sql
id               UUID PK  DEFAULT gen_random_uuid()
template_id      UUID FK → templates(id) ON DELETE CASCADE
template_version INT  NOT NULL
operator_id      UUID FK → auth.users(id) ON DELETE CASCADE
org_id           UUID FK → organizations(id) ON DELETE CASCADE
field_values     JSONB NOT NULL DEFAULT '{}'
completion_percent INT NOT NULL DEFAULT 0
name             TEXT
expires_at       TIMESTAMPTZ DEFAULT now() + 7 days
created_at       TIMESTAMPTZ
updated_at       TIMESTAMPTZ
```
RLS: Operators manage only their own drafts (`operator_id = auth.uid()`).

### `submissions`
```sql
id               UUID PK  DEFAULT gen_random_uuid()
template_id      UUID FK → templates(id) ON DELETE CASCADE
template_version INT  NOT NULL
operator_id      UUID FK → auth.users(id) ON DELETE CASCADE
org_id           UUID FK → organizations(id) ON DELETE CASCADE
field_values     JSONB NOT NULL DEFAULT '{}'
reference_number TEXT NOT NULL UNIQUE
created_at       TIMESTAMPTZ
```
RLS: Operators can INSERT own submissions and SELECT org submissions.

---

## TypeScript Interfaces (frontend)

### Extended `TemplateElement` (in `form-filler.service.ts`)
```typescript
export interface TemplateElement {
  id: string;
  key: string;
  type: 'text' | 'number' | 'date' | 'select' | 'checkbox' | 'textarea' | 'signature';
  label_ar: string;
  label_en: string;
  required: boolean;
  direction: 'rtl' | 'ltr' | 'auto';
  sort_order: number;
  validation: {
    pattern?: string;
    min?: number;
    max?: number;
    custom_rule?: string;
  } | null;
  formatting: Record<string, any> | null;
  // Added for F053 (must be included in template payload):
  options?: Array<{ value: string; label_ar: string; label_en: string }>;
  visible_when?: {
    conditions: Array<{ field: string; operator: string; value: string | number | boolean | null }>;
    logic: 'AND';
  } | null;
  required_when?: {
    conditions: Array<{ field: string; operator: string; value: string | number | boolean | null }>;
    logic: 'AND';
  } | null;
  tafqeet_enabled?: boolean;
}
```

### `FillTemplate` (no changes — already correct)
```typescript
export interface FillTemplate {
  id: string;
  name: string;
  version: number;
  language: string;
  country: string;
  is_deprecated: boolean;
  pages: TemplatePage[];  // TemplatePage contains elements: TemplateElement[]
}
```

### `DraftResponse` (no changes — already correct in `DraftService`)
```typescript
export interface DraftResponse {
  id: string;
  template_id: string;
  template_version: number;
  operator_id: string;
  org_id: string;
  field_values: Record<string, any>;
  completion_percent: number;
  name: string | null;
  expires_at: string;
  created_at: string;
  updated_at: string;
}
```

### `SubmissionResponse` (verify in `SubmissionService`)
```typescript
export interface SubmissionResponse {
  id: string;
  reference_number: string;
  template_id: string;
  template_version: number;
  created_at: string;
}
```

### New: `SubmissionConfirmedState` (route state for confirmation screen)
```typescript
export interface SubmissionConfirmedState {
  referenceNumber: string;
  templateName: string;
  submittedAt: string;
}
```

---

## State Transitions

### Draft lifecycle
```
(new form) → create_draft → in_progress
in_progress → update_draft → in_progress   (repeated auto-saves)
in_progress → submit → submitted (draft archived/deleted by backend)
in_progress → expires_at reached → expired
```

### Submission lifecycle
```
submit → Pending (if template has approval workflow)
submit → Approved (if template has no approval workflow)
```

---

## API Contracts

### Existing endpoints (no changes needed)
| Method | Path | Used by |
|--------|------|---------|
| GET | `/desk/fill/{templateId}` | `FormFillerService.getTemplate()` |
| POST | `/desk/drafts` | `DraftService.saveDraft()` |
| PATCH | `/desk/drafts/{draftId}` | `DraftService.updateDraft()` |
| GET | `/desk/drafts/{draftId}` | `DraftService.getDraft()` |
| POST | `/desk/submissions/{templateId}` | `SubmissionService.submit()` |

### Endpoint to verify/add
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/desk/drafts` | `DraftService.listDrafts()` — needed for "My Drafts" panel |
| GET | `/desk/customers/search?q=` | `CustomerService` — auto-fill search |
| GET | `/desk/customers/{id}/auto-fill?template_id=` | `CustomerService.getAutoFillData()` |

---

## Form State Model (in-memory, not persisted)

```typescript
interface FormFillerState {
  template: FillTemplate;
  draftId: string | null;
  formGroup: FormGroup;          // keyed by element.key
  visibleKeys: Set<string>;      // driven by ConditionEngineService
  requiredKeys: Set<string>;     // driven by ConditionEngineService
  tafqeetValues: Map<string, string>;  // key → Arabic word form
  loading: boolean;
  submitting: boolean;
  savingDraft: boolean;
}
```
