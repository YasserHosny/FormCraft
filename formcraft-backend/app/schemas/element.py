from uuid import UUID

from pydantic import BaseModel

from app.models.enums import Direction, ElementType


class CreateElementRequest(BaseModel):
    type: ElementType
    label_ar: str = ""
    label_en: str = ""
    x_mm: float = 0
    y_mm: float = 0
    width_mm: float = 50
    height_mm: float = 10
    required: bool = False
    direction: Direction = Direction.AUTO


class UpdateElementRequest(BaseModel):
    label_ar: str | None = None
    label_en: str | None = None
    x_mm: float | None = None
    y_mm: float | None = None
    width_mm: float | None = None
    height_mm: float | None = None
    validation: dict | None = None
    formatting: dict | None = None
    required: bool | None = None
    direction: Direction | None = None


class ReorderElementsRequest(BaseModel):
    element_ids: list[UUID]


class ElementResponse(BaseModel):
    id: UUID
    page_id: UUID
    type: ElementType
    key: str
    label_ar: str
    label_en: str
    x_mm: float
    y_mm: float
    width_mm: float
    height_mm: float
    validation: dict
    formatting: dict
    required: bool
    direction: Direction
    sort_order: int
