from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, require_role
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.admin_templates import (
    BulkActionRequest,
    BulkActionResponse,
    ComplianceDashboardResponse,
    GovernanceTemplateListResponse,
    RegulatoryAlert,
)
from app.services.compliance_service import ComplianceService
from app.services.template_governance_service import TemplateGovernanceService

router = APIRouter(prefix="/templates", tags=["Template Governance"])


@router.get("", response_model=GovernanceTemplateListResponse)
async def list_templates(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    department_id: UUID | None = Query(None),
    designer_id: UUID | None = Query(None),
    category: str | None = Query(None),
    search: str | None = Query(None),
    sort_by: str = Query("updated_at"),
    sort_dir: str = Query("desc"),
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = TemplateGovernanceService(client)
    items, total = await service.list_templates(
        org_id=current_user.org_id,
        page=page,
        page_size=page_size,
        status_filter=status_filter,
        department_id=department_id,
        designer_id=designer_id,
        category=category,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return GovernanceTemplateListResponse(
        items=items, total=total, page=page, page_size=page_size
    )


@router.post("/bulk-actions")
async def bulk_actions(
    body: BulkActionRequest,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = TemplateGovernanceService(client)
    result = await service.execute_bulk_action(
        org_id=current_user.org_id, request=body, actor_id=current_user.id
    )
    return BulkActionResponse(**result)


@router.get("/compliance")
async def get_compliance_dashboard(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = ComplianceService(client)
    result = await service.get_compliance_dashboard(current_user.org_id)
    return ComplianceDashboardResponse(**result)


@router.get("/regulatory-alerts")
async def get_regulatory_alerts(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = ComplianceService(client)
    alerts = await service.get_regulatory_alerts(current_user.org_id)
    return alerts
