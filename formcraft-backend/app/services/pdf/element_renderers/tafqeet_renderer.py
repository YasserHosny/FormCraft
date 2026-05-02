"""TafqeetRenderer — PDF element renderer for tafqeet (amount-to-words) elements.

Resolves the source element's filled value from the data map, converts it
using TafqeetConverter, and renders HTML with proper Arabic glyph shaping.
"""

import logging
from decimal import Decimal

from app.services.pdf.element_renderers.base import ElementHTMLRenderer
from app.services.pdf.bidi import apply_bidi, reshape_arabic
from app.services.tafqeet.converter import TafqeetConverter

logger = logging.getLogger(__name__)

_converter = TafqeetConverter()


class TafqeetRenderer(ElementHTMLRenderer):
    def render(self, element: dict, data: dict | None = None) -> str:
        fmt = element.get("formatting", {})
        source_key = fmt.get("sourceElementKey")

        # FR-015: null/missing source key → blank cell, no error
        if not source_key:
            return self._blank(element)

        amount_raw = (data or {}).get(source_key)

        # FR-015: absent value in data map → blank cell, no error
        if amount_raw is None:
            return self._blank(element)

        try:
            amount = Decimal(str(amount_raw))
        except Exception:
            return self._blank(element)

        currency_code = fmt.get("currencyCode", "EGP")
        language = fmt.get("outputLanguage", "ar")
        show_currency = fmt.get("showCurrency", True)
        prefix = fmt.get("prefix", "none")
        suffix = fmt.get("suffix", "none")

        result = _converter.convert(
            amount=amount,
            currency_code=currency_code,
            language=language,
            show_currency=show_currency,
            prefix=prefix,
            suffix=suffix,
        )

        if result is None:
            # FR-009b: log conversion error to audit trail (PDF render context only)
            # Audit logger requires a supabase client — log via standard logger here;
            # the pdf renderer doesn't have request context for a DB-backed audit.
            # Callers that have client context should wrap and log separately.
            logger.error(
                "tafqeet_conversion_error",
                extra={
                    "action": "tafqeet.conversion_error",
                    "resource_type": "element",
                    "resource_id": element.get("key"),
                    "metadata": {
                        "amount": str(amount_raw),
                        "currency_code": currency_code,
                    },
                },
            )
            return self._blank(element)

        lines = result.split("\n")
        html_lines = []
        for line in lines:
            is_ar = any("\u0600" <= ch <= "\u06FF" for ch in line)
            direction = "rtl" if is_ar else "ltr"
            text_align = "right" if is_ar else "left"
            # FR-013: Arabic text requires arabic-reshaper + python-bidi
            shaped = apply_bidi(reshape_arabic(line)) if is_ar else line
            html_lines.append(
                f'<p style="margin:0; direction:{direction}; text-align:{text_align};">'
                f"{shaped}</p>"
            )

        style = self._base_style(element)
        # FR-014 / Clarification Q2: overflow is visible — Designer responsibility
        style = style.replace("overflow: hidden;", "overflow: visible;")
        return f'<div style="{style}">{"".join(html_lines)}</div>'

    def _blank(self, element: dict) -> str:
        style = self._base_style(element)
        style = style.replace("overflow: hidden;", "overflow: visible;")
        return f'<div style="{style}"></div>'
