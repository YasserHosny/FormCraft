from app.services.pdf.element_renderers.base import ElementHTMLRenderer


class DateRenderer(ElementHTMLRenderer):
    def render(self, element: dict, data: dict | None = None) -> str:
        style = self._base_style(element)
        formatting = element.get("formatting", {})
        date_format = formatting.get("dateFormat", "YYYY/MM/DD")
        return f'<div style="{style} border-bottom: 0.5pt solid #999;">{date_format}</div>'
