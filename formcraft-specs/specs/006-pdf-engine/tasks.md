# Tasks: PDF Rendering Engine

**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Format: `[ID] [Priority] [Story] Description`

## Phase 1: Setup

- [ ] **T06-001** P1 Setup — Install dependencies: `weasyprint`, `arabic-reshaper`, `python-bidi`, `qrcode`, `python-barcode`, `Pillow`, add to requirements.txt
- [ ] **T06-002** P1 Setup — Add system deps to Dockerfile: libpango, libcairo, libgdk-pixbuf, libffi
- [ ] **T06-003** P1 Setup — Download and place Arabic fonts: NotoNaskhArabic-Regular.ttf, NotoNaskhArabic-Bold.ttf, NotoSans-Regular.ttf, NotoSans-Bold.ttf in `assets/fonts/`

## Phase 2: Arabic Text Utilities

- [ ] **T06-010** P1 S2 — Create `app/services/pdf/bidi.py` — `reshape_arabic(text)` using arabic-reshaper, `apply_bidi(text)` using python-bidi get_display, `prepare_text(text, direction)` combining both
- [ ] **T06-011** P1 S2 — Create `app/services/pdf/fonts.py` — Font path registry, font-face CSS generation, startup check for font file existence

## Phase 3: Element HTML Renderers

- [ ] **T06-020** P1 S5 — Create `app/services/pdf/element_renderers/base.py` — Abstract `ElementHTMLRenderer` with `render(element, data) → str` returning HTML fragment
- [ ] **T06-021** P1 S5 — Create `text_renderer.py` — Text/Number elements: positioned div with font, size, direction, Arabic shaping
- [ ] **T06-022** P1 S5 — Create `date_renderer.py` — Date element: format value per element's dateFormat setting
- [ ] **T06-023** P1 S5 — Create `currency_renderer.py` — Currency element: symbol prefix/suffix, decimal places
- [ ] **T06-024** P1 S5 — Create `checkbox_renderer.py` — Empty checkbox square (border only, no fill)
- [ ] **T06-025** P1 S5 — Create `radio_renderer.py` — Empty radio circle (border only)
- [ ] **T06-026** P1 S5 — Create `dropdown_renderer.py` — Text field with down-arrow indicator
- [ ] **T06-027** P1 S5 — Create `image_renderer.py` — Embedded image from Supabase Storage URL (base64 or direct URL)
- [ ] **T06-028** P1 S5 — Create `qr_renderer.py` — Generate QR code PNG in-memory → base64 embed in img tag
- [ ] **T06-029** P1 S5 — Create `barcode_renderer.py` — Generate Code 128 barcode SVG → inline embed
- [ ] **T06-030** P1 S5 — Create element renderer factory: `ElementType → Renderer` mapping

## Phase 4: HTML Builder & PDF Renderer

- [ ] **T06-040** P1 S1 — Create `app/services/pdf/html_builder.py` — Build full HTML document: @font-face declarations, @page CSS, page divs with absolute positioning, element divs from renderers
- [ ] **T06-041** P1 S1 — Create `app/services/pdf/renderer.py` — Orchestrator: load template+pages+elements → build HTML → call WeasyPrint `HTML(string=html).write_pdf()` → return bytes
- [ ] **T06-042** P1 S1 — Handle background images: full-page img in page div, positioned behind elements
- [ ] **T06-043** P1 S3 — Implement mixed-direction text: `dir` attribute on element divs, BiDi processing for Arabic segments

## Phase 5: API Routes

- [ ] **T06-050** P1 S1 — Create `app/api/routes/pdf.py` — POST /api/pdf/render/{template_id} returning StreamingResponse with application/pdf
- [ ] **T06-051** P2 S4 — Add GET /api/pdf/preview/{template_id} — Same render but with Content-Disposition: inline (for browser preview)

## Phase 6: Tests

- [ ] **T06-060** P1 S2 — Write `tests/unit/test_bidi.py` — Arabic reshaping correctness, BiDi ordering, mixed-direction text
- [ ] **T06-061** P1 S5 — Write `tests/unit/test_element_renderers.py` — Each renderer produces valid HTML with correct positioning CSS
- [ ] **T06-062** P1 S1 — Write `tests/unit/test_html_builder.py` — Full HTML document structure, page dimensions, font declarations
- [ ] **T06-063** P1 S1 — Write `tests/integration/test_pdf_render.py` — Render a test template, verify PDF is valid, check page count, verify file size is reasonable
- [ ] **T06-064** P1 S1 — Create `tests/fixtures/test_templates.json` — Test template data with various element types and Arabic text
- [ ] **T06-065** P2 S1 — Create `tests/fixtures/reference_pdfs/` — Reference PDF images for visual regression comparison

## Phase 7: Frontend — Preview Integration

- [ ] **T06-070** P2 S4 — Add "Preview PDF" button in Design Studio toolbar
- [ ] **T06-071** P2 S4 — Create preview dialog: MatDialog with embedded PDF viewer (iframe or pdf.js)
- [ ] **T06-072** P1 S1 — Add "Export PDF" button: calls render endpoint, triggers browser download

## Dependencies & Execution Order

```
T06-001 → T06-002 → T06-003 (setup, sequential)
T06-010, T06-011 (parallel: bidi + fonts)
T06-020 → T06-021-030 (base renderer → all type renderers)
T06-010, T06-030 → T06-040 → T06-041 (bidi + renderers → html builder → orchestrator)
T06-041 → T06-050, T06-051 (renderer → routes)
T06-060-065 (tests after implementation)
T06-070-072 (frontend, after backend routes)
```

## Parallel Opportunities

- All element renderers (T06-021 through T06-029) in parallel
- Bidi utils (T06-010) and fonts (T06-011) in parallel
- All unit tests (T06-060 through T06-062) in parallel
- Frontend preview (T06-070-072) independent of backend tests
