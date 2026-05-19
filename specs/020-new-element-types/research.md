# Research: New Element Types (Signature & Table)

**Date**: 2026-05-17

## Research Questions

No NEEDS CLARIFICATION items. Research focused on signature capture library, signature storage strategy, table data model, and PDF rendering for both element types.

## Findings

### 1. Signature Capture Library

**Options considered**:
1. `signature_pad` (npm) — lightweight canvas-based library, MIT license, 14KB gzipped
2. Custom canvas implementation — more control but significant effort
3. `ngx-signaturepad` — Angular wrapper around signature_pad

**Decision**: Use `signature_pad` directly (no Angular wrapper needed). Create an Angular component that wraps the canvas element and exposes the signature as a PNG data URL via `toDataURL('image/png')`. The library handles touch/mouse events, pressure sensitivity, and smooth line rendering.

### 2. Signature Storage Strategy

**Options**:
1. Inline data URL in submission JSONB (simple, limited size)
2. Upload to Supabase Storage, store URL in submission (scalable)
3. Hybrid: inline if < 100KB, Storage if larger

**Decision**: Hybrid approach. Most signatures are 20-50KB as PNG. Store inline as data URL for signatures under 100KB (avoids Storage round-trip). Upload to Supabase Storage `signatures/` bucket for larger ones (rare). The submission JSONB field stores either `{ "type": "inline", "data": "data:image/png;base64,..." }` or `{ "type": "storage", "path": "signatures/org_id/submission_id/element_key.png" }`.

### 3. Table Data Model in Submissions

**Decision**: Table element values stored as JSONB array of row objects in the submission data, keyed by element_key:

```json
{
  "expense_table": [
    { "description": "Office supplies", "amount": 150.00, "date": "2026-05-01" },
    { "description": "Travel", "amount": 2500.00, "date": "2026-05-10" }
  ]
}
```

Column keys from the table schema are used as object keys. This is consistent with how other element types store their values (by element_key in submission data JSONB).

### 4. Table PDF Rendering

**Challenge**: Tables can exceed page height. WeasyPrint supports `page-break-inside: avoid` for rows and automatic table continuation across pages with repeated `<thead>`.

**Decision**: Render table as HTML `<table>` within an absolutely-positioned container at the element's mm coordinates. For tables that overflow the page element boundaries:
- Use CSS `page-break-inside: avoid` on `<tr>` to prevent mid-row splits
- If table height exceeds remaining page space, let WeasyPrint flow it to the next page
- Repeat `<thead>` on continuation pages via standard HTML table semantics

### 5. ElementType Enum Expansion

Current enum values (11): text, number, date, checkbox, radio, dropdown, textarea, image, label, barcode, qr_code

**New values**: `signature`, `table`

**Migration**: Expand the CHECK constraint on elements.type to include the new values. This follows the same pattern as previous enum expansions.

### 6. Element Renderer Pattern

Both new types need:
- **Backend HTML renderer** (for PDF): `SignatureHTMLRenderer`, `TableHTMLRenderer` extending `ElementHTMLRenderer` ABC
- **Frontend form component**: Angular components registered in the form filler's element type switch

The renderer registry in `html_builder.py` maps ElementType → renderer class. New renderers implement `render(element, data)` returning HTML string.

### 7. Signature in PDF

The signature PNG is rendered as an `<img>` tag with absolute positioning:
```html
<img src="data:image/png;base64,..." 
     style="position: absolute; left: {x_mm}mm; top: {y_mm}mm; 
            width: {width_mm}mm; height: {height_mm}mm; object-fit: contain;" />
```

For Storage-referenced signatures, the PDF service fetches the image and inlines it during rendering.
