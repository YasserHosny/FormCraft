import os
from pathlib import Path

# Font directory relative to project root
FONT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "assets" / "fonts"

FONTS = {
    "NotoNaskhArabic-Regular": FONT_DIR / "NotoNaskhArabic-Regular.ttf",
    "NotoNaskhArabic-Bold": FONT_DIR / "NotoNaskhArabic-Bold.ttf",
    "NotoSans-Regular": FONT_DIR / "NotoSans-Regular.ttf",
    "NotoSans-Bold": FONT_DIR / "NotoSans-Bold.ttf",
}


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
