from app.services.pdf.element_renderers.base import ElementHTMLRenderer


class SignatureRenderer(ElementHTMLRenderer):
    def render(self, element: dict, data: dict | None = None) -> str:
        style = self._base_style(element)
        props = element.get("properties", {})

        if data and isinstance(data, dict):
            sig_type = data.get("type", "inline")
            if sig_type == "inline":
                src = data.get("data", "")
            elif sig_type == "storage":
                src = data.get("data", "") or data.get("path", "")
            else:
                src = ""
        else:
            src = ""

        if src:
            pen_color = props.get("pen_color", "#000000")
            return (
                f'<img src="{src}" '
                f'style="{style} object-fit: contain; '
                f'border: none;" />'
            )

        label = props.get("label_ar", "") or props.get("label_en", "") or "Signature"
        return (
            f'<div style="{style} border: 1pt dashed #ccc; '
            f'display: flex; align-items: center; justify-content: center; '
            f'color: #999; font-size: 8pt;">{label}</div>'
        )