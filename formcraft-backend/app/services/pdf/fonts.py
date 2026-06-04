import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Font directory relative to project root
FONT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "assets" / "fonts"

FONTS = {
    "NotoNaskhArabic-Regular": FONT_DIR / "NotoNaskhArabic-Regular.ttf",
    "NotoNaskhArabic-Bold": FONT_DIR / "NotoNaskhArabic-Bold.ttf",
    "NotoSans-Regular": FONT_DIR / "NotoSans-Regular.ttf",
    "NotoSans-Bold": FONT_DIR / "NotoSans-Bold.ttf",
}

# Canonical family names that are bundled and embedded
BUNDLED_FAMILIES = {"Noto Naskh Arabic", "Noto Sans"}


def check_fonts() -> list[str]:
    """Return list of missing font files. Empty list means all fonts present."""
    missing = []
    for name, path in FONTS.items():
        if not path.exists():
            missing.append(f"{name}: {path}")
    return missing


def generate_font_face_css() -> str:
    """Generate @font-face CSS declarations for all available fonts."""
    css_parts = []
    for name, path in FONTS.items():
        if path.exists():
            family = "Noto Naskh Arabic" if "Naskh" in name else "Noto Sans"
            weight = "bold" if "Bold" in name else "normal"
            css_parts.append(
                f"@font-face {{\n"
                f"  font-family: '{family}';\n"
                f"  src: url('file://{path}');\n"
                f"  font-weight: {weight};\n"
                f"}}"
            )
    return "\n".join(css_parts)


def resolve_font_family(name: str | None) -> str:
    """Resolve a requested font family to a bundled family or pass-through.

    If *name* is None or empty, returns the default bundled family.
    If *name* matches a bundled family exactly, returns it.
    Otherwise returns the name as-is (WeasyPrint will use system fallback)
    and logs a warning so the caller can surface a designer toast.
    """
    if not name:
        return "Noto Naskh Arabic"

    # Normalise common aliases
    lower = name.strip().lower()
    if lower in {"noto naskh arabic", "notonaskharabic", "naskh"}:
        return "Noto Naskh Arabic"
    if lower in {"noto sans", "notosans", "sans"}:
        return "Noto Sans"

    if name.strip() in BUNDLED_FAMILIES:
        return name.strip()

    logger.warning("font_family_not_bundled", extra={"requested_family": name})
    return name.strip()
