# Feature Specification: Design Studio (Canvas Editor)

**Feature Branch**: `04-design-studio`
**Created**: 2026-02-21
**Status**: Draft
**Input**: FormCraft PRD Phase 2 – Design Studio

## User Scenarios & Testing

### User Story 1 - Canvas with Absolute Positioning (Priority: P1)

A Designer opens a template and sees a Konva.js canvas rendering the page at actual dimensions (mm-based coordinate system). The canvas shows a white page area with a light grid overlay. Elements are rendered at their absolute positions.

**Why this priority**: The canvas is the core of the Design Studio. Everything else is built on top of it.

**Independent Test**: Can be tested by loading a template with elements and verifying canvas renders them at correct pixel positions (mm → px conversion at current zoom).

**Acceptance Scenarios**:

1. **Given** a page of 210x297mm (A4), **When** the canvas loads, **Then** the page is rendered at proportional pixel dimensions with a visible boundary.
2. **Given** an element at position (10, 20, 50, 8) mm, **When** the canvas renders, **Then** the element appears at the correct mm-to-pixel-converted coordinates.
3. **Given** the canvas is loaded, **When** the Designer zooms in/out, **Then** all elements maintain their relative positions and the grid scales accordingly.

---

### User Story 2 - Element Palette & Drag-to-Canvas (Priority: P1)

A left sidebar shows an element palette with all supported element types. The Designer drags an element type from the palette onto the canvas, which creates a new element at the drop position.

**Why this priority**: Adding elements to the canvas is the primary design action.

**Independent Test**: Can be tested by dragging each element type onto the canvas and verifying the element is created with correct type and drop position.

**Acceptance Scenarios**:

1. **Given** the element palette is visible, **When** the Designer drags a "Text" element onto the canvas at position (30, 50) mm, **Then** a new text element is created at that position with default dimensions.
2. **Given** the Designer drags a "Date" element, **When** it is dropped, **Then** the element is created with type "date" and default date formatting.
3. **Given** the Designer drags an element near the page edge, **When** the element would exceed page bounds, **Then** the element snaps to fit within the page boundary.

---

### User Story 3 - Select, Move, and Resize Elements (Priority: P1)

The Designer can click an element to select it, drag to move it, and use resize handles to change dimensions. Selected elements show a transformer (bounding box with handles). Multi-select is supported via Shift+Click or marquee selection.

**Why this priority**: Element manipulation is the second most frequent design action after creation.

**Independent Test**: Can be tested by selecting, moving, and resizing elements and verifying updated positions in the data model.

**Acceptance Scenarios**:

1. **Given** an element on the canvas, **When** the Designer clicks it, **Then** a Konva Transformer appears with 8 resize handles.
2. **Given** a selected element at (10, 20), **When** the Designer drags it to (30, 40), **Then** the element's position updates to (30, 40) mm in the data model.
3. **Given** a selected element, **When** the Designer drags a corner handle, **Then** the element resizes proportionally and the new dimensions are saved in mm.
4. **Given** multiple elements, **When** the Designer Shift+Clicks two elements, **Then** both are selected and can be moved together.
5. **Given** grid snap is enabled (5mm grid), **When** the Designer moves an element, **Then** the element snaps to the nearest 5mm grid intersection.

---

### User Story 4 - Right Panel: Property Editor (Priority: P1)

When an element is selected, a right panel shows its editable properties: labels (AR/EN), position (x, y, w, h), type, key, validation rules, formatting options, required toggle, and direction override.

**Why this priority**: The property panel is how designers configure element behavior beyond visual placement.

**Independent Test**: Can be tested by selecting an element and verifying all property fields reflect current values, then changing a value and verifying it persists.

**Acceptance Scenarios**:

1. **Given** a text element is selected, **When** the right panel opens, **Then** it shows fields for label_ar, label_en, x, y, width, height, key, required toggle, and direction dropdown.
2. **Given** the right panel is open, **When** the Designer changes label_ar to "الاسم", **Then** the value is immediately reflected on the canvas and saved to the data model.
3. **Given** a "date" element is selected, **When** the right panel opens, **Then** it shows additional formatting options: dateFormat dropdown (DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD).
4. **Given** a "currency" element is selected, **When** the right panel opens, **Then** it shows formatting options: currencyCode (EGP, SAR, AED, USD) and decimalPlaces.
5. **Given** a "dropdown" element is selected, **When** the right panel opens, **Then** it shows an options editor where the Designer can add/remove/reorder dropdown choices.

---

### User Story 5 - Layer Management (Priority: P2)

A layers panel shows all elements on the current page in z-order. The Designer can reorder layers (bring to front, send to back, move up, move down), toggle element visibility, and lock elements to prevent accidental editing.

**Why this priority**: Layer management is essential for complex forms with overlapping elements but is secondary to basic element CRUD.

**Independent Test**: Can be tested by reordering layers and verifying z-order changes on canvas, and by locking an element and verifying it cannot be selected.

**Acceptance Scenarios**:

1. **Given** a page with 5 elements, **When** the layers panel opens, **Then** it shows all 5 elements listed by their label (or type if no label) in z-order.
2. **Given** element A is behind element B, **When** the Designer selects "Bring to Front" on element A, **Then** element A renders on top of element B.
3. **Given** an element is locked, **When** the Designer clicks it on the canvas, **Then** it is not selected and a lock icon is shown.
4. **Given** an element is hidden, **When** the canvas renders, **Then** the element is not visible but still exists in the data model.

---

### User Story 6 - Multi-Page Navigation (Priority: P2)

The Design Studio supports multi-page templates. A page navigator at the bottom shows page thumbnails. The Designer can switch between pages, add new pages, delete pages (except the last one), and reorder pages.

**Why this priority**: Multi-page is needed for complex forms but single-page forms are a valid MVP.

**Independent Test**: Can be tested by navigating between pages and verifying the canvas loads the correct page's elements.

**Acceptance Scenarios**:

1. **Given** a template with 3 pages, **When** the Designer clicks page 2 thumbnail, **Then** the canvas loads page 2's elements and dimensions.
2. **Given** page 1 is active, **When** the Designer clicks "Add Page", **Then** a new page is added after the current page with default A4 dimensions.
3. **Given** the template has 1 page, **When** the Designer attempts to delete it, **Then** the delete button is disabled.

---

### User Story 7 - Grid and Snap System (Priority: P2)

The canvas displays an optional grid overlay. Grid spacing is configurable (1mm, 2mm, 5mm, 10mm). When snap is enabled, element positions and sizes snap to grid intersections during drag and resize.

**Why this priority**: Grid and snap improve design precision but are not blocking for basic functionality.

**Independent Test**: Can be tested by enabling snap and moving an element, verifying it lands on grid intersections.

**Acceptance Scenarios**:

1. **Given** grid is enabled with 5mm spacing, **When** the canvas renders, **Then** a light grid overlay is visible.
2. **Given** snap is enabled with 5mm grid, **When** an element at (12, 17) is released, **Then** it snaps to (10, 15).
3. **Given** snap is disabled, **When** an element is moved to (12, 17), **Then** it stays at (12, 17).
4. **Given** the grid is toggled off, **When** the canvas renders, **Then** the grid overlay is hidden but snap can still be active.

---

### User Story 8 - Form Import & Automatic Field Detection (Priority: P1)

A Designer can upload a scanned form (cheque, government form, shipping label) as a page background. The system automatically detects fillable fields using OCR, suggests element types (date, amount, text, signature), and displays them as overlays. The Designer can review, accept, reject, or modify detections before converting them to FormCraft elements.

**Why this priority**: Importing existing forms and auto-detecting fields dramatically reduces template creation time from hours to minutes.

**Independent Test**: Can be tested by uploading a bank cheque image and verifying that date, amount, and name fields are correctly detected with 90%+ accuracy.

**Acceptance Scenarios**:

1. **Given** a cheque image is uploaded, **When** the system processes it, **Then** the image is set as the page background and OCR detection starts automatically.
2. **Given** OCR completes on a cheque, **When** the Designer views the canvas, **Then** detected fields appear as colored bounding boxes with suggested types (date, currency, text).
3. **Given** a detection overlay shows 12 detected fields, **When** the Designer clicks "Accept All", **Then** all 12 fields are converted to FormCraft elements at their detected positions.
4. **Given** a detection is incorrect, **When** the Designer clicks "Reject", **Then** the detection is removed without creating an element.
5. **Given** a detection has wrong type, **When** the Designer changes type from "text" to "date" and accepts, **Then** a date element is created instead.
6. **Given** OCR misses a field, **When** the Designer drags an element from the palette, **Then** manual element creation works as normal.
7. **Given** form dimensions are ambiguous, **When** the system detects the background image, **Then** it auto-detects page size from EXIF metadata or prompts the user to specify dimensions.

---

### Edge Cases

- What happens when the canvas viewport is smaller than the page? → Scroll bars appear; canvas is pannable.
- What happens when an element is resized to less than minimum size? → Enforce minimum 2mm x 2mm.
- What happens when many elements overlap? → All render; selection picks the topmost in z-order.
- What happens when the user pastes an element from clipboard? → Paste at center of current viewport with 5mm offset from original.
- What happens on undo/redo? → Undo stack tracks element add/move/resize/delete/property-change. Ctrl+Z undoes, Ctrl+Y redoes.

## Requirements

### Functional Requirements

- **FR-001**: System MUST render a Konva.js canvas with mm-based coordinate system.
- **FR-002**: System MUST convert mm coordinates to screen pixels using configurable DPI (default 96).
- **FR-003**: System MUST support zoom (25%–400%) with mouse wheel and toolbar controls.
- **FR-004**: System MUST support pan via middle-mouse-drag or Space+drag.
- **FR-005**: System MUST render a draggable element palette in the left sidebar with all 10 element types.
- **FR-006**: System MUST support drag-from-palette-to-canvas for element creation.
- **FR-007**: System MUST render Konva Transformer on selected elements with 8 resize handles.
- **FR-008**: System MUST support multi-select via Shift+Click and marquee (rubber band) selection.
- **FR-009**: System MUST support grid overlay with configurable spacing (1, 2, 5, 10 mm).
- **FR-010**: System MUST support snap-to-grid during drag and resize operations.
- **FR-011**: System MUST render a right property panel showing all editable properties of the selected element.
- **FR-012**: Property changes MUST be immediately reflected on the canvas (two-way binding).
- **FR-013**: System MUST support element-type-specific property fields (date format, currency code, dropdown options, etc.).
- **FR-014**: System MUST support z-order management: bring to front, send to back, move up, move down.
- **FR-015**: System MUST support element locking (prevent selection/movement) and visibility toggle.
- **FR-016**: System MUST support multi-page navigation with page thumbnails.
- **FR-017**: System MUST support undo/redo with at least 50 steps.
- **FR-018**: System MUST auto-save template changes with debounce (2 seconds after last change).
- **FR-019**: System MUST enforce minimum element size of 2mm x 2mm.
- **FR-020**: System MUST prevent elements from being positioned outside page boundaries.
- **FR-021**: System MUST support keyboard shortcuts: Delete (remove element), Ctrl+Z (undo), Ctrl+Y (redo), Ctrl+C/V (copy/paste), Ctrl+A (select all).
- **FR-022**: System MUST render element type icons/labels on the canvas for visual identification.
- **FR-023**: System MUST support uploading form images (JPEG, PNG) or PDFs as page backgrounds.
- **FR-024**: System MUST detect fillable fields from uploaded forms using OCR (Azure Document Intelligence).
- **FR-025**: OCR MUST extract bounding boxes, text content, and confidence scores for detected regions.
- **FR-026**: System MUST classify detected fields into element types (date, currency, text, number, signature) with 85%+ accuracy.
- **FR-027**: System MUST display detection overlays on canvas with color-coded bounding boxes per suggested type.
- **FR-028**: System MUST allow Designers to accept, reject, or modify individual detections.
- **FR-029**: System MUST support "Accept All" and "Reject All" bulk operations for detections.
- **FR-030**: System MUST auto-detect page dimensions from image EXIF metadata or prompt for manual input.
- **FR-031**: Detection results MUST persist until template is saved (not time-limited).

### Key Entities

- **CanvasState**: Current zoom level, pan offset, active page index, selected element IDs, grid settings, snap enabled.
- **UndoStack**: Array of state snapshots for undo/redo (max 50 entries).
- **Element Palette Config**: Static list of element types with icons, default dimensions, and default properties.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Canvas renders 100 elements on a page with less than 16ms frame time (60fps).
- **SC-002**: Drag and resize operations feel smooth with no perceivable lag (< 8ms input latency).
- **SC-003**: All 10 element types can be dragged onto the canvas and configured via the property panel.
- **SC-004**: Grid snap accuracy is exact to the configured grid spacing (no sub-pixel drift).
- **SC-005**: Undo/redo correctly restores element state for all operations (add, move, resize, delete, property change).
- **SC-006**: Auto-save triggers within 2 seconds of the last change and completes within 500ms.
