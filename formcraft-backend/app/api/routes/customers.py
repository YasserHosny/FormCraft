from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.api.deps import get_current_user, require_role
from app.core.audit import AuditLogger
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.customer import (
    CustomerCreate,
    CustomerListResponse,
    CustomerResponse,
    CustomerSearchParams,
    CustomerUpdate,
)
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("", status_code=201, response_model=CustomerResponse)
async def create_customer(
    request: Request,
    body: CustomerCreate,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.OPERATOR, Role.ADMIN))
    ],
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = CustomerService(client)
    customer = await service.create_customer(
        data=body,
        org_id=current_user.org_id,
        created_by=current_user.id,
    )
    return CustomerResponse(**customer)


@router.get("", response_model=CustomerListResponse)
async def list_customers(
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.OPERATOR, Role.ADMIN))
    ],
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: str | None = Query(None),
    is_active: bool | None = Query(None),
    sort_by: str = Query("updated_at"),
    sort_order: str = Query("desc"),
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = CustomerService(client)

    if search and search.strip():
        items, total = await service.search_customers(
            org_id=current_user.org_id,
            query_text=search.strip(),
            page=page,
            page_size=page_size,
        )
    else:
        items, total = await service.list_customers(
            org_id=current_user.org_id,
            page=page,
            page_size=page_size,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    return CustomerListResponse(
        items=[CustomerResponse(**item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/recent", response_model=list[CustomerResponse])
async def get_recent_customers(
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.OPERATOR, Role.ADMIN))
    ],
    limit: int = Query(5, ge=1, le=20),
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = CustomerService(client)
    items = await service.get_recent(
        user_id=current_user.id,
        org_id=current_user.org_id,
        limit=limit,
    )
    return [CustomerResponse(**item) for item in items]


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: UUID,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.OPERATOR, Role.ADMIN))
    ],
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = CustomerService(client)
    customer = await service.get_by_id(customer_id, current_user.org_id)
    return CustomerResponse(**customer)


@router.patch("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: UUID,
    body: CustomerUpdate,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.OPERATOR, Role.ADMIN))
    ],
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = CustomerService(client)
    customer = await service.update_customer(
        customer_id=customer_id,
        org_id=current_user.org_id,
        data=body,
        actor_id=current_user.id,
    )
    return CustomerResponse(**customer)


@router.post("/{customer_id}/deactivate", response_model=CustomerResponse)
async def deactivate_customer(
    customer_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = CustomerService(client)
    customer = await service.deactivate_customer(
        customer_id=customer_id,
        org_id=current_user.org_id,
        actor_id=current_user.id,
    )
    return CustomerResponse(**customer)


@router.post("/{customer_id}/reactivate", response_model=CustomerResponse)
async def reactivate_customer(
    customer_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = CustomerService(client)
    customer = await service.reactivate_customer(
        customer_id=customer_id,
        org_id=current_user.org_id,
        actor_id=current_user.id,
    )
    return CustomerResponse(**customer)


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = CustomerService(client)
    await service.delete_customer(customer_id, current_user.org_id)
    return None


@router.get("/{customer_id}/auto-populate")
async def get_auto_populate_data(
    customer_id: UUID,
    template_id: UUID,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.OPERATOR, Role.ADMIN))
    ],
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = CustomerService(client)
    mappings = await service.get_auto_populate_data(customer_id, template_id)
    return {"mappings": mappings}


@router.get("/{customer_id}/submissions")
async def get_customer_submissions(
    customer_id: UUID,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.OPERATOR, Role.ADMIN))
    ],
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    template_id: UUID | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = CustomerService(client)
    items, total = await service.get_submissions(
        customer_id=customer_id,
        org_id=current_user.org_id,
        page=page,
        page_size=page_size,
        template_id=template_id,
        date_from=date_from,
        date_to=date_to,
    )
    return {"items": items, "total": total, "page": page, "page_size": page_size}
