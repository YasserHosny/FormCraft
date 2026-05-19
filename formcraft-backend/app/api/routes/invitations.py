"""Invitation CRUD + public accept endpoint (T025)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.supabase import get_supabase_client
from app.middleware.org_context import OrgContext, require_org_admin
from app.schemas.organization import (
    InvitationAcceptRequest,
    InvitationCreate,
    InvitationResponse,
)
from app.services.invitation_service import InvitationService

router = APIRouter(prefix="/invitations", tags=["Invitations"])

# ------------------------------------------------------------------
# Authenticated endpoints (org admin)
# ------------------------------------------------------------------


@router.post("", response_model=InvitationResponse, status_code=201)
async def create_invitation(
    body: InvitationCreate,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    """Create a new user invitation (org admin only)."""
    client = get_supabase_client()
    service = InvitationService(client)
    return await service.create_invitation(
        org_id=ctx.org_id,
        data=body.model_dump(),
        invited_by=ctx.user_id,
    )


@router.get("")
async def list_invitations(
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
    status_filter: str | None = Query(None, alias="status"),
):
    """List invitations for the current organisation (org admin only)."""
    client = get_supabase_client()
    service = InvitationService(client)
    invitations = await service.list_invitations(
        org_id=ctx.org_id, status_filter=status_filter
    )
    return {"data": invitations}


@router.delete("/{invitation_id}", status_code=204)
async def cancel_invitation(
    invitation_id: UUID,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    """Cancel a pending invitation (org admin only)."""
    client = get_supabase_client()
    service = InvitationService(client)
    await service.cancel_invitation(
        invitation_id=invitation_id,
        org_id=ctx.org_id,
        cancelled_by=ctx.user_id,
    )


# ------------------------------------------------------------------
# Public endpoint (no auth — token-based)
# ------------------------------------------------------------------

public_router = APIRouter(tags=["Invitations (Public)"])


@public_router.get("/invitations/{token}")
async def get_invitation_by_token(token: str):
    """Get invitation details by token (public, for prefilling the accept form)."""
    from fastapi import HTTPException, status as http_status

    client = get_supabase_client()
    result = (
        client.table("user_invitations")
        .select("id,email,role,org_id,department_id,branch_id,status,expires_at")
        .eq("token", token)
        .execute()
    )
    if not result.data:
        raise HTTPException(http_status.HTTP_404_NOT_FOUND, "Invitation not found")
    invitation = result.data[0]
    if invitation["status"] != "pending":
        raise HTTPException(http_status.HTTP_410_GONE, "Invitation already processed")
    # Fetch org name for display
    org = client.table("organizations").select("name_en,name_ar,logo_url").eq("id", invitation["org_id"]).execute()
    org_data = org.data[0] if org.data else {}
    return {
        "email": invitation["email"],
        "role": invitation["role"],
        "org_name_en": org_data.get("name_en", ""),
        "org_name_ar": org_data.get("name_ar", ""),
        "org_logo_url": org_data.get("logo_url"),
        "expires_at": invitation["expires_at"],
    }


@public_router.post("/invitations/accept/{token}")
async def accept_invitation(
    token: str,
    body: InvitationAcceptRequest,
):
    """Accept an invitation and create a user account (public, token-based)."""
    client = get_supabase_client()
    service = InvitationService(client)
    result = await service.accept_invitation(
        token=token,
        display_name=body.display_name,
        password=body.password,
    )
    return result
