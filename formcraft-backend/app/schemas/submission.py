import csv
import io
import json
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateSubmissionRequest(BaseModel):
    template_id: UUID
    template_version: int
    field_values: dict[str, object] = Field(default_factory=dict)
    status: str = "printed"


class SubmissionResponse(BaseModel):
    id: UUID
    reference_number: str
    template_id: UUID
    template_version: int
    operator_id: UUID
    field_values: dict
    status: str = "printed"
    created_at: datetime


class SubmissionDetailResponse(BaseModel):
    id: UUID
    reference_number: str
    template_id: UUID
    template_name: str = ""
    template_version: int
    status: str = "printed"
    operator_id: UUID
    operator_name: str = ""
    org_id: UUID | None = None
    field_values: dict
    created_at: datetime


class SubmissionListItem(BaseModel):
    id: UUID
    reference_number: str
    template_id: UUID
    template_name: str = ""
    template_version: int
    status: str = "printed"
    created_at: datetime
    key_summary: list[str] = Field(default_factory=list)


class SubmissionListResponse(BaseModel):
    items: list[SubmissionListItem]
    total: int
    page: int
    limit: int


class CreateDraftRequest(BaseModel):
    template_id: UUID
    template_version: int
    field_values: dict[str, object] = Field(default_factory=dict)
    name: str | None = None


class UpdateDraftRequest(BaseModel):
    field_values: dict[str, object] | None = None
    name: str | None = None


class DraftResponse(BaseModel):
    id: UUID
    template_id: UUID
    template_version: int
    field_values: dict
    completion_percent: int
    name: str | None
    expires_at: datetime
    created_at: datetime
    updated_at: datetime


class ValidatorFieldResponse(BaseModel):
    field_type: str
    pattern: str | None = None
    message_ar: str | None = None
    message_en: str | None = None


class ValidatorCountryResponse(BaseModel):
    country: str
    validators: list[ValidatorFieldResponse]


class ExportParams(BaseModel):
    format: str = "json"


class ReprintResponse(BaseModel):
    success: bool = True
    message: str = "Reprint generated"


def generate_csv(field_values: dict, reference_number: str, template_name: str, submitted_at: str) -> str:
    output = io.StringIO()
    output.write("\ufeff")
    writer = csv.writer(output)
    headers = ["reference_number", "template_name", "submitted_at"] + list(field_values.keys())
    writer.writerow(headers)
    values = [reference_number, template_name, submitted_at] + list(field_values.values())
    writer.writerow(values)
    return output.getvalue()