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


class Currency(StrEnum):
    SAR = "SAR"
    EGP = "EGP"
    AED = "AED"
    USD = "USD"


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
    SUBSCRIPTION_PAYMENT_FAILED = "subscription_payment_failed"


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


class ReportType(StrEnum):
    TRANSACTION_REGISTER = "transaction_register"
    DAILY_RECONCILIATION = "daily_reconciliation"
    PERIOD_SUMMARY = "period_summary"
    CUSTOM = "custom"
    BENEFICIARY = "beneficiary"
    VOID_REPRINT = "void_reprint"
    SIGNATORY_USAGE = "signatory_usage"


class ReportFrequency(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ExportFormat(StrEnum):
    XLSX = "xlsx"
    CSV = "csv"
    PDF = "pdf"


class NoDataBehavior(StrEnum):
    SEND_EMPTY = "send_empty"
    SKIP_DELIVERY = "skip_delivery"


class ScheduleStatus(StrEnum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class GenerationMethod(StrEnum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"


class DeliveryStatus(StrEnum):
    GENERATED = "generated"
    DELIVERED = "delivered"
    DELIVERY_FAILED = "delivery_failed"


class FieldTypeTag(StrEnum):
    AMOUNT = "amount"
    DATE = "date"
    CUSTOMER_NAME = "customer_name"
    CUSTOMER_ID = "customer_id"
    REFERENCE_NUMBER = "reference_number"
    BENEFICIARY = "beneficiary"
    SIGNATORY = "signatory"
