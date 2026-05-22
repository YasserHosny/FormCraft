# Research: Submission History & Reprint

**Date**: 2026-05-16

## Research Questions

No NEEDS CLARIFICATION items. Research focused on reprint watermark implementation and clone mapping strategy.

## Findings

### 1. WeasyPrint Watermark Support

WeasyPrint supports CSS `@page` rules with background-image or generated content. A diagonal "REPRINT" watermark can be implemented as:

```css
@page {
  @top-center {
    content: "";
  }
  background-image: none;
}
/* For reprint mode: */
@page {
  background: url('data:image/svg+xml,...') center center no-repeat;
}
```

Alternative: inject an SVG watermark as a positioned `<div>` in the HTML before rendering. This gives more control over rotation, opacity, and positioning.

**Decision**: Use an injected SVG-based watermark div (absolute positioned, rotated 45deg, 20% opacity, large font) in the HTML template. This is more portable than `@page` rules and gives precise control over appearance.

### 2. Template Version Retrieval

The existing templates table stores `version` as an INT that increments on publish. For reprint, we need to load the template at a specific version. Two approaches:

1. Templates table keeps all versions as separate rows (version is part of the natural key)
2. Template versioning creates new rows on each publish (id stays same, version increments)

From examining the existing code (`publish_template` just updates status to "published" on the same row), it appears **versions are NOT stored as separate rows** — publishing updates the existing template in place. This means:

**Problem**: If a template is edited after publication, the original version data is lost.

**Implication for reprints**: The `field_values` JSONB in submissions already stores all the operator's data. For reprints, we need the element *positions* (x_mm, y_mm) from the original version for PDF rendering.

**Decision**: This confirms that Template Versioning (roadmap item 1.7) is a prerequisite for perfect reprints. For now, reprints will use the *current* template version's positions. If positions haven't changed (common case), the reprint is identical. This is acceptable for MVP — perfect version-pinned reprints come with feature 1.7.

### 3. Submission Listing Performance

With index on `(operator_id, created_at DESC)` and RLS by org_id, the pagination query is:

```sql
SELECT s.*, t.name as template_name
FROM submissions s
JOIN templates t ON s.template_id = t.id
WHERE s.org_id = ?
ORDER BY s.created_at DESC
LIMIT 25 OFFSET ?
```

For 1000 rows per operator, this is fast (< 50ms). For org-wide queries (branch manager view), the org_id index handles it.

Search by reference_number uses the unique index — O(1) lookup.

### 4. Key Field Summary

The history table shows "first 3 field values" for quick identification. This requires:
- Knowing which fields are "key" fields
- Or simply taking the first 3 non-empty values from field_values

**Decision**: Take the first 3 elements by sort_order that have non-empty values in field_values. This requires joining template elements at query time or precomputing a `key_summary` column.

**Chosen**: Compute at query time (join with elements, order by sort_order, limit 3). For 25 submissions per page, this is < 50ms. No denormalization needed.

**Revised**: Actually, since field_values is JSONB and elements may change, compute the summary in the API response serializer (Python code, not SQL). Extract first 3 keys from field_values in the order they appear in the template's element sort_order.

## Alternatives Considered

| Option | Rejected Because |
|--------|-----------------|
| Store PDF binary on every submission | 100KB × 200 forms/day × 50 operators = 1GB/day storage; re-rendering is fast and free |
| Client-side PDF generation for reprints | Arabic text rendering unreliable in jsPDF; WeasyPrint already works |
| Denormalize key_summary into submissions table | Adds write complexity on insert; data duplicated; summary changes if template changes (wrong) |
| Image-based watermark in WeasyPrint | More complex than SVG overlay; harder to customize text, rotation, opacity |
| Store full template snapshot in submission | Bloats JSONB from 2KB to 50KB+; template versioning (feature 1.7) is the proper solution |
