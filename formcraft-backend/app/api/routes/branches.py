"""Flat branch routes (T020).

Provides org-wide branch listing and individual branch operations
independent of the department nesting.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.supabase import get_supabase_client
from app.middleware.org_context import OrgContext, get_org_context, require_org_admin
from app.schemas.organization import BranchResponse, BranchUpdate
from app.services.branch_service import BranchService

router = APIRouter(prefix="/branches", tags=["Branches"])


@router.get("")
async def list_all_branches(
    ctx: Annotated[OrgContext, Depends(get_org_context)],
):
    """List all branches across the organisation (flat, with department info)."""
    client = get_supabase_client()
    service = BranchService(client)
    branches = await service.list_all_branches(org_id=ctx.org_id)
    return {"data": branches}


@router.get("/{branch_id}", response_model=BranchResponse)
async def get_branch(
    branch_id: UUID,
    ctx: Annotated[OrgContext, Depends(get_org_context)],
):
    """Get a single branch by ID."""
    client = get_supabase_client()
    service = BranchService(client)
    return await service.get_branch(branch_id, ctx.org_id)


@router.patch("/{branch_id}", response_model=BranchResponse)
async def update_branch(
    branch_id: UUID,
    body: BranchUpdate,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    """Update a branch (org admin only)."""
    client = get_supabase_client()
    service = BranchService(client)
    data = body.model_dump(exclude_none=True)
    return await service.update_branch(
        branch_id=branch_id,
        org_id=ctx.org_id,
        data=data,
        updated_by=ctx.user_id,
    )


@router.delete("/{branch_id}", status_code=204)
async def deactivate_branch(
    branch_id: UUID,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    """Soft-delete (deactivate) a branch (org admin only).

    Fails with 409 if the branch still has active users.
    """
    client = get_supabase_client()
    service = BranchService(client)
    await service.deactivate_branch(
        branch_id=branch_id, org_id=ctx.org_id, updated_by=ctx.user_id
    )
