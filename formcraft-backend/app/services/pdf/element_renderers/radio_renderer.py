from app.services.pdf.element_renderers.base import ElementHTMLRenderer


class RadioRenderer(ElementHTMLRenderer):
    def render(self, element: dict, data: dict | None = None) -> str:
        style = self._base_style(element)
        return (
            f'<div style="{style} display: flex; align-items: center;">'
            f'<div style="width: 4mm; height: 4mm; border: 0.5pt solid #333; '
            f'border-radius: 50%; margin-inline-end: 2mm;"></div>'
            f"</div>"
        )
