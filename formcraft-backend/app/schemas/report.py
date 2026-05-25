from datetime import date, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import (
    DeliveryStatus,
    ExportFormat,
    GenerationMethod,
    NoDataBehavior,
    ReportFrequency,
    ReportType,
    ScheduleStatus,
)


# Report Template Schemas
class ReportTemplateBase(BaseModel):
    name: str
    name_ar: str | None = None
    report_type: ReportType
    description: str | None = None
    config: dict = {}


class ReportTemplateCreate(ReportTemplateBase):
    pass


class ReportTemplateUpdate(BaseModel):
    name: str | None = None
    name_ar: str | None = None
    description: str | None = None
    config: dict | None = None


class ReportTemplateResponse(ReportTemplateBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    org_id: UUID
    is_system: bool
    created_by: UUID
    created_at: str
    updated_at: str


# Report Schedule Schemas
class ReportScheduleBase(BaseModel):
    report_template_id: UUID
    frequency: ReportFrequency
    schedule_time: time
    day_of_week: int | None = None
    day_of_month: int | None = None
    recipients: list[str] = []
    export_format: ExportFormat = ExportFormat.XLSX
    no_data_behavior: NoDataBehavior = NoDataBehavior.SEND_EMPTY
    is_active: bool = True


class ReportScheduleCreate(ReportScheduleBase):
    pass


class ReportScheduleUpdate(BaseModel):
    frequency: ReportFrequency | None = None
    schedule_time: time | None = None
    day_of_week: int | None = None
    day_of_month: int | None = None
    recipients: list[str] | None = None
    export_format: ExportFormat | None = None
    no_data_behavior: NoDataBehavior | None = None
    is_active: bool | None = None


class ReportScheduleResponse(ReportScheduleBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    org_id: UUID
    last_run_at: str | None = None
    next_run_at: str | None = None
    last_status: ScheduleStatus
    last_error: str | None = None
    created_by: UUID
    created_at: str
    updated_at: str


class ReportScheduleHistoryItem(BaseModel):
    archive_id: UUID
    status: str
    record_count: int
    file_name: str
    delivery_status: DeliveryStatus
    delivery_recipients: list[str] | None = None
    delivery_error: str | None = None
    created_at: str


# Report Archive Schemas
class ReportArchiveResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    report_type: ReportType
    file_name: str
    export_format: ExportFormat
    record_count: int
    file_size_bytes: int
    generation_method: GenerationMethod
    generated_by: str | None = None
    created_at: str
    download_url: str | None = None


# Filter / Export Schemas
class TransactionFilter(BaseModel):
    template_id: UUID | None = None
    date_from: date
    date_to: date
    branch_id: UUID | None = None
    department_id: UUID | None = None
    operator_id: UUID | None = None
    status: str | None = None
    customer_query: str | None = None


class TransactionExportRequest(BaseModel):
    filters: TransactionFilter
    format: ExportFormat


class ReconciliationFilter(BaseModel):
    date: date
    branch_id: UUID | None = None


class PeriodSummaryFilter(BaseModel):
    period: str
    group_by: str
    date_from: date | None = None
    compare: bool = True


class FinancialReportFilter(BaseModel):
    date_from: date
    date_to: date
    template_id: UUID | None = None


class BeneficiaryFilter(FinancialReportFilter):
    beneficiary_query: str | None = None


class VoidReprintFilter(FinancialReportFilter):
    branch_id: UUID | None = None
    min_reprint_count: int = 1


class SignatoryUsageFilter(FinancialReportFilter):
    signatory_id: UUID | None = None


# Custom Report Schemas
class CustomReportDimension(BaseModel):
    source: str
    field: str | None = None
    field_key: str | None = None
    type_tag: str | None = None


class CustomReportFilterItem(BaseModel):
    field: str
    operator: str
    value: str | int | float | bool | UUID


class CustomReportAggregation(BaseModel):
    function: str
    field: str
    alias: str


class CustomReportPreviewRequest(BaseModel):
    template_ids: list[UUID]
    dimensions: list[CustomReportDimension] = []
    filters: list[CustomReportFilterItem] = []
    aggregations: list[CustomReportAggregation] = []
    group_by: list[str] = []
    date_from: date | None = None
    date_to: date | None = None


class CustomReportSaveRequest(BaseModel):
    name: str
    name_ar: str | None = None
    description: str | None = None
    config: dict


class CustomReportPreviewResponse(BaseModel):
    columns: list[dict]
    rows: list[dict]
    total_matching: int
    preview_limited: bool


# Async Job Schemas
class ExportJobResponse(BaseModel):
    job_id: UUID
    status: str
    progress_pct: int = 0
    download_url: str | None = None
    error: str | None = None


class ExportSuccessResponse(BaseModel):
    download_url: str
    file_name: str
    record_count: int
    archive_id: UUID


class ExportAsyncResponse(BaseModel):
    job_id: UUID
    status: str
    estimated_seconds: int


class ExportLimitExceededResponse(BaseModel):
    error: str = "export_limit_exceeded"
    message: str
    record_count: int
    max_allowed: int


# Pagination
class PaginatedResponse(BaseModel):
    data: list
    pagination: dict
