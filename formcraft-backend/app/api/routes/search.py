from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.api.deps import require_role
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("")
async def global_search(
    request: Request,
    q: str = Query(..., min_length=2, description="Search query"),
    types: str | None = Query(None, description="Comma-separated: template,submission,customer"),
    limit: int = Query(5, ge=1, le=20),
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
    service = SearchService(client)

    type_list = [t.strip() for t in types.split(",")] if types else None

    results = await service.search_global(
        query=q,
        org_id=current_user.org_id,
        types=type_list,
        limit_per_type=limit,
        branch_id=getattr(current_user, "branch_id", None),
        department_id=getattr(current_user, "department_id", None),
    )

    return {
        "query": q,
        "results": results,
    }


@router.get("/reference")
async def search_by_reference(
    request: Request,
    ref: str = Query(..., min_length=3, description="Reference number"),
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
    service = SearchService(client)

    result = await service.search_by_reference_number(
        reference_number=ref,
        org_id=current_user.org_id,
        branch_id=getattr(current_user, "branch_id", None),
        department_id=getattr(current_user, "department_id", None),
    )

    if not result:
        return {"found": False, "submission": None}

    return result
