from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.api.deps import require_role
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.services.quickfill_service import QuickFillService

router = APIRouter(prefix="/quickfill", tags=["QuickFill"])


@router.get("/customers")
async def quickfill_customer_search(
    request: Request,
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.OPERATOR, Role.ADMIN, Role.DESIGNER))
    ] = None,
):
    if not current_user or not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = QuickFillService(client)

    customers = await service.search_customers(
        query=q,
        org_id=current_user.org_id,
        limit=limit,
    )

    return {
        "query": q,
        "customers": customers,
    }


@router.post("/map")
async def quickfill_map(
    request: Request,
    body: dict,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.OPERATOR, Role.ADMIN, Role.DESIGNER))
    ] = None,
):
    if not current_user or not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    customer_id = body.get("customer_id")
    template_id = body.get("template_id")

    if not customer_id or not template_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="customer_id and template_id are required",
        )

    client = get_supabase_client()
    service = QuickFillService(client)

    result = await service.map_customer_to_fields(
        customer_id=UUID(customer_id),
        template_id=UUID(template_id),
        org_id=current_user.org_id,
    )

    return result
