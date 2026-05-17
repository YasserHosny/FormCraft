"""Pydantic schemas for reference data manager."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class ColumnSchema(BaseModel):
    key: str = Field(min_length=1, max_length=100, pattern=r"^[a-z][a-z0-9_]*$")
    label_ar: str = Field(min_length=1, max_length=200)
    label_en: str = Field(min_length=1, max_length=200)
    type: str = Field(pattern=r"^(text|number|date|dropdown)$")
    required: bool = False
    is_unique_key: bool = False
    is_hidden: bool = False
    options: list[str] | None = None

    @model_validator(mode="after")
    def validate_dropdown_options(self):
        if self.type == "dropdown" and (not self.options or len(self.options) == 0):
            raise ValueError("Options required for dropdown type")
        return self


class ReferenceListCreate(BaseModel):
    name_ar: str = Field(min_length=1, max_length=500)
    name_en: str = Field(min_length=1, max_length=500)
    description: str | None = None
    schema_def: list[ColumnSchema] = Field(alias="schema", min_length=1)

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def validate_unique_keys(self):
        keys = [c.key for c in self.schema_def]
        if len(keys) != len(set(keys)):
            raise ValueError("Duplicate column key")
        return self


class ReferenceListUpdate(BaseModel):
    name_ar: str | None = Field(default=None, min_length=1, max_length=500)
    name_en: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    schema_def: list[ColumnSchema] | None = Field(default=None, alias="schema", min_length=1)

    model_config = {"populate_by_name": True}


class ReferenceListResponse(BaseModel):
    id: UUID
    name_ar: str
    name_en: str
    description: str | None = None
    schema_: list[dict] = Field(alias="schema")
    is_archived: bool
    entry_count: int = 0
    created_by: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"populate_by_name": True}


class ReferenceEntryCreate(BaseModel):
    values: dict


class ReferenceEntryUpdate(BaseModel):
    values: dict


class ReferenceEntryResponse(BaseModel):
    id: UUID
    values: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DropdownItem(BaseModel):
    display: str
    value: str
    entry_id: UUID


class ImportPreviewResponse(BaseModel):
    total_rows: int
    valid_count: int
    invalid_count: int
    column_mapping: dict[str, str]
    errors: list[dict]
    preview_token: str


class ImportConfirmRequest(BaseModel):
    preview_token: str
    import_valid_only: bool = True
