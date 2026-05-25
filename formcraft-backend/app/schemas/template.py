from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import Country, Language, TemplateStatus


class Margins(BaseModel):
    top: float = Field(10.0, ge=0, le=50)
    bottom: float = Field(10.0, ge=0, le=50)
    left: float = Field(10.0, ge=0, le=50)
    right: float = Field(10.0, ge=0, le=50)


class PageSetup(BaseModel):
    page_size: str = "A4"
    custom_width_mm: float | None = Field(None, ge=50, le=1000)
    custom_height_mm: float | None = Field(None, ge=50, le=1000)
    orientation: str = "portrait"
    margins: Margins = Margins()


class CreateTemplateRequest(BaseModel):
    name: str = Field(..., max_length=100)
    description: str = Field("", max_length=500)
    category: str = Field("general", max_length=100)
    language: Language = Language.AR
    country: Country = Country.EG
    currency: str = Field("EGP", max_length=10)
    tags: list[str] = Field(default_factory=list, max_length=10)
    page_setup: PageSetup | None = None


class UpdateTemplateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    language: Language | None = None
    country: Country | None = None
    updated_at: str


class ElementComment(BaseModel):
    element_key: str
    comment: str


class TransitionRequest(BaseModel):
    status: str
    comment: str | None = None
    element_comments: list[ElementComment] | None = None


class CloneRequest(BaseModel):
    name: str | None = None


class TemplateReviewResponse(BaseModel):
    id: UUID
    template_id: UUID
    reviewer_id: UUID
    reviewer_name: str | None = None
    action: str
    comment: str | None = None
    element_comments: list[ElementComment] | None = None
    created_at: str


class VersionHistoryItem(BaseModel):
    id: UUID
    version: int
    status: str
    created_by: UUID
    created_by_name: str | None = None
    created_at: str
    published_at: str | None = None
    element_count: int = 0
    page_count: int = 0


class VersionHistoryResponse(BaseModel):
    lineage_id: UUID
    versions: list[VersionHistoryItem]


class PropertyChange(BaseModel):
    property: str
    from_value: object = None
    to_value: object = None


class ElementChange(BaseModel):
    key: str
    changes: list[PropertyChange] = []


class PageChange(BaseModel):
    key: str | None = None
    type: str | None = None
    changes: list[PropertyChange] = []


class DiffSummary(BaseModel):
    elements_added: int = 0
    elements_removed: int = 0
    elements_modified: int = 0
    pages_added: int = 0
    pages_removed: int = 0


class DiffResponse(BaseModel):
    base_version: dict
    compare_version: dict
    summary: DiffSummary
    changes: dict


class ReviewListResponse(BaseModel):
    reviews: list[TemplateReviewResponse]


class TemplateListResponse(BaseModel):
    id: UUID
    name: str
    description: str
    category: str
    status: TemplateStatus
    version: int
    lineage_id: UUID | None = None
    parent_version_id: UUID | None = None
    language: Language
    country: Country
    currency: str
    tags: list[str]
    created_at: str
    updated_at: str


class TemplateResponse(TemplateListResponse):
    created_by: UUID
    pages: list = []


class ClonePreviewResponse(BaseModel):
    template_id: UUID
    name: str
    thumbnail_url: str | None = None
    page_count: int
    element_count: int
    reference_binding_warnings: list[dict] = []


class PackageImportPreviewResponse(BaseModel):
    name: str
    page_count: int
    element_count: int
    formcraft_version: str
    version_compatible: bool
    version_warning: str | None = None
    missing_bindings: list[dict] = []
    can_import: bool


class OrgCategoryResponse(BaseModel):
    id: UUID
    name: str
    is_system_default: bool


class OrgCategoryListResponse(BaseModel):
    items: list[OrgCategoryResponse]
