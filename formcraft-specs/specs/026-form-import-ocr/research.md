# Research: Form Import & OCR Detection

**Date**: 2026-05-23
**Feature**: 026-form-import-ocr

## R1: Azure Document Intelligence — Arabic OCR Accuracy

**Decision**: Use Azure Document Intelligence `prebuilt-layout` model
**Rationale**: Already implemented in `azure_ocr.py`. The prebuilt-layout model provides word-level text extraction with polygon bounding boxes and confidence scores. Azure's Arabic text recognition quality is among the highest of cloud OCR providers, particularly for printed Arabic in financial documents.
**Alternatives Considered**:
- Google Cloud Vision API — comparable accuracy for Arabic, but would require rewriting the OCR client
- Tesseract OCR (open source) — significantly lower accuracy for Arabic script, especially mixed Arabic/English documents
- AWS Textract — good accuracy but no existing implementation; Azure is already integrated

## R2: Coordinate Conversion Strategy

**Decision**: DPI-based pixel-to-mm conversion with EXIF DPI detection fallback (default 96 DPI)
**Rationale**: Azure returns bounding boxes in pixel coordinates relative to the analyzed page. The `BoundingBoxConverter` already handles this conversion using image EXIF data for DPI when available. For scanned documents at 300 DPI, this yields sub-millimeter accuracy. For screen-resolution images without EXIF data, the 96 DPI fallback provides reasonable approximation.
**Alternatives Considered**:
- Fixed scaling ratio based on known page size (A4 = 210x297mm) — requires user to specify paper size; error-prone
- Azure's built-in unit (inches) with direct conversion — Azure sometimes returns units as "pixel" not "inch", making this unreliable
- Manual calibration workflow — too complex for V1; could be a future enhancement

## R3: Detection Storage Model

**Decision**: JSONB array column in `form_detections` table
**Rationale**: The `detected_fields` column stores an array of detection objects as JSONB. This is appropriate because: (1) detections are always read/written as a complete set per page, (2) typical count is 10-50 items, (3) no need for cross-detection queries, (4) simplifies the API (single row per import operation).
**Alternatives Considered**:
- Normalized `detection_items` table with foreign key to `form_detections` — better for large-scale querying but unnecessary overhead for small detection counts per page
- Redis/in-memory cache — detections need persistence across sessions

## R4: Canvas Overlay Rendering Approach

**Decision**: Konva.js shapes on a dedicated Group/Layer within the existing canvas
**Rationale**: The Design Studio already uses Konva.js for element rendering. Adding detection overlays as a separate Konva Group (above elements, below the UI layer) ensures: (1) overlays follow canvas zoom/pan transforms automatically, (2) no coordinate translation needed between canvas space and overlay space, (3) click/hover events work natively.
**Alternatives Considered**:
- HTML div overlay positioned absolutely — breaks on zoom/pan, requires manual coordinate sync
- SVG overlay — adds a second rendering path, complicates the canvas architecture
- Temporary Konva elements — risk of confusion with real elements; dedicated group is cleaner

## R5: Image Storage for Page Background

**Decision**: Upload to Supabase Storage, set URL as `background_asset` on the page record
**Rationale**: The existing page data model has a `background_asset` field. Supabase Storage already handles image hosting with CDN URLs. The import workflow sets this field automatically after upload, making the image visible as the canvas background.
**Alternatives Considered**:
- Inline Base64 in the page record — bloats database, slow to load
- Local filesystem storage — not scalable, breaks in production deployments

## R6: Field Classification Strategy

**Decision**: Rule-based classifier using regex patterns and proximity labels
**Rationale**: The `FieldClassifier` already implements pattern-based classification for Arabic and English forms. Rule-based approach is deterministic, fast, and easy to extend. For V1, this provides ~80% accuracy on structured financial forms. Machine learning classification can be added later if needed.
**Alternatives Considered**:
- LLM-based classification (send OCR text to GPT/Claude for type inference) — higher accuracy potential but adds latency, cost, and external dependency
- Azure Form Recognizer custom models — requires training data; overkill for V1
- No classification (all fields as "text") — loses key value proposition of reducing manual review
