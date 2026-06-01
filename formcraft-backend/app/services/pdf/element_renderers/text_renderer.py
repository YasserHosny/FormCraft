from app.services.pdf.element_renderers.base import ElementHTMLRenderer


class TextRenderer(ElementHTMLRenderer):
    def render(self, element: dict, data: dict | None = None) -> str:
        style = self._base_style(element)
        key = element.get("key", "")

        # When field_values (data) are provided and this element has a matching key,
        # show the submitted value; otherwise fall back to the label text.
        if data is not None and key and data.get(key) is not None:
            display_text = str(data[key])
        else:
            display_text = element.get("label_ar", "") or element.get("label_en", "")

        # WeasyPrint uses HarfBuzz which handles Arabic shaping and BiDi natively.
        # Do NOT pre-process with arabic_reshaper / python-bidi — that causes double
        # BiDi processing which reverses/breaks the glyph order.
        return f'<div style="{style}">{display_text}</div>'
