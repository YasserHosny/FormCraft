from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    DESIGNER = "designer"
    OPERATOR = "operator"
    VIEWER = "viewer"
    BRANCH_MANAGER = "branch_manager"


class TemplateStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED_FOR_REVIEW = "submitted_for_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


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
    SIGNATURE = "signature"
    TABLE = "table"


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


# F29: Notification Center
class NotificationType(StrEnum):
    TEMPLATE_SUBMITTED_FOR_REVIEW = "template_submitted_for_review"
    TEMPLATE_APPROVED = "template_approved"
    TEMPLATE_REJECTED = "template_rejected"
    TEMPLATE_PUBLISHED = "template_published"
    TEMPLATE_WITHDRAWN = "template_withdrawn"
    TEMPLATE_FEEDBACK_RECEIVED = "template_feedback_received"
    TEMPLATE_FEEDBACK_RESOLVED = "template_feedback_resolved"
    DRAFT_EXPIRING = "draft_expiring"
    SYSTEM_ANNOUNCEMENT = "system_announcement"


class EmailStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    SKIPPED = "skipped"


class IdentifierType(StrEnum):
    NATIONAL_ID = "national_id"
    IQAMA = "iqama"
    COMMERCIAL_REGISTER = "commercial_register"
    PASSPORT = "passport"
    OTHER = "other"
