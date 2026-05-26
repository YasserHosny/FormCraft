"""Org-admin settings routes (T018).

These endpoints are scoped to the caller's own org_id.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile

from app.core.supabase import get_supabase_client
from app.middleware.org_context import OrgContext, require_org_admin
from app.schemas.organization import OrgResponse, OrgSettingsUpdate
from app.services.organization_service import OrganizationService

router = APIRouter(prefix="/org-settings", tags=["Org Settings"])


@router.get("", response_model=OrgResponse)
async def get_my_org_settings(
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    """Get the current organisation's settings (org admin only)."""
    client = get_supabase_client()
    service = OrganizationService(client)
    return await service.get_org_settings(ctx.org_id)


@router.patch("", response_model=OrgResponse)
async def update_my_org_settings(
    body: OrgSettingsUpdate,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    """Update the current organisation's settings (org admin only)."""
    client = get_supabase_client()
    service = OrganizationService(client)
    data = body.model_dump(exclude_none=True)
    return await service.update_org_settings(
        org_id=ctx.org_id,
        data=data,
        updated_by=ctx.user_id,
    )


@router.post("/logo")
async def upload_my_org_logo(
    file: UploadFile,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    """Upload logo for the current organisation (org admin only)."""
    client = get_supabase_client()
    service = OrganizationService(client)
    file_bytes = await file.read()
    logo_url = await service.upload_logo(
        org_id=ctx.org_id,
        file_bytes=file_bytes,
        filename=file.filename or "logo.png",
        content_type=file.content_type or "image/png",
        updated_by=ctx.user_id,
    )
    return {"logo_url": logo_url}
