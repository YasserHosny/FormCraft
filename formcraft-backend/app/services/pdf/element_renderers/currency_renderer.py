from app.services.pdf.element_renderers.base import ElementHTMLRenderer


class CurrencyRenderer(ElementHTMLRenderer):
    def render(self, element: dict, data: dict | None = None) -> str:
        style = self._base_style(element)
        formatting = element.get("formatting", {})
        currency_code = formatting.get("currencyCode", "EGP")
        return f'<div style="{style} border-bottom: 0.5pt solid #999;">{currency_code}</div>'
