# Implementation Plan: Template Domain Model

**Branch**: `03-template-model` | **Date**: 2026-02-21 | **Spec**: [spec.md](./spec.md)

## Summary

Implement the normalized Template → Page → Element data model in Supabase, CRUD REST API via FastAPI, Angular services for template management, and optimistic concurrency for multi-user safety.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, supabase-py, Pydantic v2, Zod (frontend)
**Storage**: Supabase PostgreSQL — templates, pages, elements tables
**Testing**: pytest (backend unit + integration), Jasmine/Karma (frontend)
**Target Platform**: Web

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| II. Pixel-Perfect | ✅ Pass | Element positions stored in mm (float) |
| VI. Normalized Data | ✅ Pass | Three normalized tables with FK relationships |
| VIII. Security | ✅ Pass | RLS policies per role, audit fields on all entities |

## Project Structure

### Backend (formcraft-backend)

```text
app/
├── api/routes/
│   └── templates.py             # CRUD endpoints for templates, pages, elements
├── models/
│   ├── template.py              # Template, Page, Element Pydantic models
│   └── enums.py                 # TemplateStatus, ElementType, Country, Language enums
├── schemas/
│   ├── template.py              # CreateTemplateRequest, UpdateTemplateRequest, TemplateResponse
│   ├── page.py                  # CreatePageRequest, UpdatePageRequest, PageResponse
│   └── element.py               # CreateElementRequest, UpdateElementRequest, ElementResponse
└── services/
    └── template_service.py      # Template CRUD logic, optimistic concurrency

supabase/migrations/
├── 003_create_templates.sql
├── 004_create_pages.sql
├── 005_create_elements.sql
└── 006_templates_rls.sql
```

### Frontend (formcraft-frontend)

```text
src/app/
├── features/templates/
│   ├── template-list/           # Template listing with filters/search/pagination
│   ├── template-detail/         # Template view/edit page
│   └── template-create-dialog/  # Create template dialog
├── models/
│   ├── template.model.ts        # Template, Page, Element TypeScript interfaces
│   ├── template.schema.ts       # Zod schemas for validation
│   └── enums.ts                 # TemplateStatus, ElementType enums
└── core/
    └── services/
        └── template.service.ts  # HTTP service for template CRUD
```

### Database Schema

```sql
-- templates
CREATE TABLE public.templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    category TEXT NOT NULL DEFAULT 'general',
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'published')),
    version INTEGER NOT NULL DEFAULT 1,
    language TEXT NOT NULL DEFAULT 'ar' CHECK (language IN ('ar', 'en')),
    country TEXT NOT NULL DEFAULT 'EG' CHECK (country IN ('EG', 'SA', 'AE')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID NOT NULL REFERENCES auth.users(id)
);

-- pages
CREATE TABLE public.pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES public.templates(id) ON DELETE CASCADE,
    width_mm NUMERIC(7,2) NOT NULL DEFAULT 210,
    height_mm NUMERIC(7,2) NOT NULL DEFAULT 297,
    background_asset TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- elements
CREATE TABLE public.elements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    page_id UUID NOT NULL REFERENCES public.pages(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('text','number','date','currency','dropdown','radio','checkbox','image','qr','barcode')),
    key TEXT NOT NULL,
    label_ar TEXT DEFAULT '',
    label_en TEXT DEFAULT '',
    x_mm NUMERIC(7,2) NOT NULL DEFAULT 0,
    y_mm NUMERIC(7,2) NOT NULL DEFAULT 0,
    width_mm NUMERIC(7,2) NOT NULL DEFAULT 50,
    height_mm NUMERIC(7,2) NOT NULL DEFAULT 10,
    validation JSONB DEFAULT '{}',
    formatting JSONB DEFAULT '{}',
    required BOOLEAN NOT NULL DEFAULT false,
    direction TEXT NOT NULL DEFAULT 'auto' CHECK (direction IN ('rtl','ltr','auto')),
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Unique key per template (across all pages)
CREATE UNIQUE INDEX idx_element_key_per_template
    ON public.elements(key, (SELECT template_id FROM public.pages WHERE id = page_id));
```

### API Endpoints

| Method | Path | Description | Roles |
|--------|------|-------------|-------|
| POST | /api/templates | Create template | Admin, Designer |
| GET | /api/templates | List templates (filtered, paginated) | All |
| GET | /api/templates/{id} | Get template with pages and elements | All |
| PUT | /api/templates/{id} | Update template metadata | Admin, Designer (own) |
| DELETE | /api/templates/{id} | Delete template | Admin, Designer (own) |
| POST | /api/templates/{id}/publish | Publish template | Admin |
| POST | /api/templates/{id}/version | Create new draft version | Admin, Designer |
| POST | /api/templates/{id}/pages | Add page | Admin, Designer (own) |
| PUT | /api/pages/{id} | Update page | Admin, Designer (own) |
| DELETE | /api/pages/{id} | Delete page | Admin, Designer (own) |
| PUT | /api/pages/{id}/reorder | Reorder pages | Admin, Designer (own) |
| POST | /api/pages/{id}/elements | Add element | Admin, Designer (own) |
| PUT | /api/elements/{id} | Update element | Admin, Designer (own) |
| DELETE | /api/elements/{id} | Delete element | Admin, Designer (own) |
| PUT | /api/pages/{id}/elements/reorder | Reorder elements | Admin, Designer (own) |

### Optimistic Concurrency

```python
# In template_service.py
async def update_template(id: UUID, data: UpdateTemplateRequest, expected_updated_at: datetime):
    result = await supabase.table("templates") \
        .update(data.dict()) \
        .eq("id", id) \
        .eq("updated_at", expected_updated_at.isoformat()) \
        .execute()
    if not result.data:
        raise HTTPException(409, "Template was modified by another user. Please refresh.")
```

## Research Notes

- **Element key uniqueness**: Unique per template (not per page) to enable cross-page data binding. Implemented via a composite unique index.
- **Background assets**: Stored in Supabase Storage bucket `template-assets`. URL stored in `pages.background_asset`.
- **Pagination**: Offset-based with `?page=1&limit=20`. Supabase supports `range()` for this. Cursor-based deferred to Phase 2.

## Complexity Tracking

No constitution violations.
