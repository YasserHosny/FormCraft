"""Platform admin routes (F039)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.supabase import get_supabase_client
from app.middleware.org_context import OrgContext, require_platform_admin
from app.schemas.platform import (
    FirstAdminInvite,
    OrganizationCreate,
    OrganizationDetail,
    OrganizationUpdate,
    PlatformMetrics,
)
from app.services.platform_metrics_service import PlatformMetricsService
from app.services.platform_service import PlatformService

router = APIRouter(prefix="/platform", tags=["Platform Admin"])


# ------------------------------------------------------------------
# ORGANIZATIONS
# ------------------------------------------------------------------

@router.get("/organizations", response_model=dict)
async def list_organizations(
    ctx: Annotated[OrgContext, Depends(require_platform_admin())],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    tier: str | None = Query(None),
    status: str | None = Query(None),
    country: str | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
):
    """List all organizations with search, filter, sort, and pagination."""
    client = get_supabase_client()
    service = PlatformService(client)
    orgs, total = await service.list_organizations(
        page=page,
        page_size=page_size,
        search=search,
        tier=tier,
        status=status,
        country=country,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return {
        "items": orgs,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/organizations", response_model=OrganizationDetail, status_code=201)
async def create_organization(
    body: OrganizationCreate,
    ctx: Annotated[OrgContext, Depends(require_platform_admin())],
):
    """Create a new organization (platform admin only)."""
    client = get_supabase_client()
    service = PlatformService(client)
    org = await service.create_organization(
        data=body.model_dump(exclude_none=True),
        created_by=ctx.user_id,
    )
    return await service.get_organization_detail(UUID(org["id"]))


@router.get("/organizations/{org_id}", response_model=OrganizationDetail)
async def get_organization(
    org_id: UUID,
    ctx: Annotated[OrgContext, Depends(require_platform_admin())],
):
    """Get organization detail with computed fields."""
    client = get_supabase_client()
    service = PlatformService(client)
    return await service.get_organization_detail(org_id)


@router.patch("/organizations/{org_id}", response_model=OrganizationDetail)
async def update_organization(
    org_id: UUID,
    body: OrganizationUpdate,
    ctx: Annotated[OrgContext, Depends(require_platform_admin())],
):
    """Update organization profile/settings."""
    client = get_supabase_client()
    service = PlatformService(client)
    await service.update_organization(
        org_id=org_id,
        data=body.model_dump(exclude_none=True),
        updated_by=ctx.user_id,
    )
    return await service.get_organization_detail(org_id)


@router.delete("/organizations/{org_id}", status_code=204)
async def delete_organization(
    org_id: UUID,
    ctx: Annotated[OrgContext, Depends(require_platform_admin())],
):
    """Delete organization (blocked if submissions exist)."""
    client = get_supabase_client()
    service = PlatformService(client)
    await service.delete_organization(org_id=org_id, deleted_by=ctx.user_id)


@router.post("/organizations/{org_id}/suspend", response_model=OrganizationDetail)
async def suspend_organization(
    org_id: UUID,
    ctx: Annotated[OrgContext, Depends(require_platform_admin())],
):
    """Suspend an organization and revoke all active sessions."""
    client = get_supabase_client()
    service = PlatformService(client)
    return await service.suspend_organization(org_id=org_id, admin_id=ctx.user_id)


@router.post("/organizations/{org_id}/reactivate", response_model=OrganizationDetail)
async def reactivate_organization(
    org_id: UUID,
    ctx: Annotated[OrgContext, Depends(require_platform_admin())],
):
    """Reactivate a suspended organization."""
    client = get_supabase_client()
    service = PlatformService(client)
    return await service.reactivate_organization(org_id=org_id, admin_id=ctx.user_id)


@router.get("/organizations/check-domain")
async def check_domain(
    domain: str,
    ctx: Annotated[OrgContext, Depends(require_platform_admin())],
):
    """Check if a custom domain is available."""
    client = get_supabase_client()
    existing = (
        client.table("organizations")
        .select("id")
        .eq("domain", domain)
        .execute()
    )
    return {"available": not existing.data}


@router.post("/organizations/{org_id}/invite-first-admin")
async def invite_first_admin(
    org_id: UUID,
    body: FirstAdminInvite,
    ctx: Annotated[OrgContext, Depends(require_platform_admin())],
):
    """Invite the first admin user to a new organization."""
    client = get_supabase_client()
    service = PlatformService(client)
    invite = await service.invite_first_admin(
        org_id=org_id,
        email=str(body.email),
        invited_by=ctx.user_id,
    )
    return {"success": True, "invite": invite}


# ------------------------------------------------------------------
# METRICS
# ------------------------------------------------------------------

@router.get("/metrics", response_model=PlatformMetrics)
async def get_platform_metrics(
    ctx: Annotated[OrgContext, Depends(require_platform_admin())],
):
    """Get platform-wide aggregate metrics."""
    client = get_supabase_client()
    service = PlatformMetricsService(client)
    return await service.get_metrics()


@router.post("/metrics/refresh")
async def refresh_platform_metrics(
    ctx: Annotated[OrgContext, Depends(require_platform_admin())],
):
    """Manually refresh the platform metrics materialized view."""
    client = get_supabase_client()
    service = PlatformMetricsService(client)
    await service.refresh_materialized_view()
    return {"status": "refreshed"}
