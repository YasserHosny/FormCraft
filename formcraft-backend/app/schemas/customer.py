from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import IdentifierType


class CustomerBase(BaseModel):
    name_ar: str
    name_en: str | None = None
    identifier_type: IdentifierType
    identifier: str
    contact_phone: str | None = None
    contact_email: str | None = None
    address: str | None = None
    custom_fields: dict | None = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name_ar: str | None = None
    name_en: str | None = None
    identifier_type: IdentifierType | None = None
    identifier: str | None = None
    contact_phone: str | None = None
    contact_email: str | None = None
    address: str | None = None
    custom_fields: dict | None = None
    is_active: bool | None = None


class CustomerResponse(BaseModel):
    id: UUID
    org_id: UUID
    name_ar: str
    name_en: str | None = None
    identifier_type: str
    identifier: str
    contact_phone: str | None = None
    contact_email: str | None = None
    address: str | None = None
    custom_fields: dict | None = None
    is_active: bool
    created_by: UUID | None = None
    created_at: datetime
    updated_at: datetime


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    total: int
    page: int
    page_size: int


class CustomerSearchParams(BaseModel):
    page: int = 1
    page_size: int = 25
    search: str | None = None
    is_active: bool | None = None
    sort_by: str = "updated_at"
    sort_order: str = "desc"
