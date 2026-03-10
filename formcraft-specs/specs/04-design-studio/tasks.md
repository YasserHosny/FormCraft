# Tasks: Design Studio (Canvas Editor)

**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Format: `[ID] [Priority] [Story] Description`

## Phase 1: Setup

- [ ] **T04-001** P1 Setup — Install konva: `npm install konva`
- [ ] **T04-002** P1 Setup — Create `src/app/features/designer/designer.module.ts` with lazy-loaded routing
- [ ] **T04-003** P1 Setup — Create `src/app/features/designer/designer-page/` — Main layout with three-panel grid (left sidebar, center canvas, right panel)

## Phase 2: Canvas Core

- [ ] **T04-010** P1 S1 — Create `src/app/features/designer/models/coordinate-utils.ts` — mmToPx(), pxToMm() conversion functions
- [ ] **T04-011** P1 S1 — Create `src/app/features/designer/canvas/canvas.component.ts` — Konva.Stage initialization, mm-based coordinate system, page rendering (white rect with border)
- [ ] **T04-012** P1 S1 — Create `src/app/features/designer/canvas/canvas.service.ts` — Canvas state: zoom, pan, selection, active page
- [ ] **T04-013** P1 S1 — Implement zoom (25%–400%) via mouse wheel + toolbar buttons, updates all element positions
- [ ] **T04-014** P1 S1 — Implement pan via middle-mouse-drag or Space+drag

## Phase 3: Element Renderers

- [ ] **T04-020** P1 S1 — Create `canvas/element-renderers/base-renderer.ts` — Abstract base: creates Konva.Group with type-specific shapes, handles position/size from element model
- [ ] **T04-021** P1 S1 — Create `text-renderer.ts` — Konva.Text + Konva.Rect (background), supports RTL text alignment
- [ ] **T04-022** P1 S1 — Create `checkbox-renderer.ts` — Konva.Rect with checkbox outline visual
- [ ] **T04-023** P1 S1 — Create `radio-renderer.ts` — Konva.Circle with radio outline visual
- [ ] **T04-024** P1 S1 — Create `image-renderer.ts` — Konva.Image from asset URL
- [ ] **T04-025** P1 S1 — Create `qr-renderer.ts` — Konva.Image from placeholder QR graphic
- [ ] **T04-026** P1 S1 — Create `barcode-renderer.ts` — Konva.Image from placeholder barcode graphic
- [ ] **T04-027** P1 S1 — Create element renderer factory: `ElementType → Renderer` mapping
- [ ] **T04-028** P1 S1 — Integrate renderers with canvas.component: load template → render all elements on active page

## Phase 4: Element Palette (Left Sidebar)

- [ ] **T04-030** P1 S2 — Create `src/app/features/designer/models/element-defaults.ts` — Default dimensions and properties per element type
- [ ] **T04-031** P1 S2 — Create `palette/palette.component.ts` — Left sidebar listing all 10 element types with icons (Angular Material icons)
- [ ] **T04-032** P1 S2 — Create `palette/palette-item.component.ts` — Draggable card for each element type
- [ ] **T04-033** P1 S2 — Implement HTML5 drag from palette → Konva canvas drop: calculate drop position in mm, create element via API, render on canvas

## Phase 5: Select, Move, Resize

- [ ] **T04-040** P1 S3 — Implement click-to-select: attach Konva.Transformer to clicked element group
- [ ] **T04-041** P1 S3 — Implement drag-to-move: update element x,y in mm on dragend
- [ ] **T04-042** P1 S3 — Implement resize via Transformer handles: update width,height in mm on transformend
- [ ] **T04-043** P1 S3 — Implement multi-select: Shift+Click adds to selection, all selected elements get shared Transformer
- [ ] **T04-044** P1 S3 — Implement marquee (rubber band) selection: draw selection rect on empty canvas drag
- [ ] **T04-045** P1 S3 — Enforce constraints: minimum 2mm x 2mm, elements stay within page boundaries

## Phase 6: Property Panel (Right Sidebar)

- [ ] **T04-050** P1 S4 — Create `property-panel/property-panel.component.ts` — Host component, shows properties of selected element (or "No selection" state)
- [ ] **T04-051** P1 S4 — Create `property-panel/common-properties/` — Position fields (x, y, w, h), key, label_ar, label_en, required toggle, direction dropdown
- [ ] **T04-052** P1 S4 — Create `property-panel/validation-properties/` — Type-specific validation fields (regex, min/maxLength, numericOnly, required)
- [ ] **T04-053** P1 S4 — Create `property-panel/formatting-properties/` — Date format dropdown, currency code, decimal places, uppercase toggle
- [ ] **T04-054** P1 S4 — Create `property-panel/dropdown-options-editor/` — Add/remove/reorder choices for dropdown elements
- [ ] **T04-055** P1 S4 — Implement two-way binding: property panel changes → update data model → re-render canvas element

## Phase 7: Grid & Snap

- [ ] **T04-060** P2 S7 — Create `canvas/grid.service.ts` — Grid rendering on separate Konva.Layer, configurable spacing (1,2,5,10mm)
- [ ] **T04-061** P2 S7 — Implement snap-to-grid: round element position to nearest grid point on dragend/transformend
- [ ] **T04-062** P2 S7 — Add grid/snap toggle buttons in the canvas toolbar

## Phase 8: Layers Panel

- [ ] **T04-070** P2 S5 — Create `layers/layers-panel.component.ts` — List all elements on active page in z-order
- [ ] **T04-071** P2 S5 — Implement reorder: bring to front, send to back, move up, move down (updates sort_order)
- [ ] **T04-072** P2 S5 — Implement lock toggle: locked elements ignore click/drag
- [ ] **T04-073** P2 S5 — Implement visibility toggle: hidden elements not rendered but persist in model

## Phase 9: Multi-Page Navigator

- [ ] **T04-080** P2 S6 — Create `page-navigator/page-navigator.component.ts` — Bottom strip with page thumbnails
- [ ] **T04-081** P2 S6 — Create `page-navigator/page-thumbnail.component.ts` — Mini canvas rendering of page (scaled down)
- [ ] **T04-082** P2 S6 — Implement page switching: click thumbnail → load that page's elements on canvas
- [ ] **T04-083** P2 S6 — Implement add/delete page buttons, prevent deleting last page

## Phase 10: Undo/Redo & Auto-Save

- [ ] **T04-090** P1 S3 — Create `canvas/undo-redo.service.ts` — Command pattern with undo/redo stacks (max 50)
- [ ] **T04-091** P1 S3 — Track all operations: add, delete, move, resize, property change
- [ ] **T04-092** P1 S3 — Bind keyboard shortcuts: Ctrl+Z (undo), Ctrl+Y (redo), Delete (remove), Ctrl+C/V (copy/paste), Ctrl+A (select all)
- [ ] **T04-093** P1 S1 — Implement auto-save: debounce 2s after last change, batch PATCH to API, retry on failure

## Phase 11: Tests

- [ ] **T04-100** P1 — Write unit tests: coordinate-utils (mm↔px conversion accuracy)
- [ ] **T04-101** P1 — Write unit tests: canvas.service (zoom, pan, selection state)
- [ ] **T04-102** P1 — Write unit tests: undo-redo.service (command push, undo, redo, max stack)
- [ ] **T04-103** P1 — Write unit tests: element-defaults (all 10 types have valid defaults)
- [ ] **T04-104** P2 — Write unit tests: grid.service (snap calculations)

## Dependencies & Execution Order

```
T04-001 → T04-002 → T04-003 (setup)
T04-010 → T04-011, T04-012 (coordinate utils → canvas)
T04-020 → T04-021-027 → T04-028 (renderers → integration)
T04-030-033 (palette, after canvas renders)
T04-028 → T04-040-045 (selection needs rendered elements)
T04-040 → T04-050-055 (property panel needs selection)
T04-060-062 (grid, independent of property panel)
T04-070-073 (layers, after selection works)
T04-080-083 (multi-page, after element rendering works)
T04-090-093 (undo/redo, after all element operations)
```

## Parallel Opportunities

- Element renderers (T04-021 through T04-026) all in parallel
- Palette components (T04-031, T04-032) in parallel
- Property sub-panels (T04-051-054) all in parallel
- Grid (Phase 7) and Layers (Phase 8) in parallel

## Phase 12: Form Import & OCR Detection

- [ ] **T04-110** P1 S8 — Set up Azure Document Intelligence in backend: install `azure-ai-formrecognizer`, configure credentials in .env
- [ ] **T04-111** P1 S8 — Create `app/services/ocr/azure_ocr.py` — Azure OCR client with analyze_document() for layout extraction
- [ ] **T04-112** P1 S8 — Create `app/services/ocr/field_classifier.py` — Classify detected regions into element types (date, currency, text, signature) based on text patterns and position
- [ ] **T04-113** P1 S8 — Create `app/services/ocr/bounding_box_converter.py` — Convert image pixel coordinates to mm using page DPI
- [ ] **T04-114** P1 S8 — Create `app/models/form_detection.py` — DetectedField model (bbox, text, confidence, suggested_type, status)
- [ ] **T04-115** P1 S8 — Create migration for `form_detections` table (id, template_id, page_index, detected_fields JSONB, created_at)
- [ ] **T04-116** P1 S8 — Create `app/api/routes/forms.py` — POST /api/forms/import (upload image, store as background, trigger OCR, return detection_id)
- [ ] **T04-117** P1 S8 — Create endpoint GET /api/forms/{template_id}/detections — Return all detections for a template
- [ ] **T04-118** P1 S8 — Create endpoint POST /api/forms/{template_id}/detections/accept — Accept detection(s), create elements via existing element API
- [ ] **T04-119** P1 S8 — Write unit tests: azure_ocr.py (mock Azure API), field_classifier.py (pattern matching), bounding_box_converter.py (pixel↔mm accuracy)
- [ ] **T04-120** P1 S8 — Write integration test: upload sample cheque → verify 90%+ field detection rate
- [ ] **T04-121** P1 S8 — Create `src/app/features/designer/models/detected-field.model.ts` — TypeScript interface for DetectedField
- [ ] **T04-122** P1 S8 — Create `import-form/import-form-dialog.component.ts` — File upload dialog with drag-drop, preview, page size selector
- [ ] **T04-123** P1 S8 — Create `import-form/detection-review.component.ts` — Overlay component rendering colored bounding boxes on canvas
- [ ] **T04-124** P1 S8 — Implement detection card UI — Show text, suggested type dropdown, confidence %, accept/reject buttons
- [ ] **T04-125** P1 S8 — Implement "Accept All" / "Reject All" buttons — Bulk operations on all detections
- [ ] **T04-126** P1 S8 — Bind detection overlay to canvas zoom/pan — Detections scale and move with canvas transformations
- [ ] **T04-127** P1 S8 — Add keyboard shortcuts: A (accept selected), R (reject selected), arrow keys (navigate detections)
- [ ] **T04-128** P2 S8 — Create `fill-mode/fill-mode.component.ts` — Fill mode layout (field entry form + live preview)
- [ ] **T04-129** P2 S8 — Create `fill-mode/field-entry-form.component.ts` — Left panel with input fields per element, validation indicators
- [ ] **T04-130** P2 S8 — Create `fill-mode/live-preview-canvas.component.ts` — Right panel showing canvas with filled values rendered
- [ ] **T04-131** P2 S8 — Create migration for `form_submissions` table (id, template_id, filled_data JSONB, submitted_by, status, timestamps)
- [ ] **T04-132** P2 S8 — Create endpoint POST /api/forms/submissions — Save draft or submit filled form
- [ ] **T04-133** P2 S8 — Create endpoint GET /api/forms/submissions/{id} — Retrieve saved submission
- [ ] **T04-134** P2 S8 — Implement two-way binding: field entry form ↔ canvas preview updates in real-time
- [ ] **T04-135** P2 S8 — Implement validation in fill mode: highlight invalid fields, prevent export until valid
