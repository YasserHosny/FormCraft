from uuid import UUID

from pydantic import BaseModel

from app.models.enums import Direction, ElementType


class ConditionItem(BaseModel):
    field: str
    operator: str
    value: str | int | float | bool | None = None


class ConditionObject(BaseModel):
    conditions: list[ConditionItem]
    logic: str = "AND"


class PlaceholderText(BaseModel):
    ar: str = ""
    en: str = ""


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
    visible_when: ConditionObject | None = None
    required_when: ConditionObject | None = None
    computed_value: str | None = None
    default_value: str | None = None
    placeholder_text: PlaceholderText | None = None


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
    visible_when: ConditionObject | None = None
    required_when: ConditionObject | None = None
    computed_value: str | None = None
    default_value: str | None = None
    placeholder_text: PlaceholderText | None = None


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
    visible_when: dict | None = None
    required_when: dict | None = None
    computed_value: str | None = None
    default_value: str | None = None
    placeholder_text: dict | None = None
