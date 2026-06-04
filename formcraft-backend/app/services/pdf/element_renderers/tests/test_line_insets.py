import pytest

from app.services.pdf.element_renderers.base import ElementHTMLRenderer


class MockRenderer(ElementHTMLRenderer):
    def render(self, element, data=None):
        return ""


@pytest.fixture
def renderer():
    return MockRenderer()


class TestApplyLineInsets:
    def test_no_insets(self, renderer):
        element = {
            "width_mm": 50,
            "formatting": {},
        }
        html = renderer._apply_line_insets(["Line 1", "Line 2"], element)
        assert '<p style="margin:0; direction:rtl; text-align:right;">Line 1</p>' in html
        assert '<p style="margin:0; direction:rtl; text-align:right;">Line 2</p>' in html
        assert "padding-left" not in html
        assert "padding-right" not in html

    def test_first_line_left_inset(self, renderer):
        element = {
            "width_mm": 50,
            "formatting": {
                "lineLayout": {"first_line_left_inset_mm": 22},
            },
        }
        html = renderer._apply_line_insets(["Line 1", "Line 2"], element)
        assert "padding-left:22mm" in html
        # Only first line gets left padding
        parts = html.split("</p>")
        assert "padding-left:22mm" in parts[0]
        assert "padding-left" not in parts[1]

    def test_last_line_right_inset(self, renderer):
        element = {
            "width_mm": 50,
            "formatting": {
                "lineLayout": {"last_line_right_inset_mm": 26},
            },
        }
        html = renderer._apply_line_insets(["Line 1", "Line 2"], element)
        parts = html.split("</p>")
        assert "padding-right:26mm" in parts[1]
        assert "padding-right" not in parts[0]

    def test_max_lines(self, renderer):
        element = {
            "width_mm": 50,
            "formatting": {
                "lineLayout": {"max_lines": 2},
            },
        }
        html = renderer._apply_line_insets(["A", "B", "C"], element)
        assert "A" in html
        assert "B" in html
        assert "C" not in html

    def test_inset_clamping(self, renderer):
        element = {
            "width_mm": 30,
            "formatting": {
                "lineLayout": {
                    "first_line_left_inset_mm": 20,
                    "last_line_right_inset_mm": 20,
                },
            },
        }
        html = renderer._apply_line_insets(["Line 1"], element)
        # Should be clamped so total insets < width
        assert "padding-left" in html
        assert "padding-right" in html


class TestApplyOverflowPolicy:
    def test_clip_default_for_text(self, renderer):
        element = {
            "type": "text",
            "width_mm": 50,
            "height_mm": 10,
            "formatting": {},
        }
        result = renderer._apply_overflow_policy(element, "content", "overflow: hidden;")
        assert "overflow: hidden;" in result
        assert "content" in result

    def test_visible(self, renderer):
        element = {
            "type": "text",
            "width_mm": 50,
            "height_mm": 10,
            "formatting": {"overflow": "visible"},
        }
        result = renderer._apply_overflow_policy(element, "content", "overflow: hidden;")
        assert "overflow: visible;" in result

    def test_shrink_to_fit_reduces_font(self, renderer):
        element = {
            "type": "text",
            "width_mm": 50,
            "height_mm": 10,
            "formatting": {
                "overflow": "shrink-to-fit",
                "font": {"size_pt": 20, "min_size_pt": 6},
            },
        }
        result = renderer._apply_overflow_policy(element, "content", "font-size: 20pt;")
        assert "font-size: 6pt;" in result

    def test_tafqeet_default_shrink_to_fit(self, renderer):
        element = {
            "type": "tafqeet",
            "width_mm": 50,
            "height_mm": 10,
            "formatting": {},
        }
        result = renderer._apply_overflow_policy(element, "content", "font-size: 10pt;")
        # Default for tafqeet is shrink-to-fit
        assert "font-size: 6" in result

    def test_shrink_to_fit_min_size_fallback(self, renderer):
        element = {
            "type": "text",
            "width_mm": 50,
            "height_mm": 10,
            "formatting": {
                "overflow": "shrink-to-fit",
                "font": {"size_pt": 8, "min_size_pt": 6},
            },
        }
        result = renderer._apply_overflow_policy(element, "content", "font-size: 8pt;")
        assert "font-size: 6pt;" in result
