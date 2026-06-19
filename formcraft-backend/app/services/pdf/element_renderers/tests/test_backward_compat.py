from app.services.pdf.element_renderers.text_renderer import TextRenderer
from app.services.pdf.element_renderers.tafqeet_renderer import TafqeetRenderer


def test_text_renderer_backward_compat():
    renderer = TextRenderer()
    element = {
        "x_mm": 10,
        "y_mm": 20,
        "width_mm": 50,
        "height_mm": 10,
        "direction": "rtl",
        "key": "name",
        "label_ar": "الاسم",
        "label_en": "Name",
    }
    html = renderer.render(element)
    assert "font-family: 'Noto Naskh Arabic', 'Noto Sans', sans-serif;" in html
    assert "font-size: 10pt;" in html
    assert "overflow: hidden;" in html
    assert "الاسم" in html


def test_tafqeet_renderer_backward_compat_blank():
    renderer = TafqeetRenderer()
    element = {
        "type": "tafqeet",
        "x_mm": 10,
        "y_mm": 20,
        "width_mm": 50,
        "height_mm": 10,
        "direction": "rtl",
        "key": "tafqeet_1",
        "formatting": {},
    }
    html = renderer.render(element)
    # No source key → blank cell. Default overflow for tafqeet is shrink-to-fit,
    # but with no content there is nothing to overflow, so the configured
    # default 10pt must be preserved (no unconditional shrink to min).
    assert "font-size: 10pt;" in html
    assert "font-size: 6pt;" not in html
