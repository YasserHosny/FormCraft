from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import require_role
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/audit-logs")
async def get_audit_logs(
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN))
    ],
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
        query.range(offset, offset + limit - 1)
        .order("created_at", desc=True)
        .execute()
    )

    return {
        "data": result.data or [],
        "total": result.count or 0,
        "page": page,
        "limit": limit,
    }
