"""Portal schemas for public and admin DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class PublicPortalSettings(BaseModel):
    otp_required: bool
    allowed_otp_modes: list[str] = []
    captcha_enabled: bool
    captcha_provider: str | None = None
    allow_pdf_download: bool


class PublicFormSession(BaseModel):
    session_token: str
    template_id: UUID
    template_version: int
    title: str
    language_default: str = "ar"
    fields: list[dict] = []
    settings: PublicPortalSettings


class OtpSendRequest(BaseModel):
    contact_mode: str
    contact_value: str


class OtpSendResponse(BaseModel):
    status: str
    expires_at: datetime


class OtpVerifyRequest(BaseModel):
    code: str


class OtpVerifyResponse(BaseModel):
    status: str


class PublicSubmissionRequest(BaseModel):
    field_values: dict
    captcha_token: str | None = None


class PublicSubmissionResponse(BaseModel):
    reference_number: str
    pdf_download_url: str | None = None
    email_confirmation_status: str | None = None


class PortalConfiguration(BaseModel):
    template_id: UUID
    public_slug: str
    public_url: str = ""
    public_qr_svg: str | None = None
    enabled: bool
    verification_required: bool
    allowed_otp_modes: list[str] = []
    captcha_enabled: bool
    captcha_provider: str | None = None
    allow_pdf_download: bool
    send_email_confirmation: bool
    rate_limit_max: int = 10
    rate_limit_window_minutes: int = 60


class PortalConfigurationUpdate(PortalConfiguration):
    pass


class PortalTemplateListResponse(BaseModel):
    items: list[PortalConfiguration] = []


class PortalAnalyticsResponse(BaseModel):
    submission_count: int = 0
    otp_sent_count: int = 0
    otp_failure_count: int = 0
    rate_limited_count: int = 0
    email_confirmation_failure_count: int = 0
