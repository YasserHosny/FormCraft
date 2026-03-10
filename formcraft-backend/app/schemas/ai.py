from typing import Literal

from pydantic import BaseModel, Field

from app.models.enums import Country, Direction, ElementType, Language


class SuggestionRequest(BaseModel):
    label: str
    language: Language
    country: Country
    context: str = ""


class ValidationSchema(BaseModel):
    required: bool = False
    regex: str | None = None
    min_length: int | None = None
    max_length: int | None = None
    numeric_only: bool = False


class FormattingSchema(BaseModel):
    date_format: str | None = None
    currency_code: str | None = None
    decimal_places: int | None = None
    uppercase: bool = False


class SuggestionResponse(BaseModel):
    control_type: ElementType
    confidence: float = Field(ge=0.0, le=1.0)
    validation: ValidationSchema = ValidationSchema()
    formatting: FormattingSchema = FormattingSchema()
    direction: Direction = Direction.AUTO
    source: Literal["deterministic", "llm", "fallback"] = "llm"
