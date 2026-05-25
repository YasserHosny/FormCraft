from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ReviewCommentCreate(BaseModel):
    template_version: int
    element_id: UUID | None = None
    element_key: str | None = None
    page_id: UUID | None = None
    x_mm: float | None = None
    y_mm: float | None = None
    comment_text: str


class ReviewCommentResponse(BaseModel):
    id: UUID
    template_id: UUID
    template_version: int
    reviewer_id: UUID
    reviewer_name: str | None = None
    element_id: UUID | None = None
    element_key: str | None = None
    x_mm: float | None = None
    y_mm: float | None = None
    comment_text: str
    status: str
    designer_reply: str | None = None
    resolved_by: UUID | None = None
    resolved_at: datetime | None = None
    created_at: datetime


class ResolveCommentRequest(BaseModel):
    designer_reply: str | None = None


class BulkActionType(BaseModel):
    action: str  # "archive", "reassign", "change_category"
    template_ids: list[UUID]


class BulkArchiveRequest(BulkActionType):
    action: str = "archive"
    confirm_published: bool = False


class BulkReassignRequest(BulkActionType):
    action: str = "reassign"
    new_designer_id: UUID


class BulkCategoryRequest(BulkActionType):
    action: str = "change_category"
    new_category: str


class BulkActionRequest(BaseModel):
    action: str
    template_ids: list[UUID]
    dry_run: bool = True
    # Action-specific fields
    confirm_published: bool = False
    new_designer_id: UUID | None = None
    new_category: str | None = None


class BulkActionPreviewItem(BaseModel):
    template_id: UUID
    template_name: str
    current_status: str
    warning: str | None = None


class BulkActionResponse(BaseModel):
    action: str
    dry_run: bool
    affected_count: int
    warnings: list[str]
    items: list[BulkActionPreviewItem]


class GovernanceTemplateItem(BaseModel):
    id: UUID
    name: str
    category: str
    status: str
    version: int
    designer_id: UUID
    designer_name: str | None = None
    department_id: UUID | None = None
    department_name: str | None = None
    quality_score: int | None = None
    updated_at: datetime
    created_at: datetime


class GovernanceTemplateListResponse(BaseModel):
    items: list[GovernanceTemplateItem]
    total: int
    page: int
    page_size: int


class ComplianceMetric(BaseModel):
    template_id: UUID
    template_name: str
    validator_coverage_pct: float
    bilingual_label_pct: float
    help_text_coverage_pct: float
    tab_order_defined: bool
    quality_score: int
    is_stale: bool
    last_modified: datetime


class ComplianceDashboardResponse(BaseModel):
    avg_quality_score: float
    total_templates: int
    validator_coverage_pct: float
    bilingual_coverage_pct: float
    stale_count: int
    templates: list[ComplianceMetric]


class RegulatoryAlert(BaseModel):
    event_id: UUID
    validator_key: str
    change_summary: str
    effective_date: str
    affected_template_count: int
