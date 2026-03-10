from app.services.pdf.element_renderers.base import ElementHTMLRenderer


class DropdownRenderer(ElementHTMLRenderer):
    def render(self, element: dict, data: dict | None = None) -> str:
        style = self._base_style(element)
        return (
            f'<div style="{style} border: 0.5pt solid #999; padding: 1mm;">'
            f'<span style="float: inline-end;">&#9660;</span>'
            f"</div>"
        )
