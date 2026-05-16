# Plan: Template Versioning & Cloning

**Feature**: 018-template-versioning  
**Date**: 2026-05-16

## Architecture Overview

This feature extends the existing template system with:
1. Expanded lifecycle state machine (7 states with validated transitions)
2. Lineage tracking (all versions of a template linked via `lineage_id`)
3. Review workflow (submit → approve/reject cycle with comments)
4. Template cloning (independent copy with new identity)
5. Version diff (on-demand element-by-element comparison)

## Technical Approach

### State Machine (Backend)

A transition validation map in `template_service.py` defines allowed transitions. The `transition_status()` method:
1. Loads current template status
2. Validates transition against the map
3. Validates role permissions for the transition
4. Updates status atomically
5. Creates audit log entry
6. If approve/reject: creates `template_reviews` row

No external state machine library — the transition map is a simple dict.

### Lineage Tracking

- `lineage_id` column (UUID): all versions of a template share this value
- For new templates (fresh creation): `lineage_id = id` (self-referencing root)
- For versioned templates (`create_new_version`): inherits source's `lineage_id`
- For cloned templates: `lineage_id = new_id` (new independent lineage)
- `parent_version_id`: direct FK to the source template row

### Immutability Enforcement

All template/page/element mutation endpoints gain a status check:
- If `template.status` not in `['draft', 'rejected']`: return 403
- Applied at the service layer (single enforcement point), not at each route individually

### Form Desk Resolution

Dashboard query uses `DISTINCT ON (lineage_id)` with `WHERE status IN ('published', 'deprecated')` to show only the latest published version per family. Deprecated templates include `is_deprecated: true` flag.

### Diff Computation

On-demand comparison between two template versions:
1. Load elements for both versions (via template IDs)
2. Match elements by `key` (stable identifier across versions)
3. For matched keys: compare all numeric/text properties
4. Report: added (in v2 not v1), removed (in v1 not v2), modified (in both, different values)
5. Also compare pages by `sort_order` for page-level changes

### Frontend Changes

- **Design Studio**: Status badges, "Submit for Review" / "Create New Version" / "Clone" buttons in template toolbar
- **Admin Console**: Review queue (templates awaiting approval), approve/reject actions
- **Version History Panel**: Slide-over or modal showing all versions in lineage with timeline
- **Diff View**: Side-by-side or unified view showing element changes

## Phases

1. **Migration & Enum**: Add columns, expand status enum, create reviews table
2. **Backend State Machine**: Transition service, immutability guard, audit integration
3. **Backend Versioning**: Update create_new_version with lineage, add clone, history, diff endpoints
4. **Frontend Lifecycle UI**: Status badges, transition buttons, review queue
5. **Frontend Version History**: History panel, diff view
6. **Frontend Cloning**: Clone dialog, template library update
7. **Form Desk Integration**: Latest-version resolution, deprecated warning
8. **Polish**: RTL, edge cases, empty states

## Constraints

- **Backward compatibility**: Existing templates get `lineage_id = id` via backfill; no breaking changes to existing API consumers
- **No separate versions table**: Each template row IS a version (existing architecture preserved)
- **Review workflow is lightweight**: No multi-step approval chains; single reviewer approve/reject per submission
- **Diff is read-only**: No "apply diff" or "merge" functionality — this is for audit/compliance viewing only

## Risks

| Risk | Mitigation |
|------|-----------|
| Backfill migration on large templates table | Migration runs UPDATE in batches; templates table is small (< 10K rows typical) |
| Multiple concurrent new-version creation | Each creates independent draft; version number determined at publish time based on max(version) in lineage |
| Breaking existing API consumers | Status CHECK expansion is additive; existing 'draft'/'published' values still valid |
| Performance of DISTINCT ON for Form Desk | Partial index `idx_templates_lineage_published` ensures fast lookup |
