from app.services.pdf.element_renderers.base import ElementHTMLRenderer


class DropdownRenderer(ElementHTMLRenderer):
    def render(self, element: dict, data: dict | None = None) -> str:
        style = self._base_style(element)
        key = element.get("key", "")
        value = (data or {}).get(key) if key else None

        if value is not None:
            # Resolve the human-readable label for the stored value
            options = element.get("options", []) or []
            label = next(
                (o.get("label_ar") or o.get("label_en") or str(value)
                 for o in options if o.get("value") == value),
                str(value),
            )
            return f'<div style="{style} border: 0.5pt solid #999; padding: 1mm;">{label}</div>'

        return (
            f'<div style="{style} border: 0.5pt solid #999; padding: 1mm;">'
            f'<span style="float: inline-end;">&#9660;</span>'
            f"</div>"
        )
