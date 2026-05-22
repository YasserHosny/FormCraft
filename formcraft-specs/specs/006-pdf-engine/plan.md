# Implementation Plan: PDF Rendering Engine

**Branch**: `06-pdf-engine` | **Date**: 2026-02-21 | **Spec**: [spec.md](./spec.md)

## Summary

Implement server-side PDF rendering via WeasyPrint with absolute mm positioning, Arabic font embedding (Noto Naskh Arabic), glyph shaping (arabic-reshaper + python-bidi), element-type-specific renderers, multi-page support, and a preview endpoint.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: WeasyPrint, arabic-reshaper, python-bidi, qrcode, python-barcode, Pillow
**Storage**: Supabase Storage (background images, generated PDFs if cached)
**Testing**: pytest, visual regression via PDF-to-image comparison
**Target Platform**: Linux containers (WeasyPrint requires system deps: pango, cairo, gdk-pixbuf)
**Constraints**: < 10s for 20-page template, < 5s for typical 2-page template

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arabic-First | ✅ Pass | Arabic fonts embedded, glyph shaping mandatory |
| II. Pixel-Perfect | ✅ Pass | Absolute mm positioning via CSS, no auto-layout |
| IV. Deterministic | ✅ Pass | Rendering is deterministic given same input |

## Project Structure

### Backend (formcraft-backend)

```text
app/
├── api/routes/
│   └── pdf.py                          # POST /api/pdf/render/{template_id}, GET /api/pdf/preview/{template_id}
├── services/pdf/
│   ├── __init__.py
│   ├── renderer.py                     # Main render orchestrator
│   ├── html_builder.py                 # Builds HTML+CSS from template data
│   ├── element_renderers/
│   │   ├── __init__.py
│   │   ├── base.py                     # Abstract ElementHTMLRenderer
│   │   ├── text_renderer.py            # Text/Number elements
│   │   ├── date_renderer.py            # Date with format
│   │   ├── currency_renderer.py        # Currency with symbol + decimals
│   │   ├── checkbox_renderer.py        # Empty checkbox square
│   │   ├── radio_renderer.py           # Empty radio circle
│   │   ├── dropdown_renderer.py        # Text field with dropdown indicator
│   │   ├── image_renderer.py           # Embedded image
│   │   ├── qr_renderer.py             # QR code generation + embed
│   │   └── barcode_renderer.py         # Barcode generation + embed
│   ├── fonts.py                        # Font registration, Arabic font paths
│   └── bidi.py                         # arabic-reshaper + python-bidi helpers

assets/fonts/
├── NotoNaskhArabic-Regular.ttf
├── NotoNaskhArabic-Bold.ttf
├── NotoSans-Regular.ttf
└── NotoSans-Bold.ttf

tests/
├── unit/
│   ├── test_html_builder.py            # HTML generation correctness
│   ├── test_bidi.py                    # Arabic text shaping
│   └── test_element_renderers.py       # Each element type's HTML output
├── integration/
│   └── test_pdf_render.py              # Full render + position accuracy
└── fixtures/
    ├── reference_pdfs/                 # Reference PDFs for visual comparison
    └── test_templates.json             # Test template data
```

### HTML → PDF Rendering Strategy

WeasyPrint converts HTML+CSS to PDF. Each page becomes an HTML `<div>` with fixed dimensions. Each element becomes an absolutely positioned `<div>` within the page.

```html
<!-- Generated HTML structure -->
<html>
<head>
  <style>
    @font-face {
      font-family: 'Noto Naskh Arabic';
      src: url('file:///app/assets/fonts/NotoNaskhArabic-Regular.ttf');
    }
    @page { size: 210mm 297mm; margin: 0; }
    .page {
      position: relative;
      width: 210mm;
      height: 297mm;
      page-break-after: always;
      overflow: hidden;
    }
    .element {
      position: absolute;
      box-sizing: border-box;
    }
  </style>
</head>
<body>
  <div class="page" style="width:210mm; height:297mm;">
    <!-- Background image if present -->
    <img src="..." style="position:absolute; top:0; left:0; width:100%; height:100%;" />
    <!-- Elements -->
    <div class="element" style="left:10mm; top:20mm; width:50mm; height:8mm; direction:rtl; text-align:right; font-family:'Noto Naskh Arabic'; font-size:12pt;">
      محمد أحمد
    </div>
  </div>
</body>
</html>
```

### Arabic Text Pipeline

```
Raw Arabic text → arabic_reshaper.reshape(text)  → shaped text (correct ligatures)
                → bidi.get_display(shaped_text)   → visually ordered text (RTL → LTR for rendering)
                → inject into HTML with dir="rtl"  → WeasyPrint renders correctly
```

### Dockerfile Dependencies

```dockerfile
# Additional system deps for WeasyPrint
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libcairo2 \
    libffi-dev \
    fonts-noto \
    && rm -rf /var/lib/apt/lists/*
```

## Research Notes

- **WeasyPrint** chosen over ReportLab: WeasyPrint uses HTML+CSS which maps naturally to the absolute-positioning model. CSS `@page` rules handle page dimensions. Easier to maintain than ReportLab's programmatic API.
- **Arabic reshaping**: `arabic-reshaper` handles letter joining forms (initial, medial, final, isolated). `python-bidi` handles BiDi algorithm for mixed-direction text. Both are required for correct Arabic PDF output.
- **QR generation**: `qrcode` library generates PNG in-memory → base64 encode → embed as `<img>` in HTML.
- **Barcode generation**: `python-barcode` generates Code 128 SVG → embed inline in HTML.
- **Visual regression testing**: Render PDF → convert to images (pdf2image/Poppler) → pixel-diff against reference images. Threshold: < 1% pixel difference.

## Complexity Tracking

No constitution violations.
