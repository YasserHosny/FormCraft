# Implementation Plan: Submission History & Reprint

**Branch**: `017-submission-history` | **Date**: 2026-05-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/017-submission-history/spec.md`

## Summary

Build the Submission History page (`/desk/history`) — a searchable, filterable table of past form submissions with detail view, PDF reprint with watermark, clone-as-new, and data export. Builds on the `submissions` table created in feature 016 (Form Filler). Requires extending the submissions API with list/search/filter endpoints, adding a reprint watermark capability to the PDF renderer, and creating new frontend components.

## Technical Context

**Language/Version**: TypeScript / Angular 17 (frontend), Python 3.12 / FastAPI (backend)
**Primary Dependencies**: Angular Material (MatTable, MatPaginator, MatSort, MatDateRangePicker, MatFormField, MatSelect, MatDialog), @ngx-translate/core
**Storage**: Supabase PostgreSQL (reads from `submissions` table, new `reprints` tracking via audit log)
**PDF**: Existing WeasyPrint renderer + new watermark overlay logic
**Testing**: Jasmine + Karma (frontend), pytest (backend)
**Performance Goals**: History load < 1s for 1000 submissions, search < 500ms, reprint PDF < 3s
**Constraints**: Uses existing submissions table from feature 016; must handle templates that may have been updated since submission
**Scale/Scope**: Up to 1000 submissions per operator, up to 50 operators per org

## Constitution Check

| Principle | Status | Notes |
|-----------|:------:|-------|
| I. Arabic-First, RTL-Native | PASS | Table columns, search, detail view all use i18n; date formatting respects locale |
| II. mm-Precision Guarantee | PASS | Reprints use stored template version's element coordinates; mm positions preserved |
| III. Deterministic-First Validation | N/A | No validation in history view (read-only) |
| IV. Two-Mode Architecture | PASS | Lives under `/desk/history`; desk-mode users only |
| V. Data Sovereignty & Multi-Tenancy | PASS | Submissions table has org_id + RLS; operators see own org data |
| VI. Audit Everything | PASS | FORM_REPRINTED event logged on every reprint; SUBMISSION_EXPORTED on export |
| VII. Template Versioning | PASS | Reprints use original template_version; detail view shows version number |

## Project Structure

```text
formcraft-backend/
├── app/
│   ├── api/routes/
│   │   └── submissions.py              # UPDATE: add GET /api/submissions/:id, GET /api/submissions/:id/reprint, GET /api/submissions/:id/export
│   └── services/
│       ├── submission_service.py        # UPDATE: add list_submissions(), get_submission(), export_submission()
│       └── pdf/
│           └── renderer.py             # UPDATE: add watermark support for reprints

formcraft-frontend/
├── src/app/
│   ├── features/
│   │   └── desk/
│   │       ├── history/
│   │       │   ├── history.component.ts         # NEW: history list container
│   │       │   ├── history.component.html       # NEW: table + filters
│   │       │   └── history.component.scss       # NEW: responsive table styles
│   │       ├── submission-detail/
│   │       │   ├── detail.component.ts          # NEW: read-only submission view
│   │       │   ├── detail.component.html        # NEW: field values display
│   │       │   └── detail.component.scss
│   │       └── services/
│   │           └── history.service.ts           # NEW: history API client
└── src/assets/i18n/
    ├── ar.json                                  # ADD: history.* keys
    └── en.json                                  # ADD: history.* keys
```

## Phase 0: Research

**Decision 1**: Reprint implementation — re-render vs. stored PDF.
- **Chosen**: Re-render from stored field_values + template version data (not stored PDF binary).
- **Rationale**: Storing PDFs would be expensive (100KB+ per submission × thousands of submissions). Re-rendering from data is fast (< 3s), ensures the latest renderer fixes apply, and only requires the field_values JSONB already stored. The watermark is added as a post-processing overlay.

**Decision 2**: Template version retrieval for reprints.
- **Chosen**: Load template at the stored `template_version` by querying templates with version filter.
- **Rationale**: Constitution VII requires template versions to be preserved. The existing template versioning system keeps old versions accessible. If a version has been hard-deleted (shouldn't happen per constitution), fall back to field_values-only export with a warning.

**Decision 3**: History table — server-side vs. client-side pagination.
- **Chosen**: Server-side pagination with sorting and filtering via query params.
- **Rationale**: 1000+ submissions per operator makes client-side infeasible. Server-side pagination with OFFSET/LIMIT and indexed columns ensures consistent < 500ms response.

**Decision 4**: Watermark implementation.
- **Chosen**: WeasyPrint CSS `@page` rule with rotated overlay text.
- **Rationale**: WeasyPrint supports `@page` backgrounds and watermarks natively via CSS. A diagonal "REPRINT" text with low opacity is standard banking practice. No external library needed.

**Decision 5**: Clone-as-new field mapping strategy.
- **Chosen**: Map by element.key (not by position or ID). Missing keys → empty. Extra keys → ignored.
- **Rationale**: When a template is updated between the original submission and the clone, fields may be added/removed. Key-based mapping is the most resilient approach — if a field exists in both versions, its value carries over.

## Phase 1: Design

### Contracts

See `contracts/api.md`.

### i18n Keys

```json
// en.json additions
{
  "history": {
    "title": "Submission History",
    "search_placeholder": "Search by reference number or template name...",
    "filter_template": "Template",
    "filter_date_from": "From",
    "filter_date_to": "To",
    "filter_status": "Status",
    "clear_filters": "Clear",
    "col_ref": "Reference",
    "col_template": "Template",
    "col_date": "Date",
    "col_status": "Status",
    "col_summary": "Key Fields",
    "col_actions": "Actions",
    "status_printed": "Printed",
    "status_submitted": "Submitted",
    "status_reprinted": "Reprinted",
    "action_view": "View",
    "action_reprint": "Reprint",
    "action_clone": "Clone as New",
    "action_export": "Export",
    "action_download_pdf": "Download PDF",
    "export_json": "Export as JSON",
    "export_csv": "Export as CSV",
    "reprint_confirm": "Generate reprint with watermark?",
    "reprint_success": "Reprint generated",
    "clone_notice": "Form opened with data from {{ref}}. A new reference number will be assigned on print.",
    "detail_title": "Submission Detail",
    "detail_ref": "Reference Number",
    "detail_template": "Template",
    "detail_version": "Version",
    "detail_date": "Submitted",
    "detail_operator": "Operator",
    "empty_state": "No submissions yet. Print a form to see it here.",
    "no_results": "No submissions match your search.",
    "showing_results": "Showing {{count}} of {{total}} submissions"
  }
}
```

```json
// ar.json additions
{
  "history": {
    "title": "سجل الإرسالات",
    "search_placeholder": "البحث برقم المرجع أو اسم النموذج...",
    "filter_template": "النموذج",
    "filter_date_from": "من",
    "filter_date_to": "إلى",
    "filter_status": "الحالة",
    "clear_filters": "مسح",
    "col_ref": "المرجع",
    "col_template": "النموذج",
    "col_date": "التاريخ",
    "col_status": "الحالة",
    "col_summary": "حقول رئيسية",
    "col_actions": "إجراءات",
    "status_printed": "مطبوع",
    "status_submitted": "مرسل",
    "status_reprinted": "أعيدت طباعته",
    "action_view": "عرض",
    "action_reprint": "إعادة طباعة",
    "action_clone": "نسخ كجديد",
    "action_export": "تصدير",
    "action_download_pdf": "تحميل PDF",
    "export_json": "تصدير JSON",
    "export_csv": "تصدير CSV",
    "reprint_confirm": "إنشاء نسخة مطبوعة مع علامة مائية؟",
    "reprint_success": "تمت إعادة الطباعة",
    "clone_notice": "تم فتح النموذج ببيانات من {{ref}}. سيتم تعيين رقم مرجع جديد عند الطباعة.",
    "detail_title": "تفاصيل الإرسالية",
    "detail_ref": "رقم المرجع",
    "detail_template": "النموذج",
    "detail_version": "الإصدار",
    "detail_date": "تاريخ الإرسال",
    "detail_operator": "المشغل",
    "empty_state": "لا توجد إرسالات بعد. اطبع نموذجاً لتراه هنا.",
    "no_results": "لا توجد إرسالات تطابق بحثك.",
    "showing_results": "عرض {{count}} من {{total}} إرسالية"
  }
}
```

## Complexity Tracking

| Decision | Justification |
|----------|--------------|
| Re-render for reprints (not stored PDF) | Saves storage; field_values already persisted; renderer handles it in < 3s |
| CSS watermark (not image overlay) | WeasyPrint natively supports it; no binary manipulation; cleaner code |
| Key-based field mapping for clone | Most resilient to template version changes; industry standard for form migration |
| Server-side pagination | 1000+ rows makes client-side infeasible; consistent performance |
