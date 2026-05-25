from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


CredentialStatus = Literal["active", "revoked", "expired"]
CredentialScope = Literal[
    "submissions:read",
    "templates:read",
    "templates:write",
    "webhooks:write",
]
WebhookEventType = Literal[
    "form_submitted",
    "form_printed",
    "template_published",
    "batch_completed",
]
WebhookStatus = Literal["active", "paused", "disabled"]
WebhookDeliveryStatus = Literal["queued", "delivered", "failed"]


class IntegrationCredentialCreate(BaseModel):
    name: str
    scopes: list[CredentialScope] = Field(min_length=1)
    expires_at: datetime | None = None


class IntegrationCredential(BaseModel):
    id: UUID
    name: str
    key_prefix: str
    scopes: list[CredentialScope]
    status: CredentialStatus
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    created_at: datetime


class IntegrationCredentialCreated(IntegrationCredential):
    secret: str


class IntegrationCredentialListResponse(BaseModel):
    items: list[IntegrationCredential]


class WebhookSubscriptionCreate(BaseModel):
    name: str
    event_type: WebhookEventType
    target_url: HttpUrl
    signing_secret: str = Field(min_length=16)


class WebhookSubscriptionUpdate(BaseModel):
    name: str | None = None
    target_url: HttpUrl | None = None
    signing_secret: str | None = Field(default=None, min_length=16)
    status: WebhookStatus | None = None


class WebhookSubscription(BaseModel):
    id: UUID
    name: str
    event_type: WebhookEventType
    target_url: HttpUrl
    signing_secret_prefix: str | None = None
    status: WebhookStatus
    created_at: datetime


class WebhookSubscriptionListResponse(BaseModel):
    items: list[WebhookSubscription]


class WebhookDelivery(BaseModel):
    id: UUID
    subscription_id: UUID
    event_type: WebhookEventType
    event_id: UUID
    payload_preview: dict
    signature_header: str
    status: WebhookDeliveryStatus
    attempt_count: int
    next_retry_at: datetime | None = None
    last_response_code: int | None = None
    last_response_body_preview: str | None = None
    created_at: datetime


class WebhookDeliveryListResponse(BaseModel):
    items: list[WebhookDelivery]
    total: int
    page: int
    page_size: int
