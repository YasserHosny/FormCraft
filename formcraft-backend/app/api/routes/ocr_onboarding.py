"""Batch OCR onboarding endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status

from app.api.deps import require_role
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.ocr_onboarding import (
    OCRBulkAcceptRequest,
    OCRBulkAcceptResponse,
    OCRDuplicateResolveRequest,
    OCRImportBatchDetailResponse,
    OCRImportBatchListResponse,
    OCRImportBatchResponse,
    OCRImportItemResponse,
    OCRReviewDecisionRequest,
)
from app.services.ocr_onboarding_service import OCRBatchValidationError, OCROnboardingService

router = APIRouter(prefix="/ocr-onboarding", tags=["OCR Onboarding"])


def get_service() -> OCROnboardingService:
    return OCROnboardingService(get_supabase_client())


def _require_org(user: UserProfile) -> UUID:
    if not user.org_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "No organization context")
    return user.org_id


@router.post("/batches", response_model=OCRImportBatchResponse, status_code=status.HTTP_201_CREATED)
async def create_batch(
    name: str = Form(...),
    confidence_threshold: float = Form(0.85, ge=0.0, le=1.0),
    files: list[UploadFile] = File(...),
    current_user: UserProfile = Depends(require_role(Role.ADMIN, Role.DESIGNER)),
    service: OCROnboardingService = Depends(get_service),
):
    try:
        return await service.create_batch(
            org_id=_require_org(current_user),
            created_by=current_user.id,
            name=name,
            confidence_threshold=confidence_threshold,
            files=files,
        )
    except OCRBatchValidationError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc


@router.get("/batches", response_model=OCRImportBatchListResponse)
async def list_batches(
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserProfile = Depends(require_role(Role.ADMIN, Role.DESIGNER)),
    service: OCROnboardingService = Depends(get_service),
):
    items, total = await service.list_batches(
        org_id=_require_org(current_user),
        status_filter=status_filter,
        limit=limit,
        offset=offset,
    )
    return OCRImportBatchListResponse(items=items, total=total)


@router.get("/batches/{batch_id}", response_model=OCRImportBatchDetailResponse)
async def get_batch(
    batch_id: UUID,
    current_user: UserProfile = Depends(require_role(Role.ADMIN, Role.DESIGNER)),
    service: OCROnboardingService = Depends(get_service),
):
    return await service.get_batch(batch_id=batch_id, org_id=_require_org(current_user))


@router.post("/batches/{batch_id}/items/{item_id}/decision", response_model=OCRImportItemResponse)
async def record_decision(
    batch_id: UUID,
    item_id: UUID,
    payload: OCRReviewDecisionRequest,
    current_user: UserProfile = Depends(require_role(Role.ADMIN, Role.DESIGNER)),
    service: OCROnboardingService = Depends(get_service),
):
    return await service.record_decision(
        batch_id=batch_id,
        item_id=item_id,
        org_id=_require_org(current_user),
        decided_by=current_user.id,
        action=payload.action,
        payload=payload.payload,
    )


@router.post("/batches/{batch_id}/bulk-accept", response_model=OCRBulkAcceptResponse)
async def bulk_accept(
    batch_id: UUID,
    payload: OCRBulkAcceptRequest,
    current_user: UserProfile = Depends(require_role(Role.ADMIN, Role.DESIGNER)),
    service: OCROnboardingService = Depends(get_service),
):
    return await service.bulk_accept(
        batch_id=batch_id,
        org_id=_require_org(current_user),
        decided_by=current_user.id,
        item_ids=payload.item_ids,
    )


@router.post("/batches/{batch_id}/items/{item_id}/retry", response_model=OCRImportItemResponse)
async def retry_item(
    batch_id: UUID,
    item_id: UUID,
    current_user: UserProfile = Depends(require_role(Role.ADMIN, Role.DESIGNER)),
    service: OCROnboardingService = Depends(get_service),
):
    return await service.retry_item(
        batch_id=batch_id,
        item_id=item_id,
        org_id=_require_org(current_user),
        decided_by=current_user.id,
    )


@router.post("/batches/{batch_id}/duplicates/{candidate_id}/resolve")
async def resolve_duplicate(
    batch_id: UUID,
    candidate_id: UUID,
    payload: OCRDuplicateResolveRequest,
    current_user: UserProfile = Depends(require_role(Role.ADMIN, Role.DESIGNER)),
    service: OCROnboardingService = Depends(get_service),
):
    return await service.resolve_duplicate(
        candidate_id=candidate_id,
        batch_id=batch_id,
        org_id=_require_org(current_user),
        decided_by=current_user.id,
        decision=payload.decision,
    )
