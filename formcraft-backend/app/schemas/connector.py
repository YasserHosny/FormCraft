"""Schemas for Feature 049: Connector Framework."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, HttpUrl


class EventType(StrEnum):
    FORM_SUBMITTED = "form_submitted"
    FORM_PRINTED = "form_printed"
    TEMPLATE_PUBLISHED = "template_published"
    BATCH_COMPLETED = "batch_completed"


class ConnectorType(StrEnum):
    DMS = "dms"
    EMAIL = "email"
    CRM = "crm"
    BANKING = "banking"


class DeliveryStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    SUCCESS = "success"
    FAILED = "failed"


# ----------------------------------------------------------------------
# API Keys
# ----------------------------------------------------------------------

class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    scopes: list[str] = Field(default_factory=lambda: ["read"], min_length=1)
    expires_at: datetime | None = None

    @field_validator("scopes")
    @classmethod
    def _valid_scopes(cls, v: list[str]) -> list[str]:
        allowed = {"read", "write", "admin"}
        bad = [s for s in v if s not in allowed]
        if bad:
            raise ValueError(f"Invalid scopes: {bad}. Allowed: {sorted(allowed)}")
        return v


class ApiKeyResponse(BaseModel):
    id: UUID
    org_id: UUID
    name: str
    key_prefix: str   # e.g. "fck_AbC123"
    scopes: list[str]
    created_at: datetime
    last_used_at: datetime | None = None
    expires_at: datetime | None = None
    is_active: bool


class ApiKeyCreatedResponse(ApiKeyResponse):
    """One-time response that includes the cleartext secret. Show once, never store, never return again."""
    secret: str


# ----------------------------------------------------------------------
# Webhooks
# ----------------------------------------------------------------------

class WebhookCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    event_type: EventType
    endpoint_url: str = Field(..., max_length=2048)
    custom_headers: dict[str, str] | None = None

    @field_validator("endpoint_url")
    @classmethod
    def _https_only(cls, v: str) -> str:
        if not v.startswith("https://"):
            raise ValueError("endpoint_url must use HTTPS")
        return v


class WebhookUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    endpoint_url: str | None = Field(None, max_length=2048)
    custom_headers: dict[str, str] | None = None
    is_active: bool | None = None


class WebhookResponse(BaseModel):
    id: UUID
    org_id: UUID
    name: str
    event_type: EventType
    endpoint_url: str
    custom_headers_masked: dict[str, str]  # {name: '●●●●●'}
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_triggered_at: datetime | None = None


class WebhookTestRequest(BaseModel):
    pass  # Test uses a fixed canonical payload


class WebhookTestResponse(BaseModel):
    success: bool
    status_code: int | None = None
    response_body_excerpt: str | None = None
    error: str | None = None
    duration_ms: int


# ----------------------------------------------------------------------
# Webhook Deliveries
# ----------------------------------------------------------------------

class WebhookDeliveryResponse(BaseModel):
    id: UUID
    webhook_id: UUID
    event_type: EventType
    resource_id: UUID
    attempt_number: int
    status: DeliveryStatus
    status_code: int | None = None
    error_message: str | None = None
    created_at: datetime
    sent_at: datetime | None = None
    next_retry_at: datetime
    completed_at: datetime | None = None


class WebhookDeliveryListResponse(BaseModel):
    items: list[WebhookDeliveryResponse]
    total: int
    page: int
    page_size: int


# ----------------------------------------------------------------------
# Connectors
# ----------------------------------------------------------------------

class ConnectorCreate(BaseModel):
    connector_type: ConnectorType
    name: str = Field(..., min_length=1, max_length=255)
    config: dict = Field(default_factory=dict)
    secrets: dict[str, str] | None = None   # encrypted into config_enc on save
    webhook_id: UUID | None = None


class ConnectorUpdate(BaseModel):
    name: str | None = None
    config: dict | None = None
    secrets: dict[str, str] | None = None
    webhook_id: UUID | None = None
    is_active: bool | None = None


class ConnectorResponse(BaseModel):
    id: UUID
    org_id: UUID
    connector_type: ConnectorType
    name: str
    config: dict   # plaintext non-secret config
    secrets_masked: dict[str, str]   # {key: '●●●●●'}
    webhook_id: UUID | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_sync_at: datetime | None = None
    error_message: str | None = None
