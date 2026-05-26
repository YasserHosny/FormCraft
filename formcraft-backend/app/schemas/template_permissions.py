from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


TemplateCapability = Literal[
    "view",
    "edit",
    "clone",
    "import",
    "export",
    "submit_review",
    "review",
    "publish",
    "fill",
    "print",
    "reprint",
    "report",
]

GrantEffect = Literal["allow", "deny"]
PrincipalType = Literal["base_role", "custom_role", "department", "branch", "user"]
DefaultImportPolicy = Literal["admin_only", "inherit_policy"]


class TemplateAccessGrantRequest(BaseModel):
    effect: GrantEffect
    principal_type: PrincipalType
    principal_id: str
    capabilities: list[TemplateCapability] = Field(default_factory=list)
    lifecycle_states: list[str] = Field(default_factory=list)


class TemplateAccessPolicyRequest(BaseModel):
    name: str
    description: str | None = None
    default_import_policy: DefaultImportPolicy = "admin_only"
    grants: list[TemplateAccessGrantRequest] = Field(default_factory=list)


class TemplateAccessGrantResponse(TemplateAccessGrantRequest):
    id: UUID | None = None
    policy_id: UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TemplateAccessPolicyResponse(BaseModel):
    id: UUID | None = None
    template_id: UUID
    name: str
    description: str | None = None
    is_active: bool
    default_import_policy: DefaultImportPolicy
    grants: list[TemplateAccessGrantResponse] = Field(default_factory=list)


class TemplateAccessDecisionResponse(BaseModel):
    allowed: bool
    reason: str
    capability: TemplateCapability
    template_id: UUID
    user_id: UUID
    matched_grants: list[dict] = Field(default_factory=list)
    matched_restrictions: list[dict] = Field(default_factory=list)
    role_sources: list[str] = Field(default_factory=list)
    scope_matches: list[str] = Field(default_factory=list)
    stale_cache: bool = False
