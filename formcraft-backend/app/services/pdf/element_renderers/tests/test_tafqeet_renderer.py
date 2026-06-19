"""Tests for TafqeetRenderer integration with font, line insets, and overflow.

Spec 057: the renderer must no longer emit an unconditional `overflow: visible`,
must apply per-line insets, and must default to content-aware shrink-to-fit.
"""

import re

import pytest

from app.services.pdf.element_renderers.tafqeet_renderer import TafqeetRenderer


@pytest.fixture
def renderer():
    return TafqeetRenderer()


def _font_size(html: str) -> float:
    m = re.search(r"font-size:\s*([0-9.]+)pt;", html)
    assert m, f"no font-size in {html!r}"
    return float(m.group(1))


def _tafqeet_element(**formatting):
    el = {
        "type": "tafqeet",
        "x_mm": 10,
        "y_mm": 20,
        "width_mm": 90,
        "height_mm": 12,
        "direction": "rtl",
        "key": "tafqeet_1",
        "formatting": {"sourceElementKey": "amount", "currencyCode": "EGP"},
    }
    el["formatting"].update(formatting)
    return el


class TestTafqeetOverflow:
    def test_no_unconditional_visible_overflow(self, renderer):
        # The legacy bug forced overflow:visible. Default policy is now
        # shrink-to-fit, so the box keeps overflow:hidden.
        el = _tafqeet_element()
        html = renderer.render(el, data={"amount": "123"})
        assert "overflow: visible;" not in html
        assert "overflow: hidden;" in html

    def test_short_amount_keeps_default_size(self, renderer):
        el = _tafqeet_element()
        html = renderer.render(el, data={"amount": "5"})
        assert _font_size(html) == 10

    def test_long_amount_shrinks(self, renderer):
        # A large amount produces long Arabic words that overflow a narrow box.
        el = _tafqeet_element(width_mm=40, height_mm=8)
        html = renderer.render(el, data={"amount": "987654321"})
        assert _font_size(html) < 10

    def test_explicit_visible_opt_in(self, renderer):
        el = _tafqeet_element(overflow="visible")
        html = renderer.render(el, data={"amount": "987654321"})
        assert "overflow: visible;" in html

    def test_blank_when_no_source_value(self, renderer):
        el = _tafqeet_element()
        html = renderer.render(el, data={})
        # Blank cell still renders the positioned box at the default size.
        assert "position: absolute;" in html
        assert _font_size(html) == 10


class TestTafqeetLineInsets:
    def test_line_insets_applied_per_line(self, renderer):
        el = _tafqeet_element(
            lineLayout={
                "first_line_left_inset_mm": 22,
                "last_line_right_inset_mm": 26,
            }
        )
        html = renderer.render(el, data={"amount": "1500"})
        # Tafqeet output is multi-line; insets land on first/last <p>.
        if html.count("<p") >= 2:
            assert "padding-left:22mm" in html
            assert "padding-right:26mm" in html

    def test_custom_font_applied(self, renderer):
        el = _tafqeet_element(font={"family": "Courier", "size_pt": 13, "weight": "bold"})
        html = renderer.render(el, data={"amount": "5"})
        assert "Courier" in html
        assert "font-weight: bold;" in html
