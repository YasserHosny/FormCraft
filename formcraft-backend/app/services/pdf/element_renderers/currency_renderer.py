from app.services.pdf.element_renderers.base import ElementHTMLRenderer


class CurrencyRenderer(ElementHTMLRenderer):
    def render(self, element: dict, data: dict | None = None) -> str:
        style = self._base_style(element)
        key = element.get("key", "")
        value = (data or {}).get(key) if key else None

        if value is not None:
            formatting = element.get("formatting", {})
            currency_code = formatting.get("currencyCode", "")
            display = f"{value} {currency_code}".strip() if currency_code else str(value)
        else:
            display = ""

        return f'<div style="{style} border-bottom: 0.5pt solid #999;">{display}</div>'
