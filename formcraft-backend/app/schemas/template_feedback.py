from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TemplateFeedbackSubmitRequest(BaseModel):
    template_id: UUID
    page_number: int | None = None
    element_key: str | None = None
    category: str
    comment: str
    screenshot_path: str | None = None


class TemplateFeedbackUpdateRequest(BaseModel):
    status: str


class TemplateFeedbackResponse(BaseModel):
    id: UUID
    template_id: UUID
    page_number: int | None = None
    element_key: str | None = None
    category: str
    comment: str
    screenshot_path: str | None = None
    status: str
    created_by: UUID
    created_by_name: str | None = None
    resolved_by: UUID | None = None
    resolved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class TemplateFeedbackListResponse(BaseModel):
    items: list[TemplateFeedbackResponse]
    total: int


class TemplateFeedbackAdminOverviewItem(BaseModel):
    template_id: UUID
    template_name: str
    total_feedback: int
    new_count: int
    acknowledged_count: int
    resolved_count: int


class TemplateFeedbackAdminOverviewResponse(BaseModel):
    items: list[TemplateFeedbackAdminOverviewItem]