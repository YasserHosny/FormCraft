from app.services.pdf.element_renderers.base import ElementHTMLRenderer


class ImageRenderer(ElementHTMLRenderer):
    def render(self, element: dict, data: dict | None = None) -> str:
        style = self._base_style(element)
        # In print mode, show a placeholder box if no data
        return (
            f'<div style="{style} border: 0.5pt dashed #ccc; '
            f'display: flex; align-items: center; justify-content: center; '
            f'color: #999; font-size: 8pt;">IMAGE</div>'
        )
