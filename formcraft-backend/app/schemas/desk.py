from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TemplateCardResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    category: str | None = None
    status: str
    version: int
    lineage_id: UUID | None = None
    is_deprecated: bool = False
    language: str | None = None
    country: str | None = None
    updated_at: datetime
    is_pinned: bool = False


class TemplatesPageResponse(BaseModel):
    items: list[TemplateCardResponse]
    total: int
    page: int
    limit: int


class RecentTemplateResponse(BaseModel):
    template_id: UUID
    template_name: str
    category: str | None = None
    version: int
    last_used_at: datetime


class PinnedTemplateResponse(BaseModel):
    template_id: UUID
    template_name: str
    category: str | None = None
    version: int
    is_published: bool = True
    pinned_at: datetime


class NotificationResponse(BaseModel):
    id: str
    template_id: UUID
    template_name: str
    old_version: int
    new_version: int
    updated_at: datetime


class DashboardResponse(BaseModel):
    templates: TemplatesPageResponse
    recent: list[RecentTemplateResponse]
    pinned: list[PinnedTemplateResponse]
    drafts: list = []
    notifications: list[NotificationResponse]


class PinRequest(BaseModel):
    template_id: UUID