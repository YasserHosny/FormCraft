from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse, PlainTextResponse

from app.schemas.batch import (
    BatchJobResponse,
    BatchJobSummary,
    BatchScheduleCreateRequest,
    BatchScheduleUpdateRequest,
    BatchScheduleResponse,
    BatchValidationRequest,
    BatchValidationResult,
)
from app.services.batch_schedule_service import BatchScheduleService
from app.services.batch_service import BatchService

router = APIRouter(prefix="/batch-jobs", tags=["batch-jobs"])
schedule_router = APIRouter(prefix="/batch-schedules", tags=["batch-schedules"])


async def get_current_user(request: Request):
    return getattr(request.state, "user", {})


async def get_supabase(request: Request):
    return getattr(request.state, "supabase", None)


async def get_batch_service():
    return BatchService()


async def get_schedule_service():
    return BatchScheduleService()


# ---------------------------------------------------------------------------
# Batch Jobs
# ---------------------------------------------------------------------------

@router.get("", response_model=dict)
async def list_batch_jobs(
    request: Request,
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
    service: BatchService = Depends(get_batch_service),
):
    org_id = user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No org context")

    jobs, total = await service.list_jobs(
        org_id=UUID(org_id),
        status=status_filter,
        limit=limit,
        offset=offset,
        supabase_client=supabase,
    )

    return {
        "items": [
            BatchJobSummary(
                id=j.id,
                name=j.name,
                status=j.status,
                row_count=j.row_count,
                success_count=j.success_count,
                fail_count=j.fail_count,
                progress=j.progress,
                created_at=j.created_at,
                updated_at=j.updated_at,
            )
            for j in jobs
        ],
        "total": total,
    }


@router.post("", response_model=BatchJobResponse, status_code=status.HTTP_201_CREATED)
async def create_batch_job(
    request: Request,
    name: str = Form(...),
    template_id: UUID = Form(...),
    data_source_type: str = Form(...),
    column_mapping: str = Form("{}"),
    duplicate_strategy: str = Form("warn"),
    download_format: str = Form("zip"),
    printer_profile_id: UUID | None = Form(None),
    file: UploadFile | None = File(None),
    clipboard_data: str | None = Form(None),
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
    service: BatchService = Depends(get_batch_service),
):
    org_id = user.get("org_id")
    created_by = user.get("id")
    if not org_id or not created_by:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No user context")

    # Fetch template version (placeholder)
    template_version = 1

    if data_source_type in ("csv", "xlsx"):
        if not file:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="File required")
        content = await file.read()
        file_name = file.filename or "upload"
        mime_type = file.content_type or "application/octet-stream"
    elif data_source_type == "clipboard":
        if clipboard_data is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Clipboard data required")
        content = clipboard_data
        file_name = "clipboard.txt"
        mime_type = "text/plain"
    else:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid data_source_type")

    import json
    parsed_mapping = json.loads(column_mapping)

    job = await service.create_job(
        org_id=UUID(org_id),
        created_by=UUID(created_by),
        name=name,
        template_id=template_id,
        template_version=template_version,
        data_source_type=data_source_type,
        data_source_content=content,
        file_name=file_name,
        mime_type=mime_type,
        column_mapping=parsed_mapping,
        duplicate_strategy=duplicate_strategy,
        download_format=download_format,
        printer_profile_id=printer_profile_id,
        supabase_client=supabase,
    )

    return _job_to_response(job)


@router.get("/{job_id}", response_model=BatchJobResponse)
async def get_batch_job(
    job_id: UUID,
    request: Request,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
    service: BatchService = Depends(get_batch_service),
):
    job = await service.get_job(job_id, supabase)
    return _job_to_response(job)


@router.post("/{job_id}/validate", response_model=BatchValidationResult)
async def validate_batch_job(
    job_id: UUID,
    payload: BatchValidationRequest,
    request: Request,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
    service: BatchService = Depends(get_batch_service),
):
    results, duplicate_count = await service.validate_job(
        job_id=job_id,
        column_mapping=payload.column_mapping,
        duplicate_strategy=payload.duplicate_strategy,
        supabase_client=supabase,
    )

    valid_rows = sum(1 for r in results if r["status"] == "valid")
    invalid_rows = sum(1 for r in results if r["status"] == "invalid")

    return BatchValidationResult(
        total_rows=len(results),
        valid_rows=valid_rows,
        invalid_rows=invalid_rows,
        duplicate_rows=duplicate_count,
        rows=results,
    )


@router.post("/{job_id}/start", response_model=BatchJobResponse)
async def start_batch_job(
    job_id: UUID,
    request: Request,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
    service: BatchService = Depends(get_batch_service),
):
    await service.start_job(job_id, supabase)
    job = await service.get_job(job_id, supabase)
    return _job_to_response(job)


@router.post("/{job_id}/cancel", response_model=BatchJobResponse)
async def cancel_batch_job(
    job_id: UUID,
    request: Request,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
    service: BatchService = Depends(get_batch_service),
):
    cancelled_by = user.get("id")
    if not cancelled_by:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No user context")
    await service.cancel_job(job_id, UUID(cancelled_by), supabase)
    job = await service.get_job(job_id, supabase)
    return _job_to_response(job)


@router.get("/{job_id}/download")
async def download_batch_results(
    job_id: UUID,
    request: Request,
    format: str = Query(..., regex="^(zip|merged_pdf)$"),
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
    service: BatchService = Depends(get_batch_service),
):
    job = await service.get_job(job_id, supabase)
    if job.status not in ("completed", "cancelled"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Results not available")

    # Placeholder: return empty zip
    from io import BytesIO
    buffer = BytesIO()
    import zipfile
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("placeholder.txt", "Batch results placeholder")
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="batch_{job_id}.zip"'},
    )


@router.get("/{job_id}/errors", response_class=PlainTextResponse)
async def download_error_report(
    job_id: UUID,
    request: Request,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
    service: BatchService = Depends(get_batch_service),
):
    csv_content = await service.generate_error_report_csv(job_id, supabase)
    return PlainTextResponse(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="batch_{job_id}_errors.csv"'},
    )


# ---------------------------------------------------------------------------
# Batch Schedules
# ---------------------------------------------------------------------------

@schedule_router.get("", response_model=list[BatchScheduleResponse])
async def list_batch_schedules(
    request: Request,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
):
    org_id = user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No org context")

    result = await supabase.table("batch_schedules").select("*").eq("org_id", org_id).order("created_at", desc=True).execute()
    schedules = result.data or []
    return [
        BatchScheduleResponse(
            id=s["id"],
            name=s["name"],
            enabled=s["enabled"],
            template_id=s["template_id"],
            cron_expression=s["cron_expression"],
            next_run_at=s.get("next_run_at"),
            last_run_status=s.get("last_run_status"),
            last_run_at=s.get("last_run_at"),
            last_run_job_id=s.get("last_run_job_id"),
            failure_count=s.get("failure_count", 0),
            created_at=s["created_at"],
            updated_at=s["updated_at"],
        )
        for s in schedules
    ]


@schedule_router.post("", response_model=BatchScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_batch_schedule(
    payload: BatchScheduleCreateRequest,
    request: Request,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
    schedule_service: BatchScheduleService = Depends(get_schedule_service),
):
    org_id = user.get("org_id")
    created_by = user.get("id")
    if not org_id or not created_by:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No user context")

    next_run = schedule_service.compute_next_run(payload.cron_expression)

    data = {
        "id": str(__import__("uuid").uuid4()),
        "org_id": org_id,
        "template_id": str(payload.template_id),
        "created_by": created_by,
        "name": payload.name,
        "enabled": payload.enabled,
        "api_endpoint": payload.api_endpoint,
        "api_auth_type": payload.api_auth_type,
        "api_auth_credential": payload.api_auth_credential,
        "api_headers": payload.api_headers,
        "cron_expression": payload.cron_expression,
        "notification_recipients": payload.notification_recipients,
        "column_mapping": payload.column_mapping,
        "download_format": payload.download_format,
        "printer_profile_id": str(payload.printer_profile_id) if payload.printer_profile_id else None,
        "max_rows_per_run": payload.max_rows_per_run,
        "next_run_at": next_run.isoformat(),
        "created_at": __import__("datetime").datetime.utcnow().isoformat(),
        "updated_at": __import__("datetime").datetime.utcnow().isoformat(),
    }

    result = await supabase.table("batch_schedules").insert(data).execute()
    created = result.data[0] if result.data else data

    if payload.enabled:
        # Register with APScheduler
        # In production, schedule_service would be a singleton started at app startup
        pass

    return BatchScheduleResponse(
        id=created["id"],
        name=created["name"],
        enabled=created["enabled"],
        template_id=created["template_id"],
        cron_expression=created["cron_expression"],
        next_run_at=created.get("next_run_at"),
        last_run_status=created.get("last_run_status"),
        last_run_at=created.get("last_run_at"),
        last_run_job_id=created.get("last_run_job_id"),
        failure_count=created.get("failure_count", 0),
        created_at=created["created_at"],
        updated_at=created["updated_at"],
    )


@schedule_router.get("/{schedule_id}", response_model=BatchScheduleResponse)
async def get_batch_schedule(
    schedule_id: UUID,
    request: Request,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
):
    result = await supabase.table("batch_schedules").select("*").eq("id", str(schedule_id)).single().execute()
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    s = result.data
    return BatchScheduleResponse(
        id=s["id"],
        name=s["name"],
        enabled=s["enabled"],
        template_id=s["template_id"],
        cron_expression=s["cron_expression"],
        next_run_at=s.get("next_run_at"),
        last_run_status=s.get("last_run_status"),
        last_run_at=s.get("last_run_at"),
        last_run_job_id=s.get("last_run_job_id"),
        failure_count=s.get("failure_count", 0),
        created_at=s["created_at"],
        updated_at=s["updated_at"],
    )


@schedule_router.put("/{schedule_id}", response_model=BatchScheduleResponse)
async def update_batch_schedule(
    schedule_id: UUID,
    payload: BatchScheduleUpdateRequest,
    request: Request,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
    schedule_service: BatchScheduleService = Depends(get_schedule_service),
):
    org_id = user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No user context")

    update_data = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if "cron_expression" in update_data:
        update_data["next_run_at"] = schedule_service.compute_next_run(update_data["cron_expression"]).isoformat()

    update_data["updated_at"] = __import__("datetime").datetime.utcnow().isoformat()

    result = await supabase.table("batch_schedules").update(update_data).eq("id", str(schedule_id)).execute()
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    s = result.data[0]
    return BatchScheduleResponse(
        id=s["id"],
        name=s["name"],
        enabled=s["enabled"],
        template_id=s["template_id"],
        cron_expression=s["cron_expression"],
        next_run_at=s.get("next_run_at"),
        last_run_status=s.get("last_run_status"),
        last_run_at=s.get("last_run_at"),
        last_run_job_id=s.get("last_run_job_id"),
        failure_count=s.get("failure_count", 0),
        created_at=s["created_at"],
        updated_at=s["updated_at"],
    )


@schedule_router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_batch_schedule(
    schedule_id: UUID,
    request: Request,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
    schedule_service: BatchScheduleService = Depends(get_schedule_service),
):
    await supabase.table("batch_schedules").delete().eq("id", str(schedule_id)).execute()
    schedule_service.remove_schedule(schedule_id)
    return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _job_to_response(job) -> BatchJobResponse:
    return BatchJobResponse(
        id=job.id,
        name=job.name,
        status=job.status,
        template_id=job.template_id,
        template_version=job.template_version,
        data_source_type=job.data_source_type,
        column_mapping=job.column_mapping,
        row_count=job.row_count,
        success_count=job.success_count,
        fail_count=job.fail_count,
        progress=job.progress,
        duplicate_strategy=job.duplicate_strategy,
        duplicate_count=job.duplicate_count,
        download_format=job.download_format,
        printer_profile_id=job.printer_profile_id,
        scheduled_job_id=job.scheduled_job_id,
        started_at=job.started_at,
        completed_at=job.completed_at,
        cancelled_at=job.cancelled_at,
        error_summary=job.error_summary,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
