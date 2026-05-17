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
