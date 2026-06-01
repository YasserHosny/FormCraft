from app.services.pdf.element_renderers.base import ElementHTMLRenderer


class DateRenderer(ElementHTMLRenderer):
    def render(self, element: dict, data: dict | None = None) -> str:
        style = self._base_style(element)
        key = element.get("key", "")
        value = (data or {}).get(key) if key else None

        if value:
            display = str(value)
        else:
            # No submitted value — show format hint as placeholder
            formatting = element.get("formatting", {})
            display = formatting.get("dateFormat", "")

        return f'<div style="{style} border-bottom: 0.5pt solid #999;">{display}</div>'
