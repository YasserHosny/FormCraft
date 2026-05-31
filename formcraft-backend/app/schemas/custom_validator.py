"""Schemas for Feature 048: Custom Locale Validators.

See: formcraft-specs/specs/048-custom-locale-validators/spec.md
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# Spec FR-1, FR-9 hard limits
MAX_PATTERN_LENGTH = 500
MAX_NAME_LENGTH = 255
MAX_VALIDATORS_PER_ORG = 500
MAX_VALIDATORS_PER_ELEMENT = 10


class CustomValidatorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=MAX_NAME_LENGTH)
    description: str | None = None
    regex_pattern: str = Field(..., min_length=1, max_length=MAX_PATTERN_LENGTH)
    error_message_ar: str = Field(..., min_length=1)
    error_message_en: str = Field(..., min_length=1)

    @field_validator("name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name must not be blank")
        return v


class CustomValidatorCreate(CustomValidatorBase):
    pass


class CustomValidatorUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=MAX_NAME_LENGTH)
    description: str | None = None
    regex_pattern: str | None = Field(None, min_length=1, max_length=MAX_PATTERN_LENGTH)
    error_message_ar: str | None = Field(None, min_length=1)
    error_message_en: str | None = Field(None, min_length=1)


class CustomValidatorResponse(CustomValidatorBase):
    id: UUID
    org_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    updated_by: UUID


class CustomValidatorListResponse(BaseModel):
    items: list[CustomValidatorResponse]
    total: int
    page: int
    page_size: int


# Designer-facing minimal payload (FR-4, FR-5) — no audit fields
class CustomValidatorDesignerView(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    regex_pattern: str
    error_message_ar: str
    error_message_en: str


# Template usage entry (FR-6)
class ValidatorTemplateUsage(BaseModel):
    template_id: UUID
    template_name: str
    template_status: str
    last_submission_at: datetime | None = None


class ValidatorTemplateUsageResponse(BaseModel):
    items: list[ValidatorTemplateUsage]
    total: int
    page: int
    page_size: int
