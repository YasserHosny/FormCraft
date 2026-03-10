"""Builds HTML+CSS document from template data for WeasyPrint rendering."""

from app.services.pdf.element_renderers import get_renderer
from app.services.pdf.fonts import generate_font_face_css


def build_html(template: dict) -> str:
    """Build a complete HTML document from template data."""
    font_css = generate_font_face_css()
    pages = template.get("pages", [])

    # Use first page dimensions or default A4
    default_w = 210
    default_h = 297

    page_htmls = []
    for i, page in enumerate(pages):
        w = page.get("width_mm", default_w)
        h = page.get("height_mm", default_h)

        elements_html = []
        for element in page.get("elements", []):
            renderer = get_renderer(element.get("type", "text"))
            elements_html.append(renderer.render(element))

        bg_html = ""
        if page.get("background_asset"):
            bg_html = (
                f'<img src="{page["background_asset"]}" '
                f'style="position: absolute; top: 0; left: 0; '
                f'width: 100%; height: 100%;" />'
            )

        page_break = "page-break-after: always;" if i < len(pages) - 1 else ""
        page_htmls.append(
            f'<div class="page" style="width: {w}mm; height: {h}mm; {page_break}">'
            f"{bg_html}"
            f"{''.join(elements_html)}"
            f"</div>"
        )

    return f"""<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="utf-8">
<style>
{font_css}
@page {{
    size: {default_w}mm {default_h}mm;
    margin: 0;
}}
body {{
    margin: 0;
    padding: 0;
    font-family: 'Noto Naskh Arabic', 'Noto Sans', sans-serif;
}}
.page {{
    position: relative;
    overflow: hidden;
}}
</style>
</head>
<body>
{''.join(page_htmls)}
</body>
</html>"""
