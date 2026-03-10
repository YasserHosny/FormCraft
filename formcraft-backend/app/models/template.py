from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import (
    Country,
    Direction,
    ElementType,
    Language,
    TemplateStatus,
)


class Element(BaseModel):
    id: UUID
    page_id: UUID
    type: ElementType
    key: str
    label_ar: str = ""
    label_en: str = ""
    x_mm: float = 0
    y_mm: float = 0
    width_mm: float = 50
    height_mm: float = 10
    validation: dict = {}
    formatting: dict = {}
    required: bool = False
    direction: Direction = Direction.AUTO
    sort_order: int = 0
    created_at: datetime
    updated_at: datetime


class Page(BaseModel):
    id: UUID
    template_id: UUID
    width_mm: float = 210
    height_mm: float = 297
    background_asset: str | None = None
    sort_order: int = 0
    created_at: datetime
    updated_at: datetime
    elements: list[Element] = []


class Template(BaseModel):
    id: UUID
    name: str
    description: str = ""
    category: str = "general"
    status: TemplateStatus = TemplateStatus.DRAFT
    version: int = 1
    language: Language = Language.AR
    country: Country = Country.EG
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    pages: list[Page] = []
