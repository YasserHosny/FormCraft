from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.label import LabelResponse


class FeedbackUploadResponse(BaseModel):
    url: str


class FeedbackSubmitRequest(BaseModel):
    page_url: HttpUrl
    text_content: str = Field(..., min_length=1, max_length=2000)
    image_url: str | None = None
    audio_url: str | None = None


class FeedbackSubmitResponse(BaseModel):
    id: UUID
    submitted_at: datetime
    status: str


class FeedbackAdminItem(BaseModel):
    id: UUID
    user_id: UUID
    page_url: str
    text_content: str
    image_url: str | None = None
    image_signed_url: str | None = None
    audio_url: str | None = None
    audio_signed_url: str | None = None
    submitted_at: datetime
    status: str
    submitter_display_name: str | None = None
    labels: list[LabelResponse] = []


class FeedbackAdminListResponse(BaseModel):
    data: list[FeedbackAdminItem]
    total: int
    page: int
    limit: int


class FeedbackStatusUpdateRequest(BaseModel):
    status: str = Field(..., pattern=r"^(new|reviewed|resolved)$")


class FeedbackDeleteUploadRequest(BaseModel):
    url: str
