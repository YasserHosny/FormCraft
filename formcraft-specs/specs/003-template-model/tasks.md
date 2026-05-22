# Tasks: Template Domain Model

**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Format: `[ID] [Priority] [Story] Description`

## Phase 1: Database Setup

- [ ] **T03-001** P1 Setup — Create `supabase/migrations/003_create_templates.sql` — templates table with all columns, check constraints, indexes
- [ ] **T03-002** P1 Setup — Create `supabase/migrations/004_create_pages.sql` — pages table with FK to templates, default A4 dimensions
- [ ] **T03-003** P1 Setup — Create `supabase/migrations/005_create_elements.sql` — elements table with FK to pages, type check constraint, JSONB columns
- [ ] **T03-004** P1 Setup — Create unique index for element key per template
- [ ] **T03-005** P1 Setup — Run migrations via `supabase db push`

## Phase 2: Backend — Models & Schemas

- [ ] **T03-010** P1 S1 — Create `app/models/enums.py` — TemplateStatus, ElementType, Country, Language enums
- [ ] **T03-011** P1 S1 — Create `app/models/template.py` — Template, Page, Element Pydantic models (DB representation)
- [ ] **T03-012** P1 S1 — Create `app/schemas/template.py` — CreateTemplateRequest, UpdateTemplateRequest, TemplateResponse, TemplateListResponse (with pagination)
- [ ] **T03-013** P1 S2 — Create `app/schemas/page.py` — CreatePageRequest, UpdatePageRequest, PageResponse, ReorderPagesRequest
- [ ] **T03-014** P1 S3 — Create `app/schemas/element.py` — CreateElementRequest, UpdateElementRequest, ElementResponse, ReorderElementsRequest

## Phase 3: Backend — Services

- [ ] **T03-020** P1 S1 — Create `app/services/template_service.py` — create_template() (with default page), get_template() (with pages+elements), list_templates() (filtered+paginated)
- [ ] **T03-021** P1 S1 — Add to template_service: update_template() with optimistic concurrency (updated_at check), delete_template()
- [ ] **T03-022** P1 S4 — Add to template_service: publish_template(), create_new_version()
- [ ] **T03-023** P1 S2 — Create page management in template_service: add_page(), update_page(), delete_page() (prevent last page deletion), reorder_pages()
- [ ] **T03-024** P1 S3 — Create element management in template_service: add_element() (generate unique key), update_element(), delete_element(), reorder_elements()

## Phase 4: Backend — API Routes

- [ ] **T03-030** P1 S1,S5 — Create `app/api/routes/templates.py` — POST /api/templates, GET /api/templates, GET /api/templates/{id}, PUT /api/templates/{id}, DELETE /api/templates/{id}
- [ ] **T03-031** P1 S4 — Add routes: POST /api/templates/{id}/publish, POST /api/templates/{id}/version
- [ ] **T03-032** P1 S2 — Add routes: POST /api/templates/{id}/pages, PUT /api/pages/{id}, DELETE /api/pages/{id}, PUT /api/pages/{id}/reorder
- [ ] **T03-033** P1 S3 — Add routes: POST /api/pages/{id}/elements, PUT /api/elements/{id}, DELETE /api/elements/{id}, PUT /api/pages/{id}/elements/reorder
- [ ] **T03-034** P1 S1-S5 — Apply role guards: Admin+Designer for create/update/delete, all roles for read (RLS handles filtering)

## Phase 5: Backend — Tests

- [ ] **T03-040** P1 S1 — Write unit tests: template CRUD, optimistic concurrency conflict detection
- [ ] **T03-041** P1 S2 — Write unit tests: page management, prevent last page deletion
- [ ] **T03-042** P1 S3 — Write unit tests: element CRUD, unique key generation
- [ ] **T03-043** P1 S5 — Write integration tests: list templates with filters, pagination, role-based visibility
- [ ] **T03-044** P1 S4 — Write integration tests: publish → immutability, create new version

## Phase 6: Frontend — Template Module

- [ ] **T03-050** P1 S5 — Create `src/app/models/template.model.ts` — Template, Page, Element TypeScript interfaces
- [ ] **T03-051** P1 S5 — Create `src/app/models/template.schema.ts` — Zod schemas for request/response validation
- [ ] **T03-052** P1 S5 — Create `src/app/core/services/template.service.ts` — HTTP service for all template/page/element CRUD
- [ ] **T03-053** P1 S5 — Create `src/app/features/templates/template-list/` — Template listing with Angular Material table, filters (status, category, country), search, pagination
- [ ] **T03-054** P1 S1 — Create `src/app/features/templates/template-create-dialog/` — MatDialog with form (name, description, category, language, country)
- [ ] **T03-055** P1 S5 — Create `src/app/features/templates/template-detail/` — Template detail view (metadata + page navigator, links to Design Studio)

## Phase 7: Frontend — Tests

- [ ] **T03-060** P1 — Write unit tests: template.service.spec.ts — CRUD operations, error handling
- [ ] **T03-061** P1 — Write unit tests: template-list.component.spec.ts — filter/search/pagination rendering

## Dependencies & Execution Order

```
T03-001 → T03-002 → T03-003 → T03-004 → T03-005 (sequential: DB)
T03-010 → T03-011 → T03-012, T03-013, T03-014 (enums → models → schemas)
T03-012-014 → T03-020 → T03-021 → T03-022 (schemas → service)
T03-023, T03-024 (parallel with T03-021)
T03-020-024 → T03-030-034 (services → routes)
T03-050, T03-051 (parallel: FE models)
T03-052 → T03-053, T03-054, T03-055 (service → components)
```

## Parallel Opportunities

- Schemas (T03-012, T03-013, T03-014) in parallel after models
- Page + Element services (T03-023, T03-024) in parallel
- All backend routes (T03-030-034) can be split across developers
- Frontend components (T03-053, T03-054, T03-055) in parallel after service
