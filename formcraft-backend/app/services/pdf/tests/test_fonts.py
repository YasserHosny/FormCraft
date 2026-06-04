import pytest

from app.services.pdf.fonts import resolve_font_family


def test_resolve_font_family_default():
    assert resolve_font_family(None) == "Noto Naskh Arabic"
    assert resolve_font_family("") == "Noto Naskh Arabic"


def test_resolve_font_family_bundled():
    assert resolve_font_family("Noto Naskh Arabic") == "Noto Naskh Arabic"
    assert resolve_font_family("Noto Sans") == "Noto Sans"


def test_resolve_font_family_aliases():
    assert resolve_font_family("noto naskh arabic") == "Noto Naskh Arabic"
    assert resolve_font_family("NotoSans") == "Noto Sans"
    assert resolve_font_family("naskh") == "Noto Naskh Arabic"


def test_resolve_font_family_custom(caplog):
    with caplog.at_level("WARNING"):
        result = resolve_font_family("Courier")
    assert result == "Courier"
    assert "font_family_not_bundled" in caplog.text
