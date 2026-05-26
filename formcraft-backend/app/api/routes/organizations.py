"""Platform-admin organisation CRUD routes (T017)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, UploadFile

from app.core.supabase import get_supabase_client
from app.middleware.org_context import OrgContext, require_platform_admin
from app.schemas.organization import OrgCreate, OrgResponse, OrgUpdate
from app.services.organization_service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.post("", response_model=OrgResponse, status_code=201)
async def create_organization(
    body: OrgCreate,
    ctx: Annotated[OrgContext, Depends(require_platform_admin())],
):
    """Create a new organisation (platform admin only)."""
    client = get_supabase_client()
    service = OrganizationService(client)
    org = await service.create_org(
        data=body.model_dump(),
        created_by=ctx.user_id,
    )
    return org


@router.get("")
async def list_organizations(
    ctx: Annotated[OrgContext, Depends(require_platform_admin())],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    is_active: bool | None = Query(None),
):
    """List all organisations with pagination (platform admin only)."""
    client = get_supabase_client()
    service = OrganizationService(client)
    orgs, total = await service.list_orgs(
        page=page, limit=limit, search=search, is_active=is_active
    )
    return {"data": orgs, "total": total, "page": page, "limit": limit}


@router.get("/{org_id}", response_model=OrgResponse)
async def get_organization(
    org_id: UUID,
    ctx: Annotated[OrgContext, Depends(require_platform_admin())],
):
    """Get a single organisation by ID (platform admin only)."""
    client = get_supabase_client()
    service = OrganizationService(client)
    return await service.get_org(org_id)


@router.patch("/{org_id}", response_model=OrgResponse)
async def update_organization(
    org_id: UUID,
    body: OrgUpdate,
    ctx: Annotated[OrgContext, Depends(require_platform_admin())],
):
    """Update an organisation (platform admin only)."""
    client = get_supabase_client()
    service = OrganizationService(client)
    data = body.model_dump(exclude_none=True)
    return await service.update_org(org_id, data, updated_by=ctx.user_id)


@router.post("/{org_id}/logo")
async def upload_org_logo(
    org_id: UUID,
    file: UploadFile,
    ctx: Annotated[OrgContext, Depends(require_platform_admin())],
):
    """Upload organisation logo (platform admin only)."""
    client = get_supabase_client()
    service = OrganizationService(client)
    file_bytes = await file.read()
    logo_url = await service.upload_logo(
        org_id=org_id,
        file_bytes=file_bytes,
        filename=file.filename or "logo.png",
        content_type=file.content_type or "image/png",
        updated_by=ctx.user_id,
    )
    return {"logo_url": logo_url}
