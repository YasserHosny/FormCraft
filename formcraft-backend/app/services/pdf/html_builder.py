"""Builds HTML+CSS document from template data for WeasyPrint rendering."""

from app.services.pdf.element_renderers import get_renderer
from app.services.pdf.fonts import generate_font_face_css


def build_html(
    template: dict,
    overlay_mode: bool = False,
    x_offset_mm: float = 0.0,
    y_offset_mm: float = 0.0,
) -> str:
    """Build a complete HTML document from template data.

    When overlay_mode=True, only elements with include_in_overlay=True are
    rendered, backgrounds are suppressed, and positions are shifted by offset.
    """
    font_css = generate_font_face_css()
    pages = template.get("pages", [])

    default_w = 210
    default_h = 297

    page_htmls = []
    for i, page in enumerate(pages):
        w = page.get("width_mm", default_w)
        h = page.get("height_mm", default_h)

        elements_html = []
        for element in page.get("elements", []):
            if overlay_mode and not element.get("include_in_overlay", True):
                continue
            # Apply calibration offsets to element positions
            if x_offset_mm or y_offset_mm:
                element = {**element}
                element["x_mm"] = element.get("x_mm", 0) + x_offset_mm
                element["y_mm"] = element.get("y_mm", 0) + y_offset_mm
            renderer = get_renderer(element.get("type", "text"))
            elements_html.append(renderer.render(element))

        bg_html = ""
        if not overlay_mode and page.get("background_asset"):
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
<html lang="ar">
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
