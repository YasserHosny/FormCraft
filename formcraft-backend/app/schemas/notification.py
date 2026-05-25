from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: UUID
    type: str
    title_ar: str
    title_en: str
    body_ar: str | None = None
    body_en: str | None = None
    action_url: str | None = None
    source_id: UUID | None = None
    source_type: str | None = None
    is_announcement: bool = False
    read_at: datetime | None = None
    created_by: UUID | None = None
    created_at: datetime


class NotificationsListResponse(BaseModel):
    notifications: list[NotificationResponse]
    total: int
    page: int
    page_size: int


class UnreadCountResponse(BaseModel):
    unread_count: int


class MarkReadResponse(BaseModel):
    id: UUID
    read_at: datetime


class MarkAllReadResponse(BaseModel):
    marked_count: int


class NotificationPreferenceResponse(BaseModel):
    notification_type: str
    in_app_enabled: bool
    email_enabled: bool
    is_default: bool = False


class PreferencesListResponse(BaseModel):
    preferences: list[NotificationPreferenceResponse]


class PreferenceUpdateRequest(BaseModel):
    notification_type: str
    in_app_enabled: bool
    email_enabled: bool


class AnnouncementCreateRequest(BaseModel):
    title_ar: str
    title_en: str
    body_ar: str | None = None
    body_en: str | None = None
    target_audience: str  # 'all', 'role', 'department'
    target_role: str | None = None
    target_department_id: UUID | None = None


class AnnouncementResponse(BaseModel):
    announcement_id: UUID
    recipients_count: int
    created_at: datetime
