from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    DESIGNER = "designer"
    OPERATOR = "operator"
    VIEWER = "viewer"


class TemplateStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


class ElementType(StrEnum):
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    CURRENCY = "currency"
    DROPDOWN = "dropdown"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    IMAGE = "image"
    QR = "qr"
    BARCODE = "barcode"
    TAFQEET = "tafqeet"


class Country(StrEnum):
    EG = "EG"
    SA = "SA"
    AE = "AE"


class Language(StrEnum):
    AR = "ar"
    EN = "en"


class Direction(StrEnum):
    RTL = "rtl"
    LTR = "ltr"
    AUTO = "auto"
