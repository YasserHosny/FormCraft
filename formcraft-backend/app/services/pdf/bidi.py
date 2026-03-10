import arabic_reshaper
from bidi.algorithm import get_display


def reshape_arabic(text: str) -> str:
    """Apply Arabic letter joining (reshaping) for correct ligatures."""
    return arabic_reshaper.reshape(text)


def apply_bidi(text: str) -> str:
    """Apply Unicode BiDi algorithm for visual ordering."""
    return get_display(text)


def prepare_text(text: str, direction: str = "auto") -> str:
    """Full Arabic text pipeline: reshape → BiDi reorder.

    For RTL or auto direction with Arabic content, applies reshaping + BiDi.
    For LTR-only text, returns as-is.
    """
    if direction == "ltr":
        return text

    # Check if text contains any Arabic characters
    has_arabic = any("\u0600" <= c <= "\u06FF" for c in text)
    if not has_arabic and direction == "auto":
        return text

    shaped = reshape_arabic(text)
    return apply_bidi(shaped)
