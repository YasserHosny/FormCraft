import io

import barcode
from barcode.writer import SVGWriter

from app.services.pdf.element_renderers.base import ElementHTMLRenderer


class BarcodeRenderer(ElementHTMLRenderer):
    def render(self, element: dict, data: dict | None = None) -> str:
        style = self._base_style(element)
        placeholder_data = element.get("key", "000000000")

        # Generate Code 128 barcode as SVG
        code128 = barcode.get("code128", placeholder_data, writer=SVGWriter())
        buffer = io.BytesIO()
        code128.write(buffer)
        svg_str = buffer.getvalue().decode()

        return (
            f'<div style="{style}">'
            f"{svg_str}"
            f"</div>"
        )
