from app.services.pdf.bidi import prepare_text
from app.services.pdf.element_renderers.base import ElementHTMLRenderer


class TextRenderer(ElementHTMLRenderer):
    def render(self, element: dict, data: dict | None = None) -> str:
        style = self._base_style(element)
        label = element.get("label_ar", "") or element.get("label_en", "")
        direction = element.get("direction", "auto")
        display_text = prepare_text(label, direction)
        return f'<div style="{style}">{display_text}</div>'
