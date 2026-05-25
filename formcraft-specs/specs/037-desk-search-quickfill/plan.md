# Implementation Plan: Form Desk Search & Quick Fill

**Feature**: F037 - Desk Search & Quick Fill  
**Branch**: `037-desk-search-quickfill-implementation`  
**Date**: 2026-05-26  
**Status**: Planned

## Technical Context

- **Backend**: Python 3.12 + FastAPI + Supabase PostgreSQL
- **Frontend**: TypeScript + Angular 19 + Angular Material + RxJS
- **Database**: Supabase PostgreSQL with RLS, full-text search, pg_trgm
- **Existing Infrastructure**: Form Desk, templates, submissions, customer profiles, departments/branches, auth/RLS

## Architecture

### Components

1. **Backend (FastAPI)**
   - `search_service.py` — unified search logic with PostgreSQL full-text search and trigram matching
   - `quickfill_service.py` — field mapping and auto-population logic
   - `search.py` (router) — `/search` endpoint for global search
   - `quickfill.py` (router) — `/quickfill/customers`, `/quickfill/map` endpoints
   - `sql/migrations/` — database changes for search view, indexes, and trigram support

2. **Frontend (Angular)**
   - `GlobalSearchBarComponent` — standalone component with debounced input and grouped results
   - `QuickFillDialogComponent` — customer search and selection dialog
   - `QuickFillService` — maps customer data to form fields, marks auto-populated fields
   - `SearchService` — calls backend search API, caches recent results

3. **Database**
   - Materialized view `mv_global_search` — unions templates, submissions, customers with tsvector columns
   - `pg_trgm` extension — fuzzy name matching
   - `unaccent` extension — diacritic-insensitive search
   - GIN indexes on `mv_global_search.search_vector` and customer/template name trigram indexes

## Phase 0: Research & Decisions

See `research.md`.

## Phase 1: Data Model & Contracts

See `data-model.md` and `contracts/`.

## Phase 2: Implementation Phases

### Phase 2.1: Database Layer
- [ ] Enable `pg_trgm` and `unaccent` extensions
- [ ] Create `quickfill_mappings` table (org-level configurable field mappings)
- [ ] Create `mv_global_search` materialized view with refresh strategy
- [ ] Create GIN indexes on search_vector and trigram indexes on names
- [ ] Add migration script `037_desk_search_quickfill.sql`

### Phase 2.2: Backend API
- [ ] Implement `search_service.py` with:
  - `search_global(query, user, limit_per_type=5)` → grouped results
  - `search_reference_number(ref)` → exact submission match
  - `search_customers(query, org_id, limit=10)` → fuzzy name/identifier/phone search
- [ ] Implement `quickfill_service.py` with:
  - `map_customer_to_fields(customer, template_id, org_id)` → field values
  - `get_quickfill_mappings(org_id)` → current mapping config
- [ ] Implement FastAPI routers:
  - `GET /search?q={query}&types={types}` → `SearchResultGroup[]`
  - `GET /search/reference?ref={ref}` → `SubmissionDetail | null`
  - `GET /quickfill/customers?q={query}` → `Customer[]`
  - `POST /quickfill/map` → `FieldValueMap`

### Phase 2.3: Frontend Components
- [ ] `GlobalSearchBarComponent`:
  - Debounced input (200ms)
  - Grouped results dropdown (Templates, Submissions, Customers)
  - Keyboard navigation (arrow keys, enter, escape)
  - Recent searches cache (localStorage)
- [ ] `QuickFillDialogComponent`:
  - Customer search with fuzzy matching
  - Customer card display (name, identifier, recent activity)
  - "Select" action
- [ ] `QuickFillService`:
  - `autoFill(form, customer, templateId)` → populates matching fields
  - `markAutoFilled(fields)` → applies `auto-filled` CSS class
  - `saveToProfile(submission)` → optional update customer profile
- [ ] `SearchService`:
  - `search(query)` → observable of grouped results
  - `searchByReference(ref)` → navigates to submission detail

### Phase 2.4: Integration
- [ ] Wire global search bar into Form Desk shell/layout
- [ ] Wire Quick Fill dialog into template selection flow
- [ ] Integrate with existing `FormFillerComponent` to accept pre-populated values
- [ ] Link submission to customer profile on print/save

### Phase 2.5: Testing
- [ ] Backend unit tests: search service (exact, fuzzy, mixed-script), quickfill mapping, RLS compliance
- [ ] Frontend unit tests: search bar debounce, keyboard nav, quick fill dialog, service mapping
- [ ] Integration tests: end-to-end search → navigate, quick fill → print → linked customer

## Phase 3: Validation

- Verify SC-001: benchmark 95th percentile search latency < 300ms
- Verify SC-002: compare form completion time with/without Quick Fill
- Verify SC-003: verify mapping accuracy against test dataset
- Verify SC-004: benchmark reference number search < 5s
- Verify SC-005: load test 50 concurrent searches

## Risk Mitigation

- **Materialized view staleness**: Refresh on template/submission/customer changes via trigger or cron; acceptable 5-min delay
- **RLS complexity**: Search service must apply same filters as direct table access; test with multiple operators
- **Arabic fuzzy matching**: `pg_trgm` works on byte sequences; verify with Arabic name dataset
- **Performance at scale**: Monitor materialized view refresh time; consider incremental refresh if > 1M rows

## Constitution Check

- Code style: Python 3.12 + TypeScript/Angular 19 per AGENTS.md
- Security: RLS enforced in search queries; no exposure of cross-org data
- Testing: Unit + integration tests required before merge
- Documentation: API contracts in `contracts/`, quickstart in `quickstart.md`
