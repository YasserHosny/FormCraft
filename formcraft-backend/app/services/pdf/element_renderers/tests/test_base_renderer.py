import pytest

from app.services.pdf.element_renderers.base import ElementHTMLRenderer


class MockRenderer(ElementHTMLRenderer):
    def render(self, element, data=None):
        return ""


@pytest.fixture
def renderer():
    return MockRenderer()


class TestBaseStyleFontInjection:
    def test_custom_font_overrides_default(self, renderer):
        element = {
            "x_mm": 10,
            "y_mm": 20,
            "width_mm": 50,
            "height_mm": 10,
            "direction": "rtl",
            "formatting": {
                "font": {
                    "family": "Courier",
                    "size_pt": 13,
                    "weight": "bold",
                    "style": "italic",
                    "color": "#333333",
                }
            },
        }
        style = renderer._base_style(element)
        assert "font-family: 'Courier', 'Noto Naskh Arabic', 'Noto Sans', sans-serif;" in style
        assert "font-size: 13pt;" in style
        assert "font-weight: bold;" in style
        assert "font-style: italic;" in style
        assert "color: #333333;" in style

    def test_fallback_when_formatting_font_absent(self, renderer):
        element = {
            "x_mm": 10,
            "y_mm": 20,
            "width_mm": 50,
            "height_mm": 10,
            "direction": "rtl",
        }
        style = renderer._base_style(element)
        assert "font-family: 'Noto Naskh Arabic', 'Noto Sans', sans-serif;" in style
        assert "font-size: 10pt;" in style
        assert "font-weight: normal;" in style
        assert "font-style: normal;" in style

    def test_partial_font_settings(self, renderer):
        element = {
            "x_mm": 10,
            "y_mm": 20,
            "width_mm": 50,
            "height_mm": 10,
            "direction": "rtl",
            "formatting": {"font": {"size_pt": 14}},
        }
        style = renderer._base_style(element)
        assert "font-size: 14pt;" in style
        assert "font-family: 'Noto Naskh Arabic', 'Noto Sans', sans-serif;" in style
        assert "font-weight: normal;" in style
