"""Pydantic schemas for feedback threading & replies (Feature 014)."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, field_validator


class ReplyCreateRequest(BaseModel):
    text_content: str

    @field_validator("text_content")
    @classmethod
    def validate_text_content(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("Reply text cannot be empty")
        if len(v) > 2000:
            raise ValueError("Reply text cannot exceed 2000 characters")
        return v


class ReplyResponse(BaseModel):
    id: UUID
    author_role: Literal["admin", "user"]
    author_name: str
    text_content: str
    created_at: datetime


class ThreadResponse(BaseModel):
    replies: list[ReplyResponse]
    has_earlier: bool


class MyFeedbackItem(BaseModel):
    id: UUID
    page_url: str
    text_content: str
    status: str
    submitted_at: datetime
    reply_count: int
    has_unread_admin_reply: bool


class MyFeedbackResponse(BaseModel):
    results: list[MyFeedbackItem]
    total: int
    page: int
    page_size: int


class NotificationResponse(BaseModel):
    id: UUID
    feedback_id: UUID
    reply_id: UUID
    created_at: datetime
    delivered_at: datetime | None = None
    read_at: datetime | None = None


class NotificationsResponse(BaseModel):
    notifications: list[NotificationResponse]
    unread_count: int
