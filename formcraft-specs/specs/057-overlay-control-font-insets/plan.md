# Implementation Plan: Per-Control Font & Generic Line Insets for Overlay Forms

**Branch**: `057-overlay-control-font-insets` | **Date**: 2026-06-05 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/057-overlay-control-font-insets/spec.md`

## Summary

Extend the existing overlay print pipeline so designers can set per-control font styling (family, size, weight, style, color) and generic line insets (left/right per line or first/last shorthand) on any element. Replace the unconditional `overflow: visible` in tafqeet rendering with a configurable overflow policy (`clip`, `shrink-to-fit`, `visible`). All settings ride inside the existing free-form `element.formatting` JSON dict — no database migration required. Canvas preview in the Design Studio must render font and insets identically to the WeasyPrint PDF output.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript / Angular 19 (frontend)  
**Primary Dependencies**: FastAPI, Pydantic, WeasyPrint, Konva.js, Angular Material, ngx-translate  
**Storage**: Supabase PostgreSQL (no schema change)  
**Testing**: pytest (backend), Angular TestBed + Jasmine (frontend)  
**Target Platform**: Linux server (Bunny Magic Containers), modern browsers  
**Project Type**: Web application (frontend + backend + specs polyrepo)  
**Performance Goals**: PDF generation adds < 50 ms per page (NFR-01)  
**Constraints**: Pixel-perfect print fidelity (mm precision), Arabic-first RTL, zero DB migration  
**Scale/Scope**: Per-element formatting fields, existing templates unchanged  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arabic-First, RTL-Native | ✓ PASS | Insets are physical left/right (not logical start/end) per Edge Case #6; RTL text alignment is preserved |
| II. Pixel-Perfect Print Fidelity | ✓ PASS | All positioning stays in mm; WeasyPrint handles Arabic shaping natively; font embedding required |
| III. AI Suggestion, Never Auto-Apply | ✓ PASS | P3 "Match font" is deferred; manual controls work independently |
| IV. Deterministic Over Probabilistic | ✓ PASS | `shrink-to-fit` is deterministic iterative reduction |
| V. Test-First Development | ✓ PASS | Plan includes test tasks before implementation for each story |
| VI. Normalized Data Model | ✓ PASS | No DB migration; formatting rides in existing JSON dict; optional Pydantic sub-models for validation only |
| VII. Translation-Key Architecture | ✓ PASS | All new UI labels use translation keys |
| VIII. Security and Auditability | ✓ PASS | No new endpoints; no auth changes |
| IX. Simplicity and YAGNI | ✓ PASS | No new flows, no AI service, no bulk automation |

**Re-check post-design**: No violations introduced.

## Project Structure

### Documentation (this feature)

```text
specs/057-overlay-control-font-insets/
├── plan.md              # This file
├── research.md          # Not required — technology choices are constrained by existing stack
├── data-model.md        # Not required — no new DB entities
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
# Backend
formcraft-backend/
├── app/
│   ├── schemas/
│   │   └── element.py              # Optional typed Formatting sub-models (validation only)
│   └── services/
│       └── pdf/
│           ├── fonts.py            # Font family resolution + fallback
│           └── element_renderers/
│               ├── base.py         # _base_style reads formatting.font
│               ├── text_renderer.py # Inherit font + line insets
│               └── tafqeet_renderer.py # Overflow policy + per-line insets

# Frontend
formcraft-frontend/
├── src/
│   ├── app/
│   │   ├── features/
│   │   │   └── designer/
│   │   │       ├── components/
│   │   │       │   └── formatting-property-panel/
│   │   │       │       ├── formatting-property-panel.component.ts
│   │   │       │       ├── formatting-property-panel.component.html
│   │   │       │       └── formatting-property-panel.component.scss
│   │   │       ├── designer-page/
│   │   │       │   └── designer-page.component.html  # Wire formatting panel
│   │   │       └── services/
│   │   │           └── canvas.service.ts             # Konva font/inset preview
│   │   └── assets/
│   │       └── i18n/
│   │           ├── ar.json                           # New translation keys
│   │           └── en.json                           # New translation keys
│   └── tests/  (existing test structure)
```

**Structure Decision**: Existing polyrepo structure. Backend changes are confined to PDF renderer services and optional schema validation. Frontend changes are confined to the Design Studio feature module.

## Complexity Tracking

> No constitution violations. Complexity is minimal because the feature reuses existing infrastructure (formatting dict, WeasyPrint absolute positioning, Konva canvas).

## Architecture

### Backend

1. **Font Injection in `_base_style`**  
   `base.py::_base_style` currently hardcodes `font-family: 'Noto Naskh Arabic', 'Noto Sans', sans-serif; font-size: 10pt;`. It will read `element.get('formatting', {}).get('font', {})` and emit the corresponding CSS. If absent, it falls back to the current default.

2. **Line Inset Model**  
   `formatting.lineLayout` stores `maxLines`, `firstLineLeftInsetMm`, `lastLineRightInsetMm`, and optionally a full `lines` array. The renderer converts these to CSS `padding-left` / `padding-right` on individual `<p>` or `<span>` elements (one per wrapped line). Because WeasyPrint uses absolute positioning on the outer `<div>`, internal padding controls the usable width per line without affecting the outer box position.

3. **Overflow / Fit Policy**  
   - `clip`: keep `overflow: hidden` (default for plain text).  
   - `visible`: replace with `overflow: visible` (current tafqeet behavior, now explicit).  
   - `shrink-to-fit`: iteratively reduce `font-size` (down to `minSizePt` or 6pt) and re-render until the content fits within the box width/height, or the minimum size is reached. The loop is deterministic: same input → same final size.  
   - Default for tafqeet when absent: `shrink-to-fit`.  
   - Default for plain text when absent: `clip`.

4. **Font Resolution & Fallback**  
   `fonts.py` gains a `resolve_font_family(name: str) -> str` function that maps common names to bundled `@font-face` families. If the name is not bundled, it returns the name as-is (WeasyPrint will use system fallback) and logs a warning.

### Frontend

1. **Formatting Property Panel**  
   A new `FormattingPropertyPanelComponent` that appears for **all** element types (not just tafqeet/signature/table) when an element is selected. It exposes:
   - **Font**: family (dropdown + custom), size (pt), weight (normal/bold), style (normal/italic), color (color picker), min size for shrink-to-fit.
   - **Line Layout**: max lines, first-line left inset (mm), last-line right inset (mm).
   - **Overflow**: `clip` / `shrink-to-fit` / `visible`.

2. **Canvas Preview Parity**  
   `canvas.service.ts` `updateElementVisual` and `addElementInternal` read `data['formatting']` and apply:
   - `Konva.Text.fontFamily`, `fontSize`, `fontStyle`, `fill`
   - Line insets simulated by temporarily reducing `Konva.Text.width` and offsetting `x` for the first/last line. Konva does not support per-line padding natively, so the preview approximates by drawing the text with adjusted width constraints.

## Data Model

No new database entities. Optional Pydantic sub-models for request/response validation:

```python
class FontSettings(BaseModel):
    family: str | None = None
    size_pt: float | None = Field(default=None, ge=1, le=128)
    weight: Literal["normal", "bold"] | None = None
    style: Literal["normal", "italic"] | None = None
    color: str | None = None  # hex or css color
    min_size_pt: float | None = Field(default=6.0, ge=1, le=128)

class LineLayout(BaseModel):
    max_lines: int | None = Field(default=None, ge=1, le=100)
    first_line_left_inset_mm: float | None = Field(default=None, ge=0)
    last_line_right_inset_mm: float | None = Field(default=None, ge=0)

class ElementFormatting(BaseModel):
    font: FontSettings | None = None
    line_layout: LineLayout | None = None
    overflow: Literal["clip", "shrink-to-fit", "visible"] | None = None
```

These models are **not** persisted as typed columns; they validate the free-form `formatting` dict on API boundaries.

## API Contracts

No new endpoints. Existing `PATCH /templates/{id}/pages/{page_id}/elements/{element_id}` and `POST /templates/{id}/pages/{page_id}/elements` already accept `formatting: dict`. The optional Pydantic sub-models add server-side validation for the new keys without changing the contract shape.

## Testing Strategy

- **Backend unit tests**: `test_element_renderers.py` — test `_base_style` font injection, tafqeet overflow policies, line inset CSS generation, shrink-to-fit convergence.
- **Backend contract tests**: Verify `ElementResponse` still serializes `formatting` as a plain dict.
- **Frontend unit tests**: `formatting-property-panel.component.spec.ts` — test form binding, validation (inset clamping), emit events.
- **Frontend integration tests**: Canvas service — verify Konva.Text properties update when `formatting.font` changes.

## Phases

1. **Phase 1 — Backend Renderer Foundation** (blocking for all stories)
2. **Phase 2 — User Story 1: Per-Control Font** (P1)
3. **Phase 3 — User Story 2: Generic Line Insets** (P1)
4. **Phase 4 — User Story 3: Overflow / Fit Policy** (P2)
5. **Phase 5 — Polish & Cross-Cutting** (canvas parity, translation keys, edge cases)

## Research

No external research required. Technology choices are fully constrained by the existing stack (WeasyPrint, Konva, FastAPI, Pydantic) and the constitution.

## Quickstart

### Developer Setup (no new dependencies)

Backend: No new Python packages.  
Frontend: No new npm packages (uses existing Angular Material, ngx-translate, Konva).

### Run Tests

```bash
cd formcraft-backend && pytest app/services/pdf/element_renderers/tests/ -v
cd formcraft-frontend && ng test --include='**/formatting-property-panel/*' --watch=false
```

### Manual Verification

1. Open Design Studio → select any overlay element.
2. Open the new "Formatting" section in Properties panel.
3. Set font to `Courier`, `13pt`, `Bold`, color `#333`.
4. Set first-line left inset = `22mm`, last-line right inset = `26mm`.
5. Save → generate PDF → verify font and insets match canvas preview.
6. Create a tafqeet element with a long amount → verify `shrink-to-fit` prevents overflow.

## Risk Mitigation

- **Risk**: Shrink-to-fit loop is slow for very long text.  
  **Mitigation**: Cap iterations at 20; cap minimum font at 6pt; if it doesn't fit, fall back to clip behavior.
- **Risk**: Custom font family not available on server.  
  **Mitigation**: `fonts.resolve_font_family` falls back to nearest bundled family; designer sees a warning toast in the frontend.
- **Risk**: Canvas preview and PDF diverge for complex line wrapping.  
  **Mitigation**: Both use the same inset logic; any divergence is documented as a known preview limitation (not a blocker).
