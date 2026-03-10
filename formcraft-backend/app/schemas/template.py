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
    updated_at: str  # for optimistic concurrency


class TemplateListResponse(BaseModel):
    id: UUID
    name: str
    description: str
    category: str
    status: TemplateStatus
    version: int
    language: Language
    country: Country
    created_at: str
    updated_at: str


class TemplateResponse(TemplateListResponse):
    created_by: UUID
    pages: list = []
