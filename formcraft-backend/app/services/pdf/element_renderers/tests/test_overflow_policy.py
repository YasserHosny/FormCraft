"""Tests for the content-aware overflow / fit policy (US3, FR-07/08/09).

Covers clip, visible, and deterministic shrink-to-fit behavior plus the
edge cases in spec 057 (oversized font height, min-size fallback, and the
guarantee that content which already fits is never shrunk).
"""

import pytest

from app.services.pdf.element_renderers.base import (
    ElementHTMLRenderer,
    _fits_at_size,
)


class MockRenderer(ElementHTMLRenderer):
    def render(self, element, data=None):
        return ""


@pytest.fixture
def renderer():
    return MockRenderer()


def _font_size(html: str) -> float:
    """Extract the rendered font-size in pt from a result div."""
    import re

    m = re.search(r"font-size:\s*([0-9.]+)pt;", html)
    assert m, f"no font-size in {html!r}"
    return float(m.group(1))


class TestFitsAtSize:
    def test_empty_text_always_fits(self):
        assert _fits_at_size(0, 10, 50, 10) is True

    def test_short_text_fits(self):
        assert _fits_at_size(5, 10, 50, 10) is True

    def test_long_text_overflows(self):
        assert _fits_at_size(500, 10, 50, 10) is False

    def test_oversized_single_line_height_never_fits(self):
        # Edge Case #1: a line taller than the box cannot fit at this size.
        assert _fits_at_size(1, 40, 50, 5) is False

    def test_unmeasurable_box_does_not_force_shrink(self):
        # Missing dimensions => cannot measure => treat as fitting.
        assert _fits_at_size(100, 10, 0, 0) is True

    def test_max_lines_cap_reduces_capacity(self):
        # With many geometric lines available, a medium string fits...
        assert _fits_at_size(120, 8, 50, 40) is True
        # ...but capping to a single line makes the same string overflow.
        assert _fits_at_size(120, 8, 50, 40, max_lines=1) is False


class TestOverflowPolicy:
    def _el(self, **over):
        el = {"type": "text", "width_mm": 50, "height_mm": 10, "formatting": {}}
        el["formatting"].update(over)
        return el

    def test_clip_keeps_hidden(self, renderer):
        el = self._el(overflow="clip")
        out = renderer._apply_overflow_policy(
            el, "c", "overflow: hidden;", text_content="x" * 500
        )
        assert "overflow: hidden;" in out
        assert "overflow: visible;" not in out

    def test_visible_opt_in(self, renderer):
        el = self._el(overflow="visible")
        out = renderer._apply_overflow_policy(
            el, "c", "overflow: hidden;", text_content="x" * 500
        )
        assert "overflow: visible;" in out

    def test_text_default_is_clip(self, renderer):
        el = self._el()  # no overflow set, type=text
        out = renderer._apply_overflow_policy(
            el, "c", "overflow: hidden; font-size: 10pt;", text_content="x" * 500
        )
        # clip => no shrink even though content is long
        assert "font-size: 10pt;" in out

    def test_shrink_preserves_fitting_content(self, renderer):
        el = self._el(overflow="shrink-to-fit", font={"size_pt": 12, "min_size_pt": 6})
        out = renderer._apply_overflow_policy(
            el, "c", "font-size: 12pt;", text_content="abc"
        )
        assert _font_size(out) == 12

    def test_shrink_reduces_overflowing_content(self, renderer):
        el = self._el(overflow="shrink-to-fit", font={"size_pt": 18, "min_size_pt": 6})
        out = renderer._apply_overflow_policy(
            el, "c", "font-size: 18pt;", text_content="x" * 300
        )
        assert _font_size(out) < 18

    def test_shrink_never_below_min(self, renderer):
        el = self._el(overflow="shrink-to-fit", font={"size_pt": 14, "min_size_pt": 6})
        out = renderer._apply_overflow_policy(
            el, "c", "font-size: 14pt;", text_content="x" * 9000
        )
        assert _font_size(out) == 6

    def test_shrink_is_deterministic(self, renderer):
        el = self._el(overflow="shrink-to-fit", font={"size_pt": 16, "min_size_pt": 6})
        a = renderer._apply_overflow_policy(
            el, "c", "font-size: 16pt;", text_content="x" * 250
        )
        b = renderer._apply_overflow_policy(
            el, "c", "font-size: 16pt;", text_content="x" * 250
        )
        assert _font_size(a) == _font_size(b)

    def test_oversized_font_height_shrinks(self, renderer):
        # Edge Case #1: configured size taller than the box, even for short text.
        el = {
            "type": "text",
            "width_mm": 60,
            "height_mm": 4,
            "formatting": {
                "overflow": "shrink-to-fit",
                "font": {"size_pt": 30, "min_size_pt": 6},
            },
        }
        out = renderer._apply_overflow_policy(
            el, "c", "font-size: 30pt;", text_content="hi"
        )
        assert _font_size(out) < 30
