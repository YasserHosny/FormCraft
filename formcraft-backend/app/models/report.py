from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import (
    DeliveryStatus,
    ExportFormat,
    GenerationMethod,
    NoDataBehavior,
    ReportFrequency,
    ReportType,
    ScheduleStatus,
)


class ReportTemplate(BaseModel):
    id: UUID
    org_id: UUID
    name: str
    name_ar: str | None = None
    report_type: ReportType
    description: str | None = None
    config: dict = {}
    is_system: bool = False
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class ReportSchedule(BaseModel):
    id: UUID
    report_template_id: UUID
    org_id: UUID
    frequency: ReportFrequency
    schedule_time: time
    day_of_week: int | None = None
    day_of_month: int | None = None
    recipients: list[str] = []
    export_format: ExportFormat = ExportFormat.XLSX
    no_data_behavior: NoDataBehavior = NoDataBehavior.SEND_EMPTY
    is_active: bool = True
    last_run_at: datetime | None = None
    next_run_at: datetime | None = None
    last_status: ScheduleStatus = ScheduleStatus.PENDING
    last_error: str | None = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class ReportArchive(BaseModel):
    id: UUID
    org_id: UUID
    report_template_id: UUID | None = None
    schedule_id: UUID | None = None
    report_type: ReportType
    file_name: str
    file_path: str
    file_size_bytes: int
    export_format: ExportFormat
    filters_applied: dict = {}
    record_count: int
    generated_by: UUID | None = None
    generation_method: GenerationMethod
    delivery_status: DeliveryStatus = DeliveryStatus.GENERATED
    delivery_recipients: list[str] | None = None
    delivery_error: str | None = None
    expires_at: datetime
    created_at: datetime


class ReportFilter(BaseModel):
    template_id: UUID | None = None
    date_from: date | None = None
    date_to: date | None = None
    branch_id: UUID | None = None
    department_id: UUID | None = None
    operator_id: UUID | None = None
    status: str | None = None
    customer_query: str | None = None


class TransactionRegisterRow(BaseModel):
    id: UUID
    reference_number: str
    template_name: str
    template_name_ar: str | None = None
    operator_name: str
    customer_name: str | None = None
    created_at: datetime
    status: str
    key_fields: list[dict] = []


class ReconciliationSummary(BaseModel):
    total_submissions: int
    total_amount: float
    template_breakdown: list[dict] = []


class ReconciliationOperatorRow(BaseModel):
    operator_id: UUID
    name: str
    total_submissions: int
    total_amount: float
    by_template: list[dict] = []


class ReconciliationReport(BaseModel):
    date: date
    branch: dict
    summary: ReconciliationSummary
    operators: list[ReconciliationOperatorRow] = []


class PeriodGroupMetrics(BaseModel):
    count: int
    amount: float
    avg_amount: float


class PeriodGroupRow(BaseModel):
    id: UUID
    name: str
    name_ar: str | None = None
    current: PeriodGroupMetrics
    previous: PeriodGroupMetrics
    change: dict


class PeriodSummaryReport(BaseModel):
    period: str
    current: dict
    previous: dict
    groups: list[PeriodGroupRow] = []


class CustomReportDimension(BaseModel):
    source: str
    field: str | None = None
    field_key: str | None = None
    type_tag: str | None = None


class CustomReportFilter(BaseModel):
    field: str
    operator: str
    value: str | int | float | bool | UUID


class CustomReportAggregation(BaseModel):
    function: str
    field: str
    alias: str


class CustomReportConfig(BaseModel):
    template_ids: list[UUID]
    dimensions: list[CustomReportDimension] = []
    filters: list[CustomReportFilter] = []
    aggregations: list[CustomReportAggregation] = []
    group_by: list[str] = []
    chart_type: str | None = None
    chart_config: dict = {}


class ExportJobStatus(BaseModel):
    job_id: UUID
    status: str
    progress_pct: int = 0
    download_url: str | None = None
    error: str | None = None


class AsyncExportRequest(BaseModel):
    filters: ReportFilter
    format: ExportFormat


class ArchiveListItem(BaseModel):
    id: UUID
    report_type: ReportType
    file_name: str
    export_format: ExportFormat
    record_count: int
    file_size_bytes: int
    generation_method: GenerationMethod
    generated_by: str | None = None
    created_at: datetime
    download_url: str | None = None
