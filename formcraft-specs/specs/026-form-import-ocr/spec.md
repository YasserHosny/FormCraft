# Feature Specification: Form Import & OCR Detection

**Feature Branch**: `026-form-import-ocr`  
**Created**: 2026-05-23  
**Status**: Draft  
**Input**: User description: "Enable automatic field detection from uploaded form images (cheques, government forms) using Azure Document Intelligence OCR, with manual review and element creation workflow in the Design Studio."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload Form Image & Run OCR (Priority: P1)

A form designer uploads a scanned image of a physical form (e.g., a bank cheque, government application, or shipping label) to the Design Studio. The system stores the image as the page background, sends it to an external OCR service, and returns detected text regions with their positions and suggested field types. The designer sees the original form image with detection overlays highlighting where fields were found.

**Why this priority**: This is the core value proposition — without OCR extraction, the feature has no purpose. A designer can already manually place elements on a blank canvas; the key differentiator is automated detection from real-world documents.

**Independent Test**: Can be fully tested by uploading a sample cheque image and verifying that the system returns detected text regions with bounding boxes and suggested types. Delivers immediate value by showing the designer where fields are on the form.

**Acceptance Scenarios**:

1. **Given** a designer has a template open in Design Studio, **When** they upload a JPEG or PNG image of a cheque, **Then** the image is set as the page background and the system initiates OCR processing.
2. **Given** OCR processing completes successfully, **When** results are returned, **Then** each detected text region shows as an overlay on the canvas with its recognized text, confidence score, and suggested element type (date, currency, text, number, signature, checkbox).
3. **Given** an uploaded image is low quality or contains no recognizable text, **When** OCR completes, **Then** the system displays a message indicating no fields were detected and the designer can still use the image as a background.
4. **Given** the external OCR service is unavailable or credentials are not configured, **When** the designer attempts an import, **Then** the system shows a clear error message explaining the service is unavailable, and the image is still saved as a page background.

---

### User Story 2 - Review & Accept Detected Fields (Priority: P2)

After OCR detections appear as overlays on the canvas, the designer reviews each detected field. They can accept a detection (converting it into a real FormCraft element), reject it (removing the overlay), or edit its suggested type before accepting. Bulk actions allow accepting or rejecting all detections at once.

**Why this priority**: Detection alone is not useful without a review workflow. This story completes the core loop: detect, review, and convert to usable form elements. Without it, detections are just visual noise.

**Independent Test**: Can be tested by loading a template with existing detections and verifying that accept/reject/edit actions correctly create or discard elements. Requires Story 1 to generate detections, but the review UI can be tested independently with pre-seeded detection data.

**Acceptance Scenarios**:

1. **Given** a template page has pending detections displayed as overlays, **When** the designer clicks "Accept" on a single detection, **Then** the detection overlay is converted into a FormCraft element with the suggested type, position, and dimensions, and the overlay is removed.
2. **Given** a detection has an incorrect suggested type (e.g., "text" instead of "date"), **When** the designer changes the type before accepting, **Then** the created element uses the designer's chosen type.
3. **Given** a detection is a false positive (e.g., decorative text or a logo), **When** the designer clicks "Reject", **Then** the overlay is removed and no element is created.
4. **Given** multiple detections are pending, **When** the designer clicks "Accept All", **Then** all pending detections are converted to elements simultaneously.
5. **Given** the designer has accepted some detections, **When** they save the template, **Then** the accepted elements persist and appear in subsequent editing sessions.

---

### User Story 3 - Coordinate Mapping & Accurate Positioning (Priority: P3)

The system accurately maps OCR bounding box coordinates (in pixels relative to the source image) to FormCraft's millimeter-based coordinate system. Elements created from detections must align precisely with the corresponding text regions on the background image, so that when the form is printed and overlaid on the original document, fields line up correctly.

**Why this priority**: Accurate coordinate conversion is essential for the overlay printing use case (printing filled data on pre-printed forms). Without it, accepted fields would be misaligned, making the entire feature unreliable for production use.

**Independent Test**: Can be tested by uploading a form with known dimensions, accepting all detections, and verifying that created elements visually align with their corresponding text regions on the background image.

**Acceptance Scenarios**:

1. **Given** an uploaded image has known pixel dimensions and the page has known millimeter dimensions, **When** detections are converted to elements, **Then** element positions (x_mm, y_mm) and sizes (width_mm, height_mm) correctly correspond to the text region's position on the background image.
2. **Given** a form image has a different aspect ratio than the target page size, **When** the image is set as background, **Then** the system scales coordinates proportionally and maintains alignment between detections and the background.

---

### User Story 4 - Field Classification with Arabic Support (Priority: P3)

The OCR field classifier intelligently suggests element types based on detected text content, nearby labels, and spatial context. It supports both Arabic and English text recognition, identifying common form field patterns in Arabic government and financial documents (dates with Hijri format, currency amounts in EGP/SAR/AED, signature regions near Arabic labels).

**Why this priority**: Intelligent classification reduces the manual review effort for designers. Arabic support is essential since FormCraft's primary market involves Arabic-language forms. However, designers can always override suggestions, so classification accuracy is an enhancement rather than a blocker.

**Independent Test**: Can be tested by uploading sample forms in Arabic and English and verifying that field type suggestions match expected types for known fields (dates, amounts, signatures).

**Acceptance Scenarios**:

1. **Given** a detected text region contains a date pattern (DD/MM/YYYY or Hijri equivalent), **When** the classifier runs, **Then** it suggests "date" as the element type.
2. **Given** a detected text region contains currency indicators (EGP, SAR, AED, or Arabic equivalents), **When** the classifier runs, **Then** it suggests "currency" as the element type.
3. **Given** an empty rectangular region is found near a label containing signature-related keywords in Arabic or English, **When** the classifier runs, **Then** it suggests "signature" as the element type.
4. **Given** a small square region (approximately equal width and height) is detected, **When** the classifier runs, **Then** it suggests "checkbox" as the element type.

---

### User Story 5 - Detection History & Re-Import (Priority: P4)

The system retains detection history for each template page. A designer can view previous import attempts, clear detections, or re-run OCR with a different image. If a page already has detections, the designer is prompted before overwriting them.

**Why this priority**: Useful for iterative workflows where a designer may upload different versions of the same form or want to undo an import. Lower priority because the core workflow (import once, review, accept) covers most use cases.

**Independent Test**: Can be tested by performing two sequential imports on the same page and verifying that detection history is managed correctly with appropriate prompts.

**Acceptance Scenarios**:

1. **Given** a template page already has pending detections from a previous import, **When** the designer uploads a new image, **Then** the system prompts whether to replace or keep existing detections.
2. **Given** a designer wants to start over, **When** they choose to clear all detections for a page, **Then** all pending detection overlays are removed but previously accepted elements remain unchanged.

---

### Edge Cases

- What happens when an uploaded file is not a valid image (e.g., a PDF or corrupt file)? The system validates the file type before processing and shows an error for unsupported formats.
- What happens when the uploaded image exceeds the maximum allowed file size? The system rejects the upload with a message indicating the size limit.
- What happens when OCR returns overlapping bounding boxes for the same text region? The system deduplicates detections by merging overlapping regions, keeping the higher-confidence result.
- What happens when a detection spans across the page boundary (coordinates outside page dimensions)? The system clips the detection to fit within page bounds.
- What happens when the designer's session expires during a long-running OCR operation? The system stores results server-side; the designer can retrieve them when they return.
- What happens when the same form is imported to multiple pages of the same template? Each page maintains its own independent set of detections and background image.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow designers to upload JPEG and PNG images as form imports within the Design Studio.
- **FR-002**: System MUST set the uploaded image as the page background automatically upon import.
- **FR-003**: System MUST send the uploaded image to an external OCR service for text extraction and receive word-level bounding boxes with confidence scores.
- **FR-004**: System MUST convert OCR bounding box coordinates from pixel space to the template page's millimeter coordinate system.
- **FR-005**: System MUST classify each detected text region into a suggested element type (text, date, number, currency, signature, checkbox) based on content patterns, nearby labels, and spatial analysis.
- **FR-006**: System MUST support Arabic and English text recognition and classification patterns (including Hijri dates, Arabic currency names, and Arabic label matching).
- **FR-007**: System MUST display detected fields as interactive overlays on the Design Studio canvas, showing the recognized text, confidence score, and suggested type.
- **FR-008**: System MUST allow designers to accept individual detections, converting them into FormCraft elements at the detected position and dimensions.
- **FR-009**: System MUST allow designers to reject individual detections, removing them from the canvas without creating elements.
- **FR-010**: System MUST allow designers to change the suggested element type of a detection before accepting it.
- **FR-011**: System MUST provide bulk actions to accept all or reject all pending detections on a page.
- **FR-012**: System MUST persist detection records (text, bounding box, confidence, suggested type, acceptance status) for each template page.
- **FR-013**: System MUST validate uploaded files for type (JPEG/PNG only) and size (maximum 10 MB) before processing.
- **FR-014**: System MUST handle OCR service unavailability gracefully, displaying a clear error and still saving the uploaded image as page background.
- **FR-015**: System MUST deduplicate overlapping detections by merging regions with greater than 80% overlap, retaining the higher-confidence result.
- **FR-016**: System MUST prompt the designer when importing a new image to a page that already has pending detections.
- **FR-017**: System MUST log all form import and detection operations for audit purposes.

### Key Entities

- **Form Detection**: A single OCR-detected text region associated with a template page. Contains recognized text, bounding box coordinates (in mm), confidence score, suggested element type, and acceptance status (pending, accepted, rejected). Linked to the template and specific page.
- **Detection Batch**: A group of detections generated from a single OCR import operation. Tracks the source image reference, page dimensions, processing timestamp, and the template page it belongs to.

## Assumptions

- Azure Document Intelligence (or equivalent OCR service) is the assumed external provider, but the specification is service-agnostic. Any OCR service returning word-level text with bounding boxes is compatible.
- Maximum file upload size for form images is 10 MB, consistent with existing Supabase Storage limits in the project.
- The Design Studio canvas already supports background images and overlay rendering via Konva.js, as established in the existing Design Studio feature.
- Only admin and designer roles have access to the form import functionality; form fillers interact only with the resulting published templates.
- OCR processing is synchronous from the user's perspective (the designer waits for results), with expected latency of 2-5 seconds per page. Asynchronous processing with polling could be added in a future iteration if latency becomes problematic.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Designers can import a form image and see detected fields overlaid on the canvas within 10 seconds of upload completion.
- **SC-002**: At least 85% of text regions on standard Arabic bank cheques and government forms are correctly detected and positioned.
- **SC-003**: Field type suggestions are correct for at least 80% of detected regions on common Arabic financial and government forms.
- **SC-004**: Designers can complete the full import-review-accept workflow (upload image, review detections, accept/reject, save) in under 3 minutes for a typical single-page form with 10-20 fields.
- **SC-005**: Accepted elements align with their corresponding text regions on the background image with positional accuracy within 1 mm.
- **SC-006**: 90% of designers report that the import workflow reduces template creation time compared to manually placing elements on a blank canvas.
