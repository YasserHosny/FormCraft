"""SSO routes: IdP CRUD, SAML ACS, OIDC callback, identity mapping."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.deps import get_current_user, require_role
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.identity import ProviderType
from app.models.user import UserProfile
from app.schemas.identity import (
    IdentityProviderCreate,
    IdentityProviderResponse,
    IdentityProviderUpdate,
    IdentityMappingCreate,
    IdentityMappingResponse,
    IdentityMappingUpdate,
)
from app.services.sso_service import SsoService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/sso", tags=["SSO"])


# ------------------------------------------------------------------
# Identity Provider CRUD
# ------------------------------------------------------------------


@router.post("/providers", response_model=IdentityProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_provider(
    body: IdentityProviderCreate,
    request: Request,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    client = get_supabase_client()
    # Domain uniqueness check (simplified MVP)
    existing = client.table("identity_providers").select("*").execute()
    for raw in existing.data or []:
        for d in raw.get("domains", []):
            if d.lower() in [x.lower() for x in body.domains]:
                raise HTTPException(status_code=409, detail="Domain already assigned to an active provider")

    provider = SsoService.create_provider(
        org_id=current_user.org_id,
        created_by=current_user.id,
        payload=body.model_dump(),
    )
    return provider


@router.get("/providers", response_model=list[IdentityProviderResponse])
async def list_providers(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    client = get_supabase_client()
    rows = client.table("identity_providers").select("*").eq("org_id", str(current_user.org_id)).execute()
    return [IdentityProviderResponse(**r) for r in rows.data or []]


@router.patch("/providers/{provider_id}", response_model=IdentityProviderResponse)
async def update_provider(
    provider_id: str,
    body: IdentityProviderUpdate,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    client = get_supabase_client()
    row = client.table("identity_providers").select("*").eq("id", provider_id).single().execute()
    if not row.data:
        raise HTTPException(status_code=404, detail="Provider not found")
    update_data = {k: v for k, v in body.model_dump().items() if v is not None}
    client.table("identity_providers").update(update_data).eq("id", provider_id).execute()
    return IdentityProviderResponse(**{**row.data, **update_data})


@router.delete("/providers/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(
    provider_id: str,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    client = get_supabase_client()
    client.table("identity_providers").delete().eq("id", provider_id).execute()


# ------------------------------------------------------------------
# SAML / OIDC Initiation
# ------------------------------------------------------------------


@router.get("/saml/login")
async def saml_login(provider_id: str):
    # Return redirect URL to IdP SAML endpoint
    # Real implementation uses python-saml to build AuthNRequest
    return {"redirect_url": f"/saml/sso?provider={provider_id}"}


@router.post("/saml/acs")
async def saml_acs(request: Request):
    # Consume SAMLResponse, validate, provision, issue JWT
    body = await request.form()
    logger.info("SAML ACS received for provider %s", body.get("RelayState"))
    return {"token": "jwt-token-placeholder"}


@router.get("/oidc/login")
async def oidc_login(provider_id: str):
    return {"redirect_url": f"/oidc/auth?provider={provider_id}"}


@router.get("/oidc/callback")
async def oidc_callback(code: str, state: str):
    logger.info("OIDC callback received code=%s state=%s", code, state)
    return {"token": "jwt-token-placeholder"}


# ------------------------------------------------------------------
# Identity Mapping
# ------------------------------------------------------------------


@router.post("/mappings", response_model=IdentityMappingResponse, status_code=status.HTTP_201_CREATED)
async def create_mapping(
    body: IdentityMappingCreate,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    client = get_supabase_client()
    row = {
        "id": str(__import__("uuid").uuid4()),
        "org_id": str(current_user.org_id),
        "provider_id": str(body.provider_id),
        "claim_type": body.claim_type,
        "claim_value": body.claim_value,
        "assigned_role": body.assigned_role,
        "assigned_department_id": str(body.assigned_department_id) if body.assigned_department_id else None,
        "assigned_branch_id": str(body.assigned_branch_id) if body.assigned_branch_id else None,
        "default_language": body.default_language,
        "priority": body.priority,
        "is_active": True,
        "created_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "updated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "created_by": str(current_user.id),
    }
    client.table("identity_mappings").insert(row).execute()
    return IdentityMappingResponse(**row)


@router.get("/mappings", response_model=list[IdentityMappingResponse])
async def list_mappings(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    client = get_supabase_client()
    rows = client.table("identity_mappings").select("*").eq("org_id", str(current_user.org_id)).execute()
    return [IdentityMappingResponse(**r) for r in rows.data or []]
