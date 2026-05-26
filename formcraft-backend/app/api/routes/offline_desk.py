from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user
from app.core.supabase import get_supabase_client
from app.models.user import UserProfile
from app.schemas.offline_desk import (
    DeviceResponse,
    OfflineManifestResponse,
    RegisterDeviceRequest,
    ResolveConflictRequest,
    ResolveConflictResponse,
    RevokeDeviceRequest,
    RevokeDeviceResponse,
    SyncRequest,
    SyncResponse,
)
from app.services.offline_desk_service import OfflineDeskService

router = APIRouter(prefix="/offline-desk", tags=["Offline Desk"])


def get_offline_desk_service() -> OfflineDeskService:
    return OfflineDeskService(get_supabase_client())


@router.post("/devices", status_code=status.HTTP_201_CREATED, response_model=DeviceResponse)
async def register_device(
    payload: RegisterDeviceRequest,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    service: Annotated[OfflineDeskService, Depends(get_offline_desk_service)],
):
    return await service.register_device(payload, current_user)


@router.get("/packages/manifest", response_model=OfflineManifestResponse)
async def get_manifest(
    device_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    service: Annotated[OfflineDeskService, Depends(get_offline_desk_service)],
):
    return await service.get_manifest(device_id, current_user)


@router.post("/sync", status_code=status.HTTP_202_ACCEPTED, response_model=SyncResponse)
async def sync(
    payload: SyncRequest,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    service: Annotated[OfflineDeskService, Depends(get_offline_desk_service)],
):
    return await service.sync(payload, current_user)


@router.post("/conflicts/{conflict_id}/resolve", response_model=ResolveConflictResponse)
async def resolve_conflict(
    conflict_id: UUID,
    payload: ResolveConflictRequest,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    service: Annotated[OfflineDeskService, Depends(get_offline_desk_service)],
):
    return await service.resolve_conflict(conflict_id, payload.resolution, current_user)


@router.post("/devices/{device_id}/revoke", response_model=RevokeDeviceResponse)
async def revoke_device(
    device_id: UUID,
    payload: RevokeDeviceRequest,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    service: Annotated[OfflineDeskService, Depends(get_offline_desk_service)],
):
    return await service.revoke_device(device_id, current_user, payload.reason)
