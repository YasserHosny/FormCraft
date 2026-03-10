# Implementation Plan: Design Studio (Canvas Editor)

**Branch**: `04-design-studio` | **Date**: 2026-02-21 | **Spec**: [spec.md](./spec.md)

## Summary

Build a Konva.js-based canvas editor inside an Angular component with mm-coordinate system, element palette, drag-to-canvas, select/move/resize, property panel with Angular Material, grid/snap, layer management, multi-page navigation, and undo/redo.

## Technical Context

**Language/Version**: TypeScript 5.x, Angular (latest LTS)
**Primary Dependencies**: konva (npm), Angular Material, Zod
**Storage**: Template data via API (spec 03), canvas state in-memory
**Testing**: Jasmine/Karma (unit), Playwright (interaction)
**Target Platform**: Web (Chrome, Firefox, Edge, Safari)

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arabic-First | ✅ Pass | Canvas renders RTL text; property panel mirrors in RTL |
| II. Pixel-Perfect | ✅ Pass | mm-based coordinates, no auto-scaling |
| III. AI Suggest Only | ✅ Pass | AI suggestion chips shown in property panel, never auto-applied |
| VII. Translation-Key | ✅ Pass | All panel labels via i18n keys |

## Project Structure

### Frontend (formcraft-frontend)

```text
src/app/features/designer/
├── designer.module.ts
├── designer-routing.module.ts
├── designer-page/
│   └── designer-page.component.ts     # Main layout: sidebar + canvas + right panel
├── canvas/
│   ├── canvas.component.ts            # Konva Stage host, mm↔px conversion
│   ├── canvas.service.ts              # Canvas state management (zoom, pan, selection)
│   ├── element-renderers/
│   │   ├── text-renderer.ts           # Konva.Text + Konva.Rect for text elements
│   │   ├── checkbox-renderer.ts       # Konva.Rect with checkbox visual
│   │   ├── radio-renderer.ts          # Konva.Circle with radio visual
│   │   ├── image-renderer.ts          # Konva.Image for image elements
│   │   ├── qr-renderer.ts            # Konva.Image from generated QR
│   │   ├── barcode-renderer.ts        # Konva.Image from generated barcode
│   │   └── base-renderer.ts           # Abstract base with common positioning logic
│   ├── grid.service.ts                # Grid overlay rendering, snap logic
│   └── undo-redo.service.ts           # Command pattern undo/redo stack
├── palette/
│   ├── palette.component.ts           # Left sidebar with element type cards
│   └── palette-item.component.ts      # Draggable element type card
├── property-panel/
│   ├── property-panel.component.ts    # Right panel host
│   ├── common-properties/             # Position (x,y,w,h), key, labels, required, direction
│   ├── validation-properties/         # Validation config per element type
│   ├── formatting-properties/         # Date format, currency, decimal places
│   ├── dropdown-options-editor/       # Add/remove/reorder dropdown choices
│   └── ai-suggestion-chip/            # Suggestion display with accept/dismiss
├── layers/
│   ├── layers-panel.component.ts      # Layer list with reorder, lock, visibility
│   └── layer-item.component.ts        # Single layer entry
├── page-navigator/
│   ├── page-navigator.component.ts    # Bottom page thumbnails strip
│   └── page-thumbnail.component.ts    # Single page thumbnail
└── models/
    ├── canvas-state.model.ts          # Zoom, pan, selection, grid config
    ├── element-defaults.ts            # Default dimensions/properties per element type
    └── coordinate-utils.ts            # mm↔px conversion, snap-to-grid calculations
```

### mm ↔ px Conversion

```typescript
// coordinate-utils.ts
const MM_PER_INCH = 25.4;

export function mmToPx(mm: number, dpi: number = 96, zoom: number = 1): number {
  return (mm / MM_PER_INCH) * dpi * zoom;
}

export function pxToMm(px: number, dpi: number = 96, zoom: number = 1): number {
  return (px / dpi / zoom) * MM_PER_INCH;
}
```

### Canvas Architecture

```
DesignerPageComponent (host)
├── PaletteComponent (left sidebar)
│   └── draggable element types
├── CanvasComponent (center)
│   └── Konva.Stage
│       └── Konva.Layer (page background)
│       └── Konva.Layer (elements)
│       └── Konva.Layer (grid overlay)
│       └── Konva.Transformer (selection handles)
├── PropertyPanelComponent (right sidebar)
│   └── bound to selected element
├── LayersPanelComponent (right sidebar tab)
│   └── z-order list
└── PageNavigatorComponent (bottom)
    └── page thumbnails
```

### Undo/Redo Strategy

Command pattern with serializable state snapshots:

```typescript
interface UndoCommand {
  type: 'add' | 'delete' | 'move' | 'resize' | 'property_change';
  elementId: string;
  before: Partial<Element>;
  after: Partial<Element>;
}

class UndoRedoService {
  private undoStack: UndoCommand[] = []; // max 50
  private redoStack: UndoCommand[] = [];
  
  execute(command: UndoCommand): void { /* apply + push to undo */ }
  undo(): void { /* pop from undo, reverse, push to redo */ }
  redo(): void { /* pop from redo, apply, push to undo */ }
}
```

### Auto-Save Strategy

```
Element change → push to UndoStack
                → debounce 2 seconds
                → call PATCH /api/pages/{id}/elements (batch update)
                → on success: mark saved
                → on failure: retry 3x with exponential backoff
                → on final failure: show warning toast, keep changes in memory
```

## Research Notes

- **Pure Konva.js** over ngx-konva: ngx-konva is a thin wrapper with limited maintenance. Direct Konva.js integration gives full control and avoids a dependency risk.
- **Element rendering strategy**: Each element type has a dedicated renderer class that creates Konva shapes. A factory function maps `ElementType → Renderer`.
- **Grid rendering**: Konva.Line objects drawn on a separate layer. Grid layer is below elements layer. Performance: only render grid lines visible in the current viewport.
- **Multi-page**: Only the active page's elements are rendered on the Konva Stage. Switching pages replaces the elements layer.
- **DPI**: Default 96 for screen rendering. PDF rendering uses its own coordinate system (mm-native via WeasyPrint).

## Complexity Tracking

No constitution violations.
