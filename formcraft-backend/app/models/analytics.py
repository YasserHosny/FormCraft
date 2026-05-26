"""Pydantic models for F040 analytics entities."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class FieldAnalytics(BaseModel):
    id: UUID
    org_id: UUID
    template_id: UUID
    template_version: int
    field_key: str
    error_count: int = 0
    error_types: dict = {}
    empty_count: int = 0
    total_submissions: int = 0
    avg_fill_time_ms: int | None = None
    computed_at: datetime
    period_start: datetime
    period_end: datetime
    retention_bucket: str = "hot"


class OperatorAnalytics(BaseModel):
    id: UUID
    org_id: UUID
    operator_id: UUID
    period_type: str
    period_start: date
    forms_filled: int = 0
    avg_fill_time_ms: int | None = None
    error_rate: float = 0.0
    busiest_hours: dict = {}
    computed_at: datetime


class ComplianceScorecardCache(BaseModel):
    id: UUID
    org_id: UUID
    validator_coverage_pct: float = 0.0
    bilingual_label_pct: float = 0.0
    quality_score_avg: float = 0.0
    templates_needing_attention: int = 0
    customer_data_access_spike: bool = False
    computed_at: datetime
    cache_expires_at: datetime


class AnalyticsAggregationLog(BaseModel):
    id: UUID
    view_name: str
    refresh_type: str
    started_at: datetime
    completed_at: datetime | None = None
    duration_ms: int | None = None
    row_count: int | None = None
    status: str
    error_message: str | None = None
