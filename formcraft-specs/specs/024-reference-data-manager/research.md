# Research: Reference Data Manager

**Date**: 2026-05-17

## Research Questions

No NEEDS CLARIFICATION items. Research focused on storage strategy, binding mechanism, auto-fill architecture, and searchable dropdown approach.

## Findings

### 1. Storage Strategy: Typed Column Schema in JSONB

**Options considered**:
1. Dedicated table per reference list (dynamic DDL) — rejected: unmanageable at scale, breaks RLS patterns
2. EAV (Entity-Attribute-Value) model — rejected: query complexity, poor performance for CSV import
3. JSONB with schema validation at application layer — selected

**Decision**: Store column schema as JSONB array on `reference_lists` table. Store entry values as JSONB object on `reference_entries` table keyed by column key. Validate entry values against schema at API layer (Pydantic dynamic model generation).

**Rationale**: JSONB is the established pattern in FormCraft (elements.formatting, elements.properties already use it). Schema-on-read with API validation gives flexibility for schema evolution without migrations per list.

### 2. Binding Storage: Element Formatting JSONB

**Current element model**: Each element row has a `formatting` JSONB column for renderer-specific configuration.

**Decision**: Store binding config in `formatting` under a `ref_binding` key:
```json
{
  "ref_binding": {
    "list_id": "uuid",
    "display_column": "name_ar",
    "value_column": "code",
    "search_threshold": 20,
    "clear_on_deselect": false,
    "auto_fill": [
      { "target_element_key": "swift_field", "source_column": "swift" }
    ]
  }
}
```

**Rationale**: No schema migration needed for elements table. Binding is a renderer configuration concern, fitting naturally in `formatting`. The Form Filler frontend reads `ref_binding` to determine dropdown behavior.

### 3. Searchable Dropdown: Client-Side vs Server-Side Filtering

**Options**:
1. Server-side search API (`GET /reference-lists/:id/entries?q=text`) — network latency per keystroke
2. Client-side filter on pre-fetched entries — instant filtering, higher initial load
3. Hybrid: pre-fetch up to 500 entries client-side, paginated server search for 500+

**Decision**: Hybrid approach. Lists with ≤500 active entries are fetched entirely on form load (cached 5-min). Lists with >500 entries use server-side search with debounced API calls (300ms). Threshold configurable per-list.

**Rationale**: Most FormCraft reference lists will be under 500 entries (governorates=27, banks≈40, branches≈200). Pre-fetching gives instant UX. The 500-entry server-side fallback handles outlier cases without loading massive datasets client-side.

### 4. Auto-Fill Execution: Frontend Event Architecture

**Decision**: Auto-fill executes in the Form Filler component's `onEntrySelected(entry)` handler. Steps:
1. Look up `ref_binding.auto_fill` array from element config
2. For each mapping, find target element by `target_element_key`
3. If target element is visible (per ConditionEngine from feature 021), set its value
4. Emit form value change events so dependent validations re-evaluate

**Integration with Feature 021 (Advanced Validation)**: Auto-filled values trigger the same reactive form valueChanges pipeline. Computed fields and conditional visibility re-evaluate automatically.

### 5. CSV Import: Parsing & Validation Pipeline

**Libraries**: Python `csv` module (stdlib) for parsing. No third-party dependency needed.

**Pipeline**:
1. Upload CSV to Supabase Storage temp bucket
2. Parse headers → attempt auto-mapping to column schema keys (case-insensitive match)
3. Validate each row against schema: type coercion, required check, enum membership
4. Return preview response: valid_count, invalid_count, errors[] with row number + column + message
5. On confirm: batch INSERT (100-row chunks) in a transaction
6. Delete temp file from Storage

**Update mode**: If list schema has a column marked `is_unique_key: true`, import can match existing entries and UPDATE instead of INSERT.

### 6. Audit Trail Integration

**Decision**: Use existing `audit_logs` table. New action types:
- `REFERENCE_LIST_CREATED`, `REFERENCE_LIST_UPDATED`, `REFERENCE_LIST_ARCHIVED`
- `REFERENCE_ENTRY_CREATED`, `REFERENCE_ENTRY_UPDATED`, `REFERENCE_ENTRY_DEACTIVATED`, `REFERENCE_ENTRY_REACTIVATED`
- `REFERENCE_ENTRIES_IMPORTED` (bulk, with count in metadata)

Entry updates record `old_values` and `new_values` diff in audit metadata JSONB.

### 7. Caching Strategy

**Decision**: Redis/in-memory LRU cache on active entries endpoint with 5-minute TTL, keyed by `(org_id, list_id)`. Cache invalidated on entry create/update/deactivate/import.

Form Desk frontend also caches fetched entries in an Angular service (in-memory) for the session, refreshing on form reload.
