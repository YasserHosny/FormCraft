from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import require_role
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.feedback import FeedbackAdminListResponse, FeedbackStatusUpdateRequest
from app.schemas.label import (
    LabelCreateRequest,
    LabelUpdateRequest,
    LabelResponse,
    SubmissionLabelAssignRequest,
)
from app.schemas.reply import ReplyCreateRequest, ReplyResponse, ThreadResponse
from app.services.feedback.reply_service import ReplyService
from app.services.feedback.service import FeedbackService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/audit-logs")
async def get_audit_logs(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    user_id: str | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
):
    """Query audit logs (Admin only)."""
    client = get_supabase_client()
    offset = (page - 1) * limit
    query = client.table("audit_logs").select("*", count="exact")

    if user_id:
        query = query.eq("user_id", user_id)
    if action:
        query = query.eq("action", action)
    if resource_type:
        query = query.eq("resource_type", resource_type)
    if date_from:
        query = query.gte("created_at", date_from)
    if date_to:
        query = query.lte("created_at", date_to)

    result = (
        query.range(offset, offset + limit - 1).order("created_at", desc=True).execute()
    )

    return {
        "data": result.data or [],
        "total": result.count or 0,
        "page": page,
        "limit": limit,
    }


@router.get("/feedback", response_model=FeedbackAdminListResponse)
async def list_feedback(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    status: str | None = None,
    user_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    search: str | None = None,
    label_ids: str | None = None,
):
    """List all feedback submissions (Admin only, paginated)."""
    client = get_supabase_client()
    service = FeedbackService(client)
    parsed_label_ids = label_ids.split(",") if label_ids else None
    items, total = await service.list_feedback(
        page=page,
        limit=limit,
        status=status,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
        search=search,
        label_ids=parsed_label_ids,
    )
    return FeedbackAdminListResponse(data=items, total=total, page=page, limit=limit)


@router.get("/feedback/submitters")
async def list_submitters(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    client = get_supabase_client()
    service = FeedbackService(client)
    return await service.list_submitters()


@router.patch("/feedback/{feedback_id}", response_model=dict)
async def update_feedback_status(
    feedback_id: UUID,
    request: FeedbackStatusUpdateRequest,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    """Update the status of a feedback submission (Admin only)."""
    client = get_supabase_client()
    service = FeedbackService(client)
    return await service.update_status(feedback_id, request.status)


@router.get("/feedback/{feedback_id}/replies", response_model=ThreadResponse)
async def get_feedback_replies(
    feedback_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
    limit: int = Query(20, ge=1, le=100),
    before_id: UUID | None = None,
):
    """Get replies for a feedback thread (Admin only)."""
    client = get_supabase_client()
    service = ReplyService(client)
    return await service.get_replies(
        feedback_id=feedback_id,
        user_id=current_user.id,
        is_admin=True,
        limit=limit,
        before_id=before_id,
    )


@router.post(
    "/feedback/{feedback_id}/replies",
    response_model=ReplyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def post_feedback_reply(
    feedback_id: UUID,
    request: ReplyCreateRequest,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    """Post a reply to a feedback thread (Admin only)."""
    client = get_supabase_client()
    service = ReplyService(client)
    return await service.post_reply(
        feedback_id=feedback_id,
        author_id=current_user.id,
        author_role="admin",
        payload=request,
    )


@router.patch(
    "/feedback/{feedback_id}/read",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def mark_feedback_read(
    feedback_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    """Mark all user replies as read for a submission (Admin only)."""
    client = get_supabase_client()
    service = ReplyService(client)
    await service.mark_submission_read(feedback_id=feedback_id)


@router.get("/labels", response_model=list[LabelResponse])
async def list_labels(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    client = get_supabase_client()
    service = FeedbackService(client)
    return await service.list_labels()


@router.post(
    "/labels", response_model=LabelResponse, status_code=status.HTTP_201_CREATED
)
async def create_label(
    request: LabelCreateRequest,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    client = get_supabase_client()
    service = FeedbackService(client)
    return await service.create_label(admin_id=current_user.id, payload=request)


@router.patch("/labels/{label_id}", response_model=LabelResponse)
async def update_label(
    label_id: UUID,
    request: LabelUpdateRequest,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    client = get_supabase_client()
    service = FeedbackService(client)
    return await service.update_label(label_id=label_id, payload=request)


@router.delete("/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_label(
    label_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    client = get_supabase_client()
    service = FeedbackService(client)
    await service.delete_label(label_id=label_id)


@router.put("/feedback/{feedback_id}/labels")
async def assign_labels(
    feedback_id: UUID,
    request: SubmissionLabelAssignRequest,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    client = get_supabase_client()
    service = FeedbackService(client)
    return await service.assign_labels(
        feedback_id=feedback_id,
        label_ids=[str(lid) for lid in request.label_ids],
        admin_id=current_user.id,
    )
