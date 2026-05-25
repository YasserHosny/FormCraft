from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


PackageImportMode = Literal["new_draft", "new_version"]
PackageImportStatus = Literal["draft", "imported"]


class TemplatePackage(BaseModel):
    package_version: str
    exported_at: datetime
    source_template_id: UUID | None = None
    template_lineage_id: UUID | None = None
    template: dict
    pages: list[dict]
    elements: list[dict]
    validators: list[dict] = Field(default_factory=list)
    conditions: list[dict] = Field(default_factory=list)
    reference_bindings: list[dict] = Field(default_factory=list)
    checksum: str


class PackageImportReview(BaseModel):
    can_import: bool
    import_mode: PackageImportMode
    target_template_id: UUID | None = None
    warnings: list[str] = Field(default_factory=list)
    remapping_required: list[dict] = Field(default_factory=list)


class PackageImportRequest(BaseModel):
    package: TemplatePackage
    remapping: dict = Field(default_factory=dict)


class PackageImportResult(BaseModel):
    template_id: UUID
    version: int
    import_mode: PackageImportMode
    status: PackageImportStatus
