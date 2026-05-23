# Implementation Plan: Form Import & OCR Detection

**Branch**: `026-form-import-ocr` | **Date**: 2026-05-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/026-form-import-ocr/spec.md`

## Summary

Enable automatic field detection from uploaded form images using Azure Document Intelligence OCR. The system extracts text regions with bounding boxes, classifies them into FormCraft element types (date, currency, text, number, signature, checkbox), converts pixel coordinates to millimeters, and presents interactive detection overlays on the Design Studio canvas. Designers review, accept/reject, and convert detections into real elements. Significant backend work already exists (OCR client, classifier, converter, API routes, migration) — this plan focuses on completing the frontend integration, wiring up missing pieces, and adding the detection overlay UI.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript / Angular 19 (frontend)
**Primary Dependencies**: FastAPI, azure-ai-formrecognizer 3.3.0, Pillow 10.2.0, Konva.js (canvas), Angular Material
**Storage**: Supabase (PostgreSQL + Storage + Auth) — `form_detections` table (JSONB fields)
**Testing**: pytest (backend), Karma/Jasmine (frontend)
**Target Platform**: Web application (browser)
**Project Type**: Web service (SPA + REST API)
**Performance Goals**: OCR processing < 10s end-to-end, canvas overlay rendering < 500ms
**Constraints**: Azure Document Intelligence free tier (500 pages/month), 10 MB max upload, synchronous processing
**Scale/Scope**: Single-page OCR initially (multi-page future), 10-50 detections per page typical

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution file contains template placeholders only (not project-specific). No binding principles to gate against. Proceeding.

## Project Structure

### Documentation (this feature)

```text
specs/026-form-import-ocr/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── contracts/           # Phase 1 output (API contracts)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
formcraft-backend/
├── app/
│   ├── api/routes/forms.py           # ✅ EXISTS — OCR import & detection endpoints
│   ├── models/form_detection.py      # ✅ EXISTS — Pydantic models
│   ├── services/ocr/
│   │   ├── __init__.py               # ✅ EXISTS
│   │   ├── azure_ocr.py              # ✅ EXISTS — Azure Document Intelligence client
│   │   ├── field_classifier.py       # ✅ EXISTS — Field type suggester
│   │   └── bounding_box_converter.py # ✅ EXISTS — Pixel to mm converter
│   └── core/config.py                # ✅ EXISTS — Azure credentials config
├── migrations/
│   └── 028_form_detections.sql       # NEW — Migration (copy from formcraft-specs/migrations/008)
└── tests/
    └── test_ocr/                     # NEW — OCR service tests
        ├── test_field_classifier.py
        ├── test_bounding_box_converter.py
        └── test_forms_route.py

formcraft-frontend/
├── src/app/features/designer/
│   ├── models/detected-field.model.ts      # ✅ EXISTS — TypeScript interfaces
│   ├── services/
│   │   └── form-import.service.ts          # NEW — API service for import/detections
│   ├── components/
│   │   ├── import-dialog/                  # NEW — Upload form image dialog
│   │   │   ├── import-dialog.component.ts
│   │   │   ├── import-dialog.component.html
│   │   │   └── import-dialog.component.scss
│   │   ├── detection-overlay/              # NEW — Canvas overlay for detections
│   │   │   ├── detection-overlay.component.ts
│   │   │   ├── detection-overlay.component.html
│   │   │   └── detection-overlay.component.scss
│   │   └── detection-review-panel/         # NEW — Accept/reject/edit panel
│   │       ├── detection-review-panel.component.ts
│   │       ├── detection-review-panel.component.html
│   │       └── detection-review-panel.component.scss
│   └── designer-page/
│       └── designer-page.component.ts      # MODIFY — Add import button + overlay integration
```

**Structure Decision**: Web application with existing backend/frontend split. Backend OCR services are largely complete. Primary work is frontend integration (import dialog, canvas detection overlays, review panel) and backend hardening (tests, migration placement, error handling improvements).

## Phase 0: Research Decisions

| Decision | Choice | Rationale | Alternatives Considered |
|----------|--------|-----------|------------------------|
| OCR Provider | Azure Document Intelligence (prebuilt-layout) | Already implemented in `azure_ocr.py`; supports Arabic text; free tier available | Google Vision API (similar quality, different SDK), Tesseract (open-source but lower Arabic accuracy) |
| Coordinate System | DPI-based pixel-to-mm conversion | Already implemented in `bounding_box_converter.py` with EXIF DPI detection fallback | Fixed-ratio scaling (less accurate), manual calibration (too complex for users) |
| Detection Storage | JSONB array in `form_detections` table | Simple, flexible, already implemented; detection count per page is small (10-50) | Separate `detection_items` table (normalized but overkill for 10-50 items per page) |
| Canvas Overlay Rendering | Konva.js Rect + Text nodes on separate layer | Design Studio already uses Konva.js; separate layer keeps detections independent of real elements | HTML overlay div (misalignment risk with canvas zoom/pan), SVG overlay (extra rendering path) |
| Processing Model | Synchronous (designer waits) | 2-5s latency acceptable for single-page OCR; simpler implementation | Async with polling (better for multi-page but adds complexity for V1) |
| Image Storage | Supabase Storage bucket (page background) | Existing infrastructure for asset storage; background images already supported | Local filesystem (not scalable), Base64 in DB (bloats database) |

## Phase 1: Implementation Phases

### Phase 1A: Backend Hardening & Migration

1. Copy migration `008_form_detections.sql` to `migrations/028_form_detections.sql` (next available number)
2. Register forms router in `main.py` if not already registered
3. Add `azure-ai-formrecognizer` and `Pillow` to `requirements.txt`
4. Add backend tests for:
   - `FieldClassifier` — unit tests for each classification path (date, currency, signature, checkbox, number, text)
   - `BoundingBoxConverter` — unit tests for pixel-to-mm conversion, DPI detection
   - Forms route — integration tests for upload validation, detection CRUD

### Phase 1B: Frontend — Import Dialog

1. Create `FormImportService` — API client for `/forms/import`, `/forms/{id}/detections`, accept/reject endpoints
2. Create `ImportDialogComponent` — Material dialog for file upload with:
   - File picker (JPEG/PNG only, 10 MB max)
   - Page selector (dropdown for multi-page templates)
   - Upload progress indicator
   - Existing detections warning prompt
3. Add "Import Form" button to designer toolbar

### Phase 1C: Frontend — Detection Overlays

1. Create `DetectionOverlayComponent` — renders Konva Rect + Text nodes on a dedicated canvas layer
   - Each detection: semi-transparent colored rectangle (color by suggested type)
   - Tooltip on hover: recognized text, confidence %, suggested type
   - Click to select → opens review panel
   - Visual distinction: pending (dashed border), accepted (solid green), rejected (grayed out)
2. Integrate overlay layer into existing `CanvasService` zoom/pan transforms

### Phase 1D: Frontend — Review Panel

1. Create `DetectionReviewPanelComponent` — side panel listing all detections
   - Per-detection actions: Accept, Reject, Change Type (dropdown)
   - Bulk actions: Accept All, Reject All
   - Summary: X pending, Y accepted, Z rejected
2. Wire accept action → `POST /forms/{template_id}/detections/{detection_id}/accept`
3. Wire reject action → update local state, optionally `DELETE /forms/detections/{detection_id}`

### Phase 1E: Integration & Polish

1. End-to-end flow: Upload → OCR → Overlays → Review → Accept → Elements created → Save
2. Background image management: uploaded image set as page background via existing page API
3. Audit logging for import/accept/reject operations
4. Error handling: OCR timeout, service unavailable, credential misconfiguration
5. RTL/i18n: Arabic labels in import dialog and review panel
