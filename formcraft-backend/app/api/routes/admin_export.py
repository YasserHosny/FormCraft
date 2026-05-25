from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from app.api.deps import require_role
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.export import (
    ExportDownloadRequest,
    ExportHistoryResponse,
    ExportPreviewRequest,
    ExportPreviewResponse,
    ExportSchedule,
    ExportScheduleCreate,
    ExportScheduleListResponse,
    ExportScheduleUpdate,
)
from app.services.export_service import ExportService

router = APIRouter(prefix="/export", tags=["Data Export"])


@router.get("/health")
async def export_health(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    """Placeholder endpoint for F32 export route registration."""
    return {"status": "ok", "org_id": str(current_user.org_id) if current_user.org_id else None}


@router.post("/preview", response_model=ExportPreviewResponse)
async def preview_export(
    request: ExportPreviewRequest,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    service = ExportService(get_supabase_client())
    return await service.preview_submissions(current_user.org_id, current_user.id, request)


@router.post("/download")
async def download_export(
    request: ExportDownloadRequest,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    service = ExportService(get_supabase_client())
    content, media_type, file_name = await service.download_submissions(
        current_user.org_id,
        current_user.id,
        request,
    )
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )


@router.get("/history", response_model=ExportHistoryResponse)
async def export_history(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
):
    service = ExportService(get_supabase_client())
    items, total = await service.list_history(current_user.org_id, page, page_size)
    return ExportHistoryResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/schedules", response_model=ExportScheduleListResponse)
async def list_schedules(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    service = ExportService(get_supabase_client())
    items = await service.list_schedules(current_user.org_id)
    return ExportScheduleListResponse(items=items)


@router.post("/schedules", response_model=ExportSchedule)
async def create_schedule(
    request: ExportScheduleCreate,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    service = ExportService(get_supabase_client())
    result = await service.create_schedule(
        current_user.org_id, current_user.id, request.model_dump(mode="json")
    )
    return ExportSchedule(**result)


@router.patch("/schedules/{schedule_id}", response_model=ExportSchedule)
async def update_schedule(
    schedule_id: str,
    request: ExportScheduleUpdate,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    from uuid import UUID
    service = ExportService(get_supabase_client())
    result = await service.update_schedule(
        current_user.org_id,
        UUID(schedule_id),
        current_user.id,
        request.model_dump(mode="json", exclude_none=True),
    )
    return ExportSchedule(**result)


@router.post("/schedules/{schedule_id}/run-now")
async def run_schedule_now(
    schedule_id: str,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    from uuid import UUID
    service = ExportService(get_supabase_client())
    return await service.run_schedule_now(
        current_user.org_id, UUID(schedule_id), current_user.id
    )


@router.get("/deliveries")
async def list_deliveries(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
    schedule_id: str | None = None,
):
    from uuid import UUID
    service = ExportService(get_supabase_client())
    schedule_uuid = UUID(schedule_id) if schedule_id else None
    items = await service.list_deliveries(current_user.org_id, schedule_uuid)
    return {"items": items}
