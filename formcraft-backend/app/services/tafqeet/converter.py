"""TafqeetConverter — pure stateless amount-to-words converter.

Arabic: tafqit library
English: num2words library (lang="en")
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Literal

from num2words import num2words


def _tafqit(n: int) -> str:
    """Convert integer to Arabic words using num2words."""
    return num2words(n, lang="ar")


# ---------------------------------------------------------------------------
# Currency map: code → (ar_unit, en_unit, ar_subunit, en_subunit, factor)
# ---------------------------------------------------------------------------

CURRENCY_MAP: dict[str, tuple[str, str, str, str, int]] = {
    "EGP": ("جنيه مصري",    "Egyptian Pound",  "قرش",  "Piastre",  100),
    "SAR": ("ريال سعودي",   "Saudi Riyal",     "هللة", "Halala",   100),
    "AED": ("درهم إماراتي", "UAE Dirham",       "فلس",  "Fils",     100),
    "USD": ("دولار أمريكي", "US Dollar",        "سنت",  "Cent",     100),
}

# prefix map: key → (arabic_text, english_text)
PREFIX_MAP: dict[str, tuple[str, str]] = {
    "faqat": ("فقط", ""),
    "none":  ("",    ""),
}

# suffix map: key → (arabic_text, english_text)
SUFFIX_MAP: dict[str, tuple[str, str]] = {
    "la_ghair":       ("لا غير",      ""),
    "faqat_la_ghair": ("فقط لا غير",  ""),
    "only":           ("",             "Only"),
    "none":           ("",             ""),
}


class TafqeetConverter:
    """Stateless converter. No external dependencies beyond tafqit and num2words."""

    def convert(
        self,
        amount: Decimal,
        currency_code: str,
        language: Literal["ar", "en", "both"],
        show_currency: bool,
        prefix: str,
        suffix: str,
    ) -> str | None:
        """Convert amount to words.

        Returns converted text or None for:
        - negative amounts
        - amounts > 999,999,999,999
        - unexpected library exceptions
        """
        try:
            if amount < 0 or amount > 999_999_999_999:
                return None

            amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            int_part = int(amount)
            sub_part = int(round((float(amount) - int_part) * 100))

            ar_unit, en_unit, ar_sub, en_sub, _ = CURRENCY_MAP[currency_code]

            lines: list[str] = []
            if language in ("ar", "both"):
                lines.append(
                    self._build_ar(int_part, sub_part, ar_unit, ar_sub, show_currency, prefix, suffix)
                )
            if language in ("en", "both"):
                lines.append(
                    self._build_en(int_part, sub_part, en_unit, en_sub, show_currency, suffix)
                )

            return "\n".join(lines)

        except Exception:
            return None  # caller decides whether to audit-log

    # ------------------------------------------------------------------
    # Private builders
    # ------------------------------------------------------------------

    def _build_ar(
        self,
        int_part: int,
        sub_part: int,
        unit: str,
        sub_unit: str,
        show_currency: bool,
        prefix: str,
        suffix: str,
    ) -> str:
        ar_prefix, _ = PREFIX_MAP.get(prefix, ("", ""))
        ar_suffix, _ = SUFFIX_MAP.get(suffix, ("", ""))

        body = _tafqit(int_part)
        if show_currency:
            body = f"{body} {unit}"
            if sub_part > 0:
                body = f"{body} و{_tafqit(sub_part)} {sub_unit}"

        parts = [p for p in [ar_prefix, body, ar_suffix] if p]
        return " ".join(parts)

    def _build_en(
        self,
        int_part: int,
        sub_part: int,
        unit: str,
        sub_unit: str,
        show_currency: bool,
        suffix: str,
    ) -> str:
        _, en_suffix = SUFFIX_MAP.get(suffix, ("", ""))

        body = num2words(int_part, lang="en").capitalize()
        if show_currency:
            plural = "s" if int_part != 1 else ""
            body = f"{body} {unit}{plural}"
            if sub_part > 0:
                sub_words = num2words(sub_part, lang="en").capitalize()
                sub_plural = "s" if sub_part != 1 else ""
                body = f"{body} and {sub_words} {sub_unit}{sub_plural}"

        parts = [p for p in [body, en_suffix] if p]
        return " ".join(parts)
