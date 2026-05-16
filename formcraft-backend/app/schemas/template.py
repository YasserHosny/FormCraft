from uuid import UUID

from pydantic import BaseModel

from app.models.enums import Country, Language, TemplateStatus


class CreateTemplateRequest(BaseModel):
    name: str
    description: str = ""
    category: str = "general"
    language: Language = Language.AR
    country: Country = Country.EG


class UpdateTemplateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    language: Language | None = None
    country: Country | None = None
    updated_at: str


class TransitionRequest(BaseModel):
    status: str
    comment: str | None = None


class CloneRequest(BaseModel):
    name: str | None = None


class TemplateReviewResponse(BaseModel):
    id: UUID
    template_id: UUID
    reviewer_id: UUID
    reviewer_name: str | None = None
    action: str
    comment: str | None = None
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
    created_at: str
    updated_at: str


class TemplateResponse(TemplateListResponse):
    created_by: UUID
    pages: list = []