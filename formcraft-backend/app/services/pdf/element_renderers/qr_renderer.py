import base64
import io

import qrcode

from app.services.pdf.element_renderers.base import ElementHTMLRenderer


class QRRenderer(ElementHTMLRenderer):
    def render(self, element: dict, data: dict | None = None) -> str:
        style = self._base_style(element)
        placeholder_data = element.get("key", "placeholder")

        # Generate QR code as PNG in-memory
        qr = qrcode.make(placeholder_data)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode()

        return (
            f'<div style="{style}">'
            f'<img src="data:image/png;base64,{b64}" '
            f'style="width: 100%; height: 100%; object-fit: contain;" />'
            f"</div>"
        )
