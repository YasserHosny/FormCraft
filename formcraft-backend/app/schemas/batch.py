from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class BatchJobStatus:
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BatchDataSourceType:
    CSV = "csv"
    XLSX = "xlsx"
    CLIPBOARD = "clipboard"


class BatchDownloadFormat:
    ZIP = "zip"
    MERGED_PDF = "merged_pdf"
    PRINTER_QUEUE = "printer_queue"


class DuplicateStrategy:
    WARN = "warn"
    SKIP = "skip"
    INCLUDE = "include"


class BatchApiAuthType:
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"


class BatchErrorType:
    VALIDATION = "validation"
    GENERATION = "generation"
    MAPPING = "mapping"
    DUPLICATE = "duplicate"
    TEMPLATE_CHANGED = "template_changed"


class BatchJob(BaseModel):
    id: UUID
    org_id: UUID
    template_id: UUID
    template_version: int
    created_by: UUID
    name: str
    status: str = BatchJobStatus.QUEUED
    data_source_type: str
    data_source_id: UUID | None = None
    column_mapping: dict = {}
    row_count: int = 0
    success_count: int = 0
    fail_count: int = 0
    progress: int = 0
    duplicate_strategy: str = DuplicateStrategy.WARN
    duplicate_count: int = 0
    download_format: str = BatchDownloadFormat.ZIP
    printer_profile_id: UUID | None = None
    scheduled_job_id: UUID | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    cancelled_by: UUID | None = None
    error_summary: str | None = None
    created_at: datetime
    updated_at: datetime


class BatchDataSource(BaseModel):
    id: UUID
    org_id: UUID
    file_name: str
    storage_path: str
    mime_type: str
    file_size_bytes: int
    encoding: str | None = None
    column_headers: list[str] = []
    checksum: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class BatchSchedule(BaseModel):
    id: UUID
    org_id: UUID
    template_id: UUID
    created_by: UUID
    name: str
    enabled: bool = False
    data_source_type: str = "api"
    api_endpoint: str
    api_auth_type: str
    api_auth_credential: str
    api_headers: dict = {}
    cron_expression: str
    notification_recipients: list[dict] = []
    column_mapping: dict = {}
    download_format: str = BatchDownloadFormat.ZIP
    printer_profile_id: UUID | None = None
    max_rows_per_run: int = 1000
    last_run_at: datetime | None = None
    last_run_status: str | None = None
    last_run_job_id: UUID | None = None
    next_run_at: datetime | None = None
    failure_count: int = 0
    created_at: datetime
    updated_at: datetime


class BatchError(BaseModel):
    id: UUID
    org_id: UUID
    batch_job_id: UUID
    row_number: int
    field_key: str | None = None
    error_type: str
    error_message: str
    created_at: datetime


class BatchJobCreateRequest(BaseModel):
    name: str
    template_id: UUID
    data_source_type: str
    column_mapping: dict = {}
    duplicate_strategy: str = DuplicateStrategy.WARN
    download_format: str = BatchDownloadFormat.ZIP
    printer_profile_id: UUID | None = None


class BatchJobResponse(BaseModel):
    id: UUID
    name: str
    status: str
    template_id: UUID
    template_version: int
    data_source_type: str
    column_mapping: dict
    row_count: int
    success_count: int
    fail_count: int
    progress: int
    duplicate_strategy: str
    duplicate_count: int
    download_format: str
    printer_profile_id: UUID | None = None
    scheduled_job_id: UUID | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    error_summary: str | None = None
    created_at: datetime
    updated_at: datetime


class BatchJobSummary(BaseModel):
    id: UUID
    name: str
    status: str
    template_name: str = ""
    row_count: int
    success_count: int
    fail_count: int
    progress: int
    created_at: datetime
    updated_at: datetime


class BatchValidationRequest(BaseModel):
    column_mapping: dict
    duplicate_strategy: str = DuplicateStrategy.WARN


class ValidationRowResult(BaseModel):
    row_number: int
    status: Literal["valid", "invalid", "duplicate"]
    field_errors: dict[str, str] = {}


class BatchValidationResult(BaseModel):
    total_rows: int
    valid_rows: int
    invalid_rows: int
    duplicate_rows: int
    rows: list[ValidationRowResult]


class BatchScheduleCreateRequest(BaseModel):
    name: str
    template_id: UUID
    enabled: bool = False
    api_endpoint: str
    api_auth_type: str
    api_auth_credential: str
    api_headers: dict = {}
    cron_expression: str
    notification_recipients: list[dict] = []
    column_mapping: dict = {}
    download_format: str = BatchDownloadFormat.ZIP
    printer_profile_id: UUID | None = None
    max_rows_per_run: int = 1000


class BatchScheduleUpdateRequest(BaseModel):
    name: str | None = None
    template_id: UUID | None = None
    enabled: bool | None = None
    api_endpoint: str | None = None
    api_auth_type: str | None = None
    api_auth_credential: str | None = None
    api_headers: dict | None = None
    cron_expression: str | None = None
    notification_recipients: list[dict] | None = None
    column_mapping: dict | None = None
    download_format: str | None = None
    printer_profile_id: UUID | None = None
    max_rows_per_run: int | None = None


class BatchScheduleResponse(BaseModel):
    id: UUID
    name: str
    enabled: bool
    template_name: str = ""
    template_id: UUID
    cron_expression: str
    next_run_at: datetime | None = None
    last_run_status: str | None = None
    last_run_at: datetime | None = None
    last_run_job_id: UUID | None = None
    failure_count: int
    created_at: datetime
    updated_at: datetime
