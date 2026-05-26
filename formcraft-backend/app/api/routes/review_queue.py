from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, require_role
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.review_queue import (
    DefaultReviewerRequest,
    DefaultReviewerResponse,
    GovernanceMetrics,
    ReviewQueueResponse,
    TimelineResponse,
)
from app.services.review_queue_service import ReviewQueueService

router = APIRouter(prefix="/review-queue", tags=["Review Queue"])


@router.get("", response_model=ReviewQueueResponse)
async def get_review_queue(
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN, Role.BRANCH_MANAGER))
    ],
    status: str | None = Query(None),
    department_id: UUID | None = Query(None),
    designer_id: UUID | None = Query(None),
    sort_by: str = Query("submitted_at"),
    sort_dir: str = Query("asc"),
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = ReviewQueueService(client)

    # Branch managers can only see their own department
    effective_dept_id = department_id
    if current_user.role == Role.BRANCH_MANAGER and current_user.department_id:
        effective_dept_id = current_user.department_id

    result = await service.get_review_queue(
        org_id=current_user.org_id,
        status_filter=status,
        department_id=effective_dept_id,
        designer_id=designer_id,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return ReviewQueueResponse(**result)


@router.get("/metrics", response_model=GovernanceMetrics)
async def get_governance_metrics(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
    since: str | None = Query(None),
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    since_dt = None
    if since:
        try:
            since_dt = datetime.strptime(since, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid since format. Use YYYY-MM-DD",
            )
    else:
        since_dt = datetime.now(timezone.utc) - timedelta(days=30)

    client = get_supabase_client()
    service = ReviewQueueService(client)
    result = await service.get_governance_metrics(
        org_id=current_user.org_id,
        since=since_dt,
    )
    return GovernanceMetrics(**result)


@router.get("/{template_id}/timeline", response_model=TimelineResponse)
async def get_timeline(
    template_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = ReviewQueueService(client)

    # Role-based scoping
    # Admin sees all, branch_manager sees own dept, designer sees own templates
    if current_user.role == Role.BRANCH_MANAGER and current_user.department_id:
        # Verify template is in their department
        tmpl = (
            client.table("templates")
            .select("department_id")
            .eq("id", str(template_id))
            .single()
            .execute()
        )
        if not tmpl.data or tmpl.data.get("department_id") != str(
            current_user.department_id
        ):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")
    elif current_user.role == Role.DESIGNER:
        # Verify template was created by them
        tmpl = (
            client.table("templates")
            .select("created_by")
            .eq("id", str(template_id))
            .single()
            .execute()
        )
        if not tmpl.data or tmpl.data.get("created_by") != str(current_user.id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")

    result = await service.get_timeline(
        org_id=current_user.org_id,
        template_id=template_id,
    )
    return TimelineResponse(**result)


@router.get(
    "/departments/{department_id}/default-reviewer",
    response_model=DefaultReviewerResponse,
)
async def get_default_reviewer(
    department_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = ReviewQueueService(client)
    result = await service.get_default_reviewer(current_user.org_id, department_id)
    if not result:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No default reviewer assigned")
    return DefaultReviewerResponse(**result)


@router.put(
    "/departments/{department_id}/default-reviewer",
    response_model=DefaultReviewerResponse,
)
async def set_default_reviewer(
    department_id: UUID,
    body: DefaultReviewerRequest,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = ReviewQueueService(client)
    result = await service.set_default_reviewer(
        current_user.org_id, department_id, body.reviewer_id
    )
    return DefaultReviewerResponse(**result)


@router.delete("/departments/{department_id}/default-reviewer", status_code=204)
async def remove_default_reviewer(
    department_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = ReviewQueueService(client)
    await service.remove_default_reviewer(current_user.org_id, department_id)
    return None
