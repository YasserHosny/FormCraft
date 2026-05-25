from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, require_role
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.marketplace import (
    MarketplaceImportRequest,
    MarketplaceImportResponse,
    MarketplaceListResponse,
    MarketplaceListingCreate,
    MarketplaceListingDetail,
    MarketplaceListingResponse,
    MarketplaceModerationRequest,
    MarketplacePurchaseRequest,
    MarketplaceReviewCreate,
    MarketplaceReviewListResponse,
    MarketplaceReviewResponse,
    MarketplaceTransactionResponse,
)
from app.services.marketplace_service import MarketplaceService


router = APIRouter(prefix="/marketplace", tags=["Marketplace"])
admin_router = APIRouter(prefix="/marketplace", tags=["Admin Marketplace"])


def _require_org(current_user: UserProfile) -> UUID:
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )
    return current_user.org_id


@router.get("/listings", response_model=MarketplaceListResponse)
async def list_marketplace_listings(
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    search: str | None = None,
    country: str | None = None,
    category: str | None = None,
    language: str | None = None,
    compliance: str | None = None,
    price_type: str | None = None,
    sort_by: str = "quality_score",
    sort_dir: str = "desc",
    page: int = Query(1, ge=1),
    page_size: int = Query(24, ge=1, le=100),
):
    service = MarketplaceService(get_supabase_client())
    items, total = await service.list_listings(
        page=page,
        page_size=page_size,
        search=search,
        country=country,
        category=category,
        language=language,
        compliance=compliance,
        price_type=price_type,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return MarketplaceListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/listings/{listing_id}", response_model=MarketplaceListingDetail)
async def get_marketplace_listing(
    listing_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    service = MarketplaceService(get_supabase_client())
    return await service.get_listing_detail(listing_id)


@router.post("/listings", response_model=MarketplaceListingResponse, status_code=201)
async def publish_marketplace_listing(
    body: MarketplaceListingCreate,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    org_id = _require_org(current_user)
    service = MarketplaceService(get_supabase_client())
    return await service.publish_listing(
        org_id=org_id,
        actor_id=current_user.id,
        data=body.model_dump(mode="json"),
    )


@router.post(
    "/listings/{listing_id}/purchase",
    response_model=MarketplaceTransactionResponse,
    status_code=201,
)
async def purchase_marketplace_listing(
    listing_id: UUID,
    body: MarketplacePurchaseRequest,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    org_id = _require_org(current_user)
    service = MarketplaceService(get_supabase_client())
    return await service.purchase_listing(
        listing_id=listing_id,
        consumer_org_id=org_id,
        actor_id=current_user.id,
        provider=body.provider,
        idempotency_key=body.idempotency_key,
    )


@router.post(
    "/listings/{listing_id}/import",
    response_model=MarketplaceImportResponse,
    status_code=201,
)
async def import_marketplace_listing(
    listing_id: UUID,
    body: MarketplaceImportRequest,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    org_id = _require_org(current_user)
    service = MarketplaceService(get_supabase_client())
    return await service.import_listing(
        listing_id=listing_id,
        consumer_org_id=org_id,
        actor_id=current_user.id,
        draft_name=body.draft_name,
        reference_mappings=body.reference_mappings,
        accept_disabled_dependencies=body.accept_disabled_dependencies,
    )


@router.post(
    "/listings/{listing_id}/reviews",
    response_model=MarketplaceReviewResponse,
    status_code=201,
)
async def create_marketplace_review(
    listing_id: UUID,
    body: MarketplaceReviewCreate,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    org_id = _require_org(current_user)
    service = MarketplaceService(get_supabase_client())
    return await service.create_or_update_review(
        listing_id=listing_id,
        consumer_org_id=org_id,
        actor_id=current_user.id,
        import_id=body.import_id,
        rating=body.rating,
        review_text=body.review_text,
    )


@router.get(
    "/listings/{listing_id}/reviews",
    response_model=MarketplaceReviewListResponse,
)
async def list_marketplace_reviews(
    listing_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    service = MarketplaceService(get_supabase_client())
    items, total = await service.list_reviews(listing_id)
    return MarketplaceReviewListResponse(items=items, total=total)


@admin_router.post("/listings/{listing_id}/moderation", response_model=MarketplaceListingResponse)
async def moderate_marketplace_listing(
    listing_id: UUID,
    body: MarketplaceModerationRequest,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    service = MarketplaceService(get_supabase_client())
    return await service.moderate_listing(
        listing_id=listing_id,
        actor_id=current_user.id,
        action=body.action,
        comment=body.comment,
    )
