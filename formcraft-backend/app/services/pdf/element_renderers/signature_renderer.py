from app.services.pdf.element_renderers.base import ElementHTMLRenderer


class SignatureRenderer(ElementHTMLRenderer):
    def render(self, element: dict, data: dict | None = None) -> str:
        style = self._base_style(element)
        props = element.get("properties", {})
        key = element.get("key", "")

        # Look up the signature value from field_values by element key
        sig_value = data.get(key) if data and key else None

        src = ""
        if sig_value and isinstance(sig_value, str) and sig_value.startswith("data:image"):
            # Raw base64 data URL (e.g. from Spark form filler)
            src = sig_value
        elif sig_value and isinstance(sig_value, dict):
            sig_type = sig_value.get("type", "inline")
            if sig_type == "inline":
                src = sig_value.get("data", "")
            elif sig_type == "storage":
                src = sig_value.get("data", "") or sig_value.get("path", "")

        if src:
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
