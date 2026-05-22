# Research: Feedback Dashboard Search & Labels

**Branch**: `012-feedback-dashboard-search` | **Phase**: 0

## Decision Log

---

### 1. Search Implementation Strategy

**Decision**: Server-side ILIKE search on `text_content` column, triggered by a debounced API call (300–500 ms after keystroke), with a `search` query parameter added to the existing `GET /api/admin/feedback` endpoint.

**Rationale**: The existing paginated list endpoint already accepts query parameters (status, user_id, date_from, date_to). Adding `search` as one more parameter is the minimal-change path — it requires no new endpoint, no new indexing infrastructure, and is correct for datasets up to 10,000 submissions (SC-001's upper bound). A PostgreSQL `ILIKE '%term%'` on an indexed `text_content` column handles this volume within the 2-second SLA without full-text search overhead.

**Alternatives considered**:
- PostgreSQL `tsvector` / `to_tsquery` full-text search: better relevance ranking, but Out of Scope per spec. Can be migrated to later without changing the API contract.
- Client-side filtering: fast for small sets, breaks pagination correctness for large datasets.
- Dedicated search service (Elasticsearch/Typesense): unnecessary for this scale.

---

### 2. Filter State Persistence

**Decision**: Store active filter state in Angular component memory (service-level BehaviorSubject), scoped to the admin's browser session. No URL query params, no localStorage.

**Rationale**: The spec requires session-only persistence (FR-008). A shared `FeedbackFilterStateService` (singleton Angular service) holds the current filter snapshot and survives route navigation within the same SPA session. This is the lightest implementation and requires no storage API.

**Alternatives considered**:
- URL query params: more shareable and bookmarkable, but adds complexity and is not required by the spec.
- localStorage: survives page refresh (cross-session), explicitly out of scope.

---

### 3. Label Colour Palette

**Decision**: 10 named semantic colour tokens stored as an enum string in the database. Palette: `red`, `orange`, `yellow`, `green`, `teal`, `blue`, `purple`, `pink`, `grey`, `brown`.

**Rationale**: 10 colours cover the common tag-colour vocabulary seen in tools like GitHub, Linear, and Jira. Named tokens map directly to Angular Material theme palette classes, keeping the frontend purely CSS-class-driven with no runtime hex manipulation. The CHECK constraint in PostgreSQL enforces the allowed values at the DB level.

**Alternatives considered**:
- Hex codes: requires a colour picker widget, more implementation cost, not needed for semantic labels.
- Integer index: indirect mapping; harder to read in raw DB queries and migration files.

---

### 4. Label Management UI Pattern

**Decision**: A "Manage Labels" button in the dashboard toolbar opens an Angular Material `MatDialog` (modal). The modal contains a list of existing labels with inline edit/delete controls, plus a "New label" form at the bottom.

**Rationale**: A modal keeps label management on the same route without adding navigation complexity. MatDialog is already used in the FormCraft frontend for similar admin actions. It avoids a side-panel layout shift that would collapse the submission table.

**Alternatives considered**:
- Dedicated `/admin/labels` route: adds a route and breadcrumb; unnecessary for a secondary management task.
- Inline chip-input ad-hoc creation: conflates discovery (browsing labels) with assignment; harder to support edit/delete.

---

### 5. Label Assignment Interaction

**Decision**: Inline chip-autocomplete input on each expanded submission row. Clicking a chip removes the label. A "+" button opens the autocomplete. The change is persisted immediately via `PATCH /api/admin/feedback/{id}/labels` without a save button.

**Rationale**: Optimistic UI with immediate persistence matches SC-003 (reflected within 1 second). A save button adds a step that offers no value when the only risk is accidental label assignment (which is trivially reversible by removing the chip).

**Alternatives considered**:
- Checkbox multi-select dropdown: works but requires an explicit apply step; slower for power users.
- Drag-and-drop kanban by label: out of scope.

---

### 6. Multi-Label Filter Logic

**Decision**: OR logic within the label filter facet; AND logic across different filter facets (status AND date AND label).

**Rationale**: Confirmed via `/speckit.clarify` session (2026-05-07). Within a single facet (labels), OR is standard — selecting "Bug" and "Feature Request" means "show me either". Across facets, AND is standard — "new AND Bug" narrows to new bug reports specifically.

---

### 7. Database Migration Numbering

**Decision**: `009_create_feedback_labels.sql` — next sequential number after feature 011's `008_create_feedback_submissions.sql`.

**Rationale**: Follows the established `001…00N` sequential convention observed across all prior migrations.
