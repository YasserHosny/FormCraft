"""Models for template print settings and printer profiles."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class TemplatePrintSettings:
    id: UUID
    template_id: UUID
    print_mode: str
    org_id: UUID
    created_at: datetime
    updated_at: datetime


@dataclass
class PrinterProfile:
    id: UUID
    name: str
    description: str | None
    x_offset_mm: float
    y_offset_mm: float
    is_default: bool
    is_active: bool
    org_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime
