# Research: Operator Dashboard

**Date**: 2026-05-16

## Research Questions

No NEEDS CLARIFICATION items in the spec. Research focused on implementation approach validation.

## Findings

### 1. Dashboard Aggregation Pattern

**Decision**: Single `GET /api/desk/dashboard` endpoint returning all sections.

**Rationale**: The dashboard has 5 sections (templates, recent, pinned, drafts, notifications). Making 5 separate API calls would violate NFR-004 (no N+1). A single endpoint lets the backend run queries in parallel (using `asyncio.gather`) and return a single JSON response. The backend controls the data shape, avoiding over-fetching.

**Key insight from existing code**: The templates list endpoint (`GET /api/templates`) already supports pagination, filtering, and search. The dashboard endpoint wraps similar logic but adds the aggregated sections.

### 2. Pin Storage Approach

**Decision**: New `operator_pins` table with (operator_id, template_id, org_id) unique constraint.

**Rationale**:
- Constitution V (Data Sovereignty) requires org_id on all user-data tables + RLS
- A join table is the simplest relational pattern for a many-to-many relationship
- Unique constraint prevents duplicate pins
- CASCADE on template delete auto-cleans pins when templates are removed
- No complex migration — new table only, no ALTER on existing tables

### 3. Recently Used Derivation

**Decision**: Derive from `submissions` table via `SELECT template_id, MAX(created_at) FROM submissions WHERE operator_id = ? GROUP BY template_id ORDER BY 2 DESC LIMIT 10`.

**Rationale**:
- Submissions table already tracks who filled what and when
- No new table needed — avoids schema bloat
- Query is fast with existing index on (operator_id, created_at)
- If submissions table doesn't exist yet (built in Form Filler feature), return empty array — dashboard still works

### 4. Template Version Notifications

**Decision**: Derive notifications at query time, not via a stored notification table.

**Rationale**:
- A version notification = "template_id where current version > version the operator last used"
- This is a join between `submissions` (operator's last version per template) and `templates` (current version)
- No notification table needed — avoids write amplification (publishing a template would have to fan out notifications to all operators)
- Dismissals stored in a lightweight `dismissed_notifications` table or JSONB on the user profile
- Trade-off: slightly more complex query, but zero write overhead on template publish

**Revised decision**: Use a `notification_dismissals` table to track which (operator_id, template_id, version) notifications have been dismissed. This is cleaner than JSONB and supports RLS.

### 5. Search Implementation

**Decision**: PostgreSQL `ILIKE` on `name` and `description` columns.

**Rationale**:
- Organization template count is bounded (< 200 per spec)
- `ILIKE` is fast enough at this scale without specialized indexes
- Supports Arabic text natively (PostgreSQL's `ILIKE` is case-insensitive but handles Unicode)
- No additional extensions needed (no pg_trgm, no tsvector)
- If scale increases, can add GIN index later without API changes

## Alternatives Considered

| Option | Rejected Because |
|--------|-----------------|
| Separate API endpoints per dashboard section | Violates NFR-004; 5 round trips vs 1; harder to coordinate loading states |
| GraphQL for flexible dashboard queries | Not in tech stack (constitution forbids unlisted tech); over-engineering for a fixed layout |
| Pin storage in user profile JSONB column | Array manipulation in SQL is fragile; harder to query "most pinned templates" for analytics |
| Stored notifications table (write on publish) | Fan-out problem: publishing 1 template creates N notification rows for N operators; complex cleanup |
| Client-side template filtering | Breaks pagination; loads all 200 templates upfront; doesn't work with RLS |
| Redis/cache layer for dashboard | Not in tech stack; PostgreSQL query cache is sufficient at this scale |
