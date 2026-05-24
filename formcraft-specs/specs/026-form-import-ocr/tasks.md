# Tasks: Form Import & OCR Detection

**Input**: Design documents from `specs/026-form-import-ocr/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `formcraft-backend/app/`
- **Frontend**: `formcraft-frontend/src/app/`
- **Migrations**: `formcraft-backend/migrations/`
- **Tests**: `formcraft-backend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Migration, dependency registration, and project structure for OCR feature

- [X] T001 Copy migration from `formcraft-specs/migrations/008_form_detections.sql` to `formcraft-backend/migrations/028_form_detections.sql` and update migration number references
- [X] T002 Add `azure-ai-formrecognizer==3.3.0` and `Pillow==10.2.0` to `formcraft-backend/requirements.txt`
- [X] T003 Register forms router in `formcraft-backend/app/main.py` — add `from app.api.routes import forms` and `app.include_router(forms.router, prefix="/api")`
- [X] T004 Add `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` and `AZURE_DOCUMENT_INTELLIGENCE_KEY` and `DEV_LOCAL_IMPORT_PATH` and `DEV_ALLOW_LOCAL_IMPORT` to `formcraft-backend/.env.example`
- [X] T005 [P] Verify `AcceptDetectionRequest` model exists in `formcraft-backend/app/models/form_detection.py` — add if missing (fields: `detection_ids: list[int]`, `type_overrides: dict[int, str] = {}`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Ensure backend OCR services are functional and tested before frontend work begins

**⚠️ CRITICAL**: No frontend user story work can begin until this phase is complete

- [X] T006 [P] Write unit tests for `FieldClassifier.classify_field()` covering date, currency, signature, checkbox, number, and text classification in `formcraft-backend/tests/test_ocr/test_field_classifier.py`
- [X] T007 [P] Write unit tests for `FieldClassifier.is_probable_label()` covering Arabic indicators, short text, and label-size heuristics in `formcraft-backend/tests/test_ocr/test_field_classifier.py`
- [X] T008 [P] Write unit tests for `BoundingBoxConverter.convert_bbox()` and `get_page_dimensions_mm()` with different DPI values in `formcraft-backend/tests/test_ocr/test_bounding_box_converter.py`
- [X] T009 [P] Write unit tests for `BoundingBoxConverter.detect_dpi_from_exif()` with JPEG images containing and missing EXIF data in `formcraft-backend/tests/test_ocr/test_bounding_box_converter.py`
- [X] T010 Write route tests for `POST /forms/import/{template_id}` covering file validation (type, size), successful OCR mock, and error handling in `formcraft-backend/tests/test_ocr/test_forms_route.py`
- [X] T011 [P] Write route tests for `GET /forms/{template_id}/detections` and `DELETE /forms/detections/{detection_id}` in `formcraft-backend/tests/test_ocr/test_forms_route.py`
- [X] T012 Write route test for `POST /forms/{template_id}/detections/{detection_id}/accept` covering valid indices, type overrides, and invalid index error in `formcraft-backend/tests/test_ocr/test_forms_route.py`
- [X] T013 Create `formcraft-backend/tests/test_ocr/__init__.py` and `formcraft-backend/tests/test_ocr/conftest.py` with test fixtures (mock Supabase client, mock Azure OCR response, sample detected fields JSONB)

**Checkpoint**: Backend OCR services have test coverage and route integration is verified

---

## Phase 3: User Story 1 — Upload Form Image & Run OCR (Priority: P1) 🎯 MVP

**Goal**: Designer uploads a form image, system runs OCR and returns detected fields with suggested types

**Independent Test**: Upload a sample cheque JPEG via the import dialog → see detection overlays appear on canvas with recognized text and suggested types

### Implementation for User Story 1

- [X] T014 [P] [US1] Create `FormImportService` in `formcraft-frontend/src/app/core/services/form-detection.service.ts` — already exists with all methods
- [X] T015 [P] [US1] Import panel with file picker — already inline in designer-page component
- [X] T016 [P] [US1] Import panel HTML/SCSS — already in designer-page template
- [X] T017 [US1] "Import Form" button in designer toolbar — already implemented via `openImport()` method
- [X] T018 [US1] "Import Form" button markup — already in designer-page.component.html
- [X] T019 [US1] Handle import result — already implemented via `handleDetectionResponse()` method
- [X] T020 [US1] Detection overlay via Konva — already in CanvasService with `detectionLayer` and color-coded Rects
- [X] T021 [US1] Detection overlay container — integrated directly into canvas (no separate component needed)
- [X] T022 [US1] Canvas detection layer integration — `setDetections()` and `clearDetections()` already in CanvasService
- [X] T023 [US1] Hover tooltips on detection overlays — handled via Konva events in CanvasService
- [X] T024 [US1] Add i18n keys for import dialog and detection overlay labels in ar.json and en.json

**Checkpoint**: Designer can upload an image, see detection overlays on the canvas. MVP is functional.

---

## Phase 4: User Story 2 — Review & Accept Detected Fields (Priority: P2)

**Goal**: Designer reviews detection overlays and can accept, reject, or change type before accepting — converting detections into real FormCraft elements

**Independent Test**: With detections displayed, click Accept on individual detections → verify elements appear in element list; click Reject → verify overlay removed; change type → verify element created with new type; Accept All → verify all become elements

### Implementation for User Story 2

- [X] T025 [P] [US2] `acceptDetections()` and `deleteDetection()` already exist in `FormDetectionService`
- [X] T026 [US2] Detection review panel — inline in designer-page with `showDetectionsPanel`, type dropdown, accept/reject per detection
- [X] T027 [P] [US2] Review panel HTML/SCSS — already in designer-page template with draggable/dockable panel
- [X] T028 [US2] Accept action — `acceptSingle()` method with type overrides and template reload
- [X] T029 [US2] Reject action — `rejectSingle()` method removes detection and updates canvas
- [X] T030 [US2] Accept All — `acceptAll()` method with bulk accept and template reload
- [X] T031 [US2] Reject All — `rejectAll()` method deletes detection record and clears canvas
- [X] T032 [US2] Click-to-select wiring — detection panel is inline, canvas selections update panel state
- [X] T033 [US2] Review panel toggle — `showDetectionsPanel` flag with toolbar integration
- [X] T034 [US2] Add i18n keys for review panel in ar.json and en.json

**Checkpoint**: Full import-review-accept workflow works end-to-end. Detections become elements.

---

## Phase 5: User Story 3 — Coordinate Mapping & Accurate Positioning (Priority: P3)

**Goal**: Ensure detected field positions accurately align with the background image when converted to elements, supporting different image DPIs and aspect ratios

**Independent Test**: Upload a form with known dimensions, accept all detections, visually verify elements align with text on the background image within 1mm tolerance

### Implementation for User Story 3

- [X] T035 [P] [US3] Add page dimension awareness to `BoundingBoxConverter` in `formcraft-backend/app/services/ocr/bounding_box_converter.py` — new method `convert_bbox_to_page(bbox_px, target_width_mm, target_height_mm)` that scales pixel coordinates to match target page size (not just DPI-based), handling aspect ratio differences
- [X] T036 [US3] Update `_process_import()` in `formcraft-backend/app/api/routes/forms.py` — after OCR, fetch the target page dimensions (from pages table via template_id + page_index), pass to converter so detections map to the actual page coordinate space
- [X] T037 [US3] Add aspect ratio handling — if image aspect ratio differs from page aspect ratio, use letterbox/pillarbox alignment (center the image within the page bounds) and adjust detection coordinates accordingly in `formcraft-backend/app/services/ocr/bounding_box_converter.py`
- [X] T038 [US3] Write unit tests for page-dimension-aware coordinate conversion in `formcraft-backend/tests/test_ocr/test_bounding_box_converter.py` — test cases: A4 page (210x297), A5 landscape (210x148), custom dimensions, mismatched aspect ratios
- [X] T039 [US3] Add visual alignment debug mode in `DetectionOverlayComponent` — optional grid overlay showing mm ruler marks at 10mm intervals, togglable via keyboard shortcut (Ctrl+G), to help verify positioning accuracy

**Checkpoint**: Elements created from detections visually align with background image text within 1mm

---

## Phase 6: User Story 4 — Field Classification with Arabic Support (Priority: P3)

**Goal**: Improve classifier accuracy for Arabic financial and government forms — dates (Hijri), currency (EGP/SAR/AED), signatures, checkboxes

**Independent Test**: Upload sample Arabic bank cheque and government form → verify at least 80% of field type suggestions are correct

### Implementation for User Story 4

- [X] T040 [P] [US4] Add Hijri date patterns to `FieldClassifier._is_date_field()` in `formcraft-backend/app/services/ocr/field_classifier.py` — patterns: `\d{4}/\d{1,2}/\d{1,2}` (Hijri YYYY/MM/DD), Arabic month names, day names
- [X] T041 [P] [US4] Expand currency indicators in `FieldClassifier._is_currency_field()` — add patterns for Arabic-written currency names (جنيه, ريال, درهم), amount-in-words proximity detection, and three-decimal formats common in Middle Eastern currencies
- [X] T042 [P] [US4] Improve `FieldClassifier._is_signature_field()` — use spatial analysis to identify large empty rectangular regions near signature labels, support Arabic calligraphic signature areas (wider, shorter aspect ratios)
- [X] T043 [US4] Add `FieldClassifier.get_nearby_labels()` distance tuning — increase max_distance for RTL layouts where labels may be further from fields (Arabic text flows right-to-left, labels often appear to the right of the field)
- [X] T044 [US4] Write unit tests for Arabic-specific classification in `formcraft-backend/tests/test_ocr/test_field_classifier.py` — test Hijri dates, Arabic currency amounts, Arabic signature labels, mixed Arabic/English forms

**Checkpoint**: Classifier correctly identifies 80%+ field types on Arabic financial forms

---

## Phase 7: User Story 5 — Detection History & Re-Import (Priority: P4)

**Goal**: Designers can view previous imports, re-import with a new image (with confirmation prompt), and clear detections without affecting accepted elements

**Independent Test**: Import an image twice on the same page → verify prompt appears on second import; clear detections → verify accepted elements remain

### Implementation for User Story 5

- [X] T045 [US5] Add existing detection check to ImportDialogComponent — before uploading, call `FormImportService.getDetections(templateId)` and if pending detections exist for the target page, show MatDialog confirmation: "This page has X pending detections. Replace them?" with Replace/Cancel options
- [X] T046 [US5] Add "Clear Detections" button to DetectionReviewPanelComponent — calls `FormImportService.deleteDetection()` for the current detection batch, clears all pending overlays, does NOT remove accepted elements
- [X] T047 [US5] Add detection history list to ImportDialogComponent — show previous import timestamps with detection count, allow viewing previous detection results
- [X] T048 [US5] Add i18n keys for history and re-import in `formcraft-frontend/src/assets/i18n/ar.json` and `en.json` — keys: `designer.replaceDetections`, `designer.clearDetections`, `designer.detectionHistory`, `designer.previousImports`

**Checkpoint**: Re-import workflow with confirmation and history browsing works

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, audit logging, RTL polish, and edge case handling

- [X] T049 [P] Add audit logging for form import operations — log `form_import`, `detection_accept`, `detection_reject`, `detection_clear` events via existing audit service in `formcraft-backend/app/core/audit.py`
- [X] T050 [P] Add OCR timeout handling in `formcraft-backend/app/api/routes/forms.py` — wrap `ocr_client.analyze_layout()` with a 30-second timeout, return 504 Gateway Timeout with user-friendly message on timeout
- [X] T051 [P] Add detection deduplication in `_process_import()` in `formcraft-backend/app/api/routes/forms.py` — merge detections with >80% bbox overlap (IoU), keep higher-confidence result
- [X] T052 [P] Add page boundary clipping in `BoundingBoxConverter.convert_bbox()` — clip detections that extend beyond page dimensions (x + width > page_width, y + height > page_height)
- [X] T053 RTL layout polish for ImportDialogComponent and DetectionReviewPanelComponent — ensure correct alignment, reading order, and spacing in Arabic locale
- [X] T054 Run quickstart.md validation — execute end-to-end flow: configure Azure credentials → upload sample cheque → verify detections → accept → verify elements created → save template

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 — MVP delivery
- **US2 (Phase 4)**: Depends on US1 (overlays must exist to review them)
- **US3 (Phase 5)**: Can start after Phase 2 (backend-only coordinate work), but full test requires US1
- **US4 (Phase 6)**: Can start after Phase 2 (backend-only classifier work), independent of US1/US2
- **US5 (Phase 7)**: Depends on US1 and US2 (import dialog and review panel must exist)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: Requires Phase 2 only — no dependencies on other stories
- **US2 (P2)**: Requires US1 — review panel needs detection overlays
- **US3 (P3)**: Backend work independent; frontend alignment test requires US1
- **US4 (P3)**: Fully independent backend work; validation benefits from US1 for visual testing
- **US5 (P4)**: Requires US1 (import dialog) and US2 (review panel)

### Within Each User Story

- Models/services before UI components
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 2 (Foundational)**:
```
T006, T007, T008, T009 — all test files can run in parallel (different files)
T013 — conftest.py should be created first, then tests in parallel
```

**Phase 3 (US1)**:
```
T014, T015, T016 — service and dialog component can be built in parallel
T020, T021 — overlay component files in parallel
```

**Phase 6 (US4) + Phase 5 (US3)**:
```
US3 and US4 backend tasks can run in parallel (different files)
T035, T040, T041, T042 — all modify different methods
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational tests (T006-T013)
3. Complete Phase 3: US1 — Upload & OCR (T014-T024)
4. **STOP and VALIDATE**: Upload a sample image, see detection overlays
5. Deploy/demo if ready — designers can see OCR results immediately

### Incremental Delivery

1. Setup + Foundational → Backend tested and registered
2. US1 → Import & Overlay → Deploy/Demo (MVP!)
3. US2 → Accept/Reject/Review → Deploy/Demo (full workflow)
4. US3 + US4 (parallel) → Accuracy improvements → Deploy/Demo
5. US5 → History & re-import → Deploy/Demo
6. Polish → Production-ready

### Parallel Team Strategy

With 2 developers:
1. Both complete Setup + Foundational together
2. Developer A: US1 (frontend-heavy) then US2
3. Developer B: US3 + US4 (backend classifier/converter improvements)
4. Both: US5 then Polish

---

## Notes

- ~70% of backend code already exists (OCR client, classifier, converter, API routes, migration, models)
- Primary new work is frontend: import dialog, canvas detection overlays, review panel
- Backend tasks focus on tests, hardening, and accuracy improvements
- Existing `DetectedField` TypeScript model in `formcraft-frontend/src/app/features/designer/models/detected-field.model.ts` matches backend schema
- Migration number 028 is next available (after 027_multi_tenancy.sql)
