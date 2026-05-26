"""Models for reference data lists and entries."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class ReferenceList:
    id: UUID
    name_ar: str
    name_en: str
    description: str | None
    schema: list[dict]
    is_archived: bool
    org_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime


@dataclass
class ReferenceEntry:
    id: UUID
    list_id: UUID
    values: dict
    is_active: bool
    org_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime
