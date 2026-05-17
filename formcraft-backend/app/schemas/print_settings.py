"""Pydantic schemas for overlay print mode."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PrintSettingsUpdate(BaseModel):
    print_mode: str = Field(pattern=r"^(full|overlay|both)$")


class PrintSettingsResponse(BaseModel):
    template_id: UUID
    print_mode: str
    updated_at: datetime


class PrinterProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    x_offset_mm: float = Field(default=0.0, ge=-50.0, le=50.0)
    y_offset_mm: float = Field(default=0.0, ge=-50.0, le=50.0)
    is_default: bool = False


class PrinterProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    x_offset_mm: float | None = Field(default=None, ge=-50.0, le=50.0)
    y_offset_mm: float | None = Field(default=None, ge=-50.0, le=50.0)


class PrinterProfileResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    x_offset_mm: float
    y_offset_mm: float
    is_default: bool
    is_active: bool
    created_at: datetime


class PdfGenerationRequest(BaseModel):
    printer_profile_id: UUID | None = None
    print_mode_override: str | None = Field(default=None, pattern=r"^(full|overlay|both)$")
