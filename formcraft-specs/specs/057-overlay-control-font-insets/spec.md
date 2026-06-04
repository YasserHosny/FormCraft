# Feature Specification: Per-Control Font & Generic Line Insets for Overlay Forms

**Feature Branch**: `057-overlay-control-font-insets`
**Created**: 2026-06-05
**Status**: Draft
**Input**: Designer brainstorming — pre-printed forms (e.g., Al Baraka cheque) produce overlapping data, wrong fonts, and mispositioned tafqeet when printed. Designers need per-control font control and a generic multi-line inset model so values fit blank ruled areas that are interrupted by pre-printed labels.

## Background & Problem

FormCraft already supports the upstream flow: a designer uploads a scanned form, OCR detects regions (`026-form-import-ocr`), accepted detections become absolutely-positioned elements, and overlay/print modes exist (`023-overlay-print-mode`). The PDF renderer already positions every element absolutely (`position: absolute; left: x_mm; top: y_mm`).

Three concrete gaps remain, all confirmed in the renderer:

1. **Font is hardcoded.** `base.py::_base_style` emits a fixed `font-size: 10pt` and a fixed Noto family for every control. Designers cannot match the pre-printed label style, and values too large for their box overflow.
2. **Tafqeet text spills onto neighbors.** `tafqeet_renderer.py` replaces `overflow: hidden` with `overflow: visible` unconditionally, so long amounts bleed out of their box and overlap adjacent controls (the reported bug).
3. **No line-inset model.** A pre-printed writing area is often *not* a clean rectangle: line 1 is indented on the left by a label ("The sum of"), and the last line is indented on the right by another label ("بالحروف"). A single bounding box would cover the labels. There is no way to inset individual lines.

This feature closes all three gaps without introducing a new designer flow. It extends the existing element model, Properties panel, and PDF renderer.

## Scope Principles

- **No new flow.** Reuse the existing OCR-import + overlay-print pipeline and the existing Design Studio Properties panel.
- **No DB migration.** All new settings live under the existing free-form `element.formatting` JSON dict.
- **Generic, not tafqeet-specific.** The line-inset model applies to *any* multi-line-capable control. Tafqeet inherits it like every other element.
- **Renderer parity.** The Design Studio canvas preview and the WeasyPrint PDF output must render font and insets identically.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Per-Control Font Styling (Priority: P1)

A designer selects an overlay control and sets its font family, size, weight, and color in the Properties panel so the printed value visually matches the pre-printed label beside it. The setting is stored per element and applied identically in the canvas preview and the generated PDF.

**Why this priority**: The reported "inadequate font" and overlap symptoms both stem from a hardcoded 10pt font. Per-control font is the single highest-leverage fix.

**Independent Test**: Open a control → set font to `Courier`, `13px`, `Bold` → save → generate PDF → verify the value renders in Courier 13px bold (not Noto 10pt) at the control's position.

**Acceptance Scenarios**:

1. **Given** a control is selected, **When** the designer opens the Properties panel, **Then** a Font section shows family, size, weight, style, and color inputs.
2. **Given** a designer sets font family/size/weight/color, **When** the element is saved, **Then** the values persist under `formatting.font` and survive reload.
3. **Given** a control has a custom font set, **When** a PDF is generated, **Then** the rendered text uses that font instead of the default 10pt Noto.
4. **Given** a control has NO custom font, **When** a PDF is generated, **Then** the current default (Noto 10pt) is used — existing templates render unchanged.
5. **Given** the designer changes the font, **When** the canvas preview refreshes, **Then** the preview reflects the new font without a full reload.

---

### User Story 2 — Generic Line Insets (Priority: P1)

A designer configures, on any control, how many text lines the box holds and an optional left/right inset per line (or first-line / last-line shorthand). Lines whose ruled area is interrupted by a pre-printed label are inset to clear the label. The setting is generic and not specific to tafqeet.

**Why this priority**: This is the geometry problem that a single rectangle cannot solve. Without it, multi-line values either cover pre-printed labels or wrap incorrectly.

**Independent Test**: On a 2-line tafqeet control over the Al Baraka cheque, set first-line left-inset = 22mm and last-line right-inset = 26mm → generate PDF → verify line 1 starts clear of "The sum of" and line 2 ends clear of "بالحروف", with neither label covered.

**Acceptance Scenarios**:

1. **Given** any control, **When** the designer opens the Properties panel, **Then** a Line Layout section exposes max lines and per-line (or first/last) left/right inset inputs in mm.
2. **Given** a control with first-line left-inset = N, **When** rendered, **Then** the first wrapped line begins N mm from the box's left edge while subsequent lines start at the box edge.
3. **Given** a control with last-line right-inset = M, **When** rendered, **Then** the final line's available width is reduced by M mm on the right.
4. **Given** insets are zero/unset (default), **When** rendered, **Then** all lines use the full box width — existing templates render unchanged.
5. **Given** insets are set, **When** the canvas preview refreshes, **Then** the preview shows the same staggered line geometry as the PDF.
6. **Given** a non-tafqeet text control with a long value, **When** max lines and insets are set, **Then** the same inset behavior applies — confirming the model is generic.

---

### User Story 3 — Overflow / Fit Policy (Priority: P2)

A designer chooses how a control behaves when its content exceeds the box: **clip** (hide overflow), **shrink-to-fit** (auto-reduce font size until it fits), or **visible** (current spill behavior, retained for back-compat). This replaces the unconditional `overflow: visible` that causes the reported overlap.

**Why this priority**: Even with correct fonts and insets, an unexpectedly long value must fail gracefully instead of bleeding onto neighbors. Shrink-to-fit directly prevents the screenshot's overlap.

**Independent Test**: Set a tafqeet control to `shrink-to-fit`, feed an amount whose words exceed the box at the chosen size → generate PDF → verify the text auto-reduces to fit within the box bounds and does not overlap adjacent controls.

**Acceptance Scenarios**:

1. **Given** a control, **When** the designer opens the Properties panel, **Then** an Overflow setting offers clip / shrink-to-fit / visible.
2. **Given** `clip`, **When** content exceeds the box, **Then** the overflow is hidden (no spill onto neighbors).
3. **Given** `shrink-to-fit`, **When** content exceeds the box at the configured size, **Then** the renderer reduces font size (down to a configurable minimum) until the content fits.
4. **Given** `visible`, **When** content exceeds the box, **Then** behavior matches today (spill allowed) — explicit opt-in only.
5. **Given** an existing tafqeet element with no overflow setting, **When** rendered, **Then** the default policy applies (see Edge Case #4) without breaking current outputs.

---

### User Story 4 — AI Font & Inset Suggestion (Priority: P3)

The designer clicks "Match font" on a selected overlay control. A vision pass samples the background-image region near the control (and its neighboring pre-printed label) and suggests font family/size/weight and any label-induced line insets. The designer accepts or edits the suggestion; nothing is applied without confirmation.

**Why this priority**: A convenience layer on top of P1/P2. The manual controls must work independently; AI only pre-populates them.

**Independent Test**: With a cheque background loaded, select the tafqeet control → click "Match font" → verify a suggestion populates the Font and Line Layout fields, and the designer can accept or discard it.

**Acceptance Scenarios**:

1. **Given** a control over a page with a background image, **When** the designer clicks "Match font", **Then** the system returns suggested font + inset values and shows them as a preview the designer can accept or reject.
2. **Given** the designer accepts a suggestion, **When** applied, **Then** the values populate `formatting.font` / `formatting.lineLayout` exactly as if entered manually.
3. **Given** the page has no background image, **When** the designer looks for "Match font", **Then** the action is disabled with an explanatory tooltip.
4. **Given** the vision service is unavailable, **When** the designer clicks "Match font", **Then** a clear error is shown and manual fields remain editable.

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Each element may store `formatting.font` = { family, size_pt, weight, style, color } | P1 |
| FR-02 | PDF renderer applies `formatting.font` per element, falling back to the current default (Noto 10pt) when absent | P1 |
| FR-03 | Properties panel exposes font family/size/weight/style/color for the selected control | P1 |
| FR-04 | Each element may store `formatting.lineLayout` = { maxLines, lines: [{ leftInsetMm, rightInsetMm }], firstLineLeftInsetMm, lastLineRightInsetMm } | P1 |
| FR-05 | Renderer applies per-line left/right insets in mm; absent/zero insets use full box width | P1 |
| FR-06 | Line-inset model is element-type-agnostic (works for text, tafqeet, currency, etc.) | P1 |
| FR-07 | Each element may store `formatting.overflow` = clip \| shrink-to-fit \| visible | P2 |
| FR-08 | `shrink-to-fit` reduces font size down to `formatting.font.minSizePt` (configurable, sensible default) until content fits the box | P2 |
| FR-09 | Replace the unconditional `overflow: visible` in tafqeet rendering with the configured overflow policy | P2 |
| FR-10 | Canvas preview in Design Studio renders font, insets, and overflow identically to the PDF | P1 |
| FR-11 | "Match font" AI action returns suggested font + insets for a control, applied only on designer confirmation | P3 |
| FR-12 | "Match font" is disabled when the page has no background image | P3 |
| FR-13 | All new settings persist under the existing `element.formatting` dict (no schema migration) | P1 |
| FR-14 | Templates with no new settings render byte-for-byte as today (backward compatible) | P1 |

## Non-Functional Requirements

| ID | Requirement | Metric |
|----|-------------|--------|
| NFR-01 | Per-control font/inset rendering adds no measurable overhead vs current PDF generation | < 50ms added per page |
| NFR-02 | Inset precision honored to 0.1mm in generated PDF | ±0.1mm |
| NFR-03 | shrink-to-fit converges deterministically (same input → same final size) | Deterministic |
| NFR-04 | New `formatting` keys validated; unknown/garbage values ignored, never crash the renderer | Zero render crashes |
| NFR-05 | Canvas-preview vs PDF font/inset divergence is imperceptible at 100% zoom | Visual parity |

## Edge Cases

| # | Case | Handling |
|---|------|----------|
| 1 | Font size set larger than the box height | Honored as-is unless overflow=shrink-to-fit, which reduces it |
| 2 | Inset larger than box width (left+right ≥ width) | Clamp so usable width ≥ a minimum; warn in Properties panel |
| 3 | maxLines exceeded by content | Apply overflow policy (clip/shrink/visible) to the surplus |
| 4 | Existing tafqeet element with no overflow setting | Default policy = `shrink-to-fit` for tafqeet (prevents today's overlap); `clip` for plain text; documented and configurable |
| 5 | Custom font family not bundled in WeasyPrint font set | Fall back to nearest bundled family; surface a designer warning |
| 6 | RTL/Arabic line with insets | Insets are physical left/right (not logical start/end) so they map to printed geometry regardless of direction |
| 7 | "Match font" on a low-res / noisy background region | Return low-confidence suggestion flagged as such; designer edits manually |
| 8 | Overlay print mode + custom font | Font travels with the element into overlay output unchanged |

## Success Criteria

- A designer reproduces the Al Baraka cheque tafqeet correctly: two lines, line 1 clears "The sum of", line 2 clears "بالحروف", value in a font matching the pre-printed label, no overlap with neighboring controls.
- Setting a per-control font visibly changes the PDF output and matches the canvas preview.
- A deliberately oversized value under `shrink-to-fit` fits inside its box in the PDF with no spill.
- Existing templates (no new settings) generate identical PDFs to the pre-feature baseline.
- The same inset settings work on a plain text control as on tafqeet, proving genericity.

## Clarifications

### Session 2026-06-05

- **Q**: What is the sensible default for `formatting.font.minSizePt` in FR-08?  
  **A**: 6pt. This is the minimum readable font size for printed Arabic text on pre-printed forms while preserving legibility. The renderer will never shrink below 6pt; if content still does not fit, the overflow policy takes over.
- **Q**: How should the Design Studio canvas preview (Konva.js) reflect per-control font and line-inset changes?  
  **A**: Font family, size, weight, style, and color are applied directly to the `Konva.Text` node of the selected element. Line insets are simulated by adjusting the effective text width of each wrapped line in the preview; the preview must visually match the PDF geometry at 100% zoom.
- **Q**: Which font families should the Properties panel dropdown offer, given the current bundled font set?  
  **A**: The dropdown lists the four bundled families (`Noto Naskh Arabic`, `Noto Sans`, `Courier`, `Arial`) plus a "Custom" option that allows free-text entry. Custom families are passed to WeasyPrint as-is; if the family is not available on the server, WeasyPrint falls back to the default sans-serif and the designer sees a warning toast.
- **Q**: Should the "Match font" AI suggestion (P3) be built in this increment?  
  **A**: No — it is deferred to a follow-up feature. The manual Font and Line Layout controls must work independently. When the follow-up is planned, it must respect Constitution Principle III (AI suggestion, never auto-apply) and use the existing `POST /ai/suggest-control` endpoint pattern rather than introducing a new AI service.
- **Q**: For Edge Case #4 (existing tafqeet with no overflow setting), what is the precise default?  
  **A**: Tafqeet default = `shrink-to-fit` (prevents the current overlap bug). Plain text default = `clip`. These defaults are hard-coded in the renderer when `formatting.overflow` is absent; they are not persisted to the database to keep the "no migration" guarantee.

## Out of Scope

- Changing the OCR detection engine or the accept/reject review UI (`026`).
- Printer offset calibration (`023`, unchanged).
- Rich text / per-character styling within a single control (only whole-control font).
- Polygon / arbitrary-shape flow regions (insets cover the staggered-rectangle case; freeform polygons are explicitly deferred).
- Auto-applying AI suggestions without designer confirmation.
- The "Match font" AI suggestion action (P3) — deferred to a future feature that extends `POST /ai/suggest-control`.

## Dependencies & Touch Points

- **Backend renderer**: `app/services/pdf/element_renderers/base.py` (`_base_style` font + inset injection), `tafqeet_renderer.py` (overflow policy, per-line insets), `text_renderer.py` and siblings (inherit font), `html_builder.py` (no structural change expected).
- **Backend schema**: `app/schemas/element.py` — settings ride inside existing `formatting: dict`; optional typed sub-models for validation only.
- **Frontend**: Design Studio Properties panel (new Font / Line Layout / Overflow sections), canvas preview renderer (parity), AI "Match font" action wiring.
- **Reuses**: `023-overlay-print-mode`, `026-form-import-ocr` (background image + coordinate mapping), existing tafqeet converter and font registry (`app/services/pdf/fonts.py`).
