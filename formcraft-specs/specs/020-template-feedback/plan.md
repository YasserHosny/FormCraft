# Implementation Plan: Template Feedback

**Date**: 2026-05-17  
**Feature Branch**: `019-template-feedback`  
**Depends on**: Feature 015 (Operator Dashboard for Form Desk context), Feature 018 (Template Versioning for version reference)

## Architecture Overview

Template Feedback adds a structured feedback loop between operators (Form Desk) and designers (Design Studio). It introduces one new database table and surfaces feedback through three UI integration points: Form Desk submission panel, Design Studio review panel, and Admin overview page.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Form Desk (Operator)                          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ FeedbackButtonComponent → FeedbackPanelComponent            ││
│  │ (category, text, page/element selector)                     ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│                    Design Studio (Designer)                       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ FeedbackTabComponent → FeedbackListComponent                ││
│  │ (filter, resolve, navigate to element)                      ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│                    Admin Panel                                    │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ TemplateFeedbackOverviewComponent (grid, export)            ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│                         Backend API                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ template_feedback routes + service + audit logging        │   │
│  └──────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                        Database                                   │
│  template_feedback (NEW)                                         │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

- **Backend**: Python 3.12, FastAPI, Pydantic v2, Supabase PostgreSQL
- **Frontend**: Angular 17, Angular Material (mat-table, mat-dialog, mat-chip), Reactive Forms
- **i18n**: @ngx-translate/core

## Implementation Phases

### Phase 1: Database Migration & Backend Models

Create template_feedback table, SQLAlchemy model, Pydantic schemas.

### Phase 2: Backend Service & Routes

CRUD service with debounce logic, resolve workflow, audit logging. Routes for submit, list, resolve, summary, admin overview, export.

### Phase 3: Frontend - Form Desk Feedback Panel

Feedback button in Form Desk toolbar, slide-out panel with form (category, text, page/element selector), submission toast.

### Phase 4: Frontend - Design Studio Feedback Tab

Tab in Design Studio properties sidebar showing feedback list, filters, resolve action, element navigation on click.

### Phase 5: Frontend - Admin Overview

Admin page at /admin/template-feedback with template grid, expandable rows, CSV export.

### Phase 6: Polish & Integration

Feedback count badge on template cards, empty states, error handling.

## Technical Constraints

1. **Separate from existing feedback system** — `template_feedback` is independent of `feedback_submissions`
2. **Element reference by key, not FK** — survives element deletion across versions
3. **No real-time push in v1** — passive badge notification; Supabase Realtime can be added later
4. **RLS enforced** — all queries scoped by org_id
5. **Audit all actions** — submit and resolve logged

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Duplicate feedback spam | Noise for designers | 60-second debounce on same text + element |
| Element deleted after feedback | Broken reference | Store element_key (string), show "Element no longer exists" in UI |
| Large feedback volume on popular templates | Slow panel load | Pagination (50/page), status filter defaults to "open" |
