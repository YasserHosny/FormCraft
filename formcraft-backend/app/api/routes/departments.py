"""Department + nested branch routes (T019).

All endpoints are scoped to the caller's org_id.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.supabase import get_supabase_client
from app.middleware.org_context import OrgContext, require_org_admin, get_org_context
from app.schemas.organization import (
    BranchCreate,
    BranchResponse,
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.services.branch_service import BranchService
from app.services.department_service import DepartmentService

router = APIRouter(prefix="/departments", tags=["Departments"])


# ------------------------------------------------------------------
# Department CRUD
# ------------------------------------------------------------------


@router.post("", response_model=DepartmentResponse, status_code=201)
async def create_department(
    body: DepartmentCreate,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    """Create a department within the caller's organisation."""
    client = get_supabase_client()
    service = DepartmentService(client)
    return await service.create_department(
        org_id=ctx.org_id,
        data=body.model_dump(),
        created_by=ctx.user_id,
    )


@router.get("")
async def list_departments(
    ctx: Annotated[OrgContext, Depends(get_org_context)],
    include_inactive: bool = Query(False),
):
    """List all departments in the caller's organisation."""
    client = get_supabase_client()
    service = DepartmentService(client)
    depts = await service.list_departments(
        org_id=ctx.org_id, include_inactive=include_inactive
    )
    return {"data": depts}


@router.get("/{dept_id}", response_model=DepartmentResponse)
async def get_department(
    dept_id: UUID,
    ctx: Annotated[OrgContext, Depends(get_org_context)],
):
    """Get a single department."""
    client = get_supabase_client()
    service = DepartmentService(client)
    return await service.get_department(dept_id, ctx.org_id)


@router.patch("/{dept_id}", response_model=DepartmentResponse)
async def update_department(
    dept_id: UUID,
    body: DepartmentUpdate,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    """Update a department (org admin only)."""
    client = get_supabase_client()
    service = DepartmentService(client)
    data = body.model_dump(exclude_none=True)
    return await service.update_department(
        dept_id=dept_id, org_id=ctx.org_id, data=data, updated_by=ctx.user_id
    )


@router.delete("/{dept_id}", status_code=204)
async def deactivate_department(
    dept_id: UUID,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    """Soft-delete (deactivate) a department (org admin only).

    Fails with 409 if the department still has active users.
    """
    client = get_supabase_client()
    service = DepartmentService(client)
    await service.deactivate_department(
        dept_id=dept_id, org_id=ctx.org_id, updated_by=ctx.user_id
    )


# ------------------------------------------------------------------
# Nested branch routes under /departments/{dept_id}/branches
# ------------------------------------------------------------------


@router.post(
    "/{dept_id}/branches", response_model=BranchResponse, status_code=201
)
async def create_branch(
    dept_id: UUID,
    body: BranchCreate,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    """Create a branch under a department."""
    client = get_supabase_client()
    service = BranchService(client)
    return await service.create_branch(
        dept_id=dept_id,
        org_id=ctx.org_id,
        data=body.model_dump(),
        created_by=ctx.user_id,
    )


@router.get("/{dept_id}/branches")
async def list_branches(
    dept_id: UUID,
    ctx: Annotated[OrgContext, Depends(get_org_context)],
    include_inactive: bool = Query(False),
):
    """List branches under a department."""
    client = get_supabase_client()
    service = BranchService(client)
    branches = await service.list_branches(
        dept_id=dept_id, org_id=ctx.org_id, include_inactive=include_inactive
    )
    return {"data": branches}
