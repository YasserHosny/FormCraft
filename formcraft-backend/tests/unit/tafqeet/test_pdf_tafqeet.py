"""PDF integration tests for TafqeetRenderer — written FIRST (TDD Red phase).

These tests MUST fail until app/services/pdf/element_renderers/tafqeet_renderer.py
is implemented and registered in RENDERER_MAP.

Run with: pytest tests/unit/tafqeet/test_pdf_tafqeet.py -v
"""

import pytest

from app.services.pdf.element_renderers.tafqeet_renderer import TafqeetRenderer

renderer = TafqeetRenderer()


def _element(
    source_key="amount",
    currency_code="SAR",
    language="ar",
    show_currency=True,
    prefix="none",
    suffix="none",
    x_mm=10, y_mm=10, width_mm=80, height_mm=12,
    direction="rtl",
    key="tafqeet_1",
):
    return {
        "key": key,
        "type": "tafqeet",
        "x_mm": x_mm,
        "y_mm": y_mm,
        "width_mm": width_mm,
        "height_mm": height_mm,
        "direction": direction,
        "label_ar": "المبلغ كتابةً",
        "label_en": "Amount in Words",
        "formatting": {
            "sourceElementKey": source_key,
            "currencyCode": currency_code,
            "outputLanguage": language,
            "showCurrency": show_currency,
            "prefix": prefix,
            "suffix": suffix,
        },
    }


# ---------------------------------------------------------------------------
# Filled data — renders non-blank
# ---------------------------------------------------------------------------

class TestPDFRendererFilled:
    def test_arabic_renders_non_blank(self):
        el = _element(source_key="amount", currency_code="SAR", language="ar")
        html = renderer.render(el, {"amount": "7350.00"})
        assert html
        # Should contain a <div> (the wrapper)
        assert "<div" in html
        # Blank check: a blank render is just an empty div
        assert "ريال سعودي" in html or html.count(">") > 1  # not empty

    def test_arabic_rtl_direction_present(self):
        el = _element(source_key="amount", currency_code="SAR", language="ar")
        html = renderer.render(el, {"amount": "1000.00"})
        assert 'direction:rtl' in html or 'dir="rtl"' in html

    def test_both_mode_two_p_tags(self):
        el = _element(source_key="amount", currency_code="EGP", language="both")
        html = renderer.render(el, {"amount": "500.50"})
        assert html.count("<p") == 2

    def test_both_mode_arabic_above_english(self):
        el = _element(source_key="amount", currency_code="EGP", language="both")
        html = renderer.render(el, {"amount": "500.50"})
        rtl_pos = html.find('direction:rtl')
        ltr_pos = html.find('direction:ltr')
        assert rtl_pos != -1 and ltr_pos != -1
        assert rtl_pos < ltr_pos  # Arabic (<p rtl>) comes before English (<p ltr>)

    def test_overflow_visible_in_style(self):
        el = _element(source_key="amount", currency_code="SAR", language="ar")
        html = renderer.render(el, {"amount": "1000.00"})
        # TafqeetRenderer must set overflow: visible (not hidden) per Clarification Q2
        assert "overflow: visible" in html
        assert "overflow: hidden" not in html

    def test_faqat_la_ghair_suffix(self):
        import arabic_reshaper
        from bidi.algorithm import get_display
        el = _element(source_key="amount", currency_code="SAR", language="ar", suffix="faqat_la_ghair")
        html = renderer.render(el, {"amount": "7350.00"})
        # The renderer applies arabic_reshaper + bidi, so check for reshaped form
        reshaped = get_display(arabic_reshaper.reshape("فقط لا غير"))
        assert reshaped in html

    def test_whole_number_no_subunit(self):
        el = _element(source_key="amount", currency_code="SAR", language="ar")
        html = renderer.render(el, {"amount": "7350.00"})
        assert "هللة" not in html


# ---------------------------------------------------------------------------
# Missing / null source value — renders blank
# ---------------------------------------------------------------------------

class TestPDFRendererBlank:
    def test_null_data_renders_blank(self):
        el = _element(source_key="amount")
        html = renderer.render(el, None)
        # Blank: no text content inside the div, just empty wrapper
        assert "<div" in html
        assert "ريال" not in html
        assert "Egyptian" not in html

    def test_missing_source_key_in_data_renders_blank(self):
        el = _element(source_key="amount")
        html = renderer.render(el, {"other_field": "1000"})
        assert "<div" in html
        assert "ريال" not in html

    def test_null_source_key_renders_blank(self):
        el = _element()
        el["formatting"]["sourceElementKey"] = None
        html = renderer.render(el, {"amount": "1000.00"})
        assert "<div" in html
        assert "ريال" not in html

    def test_non_numeric_source_value_renders_blank(self):
        el = _element(source_key="amount")
        html = renderer.render(el, {"amount": "not-a-number"})
        assert "<div" in html
        # Should not raise and should render blank
        assert "ريال" not in html


# ---------------------------------------------------------------------------
# RENDERER_MAP registration
# ---------------------------------------------------------------------------

class TestRendererMapRegistration:
    def test_tafqeet_in_renderer_map(self):
        from app.services.pdf.element_renderers import RENDERER_MAP
        assert "tafqeet" in RENDERER_MAP

    def test_get_renderer_returns_tafqeet_renderer(self):
        from app.services.pdf.element_renderers import get_renderer
        r = get_renderer("tafqeet")
        assert isinstance(r, TafqeetRenderer)
