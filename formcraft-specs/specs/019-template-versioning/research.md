# Research: Template Versioning & Cloning

**Date**: 2026-05-16

## Research Questions

No NEEDS CLARIFICATION items. Research focused on lineage tracking strategy, state machine enforcement, and diff computation approach.

## Findings

### 1. Existing Version Mechanism

The current `create_new_version()` in `template_service.py` (line 284) already:
- Creates a new template row with incremented version
- Copies all pages and elements
- Only works on published templates (enforced with 400 error)

**Gap**: It creates a new row with a NEW `id` (UUID). There is no `lineage_id` or `parent_version_id` linking versions together. The new template appears as a completely independent entity in the library.

**Decision**: Add `lineage_id` (UUID) and `parent_version_id` (UUID, nullable) columns to the templates table. When the first version is created (or for existing templates without a lineage), `lineage_id` defaults to the template's own `id`. When `create_new_version()` is called, the new row inherits the source's `lineage_id` and sets `parent_version_id` to the source's `id`.

### 2. State Machine Enforcement

Current state: only `draft` and `published` in the `TemplateStatus` enum. The DS-08 vision adds: `submitted_for_review`, `approved`, `rejected`, `archived`, `deprecated`.

**Approach options**:
1. Enum expansion + transition validation in service layer (Python code)
2. PostgreSQL CHECK constraint with allowed transitions
3. State machine library (e.g., `transitions` package)

**Decision**: Enum expansion + service-layer validation. The state machine is simple enough (7 states, ~10 transitions) that a library is overkill. Service method `transition_status(template_id, new_status, actor_id, comment?)` validates the transition against an allowed-transitions map and raises 422 on invalid transitions. PostgreSQL CHECK constraint ensures only valid status values at DB level.

**Transition map**:
```
draft → submitted_for_review
submitted_for_review → approved, rejected
approved → published
rejected → draft
published → archived, deprecated
archived → published (un-archive)
deprecated → archived
```

### 3. Diff Computation Strategy

Two approaches for computing differences between versions:

1. **Stored diff**: compute and store diff JSON at publish time
2. **Computed diff**: compute on-demand when user requests comparison

**Decision**: Compute on-demand. Reasons:
- Storage of diffs duplicates element data (bloat)
- Diffs may need to be recomputed if the diff format evolves
- With indexed element keys and max ~200 elements per template, computation is fast (< 100ms)
- Algorithm: load both versions' elements, match by `key`, compare all properties

**Diff algorithm**:
```python
def compute_diff(v1_elements, v2_elements):
    v1_map = {e.key: e for e in v1_elements}
    v2_map = {e.key: e for e in v2_elements}
    added = [e for k, e in v2_map.items() if k not in v1_map]
    removed = [e for k, e in v1_map.items() if k not in v2_map]
    modified = []
    for key in v1_map.keys() & v2_map.keys():
        changes = diff_properties(v1_map[key], v2_map[key])
        if changes:
            modified.append({"key": key, "changes": changes})
    return {"added": added, "removed": removed, "modified": modified}
```

### 4. Form Desk Version Resolution

Form Desk needs to show only the latest published version per lineage. Two approaches:

1. **Query-time filtering**: `SELECT DISTINCT ON (lineage_id) ... WHERE status = 'published' ORDER BY lineage_id, version DESC`
2. **Materialized view or flag**: `is_latest_published` boolean column

**Decision**: Query-time filtering with PostgreSQL `DISTINCT ON`. This avoids maintaining a flag that could become inconsistent. The query is performant with an index on `(lineage_id, version DESC)` and the templates table is small (< 10K rows per org).

### 5. Rejection Comments Storage

Options:
1. JSONB column on templates (`review_comments` array)
2. Separate `template_reviews` table

**Decision**: Separate `template_reviews` table. Reasons:
- Multiple review cycles possible (submit → reject → resubmit → reject → resubmit → approve)
- Each review event has: reviewer_id, action (approve/reject), comment, timestamp
- Clean audit trail separate from template data
- Supports future features like threaded review discussions

### 6. Backward Compatibility

Existing templates have no `lineage_id` or `parent_version_id`. Migration strategy:
- Add columns as NULLABLE
- Backfill: SET `lineage_id = id` for all existing templates (each is its own lineage root)
- `parent_version_id` stays NULL for existing templates (they have no tracked parent)
- Going forward, `create_new_version()` sets both columns

## Alternatives Considered

| Option | Rejected Because |
|--------|-----------------|
| Git-like branching model for templates | Over-engineering for form templates; linear versioning is sufficient |
| Store full template snapshots in a versions table | Duplicates data already in templates table; each template row IS a version |
| Auto-publish after approval (no separate publish step) | Banks require explicit publish control — approval means "ready" not "live" |
| Version numbers as semver (1.2.3) | Adds complexity without value — forms don't have patch vs. minor vs. major changes meaningful to end users |
| Soft-delete instead of archive/deprecated states | Loses the distinction between "hidden but valid" (archived) and "visible with warning" (deprecated) |
| Store diff at publish time | Bloats storage, diffs may need reformatting, on-demand computation is fast enough |
