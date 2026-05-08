from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator

from app.schemas.label import LabelResponse


class FeedbackUploadResponse(BaseModel):
    storage_path: str


class FeedbackImageSubmitItem(BaseModel):
    id: UUID
    storage_path: str
    display_order: int


class FeedbackImageResponse(BaseModel):
    id: UUID
    storage_url: str
    display_order: int


class FeedbackSubmitRequest(BaseModel):
    page_url: HttpUrl
    text_content: str = Field(..., min_length=1, max_length=2000)
    image_paths: list[str] | None = None
    audio_url: str | None = None
    video_url: str | None = None

    @field_validator("image_paths")
    @classmethod
    def validate_image_count(cls, v):
        if v is not None and len(v) > 5:
            raise ValueError("Maximum 5 images allowed per submission")
        return v

    @model_validator(mode="after")
    def check_audio_video_mutual_exclusion(self):
        if self.audio_url is not None and self.video_url is not None:
            raise ValueError(
                "Audio and video cannot both be attached to the same submission"
            )
        return self


class FeedbackSubmitResponse(BaseModel):
    id: UUID
    submitted_at: datetime
    status: str
    images: list[FeedbackImageSubmitItem] = []
    audio_url: str | None = None
    video_url: str | None = None


class FeedbackAdminItem(BaseModel):
    id: UUID
    user_id: UUID
    page_url: str
    text_content: str
    images: list[FeedbackImageResponse] = []
    audio_url: str | None = None
    audio_signed_url: str | None = None
    video_url: str | None = None
    video_signed_url: str | None = None
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
    storage_path: str
