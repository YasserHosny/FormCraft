"""Pydantic schemas for F040 Enhanced Analytics Dashboard."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PeriodFilter(BaseModel):
    from_date: date | None = None
    to_date: date | None = None


class TopErrorItem(BaseModel):
    message: str
    count: int


class FieldAnalyticsItem(BaseModel):
    field_key: str
    error_rate: float = Field(ge=0.0, le=1.0)
    top_errors: list[TopErrorItem]
    empty_rate: float = Field(ge=0.0, le=1.0)
    avg_fill_time_ms: int | None = None
    warning: bool = False


class FieldAnalyticsResponse(BaseModel):
    template_id: UUID
    template_name: str
    template_version: int
    period: dict[str, str | None]
    fields: list[FieldAnalyticsItem]
    computed_at: datetime


class OperatorAnalyticsItem(BaseModel):
    operator_id: UUID
    operator_name: str
    forms_filled: int = Field(ge=0)
    avg_fill_time_ms: int | None = None
    error_rate: float = Field(ge=0.0, le=1.0)
    coaching_flag: bool = False


class OperatorAnalyticsResponse(BaseModel):
    period_type: str
    period: dict[str, str | None]
    operators: list[OperatorAnalyticsItem]
    org_average_error_rate: float
    computed_at: datetime


class HeatmapItem(BaseModel):
    hour: int = Field(ge=0, le=23)
    day_of_week: int = Field(ge=0, le=6)
    submission_count: int = Field(ge=0)


class BusiestHoursResponse(BaseModel):
    heatmap: list[HeatmapItem]
    peak_hour: int
    peak_day: int
    computed_at: datetime


class ComplianceScorecardResponse(BaseModel):
    org_id: UUID
    validator_coverage_pct: float
    bilingual_label_pct: float
    quality_score_avg: float
    templates_needing_attention: int
    customer_data_access_spike: bool
    computed_at: datetime
    cache_expires_at: datetime


class NonCompliantTemplateItem(BaseModel):
    template_id: UUID
    template_name: str
    quality_score: float
    missing_validators: list[str]
    missing_bilingual_labels: list[str]


class TemplatesNeedingAttentionResponse(BaseModel):
    templates: list[NonCompliantTemplateItem]


class FunnelData(BaseModel):
    started_count: int
    draft_count: int
    submitted_count: int
    printed_count: int
    conversion_rates: dict[str, float]


class DepartmentUsageItem(BaseModel):
    department_id: UUID
    department_name: str
    submitted_count: int


class TemplateUsageResponse(BaseModel):
    template_id: UUID | None = None
    template_name: str | None = None
    funnel: FunnelData
    avg_fill_time_ms: int | None = None
    by_department: list[DepartmentUsageItem] | None = None
    computed_at: datetime


class VersionAdoptionItem(BaseModel):
    version: int
    day: date
    count: int
    pct_of_total: float


class VersionAdoptionResponse(BaseModel):
    template_id: UUID
    template_name: str
    adoption: list[VersionAdoptionItem]


class ExportRequest(BaseModel):
    report_type: str = Field(..., pattern="^(field_analytics|operator_analytics|compliance_scorecard|template_usage|busiest_hours)$")
    template_id: UUID | None = None
    from_date: date | None = None
    to_date: date | None = None
    format: str = Field(..., pattern="^(csv|png|pdf)$")


class ExportResponse(BaseModel):
    download_url: str
    expires_at: datetime
