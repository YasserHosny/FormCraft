from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

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
    validation: dict = Field(default_factory=dict)
    formatting: dict = Field(default_factory=dict)
    properties: dict | None = None
    required: bool = False
    direction: Direction = Direction.AUTO
    visible_when: ConditionObject | None = None
    required_when: ConditionObject | None = None
    computed_value: str | None = None
    default_value: str | None = None
    placeholder_text: PlaceholderText | None = None
    custom_validators_ids: list[UUID] = []


class UpdateElementRequest(BaseModel):
    label_ar: str | None = None
    label_en: str | None = None
    x_mm: float | None = None
    y_mm: float | None = None
    width_mm: float | None = None
    height_mm: float | None = None
    validation: dict | None = None
    formatting: dict | None = None
    properties: dict | None = None
    required: bool | None = None
    direction: Direction | None = None
    visible_when: ConditionObject | None = None
    required_when: ConditionObject | None = None
    computed_value: str | None = None
    default_value: str | None = None
    placeholder_text: PlaceholderText | None = None
    custom_validators_ids: list[UUID] | None = None


class ReorderElementsRequest(BaseModel):
    element_ids: list[UUID]


class FontSettings(BaseModel):
    family: str | None = None
    size_pt: float | None = Field(default=None, ge=1, le=128)
    weight: Literal["normal", "bold"] | None = None
    style: Literal["normal", "italic"] | None = None
    color: str | None = None
    min_size_pt: float | None = Field(default=6.0, ge=1, le=128)


class LineLayout(BaseModel):
    max_lines: int | None = Field(default=None, ge=1, le=100)
    first_line_left_inset_mm: float | None = Field(default=None, ge=0)
    last_line_right_inset_mm: float | None = Field(default=None, ge=0)


class ElementFormatting(BaseModel):
    font: FontSettings | None = None
    line_layout: LineLayout | None = None
    overflow: Literal["clip", "shrink-to-fit", "visible"] | None = None


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
    custom_validators_ids: list[UUID] = []
