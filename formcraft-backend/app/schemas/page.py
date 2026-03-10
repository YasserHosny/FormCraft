from uuid import UUID

from pydantic import BaseModel


class CreatePageRequest(BaseModel):
    width_mm: float = 210
    height_mm: float = 297


class UpdatePageRequest(BaseModel):
    width_mm: float | None = None
    height_mm: float | None = None
    background_asset: str | None = None


class ReorderPagesRequest(BaseModel):
    page_ids: list[UUID]


class PageResponse(BaseModel):
    id: UUID
    template_id: UUID
    width_mm: float
    height_mm: float
    background_asset: str | None
    sort_order: int
    elements: list = []
