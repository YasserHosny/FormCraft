# Research: Desk Search & Quick Fill

**Date**: 2026-05-26

## Decision: Search Implementation

**Chosen**: PostgreSQL materialized view with full-text search (`tsvector`) + `pg_trgm` for fuzzy matching + `unaccent` for diacritic normalization.

**Rationale**:
- Project already uses Supabase PostgreSQL; no additional infrastructure needed
- Materialized view provides fast reads for search (< 300ms target) while accepting 5-min staleness
- `pg_trgm` (trigram) extension handles fuzzy name matching efficiently
- `unaccent` extension normalizes Arabic diacritics (tashkeel) and accented Latin characters
- RLS can be applied by joining with existing tables in the materialized view definition

**Alternatives considered**:
- Client-side search (Fuse.js): rejected due to dataset size; operator desks may have 10k+ submissions
- ElasticSearch/Meilisearch: rejected; adds infrastructure overhead not justified for current scale
- Supabase Vector (pgvector): rejected; semantic search not required for this use case

## Decision: Quick Fill Mapping Strategy

**Chosen**: Configurable per-organization default mapping table with standard key conventions.

**Rationale**:
- Different organizations use different field keys (e.g., `national_id` vs `id_number`)
- A mapping table allows admins to customize without code changes
- Standard defaults cover 80%+ of common forms
- Case-insensitive matching simplifies frontend key normalization

**Alternatives considered**:
- Hardcoded mapping in frontend: rejected; not flexible across organizations
- AI-based field matching: rejected; over-engineered for current requirements
- Manual field linking per template: rejected; too much admin overhead

## Decision: Auto-Populated Data Handling

**Chosen**: Modifications remain local to submission; explicit "Save to Profile" action.

**Rationale**:
- Prevents accidental customer profile corruption from typos or test data
- Gives operator control over when to update the master record
- Aligns with common CRM patterns (draft vs. committed changes)
- Simplifies implementation (no need for dirty tracking on customer record)

## Decision: Search Permission Scope

**Chosen**: Respect existing RLS — templates in org, submissions in branch/department scope, customers org-wide.

**Rationale**:
- Consistent with existing security model
- Customer lookup across organization is required for cross-branch service
- Submission scope limits data exposure appropriately
- Materialized view can include `org_id`, `branch_id`, `department_id` columns for filtering

## Decision: Mixed-Script Search

**Chosen**: Normalize both query and indexed text with `unaccent` + Arabic diacritic removal + `pg_trgm`.

**Rationale**:
- Operators may type Arabic names in English or vice versa; exact transliteration is impossible, so fuzzy matching is best effort
- `unaccent` handles Latin accents; Arabic diacritics stripped via `regexp_replace` in view definition
- `pg_trgm` similarity threshold set to 0.3 for fuzzy matches
- Exact matches always rank higher than fuzzy matches

## Decision: Materialized View Refresh Strategy

**Chosen**: Refresh every 5 minutes via cron job or trigger-based refresh on significant changes.

**Rationale**:
- 5-minute staleness acceptable for search results (templates, customers change infrequently)
- Reference number exact match bypasses materialized view (direct table query)
- If refresh time exceeds 10s at scale, switch to concurrent refresh or incremental updates

## Performance Assumptions

- Expected dataset: 1,000 templates, 100,000 submissions, 50,000 customers per organization
- Materialized view size: ~200MB per org (acceptable)
- Search query target: < 50ms database time, < 300ms total with network
- Concurrent load: 50 concurrent operators = ~10-20 active searches/second (debounced)
