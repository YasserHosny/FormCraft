from app.services.pdf.element_renderers.text_renderer import TextRenderer
from app.services.pdf.element_renderers.date_renderer import DateRenderer
from app.services.pdf.element_renderers.currency_renderer import CurrencyRenderer
from app.services.pdf.element_renderers.checkbox_renderer import CheckboxRenderer
from app.services.pdf.element_renderers.radio_renderer import RadioRenderer
from app.services.pdf.element_renderers.dropdown_renderer import DropdownRenderer
from app.services.pdf.element_renderers.image_renderer import ImageRenderer
from app.services.pdf.element_renderers.qr_renderer import QRRenderer
from app.services.pdf.element_renderers.barcode_renderer import BarcodeRenderer
from app.services.pdf.element_renderers.tafqeet_renderer import TafqeetRenderer
from app.services.pdf.element_renderers.signature_renderer import SignatureRenderer
from app.services.pdf.element_renderers.table_renderer import TableRenderer

RENDERER_MAP = {
    "text": TextRenderer(),
    "number": TextRenderer(),
    "date": DateRenderer(),
    "currency": CurrencyRenderer(),
    "checkbox": CheckboxRenderer(),
    "radio": RadioRenderer(),
    "dropdown": DropdownRenderer(),
    "image": ImageRenderer(),
    "qr": QRRenderer(),
    "barcode": BarcodeRenderer(),
    "tafqeet": TafqeetRenderer(),
    "signature": SignatureRenderer(),
    "table": TableRenderer(),
}


def get_renderer(element_type: str):
    return RENDERER_MAP.get(element_type, TextRenderer())
