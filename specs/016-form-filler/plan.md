# Implementation Plan: Form Filler

**Branch**: `016-form-filler` | **Date**: 2026-05-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/016-form-filler/spec.md`

## Summary

Build the Form Filler (`/desk/fill/:templateId`) — the operator's primary daily tool for filling published templates. Implements Flow Layout rendering, live validation, tafqeet auto-computation, draft save/resume, PDF generation with filled data, submission records with reference numbers, and keyboard-optimized workflow. This is the most complex single feature in the platform and the core of the Form Desk experience.

## Technical Context

**Language/Version**: TypeScript / Angular 17 (frontend), Python 3.12 / FastAPI (backend)
**Primary Dependencies**: Angular Material (MatFormField, MatInput, MatSelect, MatRadio, MatCheckbox, MatDatepicker, MatButton, MatToolbar, MatSnackBar), Angular Reactive Forms, @ngx-translate/core
**Storage**: Supabase PostgreSQL (new `submissions` table, new `drafts` table, queries against `templates`, `pages`, `elements`)
**PDF**: Existing WeasyPrint renderer (extended to accept field_values)
**Validation**: Existing ValidatorRegistry (Egypt, Saudi, UAE validators), extended with client-side integration
**Testing**: Jasmine + Karma (frontend), pytest (backend)
**Performance Goals**: Form load < 1s, tafqeet < 200ms, validation < 100ms, draft save non-blocking, PDF < 3s
**Constraints**: Must use existing template data model (pages → elements with type, key, validation JSONB); must integrate with existing PDF renderer
**Scale/Scope**: Up to 50 elements per template, up to 5 pages per template

## Constitution Check

| Principle | Status | Notes |
|-----------|:------:|-------|
| I. Arabic-First, RTL-Native | PASS | Labels use i18n (label_ar/label_en based on user language); element direction property respected; validation errors bilingual |
| II. mm-Precision Guarantee | PASS | PDF output uses existing WeasyPrint renderer which guarantees mm positioning; Flow Layout is for data entry only (not print layout) |
| III. Deterministic-First Validation | PASS | Country-specific validators (deterministic regex) fire first; AI suggestions are not part of form filling (design-time only) |
| IV. Two-Mode Architecture | PASS | Form Filler lives under `/desk/fill/*`; only desk-mode users can access |
| V. Data Sovereignty & Multi-Tenancy | PASS | submissions and drafts tables require org_id + RLS; operators only see their own drafts |
| VI. Audit Everything | PASS | FORM_SUBMITTED audit event on every print; DRAFT_SAVED/DRAFT_DELETED events for draft lifecycle |
| VII. Template Versioning | PASS | Submissions reference exact template version; drafts warn on version mismatch |

## Project Structure

### Source Code

```text
formcraft-backend/
├── app/
│   ├── api/routes/
│   │   └── submissions.py              # NEW: POST /api/submissions, GET /api/submissions
│   │   └── drafts.py                   # NEW: CRUD /api/desk/drafts
│   ├── models/
│   │   └── submission.py               # NEW: Submission, Draft models
│   ├── schemas/
│   │   └── submission.py               # NEW: request/response schemas
│   └── services/
│       ├── submission_service.py        # NEW: submission creation, ref number generation
│       ├── draft_service.py             # NEW: draft CRUD, expiry, version check
│       └── pdf/
│           └── renderer.py             # UPDATE: accept field_values param for filled PDF
└── migrations/
    ├── 017_submissions.sql              # NEW: submissions table
    └── 018_drafts.sql                   # NEW: drafts table

formcraft-frontend/
├── src/app/
│   ├── features/
│   │   └── desk/
│   │       ├── fill/
│   │       │   ├── fill.component.ts           # NEW: main form filler container
│   │       │   ├── fill.component.html         # NEW: form layout template
│   │       │   ├── fill.component.scss         # NEW: flow layout styles
│   │       │   └── fill.module.ts              # NEW: FormFillerModule
│   │       ├── components/
│   │       │   ├── field-renderer/             # NEW: dynamic field component factory
│   │       │   ├── tafqeet-field/              # NEW: read-only auto-computed field
│   │       │   ├── form-toolbar/               # NEW: action bar
│   │       │   ├── error-summary/              # NEW: validation error banner
│   │       │   └── version-warning/            # NEW: draft version mismatch dialog
│   │       └── services/
│   │           ├── form-filler.service.ts      # NEW: form state management
│   │           ├── validation.service.ts       # NEW: client-side validation logic
│   │           ├── tafqeet.service.ts          # NEW: tafqeet API integration
│   │           ├── draft.service.ts            # NEW: draft save/resume
│   │           └── submission.service.ts       # NEW: print + submit
│   └── shared/
│       └── validators/                         # NEW: Angular validator adapters
│           ├── required.validator.ts
│           ├── pattern.validator.ts
│           └── country.validator.ts
└── src/assets/i18n/
    ├── ar.json                                 # ADD: filler.* keys
    └── en.json                                 # ADD: filler.* keys
```

## Phase 0: Research

**Decision 1**: Angular Reactive Forms vs. Template-Driven Forms.
- **Chosen**: Reactive Forms (FormGroup + FormControl per element).
- **Rationale**: Dynamic form generation (fields defined by template data, not hardcoded HTML) requires programmatic form construction. Reactive Forms enable dynamic FormControl creation, custom validators, and valueChanges subscriptions for tafqeet. Template-driven forms are too static.

**Decision 2**: Field rendering strategy — one component per type vs. dynamic component.
- **Chosen**: Single FieldRendererComponent with `[ngSwitch]` on element.type.
- **Rationale**: 11 element types mapped to ~7 unique Material controls (text/number/date → mat-input variants; dropdown → mat-select; radio → mat-radio-group; checkbox → mat-checkbox; tafqeet → read-only display; image/QR/barcode → special). A switch is simpler than ComponentFactoryResolver for this bounded set.

**Decision 3**: Validation execution — client-only vs. client+server.
- **Chosen**: Client-side validation on blur with server-side re-validation before submission.
- **Rationale**: Instant feedback requires client-side. Server-side re-validation on submit is a safety net (prevents API manipulation). Country validators are simple regex — can run in both environments. The ValidatorRegistry pattern already exists server-side; we mirror it client-side.

**Decision 4**: Tafqeet computation — client-side vs. API call.
- **Chosen**: API call to existing `POST /api/tafqeet/preview` endpoint, debounced at 200ms.
- **Rationale**: The TafqeetConverter already handles all edge cases (currency names, decimal handling, overflow). Duplicating 500+ lines of Arabic number-to-words logic client-side would be fragile and violate DRY. The API call is lightweight (< 50ms server-side). Debounce prevents excess calls during fast typing.

**Decision 5**: Draft storage and auto-save.
- **Chosen**: Server-side `drafts` table with auto-save via debounced PATCH every 60 seconds.
- **Rationale**: Constitution V requires server-side persistence for data sovereignty. Auto-save uses the same PATCH endpoint as manual save — just triggered by a timer. Non-blocking: fire-and-forget with retry on failure.

**Decision 6**: Reference number generation.
- **Chosen**: PostgreSQL sequence per (org_id, year, month) — `FC-{YYYY}-{MM}-{sequence}`.
- **Rationale**: Sequences are atomic and gap-free under concurrent inserts. Per-org isolation via a function that creates/selects the appropriate sequence. Format matches banking reference number conventions.

**Decision 7**: PDF generation with filled data.
- **Chosen**: Extend existing `render_template_pdf()` to accept a `field_values: dict` parameter. The renderer already positions elements at mm coordinates — it just needs to render the operator's values instead of placeholder/empty content.
- **Rationale**: The PDF infrastructure (WeasyPrint + element renderers) already exists. Each ElementRenderer's `render()` method already handles the element's position/style — we just pass the value.

## Phase 1: Design

### Data Model

**New Table**: `submissions`

```sql
CREATE TABLE submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES templates(id),
    template_version INT NOT NULL,
    operator_id UUID NOT NULL REFERENCES auth.users(id),
    org_id UUID NOT NULL REFERENCES organizations(id),
    field_values JSONB NOT NULL DEFAULT '{}',
    reference_number TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_submissions_operator ON submissions(operator_id, created_at DESC);
CREATE INDEX idx_submissions_template ON submissions(template_id);
CREATE INDEX idx_submissions_org ON submissions(org_id);
CREATE INDEX idx_submissions_ref ON submissions(reference_number);

ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users see own org submissions"
ON submissions FOR SELECT
USING (org_id = (SELECT org_id FROM profiles WHERE id = auth.uid()));

CREATE POLICY "Users create own submissions"
ON submissions FOR INSERT
WITH CHECK (operator_id = auth.uid());
```

**New Table**: `drafts`

```sql
CREATE TABLE drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES templates(id),
    template_version INT NOT NULL,
    operator_id UUID NOT NULL REFERENCES auth.users(id),
    org_id UUID NOT NULL REFERENCES organizations(id),
    field_values JSONB NOT NULL DEFAULT '{}',
    completion_percent INT NOT NULL DEFAULT 0,
    name TEXT,
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (now() + INTERVAL '7 days'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_drafts_operator ON drafts(operator_id, updated_at DESC);

ALTER TABLE drafts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users manage own drafts"
ON drafts FOR ALL
USING (operator_id = auth.uid())
WITH CHECK (operator_id = auth.uid());
```

**Reference Number Function**:

```sql
CREATE OR REPLACE FUNCTION generate_submission_ref(p_org_id UUID)
RETURNS TEXT AS $$
DECLARE
    seq_name TEXT;
    next_val INT;
    ref TEXT;
BEGIN
    seq_name := 'submission_seq_' || replace(p_org_id::text, '-', '_') || '_' || to_char(now(), 'YYYY_MM');
    
    -- Create sequence if not exists
    EXECUTE format('CREATE SEQUENCE IF NOT EXISTS %I START 1', seq_name);
    
    -- Get next value
    EXECUTE format('SELECT nextval(%L)', seq_name) INTO next_val;
    
    ref := 'FC-' || to_char(now(), 'YYYY') || '-' || to_char(now(), 'MM') || '-' || lpad(next_val::text, 4, '0');
    RETURN ref;
END;
$$ LANGUAGE plpgsql;
```

### PDF Renderer Extension

The existing `render_template_pdf(template)` function will be extended to `render_template_pdf(template, field_values=None)`. When `field_values` is provided:
- Each element renderer receives the value for its element.key from field_values
- Text/number/currency renders the filled value instead of empty
- Tafqeet renderer computes from the source field's value in field_values
- Elements with no value in field_values render as blank (matching current behavior)

### Contracts

See `contracts/api.md` for full endpoint specifications.

### i18n Keys

```json
// en.json additions
{
  "filler": {
    "title": "Fill Form",
    "save_draft": "Save Draft",
    "preview": "Preview PDF",
    "print": "Print",
    "print_next": "Print & Next",
    "clear_all": "Clear All",
    "cancel": "Cancel",
    "cancel_confirm": "Discard changes and return to dashboard?",
    "clear_confirm": "Clear all field values?",
    "errors_remaining": "{{count}} errors remaining",
    "required_error": "This field is required",
    "pattern_error": "Invalid format",
    "print_disabled": "Fix all errors before printing",
    "draft_saved": "Draft saved",
    "draft_auto_saved": "Auto-saved",
    "draft_save_failed": "Save failed — will retry",
    "draft_version_warning": "Template updated since draft was saved",
    "draft_continue_old": "Continue with saved data",
    "draft_discard": "Start fresh with new version",
    "draft_expired": "This draft has expired",
    "print_success": "Printed successfully. Ref: {{ref}}",
    "print_next_success": "Printed. Ref: {{ref}} — Ready for next entry",
    "no_fillable_fields": "This template has no fillable fields",
    "unsaved_changes": "You have unsaved changes",
    "page_divider": "Page {{current}} of {{total}}"
  }
}
```

```json
// ar.json additions
{
  "filler": {
    "title": "تعبئة النموذج",
    "save_draft": "حفظ المسودة",
    "preview": "معاينة PDF",
    "print": "طباعة",
    "print_next": "طباعة والتالي",
    "clear_all": "مسح الكل",
    "cancel": "إلغاء",
    "cancel_confirm": "تجاهل التغييرات والعودة للوحة؟",
    "clear_confirm": "مسح جميع القيم؟",
    "errors_remaining": "{{count}} أخطاء متبقية",
    "required_error": "هذا الحقل مطلوب",
    "pattern_error": "صيغة غير صحيحة",
    "print_disabled": "أصلح جميع الأخطاء قبل الطباعة",
    "draft_saved": "تم حفظ المسودة",
    "draft_auto_saved": "حفظ تلقائي",
    "draft_save_failed": "فشل الحفظ — سيتم إعادة المحاولة",
    "draft_version_warning": "تم تحديث النموذج منذ حفظ المسودة",
    "draft_continue_old": "متابعة بالبيانات المحفوظة",
    "draft_discard": "البدء من جديد بالإصدار الجديد",
    "draft_expired": "انتهت صلاحية هذه المسودة",
    "print_success": "تمت الطباعة بنجاح. المرجع: {{ref}}",
    "print_next_success": "تمت الطباعة. المرجع: {{ref}} — جاهز للإدخال التالي",
    "no_fillable_fields": "هذا النموذج لا يحتوي على حقول قابلة للتعبئة",
    "unsaved_changes": "لديك تغييرات غير محفوظة",
    "page_divider": "صفحة {{current}} من {{total}}"
  }
}
```

## Complexity Tracking

| Decision | Justification |
|----------|--------------|
| API call for tafqeet (not client-side) | TafqeetConverter is 500+ lines with complex Arabic rules; duplicating client-side is fragile |
| Reactive Forms (not template-driven) | Dynamic form generation from template data requires programmatic FormControl creation |
| Server-side validation on submit (redundant with client) | Safety net against API manipulation; constitution requires accuracy |
| Per-org sequence for reference numbers | Atomic, gap-free, org-isolated; standard banking pattern |
| Auto-save every 60s (not on every keystroke) | Balance between data safety and API load; 60s is industry standard for auto-save |
