from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.core.report_permissions import can_schedule_reports
from app.schemas.report import (
    PaginatedResponse,
    ReportScheduleCreate,
    ReportScheduleResponse,
    ReportScheduleUpdate,
)
from app.services.reports.report_scheduler import ReportSchedulerService

router = APIRouter(prefix="/reports/schedules", tags=["report-schedules"])

async def get_current_user(request: Request):
    return getattr(request.state, "user", {})

async def get_supabase(request: Request):
    return getattr(request.state, "supabase", None)


@router.get("", response_model=PaginatedResponse)
async def list_schedules(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    is_active: bool | None = None,
    report_type: str | None = None,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
):
    if not can_schedule_reports(user.get("role", "")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    # Placeholder: integrate with schedule query service
    return PaginatedResponse(data=[], pagination={"page": page, "page_size": page_size, "total_count": 0, "total_pages": 0})


@router.post("", response_model=ReportScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    request: Request,
    body: ReportScheduleCreate,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
):
    if not can_schedule_reports(user.get("role", "")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    scheduler = ReportSchedulerService()
    next_run = scheduler.compute_next_run(
        frequency=body.frequency.value,
        schedule_time=body.schedule_time,
        day_of_week=body.day_of_week,
        day_of_month=body.day_of_month,
    )

    # Placeholder: persist to DB and add to scheduler
    return ReportScheduleResponse(
        id=UUID(int=0),
        org_id=user.get("org_id"),
        report_template_id=body.report_template_id,
        frequency=body.frequency,
        schedule_time=body.schedule_time,
        day_of_week=body.day_of_week,
        day_of_month=body.day_of_month,
        recipients=body.recipients,
        export_format=body.export_format,
        no_data_behavior=body.no_data_behavior,
        is_active=body.is_active,
        next_run_at=next_run.isoformat(),
        last_status="pending",
        created_by=user.get("id"),
        created_at="",
        updated_at="",
    )


@router.patch("/{schedule_id}", response_model=ReportScheduleResponse)
async def update_schedule(
    request: Request,
    schedule_id: UUID,
    body: ReportScheduleUpdate,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
):
    if not can_schedule_reports(user.get("role", "")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    # Placeholder: update DB record and reschedule if needed
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Update not yet implemented")


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    request: Request,
    schedule_id: UUID,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
):
    if not can_schedule_reports(user.get("role", "")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    # Placeholder: soft-delete or hard-delete
    return None


@router.post("/{schedule_id}/run-now")
async def run_schedule_now(
    request: Request,
    schedule_id: UUID,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
):
    if not can_schedule_reports(user.get("role", "")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    job_id = UUID(int=0)
    return {"job_id": str(job_id), "message": "Report generation started"}


@router.get("/{schedule_id}/history", response_model=PaginatedResponse)
async def get_schedule_history(
    request: Request,
    schedule_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    status_filter: str | None = None,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
):
    if not can_schedule_reports(user.get("role", "")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    return PaginatedResponse(data=[], pagination={"page": page, "page_size": page_size, "total_count": 0, "total_pages": 0})
