from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


ExportFormat = Literal["csv", "xlsx", "json"]
ExportScope = Literal["flattened", "structured"]
ExportDataset = Literal["submissions"]
ExportRequestStatus = Literal["previewed", "completed", "rejected", "failed"]
ExportScheduleFrequency = Literal["daily", "weekly"]
ExportScheduleStatus = Literal["active", "paused", "disabled"]
NoDataBehavior = Literal["send_empty_file", "send_notice"]
ExportDeliveryStatus = Literal["queued", "sent", "failed"]


class ExportFilters(BaseModel):
    template_id: UUID | None = None
    date_from: str | None = None
    date_to: str | None = None
    department_id: UUID | None = None
    branch_id: UUID | None = None
    operator_id: UUID | None = None
    status: str | None = None


class ExportPreviewRequest(BaseModel):
    filters: ExportFilters = Field(default_factory=ExportFilters)
    format: ExportFormat
    scope: ExportScope


class ExportDownloadRequest(ExportPreviewRequest):
    pass


class ExportPreviewResponse(BaseModel):
    matching_count: int
    estimated_file_size_bytes: int | None = None
    can_download: bool
    rejection_reason: str | None = None
    warnings: list[str] = Field(default_factory=list)


class ExportRequestRecord(BaseModel):
    id: UUID
    dataset: ExportDataset
    format: ExportFormat
    scope: ExportScope
    status: ExportRequestStatus
    matching_count: int
    rejection_reason: str | None = None
    created_at: datetime


class ExportHistoryResponse(BaseModel):
    items: list[ExportRequestRecord]
    total: int
    page: int
    page_size: int


class ExportScheduleCreate(BaseModel):
    name: str
    filters: ExportFilters = Field(default_factory=ExportFilters)
    format: ExportFormat
    scope: ExportScope
    frequency: ExportScheduleFrequency
    email_recipients: list[EmailStr] = Field(min_length=1)
    no_data_behavior: NoDataBehavior = "send_empty_file"
    next_run_at: datetime


class ExportScheduleUpdate(BaseModel):
    name: str | None = None
    filters: ExportFilters | None = None
    frequency: ExportScheduleFrequency | None = None
    email_recipients: list[EmailStr] | None = Field(default=None, min_length=1)
    status: ExportScheduleStatus | None = None
    next_run_at: datetime | None = None


class ExportSchedule(ExportScheduleCreate):
    id: UUID
    dataset: ExportDataset = "submissions"
    status: ExportScheduleStatus
    last_run_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ExportScheduleListResponse(BaseModel):
    items: list[ExportSchedule]


class ExportDelivery(BaseModel):
    id: UUID
    schedule_id: UUID
    status: ExportDeliveryStatus
    attempt_count: int
    failure_reason: str | None = None
    sent_at: datetime | None = None
    created_at: datetime
