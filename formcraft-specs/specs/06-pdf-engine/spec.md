# Feature Specification: PDF Rendering Engine

**Feature Branch**: `06-pdf-engine`
**Created**: 2026-02-21
**Status**: Draft
**Input**: FormCraft PRD Phase 4 – PDF Rendering Engine

## User Scenarios & Testing

### User Story 1 - Render Template to PDF with Absolute Positioning (Priority: P1)

A user (Designer or Operator) can export a template to PDF. The PDF renders all elements at their exact positions (x, y, width, height in mm) matching the canvas design. Page dimensions match the template's page configuration. Multi-page templates produce multi-page PDFs.

**Why this priority**: PDF export is the primary output of the entire application.

**Independent Test**: Can be tested by creating a template with elements at known positions, generating the PDF, and measuring element positions in the output.

**Acceptance Scenarios**:

1. **Given** a template with an A4 page (210x297mm) and a text element at (10, 20, 50, 8) mm, **When** the PDF is generated, **Then** the text element appears at exactly 10mm from the left edge and 20mm from the top edge, with width 50mm and height 8mm.
2. **Given** a template with 3 pages, **When** the PDF is generated, **Then** the output PDF has exactly 3 pages with correct dimensions per page.
3. **Given** a page with a background image, **When** the PDF is generated, **Then** the background image fills the entire page without distortion.

---

### User Story 2 - Arabic Text Rendering with Glyph Shaping (Priority: P1)

Arabic text in PDF output is correctly shaped using arabic-reshaper and rendered RTL using python-bidi. Fonts with Arabic glyph support (Noto Naskh Arabic) are embedded. Arabic text aligns to the right edge of the element bounding box.

**Why this priority**: Correct Arabic rendering in PDF is a constitutional requirement (Principle I and II).

**Independent Test**: Can be tested by rendering Arabic text "بسم الله الرحمن الرحيم" and verifying correct ligature formation and RTL flow in the PDF.

**Acceptance Scenarios**:

1. **Given** an element with Arabic text "محمد أحمد", **When** the PDF is generated, **Then** the text shows correct Arabic ligatures (connected letters) and flows right-to-left.
2. **Given** an element with direction "rtl", **When** the PDF renders text, **Then** the text is right-aligned within the element bounding box.
3. **Given** Arabic text with diacritics "مُحَمَّد", **When** the PDF is generated, **Then** diacritics are correctly positioned above/below letters.

---

### User Story 3 - Mixed Direction Text (Priority: P1)

Elements containing both Arabic and English text render correctly following Unicode BiDi rules. Arabic segments flow RTL, English segments flow LTR, within the same line.

**Why this priority**: Government forms frequently mix Arabic labels with English values (e.g., "رقم Passport: AB123456").

**Independent Test**: Can be tested by rendering mixed text and verifying segment ordering matches BiDi algorithm output.

**Acceptance Scenarios**:

1. **Given** a text element containing "رقم الجواز Passport Number: AB123456", **When** the PDF renders, **Then** Arabic text flows RTL and English text flows LTR within the same line.
2. **Given** a number element with Arabic label and numeric value, **When** the PDF renders, **Then** numbers display in Western Arabic numerals (0-9), not Eastern Arabic (٠-٩).

---

### User Story 4 - PDF Preview in Browser (Priority: P2)

Before downloading, the user can preview the PDF in the browser using an embedded PDF viewer. The preview reflects the current template state.

**Why this priority**: Preview reduces export-check-fix cycles but is not blocking for basic PDF generation.

**Independent Test**: Can be tested by clicking Preview and verifying the PDF loads in the browser viewer.

**Acceptance Scenarios**:

1. **Given** a template in the Design Studio, **When** the Designer clicks "Preview PDF", **Then** a dialog opens with an embedded PDF viewer showing the rendered output.
2. **Given** the preview is open, **When** the Designer closes it and changes an element, **Then** the next preview reflects the changes.

---

### User Story 5 - Element Type Rendering (Priority: P1)

Each element type renders appropriately in the PDF:
- **Text/Number**: Rendered as text at specified font, size, alignment.
- **Date**: Rendered with applied date format.
- **Currency**: Rendered with currency symbol and decimal places.
- **Checkbox**: Rendered as an empty checkbox square (for print-and-fill forms).
- **Radio**: Rendered as an empty radio circle.
- **Dropdown**: Rendered as a text field with dropdown indicator.
- **Image**: Embedded image at element position and dimensions.
- **QR**: Generated QR code image from element value or placeholder.
- **Barcode**: Generated barcode image (Code 128) from element value or placeholder.

**Why this priority**: All element types must render correctly for the PDF to be useful.

**Independent Test**: Can be tested by creating one element of each type and verifying PDF rendering.

**Acceptance Scenarios**:

1. **Given** a checkbox element, **When** the PDF renders, **Then** an empty square (checkbox outline) appears at the element's position.
2. **Given** a QR element with value "https://formcraft.iron-sys.com/form/123", **When** the PDF renders, **Then** a scannable QR code image appears at the correct position.
3. **Given** a barcode element with value "1234567890", **When** the PDF renders, **Then** a Code 128 barcode image appears at the correct position.
4. **Given** a currency element with currencyCode "SAR" and decimalPlaces 2, **When** the PDF renders, **Then** the value shows as "ر.س 1,234.56".

---

### User Story 6 - Render PDF with Filled Data (Priority: P2)

A user can export a PDF with pre-filled data values. The system accepts a data dictionary mapping element keys to values and renders each element with its filled value instead of its label. This supports both fill-mode workflows and data-driven form generation.

**Why this priority**: Fill mode and data export are essential for operators filling out forms and for automated form generation workflows.

**Independent Test**: Can be tested by providing filled data for a template and verifying the PDF renders with actual values instead of labels.

**Acceptance Scenarios**:

1. **Given** a template with element key "payee_name", **When** PDF is rendered with data `{"payee_name": "محمد أحمد"}`, **Then** the PDF shows "محمد أحمد" instead of the element label.
2. **Given** a date element with key "issue_date", **When** PDF is rendered with data `{"issue_date": "25/09/2012"}`, **Then** the PDF shows the formatted date.
3. **Given** a currency element with key "amount", **When** PDF is rendered with data `{"amount": "12345.678"}`, **Then** the PDF shows "12,345.68 EGP" with correct formatting.
4. **Given** elements without provided data, **When** PDF is rendered, **Then** those elements show their labels or remain empty (configurable).
5. **Given** a checkbox element with key "agreed", **When** PDF is rendered with data `{"agreed": true}`, **Then** the checkbox shows as checked (X or ✓ inside).

---

### Edge Cases

- What happens when an Arabic font is missing from the server? → Build fails at startup; font availability is checked at boot time.
- What happens when an element has no text content? → Renders as an empty bounding box (placeholder outline for print-and-fill).
- What happens when an image element references a deleted asset? → Renders a placeholder "Image Not Found" box.
- What happens when the PDF has 100+ pages? → WeasyPrint handles it; response streams to avoid memory issues.
- What happens with very small text (< 6pt)? → Minimum font size enforced at 6pt in rendering.

## Requirements

### Functional Requirements

- **FR-001**: System MUST expose `POST /api/pdf/render/{template_id}` endpoint that returns a PDF binary.
- **FR-002**: PDF MUST use absolute positioning in mm for all elements. No auto-layout or reflow.
- **FR-003**: PDF page dimensions MUST match the template's page width and height.
- **FR-004**: System MUST embed Arabic fonts (Noto Naskh Arabic) in every PDF. No system font fallback.
- **FR-005**: System MUST use arabic-reshaper for glyph shaping and python-bidi for BiDi text ordering.
- **FR-006**: System MUST render all 10 element types correctly (text, number, date, currency, dropdown, radio, checkbox, image, qr, barcode).
- **FR-007**: QR codes MUST be generated using the `qrcode` Python library.
- **FR-008**: Barcodes MUST be generated using `python-barcode` library (Code 128 format).
- **FR-009**: System MUST support background images per page (JPEG, PNG).
- **FR-010**: System MUST support multi-page PDF generation.
- **FR-011**: PDF generation MUST complete within 10 seconds for templates up to 20 pages.
- **FR-012**: System MUST stream PDF response with `Content-Type: application/pdf`.
- **FR-013**: System MUST support a preview endpoint that returns the same PDF for in-browser display.
- **FR-014**: RTL text MUST right-align within element bounding boxes.
- **FR-015**: Mixed-direction text MUST follow Unicode BiDi algorithm.
- **FR-016**: Numbers MUST render as Western Arabic numerals (0-9) in all locales.
- **FR-017**: Minimum font size for PDF text is 6pt.
- **FR-018**: Currency formatting MUST respect the element's currencyCode and decimalPlaces settings.
- **FR-019**: Date formatting MUST respect the element's dateFormat setting.
- **FR-020**: System MUST accept optional `data` parameter in PDF render endpoint mapping element keys to filled values.
- **FR-021**: When `data` is provided, system MUST render filled values instead of element labels.
- **FR-022**: Elements without filled data MUST render as empty or show labels (configurable via `empty_mode` parameter).
- **FR-023**: Filled data MUST be validated against element types and constraints before rendering.
- **FR-024**: Checkbox elements with boolean filled data MUST render as checked (✓) or unchecked (empty square).
- **FR-025**: Date elements with string filled data MUST apply the element's dateFormat before rendering.
- **FR-026**: Currency elements with numeric filled data MUST apply currencyCode and decimalPlaces formatting.

### Key Entities

- **PDFRenderRequest**: template_id, data (optional key-value map for filled forms)
- **PDFRenderContext**: Resolved template with all pages, elements, fonts, and assets loaded.
- **ElementRenderer**: Strategy pattern — each element type has a dedicated renderer class.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Element positions in the generated PDF are accurate to within 0.5mm of the canvas design.
- **SC-002**: Arabic text ligatures render correctly (verified by visual comparison tests against reference PDFs).
- **SC-003**: PDF generation completes within 5 seconds for a typical 2-page A4 template (p95).
- **SC-004**: All 10 element types render correctly in the PDF (verified by automated snapshot tests).
- **SC-005**: QR codes in the PDF are scannable by standard QR readers.
- **SC-006**: Mixed Arabic-English text follows correct BiDi ordering (verified against reference rendering).
