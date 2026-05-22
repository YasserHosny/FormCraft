# Implementation Plan: Reference Data Manager

**Date**: 2026-05-17  
**Feature Branch**: `023-reference-data-manager`  
**Depends on**: Feature 016 (Form Filler dropdown rendering), Feature 021 (ConditionEngine for auto-fill + visibility interaction)

## Architecture Overview

Reference Data Manager adds a centralized data administration layer that feeds into the existing Form Filler dropdown experience. It introduces two new database tables, a backend CRUD service, a CSV import pipeline, and a frontend admin UI — plus modifications to the Form Filler dropdown component to support bound lists with search and auto-fill.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Admin UI                                     │
│  ┌───────────────┐  ┌──────────────────┐  ┌─────────────────────┐  │
│  │ List Manager  │  │ Entry Grid/CRUD  │  │ CSV Import Wizard  │  │
│  └───────────────┘  └──────────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│                    Design Studio (binding config)                     │
│  ┌──────────────────────────────────────────┐                       │
│  │ Dropdown Properties → Ref Binding Panel  │                       │
│  └──────────────────────────────────────────┘                       │
├─────────────────────────────────────────────────────────────────────┤
│                    Form Desk (consumption)                            │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ BoundDropdownComponent → SearchableSelect → AutoFillService   │ │
│  └────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────┤
│                         Backend API                                   │
│  ┌──────────────────┐  ┌───────────────────┐  ┌─────────────────┐  │
│  │ reference_lists  │  │ reference_entries │  │ CSV Importer    │  │
│  │ routes + service │  │ routes + service  │  │ service         │  │
│  └──────────────────┘  └───────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│                        Database                                       │
│  reference_lists ──1:N──> reference_entries                          │
│  elements.formatting.ref_binding.list_id ──ref──> reference_lists   │
└─────────────────────────────────────────────────────────────────────┘
```

## Technology Stack

- **Backend**: Python 3.12, FastAPI, Pydantic v2, Supabase PostgreSQL
- **Frontend**: Angular 17, Angular Material (mat-table, mat-autocomplete, mat-select), Reactive Forms
- **CSV parsing**: Python stdlib `csv` module
- **Caching**: In-memory LRU (backend service), Angular service cache (frontend)
- **i18n**: @ngx-translate/core (bilingual column labels)

## Implementation Phases

### Phase 1: Database & Backend Models (Foundation)

Create migration, SQLAlchemy/Pydantic models, and basic service skeleton.

**Files**:
- `formcraft-backend/migrations/026_reference_data.sql`
- `formcraft-backend/app/models/reference.py`
- `formcraft-backend/app/schemas/reference.py`

### Phase 2: Backend List & Entry CRUD

Implement full CRUD for reference lists and entries with validation, audit logging, and binding protection.

**Files**:
- `formcraft-backend/app/services/reference_service.py`
- `formcraft-backend/app/api/routes/reference.py`
- `formcraft-backend/app/main.py` (register router)

### Phase 3: CSV Import Pipeline

Upload, parse, validate, preview, and bulk insert with transaction safety.

**Files**:
- `formcraft-backend/app/services/reference_import_service.py`
- Extend `formcraft-backend/app/api/routes/reference.py` (import endpoints)

### Phase 4: Form Desk Integration API

Optimized dropdown endpoint, entry fetch for auto-fill, caching layer.

**Files**:
- Extend `formcraft-backend/app/api/routes/reference.py` (dropdown endpoint)
- `formcraft-backend/app/services/reference_cache.py`

### Phase 5: Frontend Admin - List Management

Angular module with list grid, create/edit dialog, archive/delete actions.

**Files**:
- `formcraft-frontend/src/app/features/admin/reference-data/` (module, component, service)
- Route registration in admin routing module
- i18n keys

### Phase 6: Frontend Admin - Entry Management

Entry grid with CRUD, active/inactive toggle, inline editing.

**Files**:
- `formcraft-frontend/src/app/features/admin/reference-data/entries/` (component, dialogs)

### Phase 7: Frontend Admin - CSV Import Wizard

Multi-step import UI: upload → column mapping → preview → confirm.

**Files**:
- `formcraft-frontend/src/app/features/admin/reference-data/import/` (component, stepper)

### Phase 8: Design Studio - Binding Configuration

Properties panel for dropdown elements: list picker, column selection, auto-fill mapping editor.

**Files**:
- Modify Design Studio element properties panel
- `formcraft-frontend/src/app/features/studio/components/ref-binding-panel/`

### Phase 9: Form Desk - Bound Dropdown & Auto-Fill

Render bound dropdowns with searchable type-ahead, execute auto-fill on selection.

**Files**:
- `formcraft-frontend/src/app/features/desk/components/bound-dropdown/`
- `formcraft-frontend/src/app/features/desk/services/auto-fill.service.ts`
- Modify form filler to detect ref_binding and render BoundDropdownComponent

## Technical Constraints

1. **No new npm dependencies** for searchable dropdown — use Angular Material `mat-autocomplete` (already in project)
2. **No DDL per reference list** — all data stored in JSONB, validated at API layer
3. **RLS enforced** — all queries scoped by org_id
4. **Backwards compatible** — existing dropdown elements without ref_binding continue working unchanged
5. **Audit granularity** — individual entry changes logged, bulk import logged as single action with count metadata

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Large CSV import timeout | P2 feature unavailable | Background processing with status polling for >5K rows |
| Schema evolution breaks entries | Data corruption | Soft-remove columns only, never hard-delete JSONB keys |
| Auto-fill race condition | Wrong values populated | Auto-fill executes synchronously in Angular change detection cycle |
| Cache staleness | Operator sees outdated list | 5-min TTL + manual cache-bust on entry modification + form reload |
