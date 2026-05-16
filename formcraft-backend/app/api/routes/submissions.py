import io
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import StreamingResponse, JSONResponse

from app.api.deps import get_current_user
from app.core.audit import AuditLogger
from app.core.supabase import get_supabase_client
from app.models.user import UserProfile
from app.schemas.submission import (
    CreateSubmissionRequest,
    SubmissionResponse,
    SubmissionListResponse,
    SubmissionListItem,
    SubmissionDetailResponse,
    ReprintResponse,
)
from app.services.submission_service import SubmissionService

router = APIRouter(prefix="/submissions", tags=["Submissions"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=SubmissionResponse)
async def create_submission(
    body: CreateSubmissionRequest,
    request: Request,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    client = get_supabase_client()
    service = SubmissionService(client)

    submission = await service.create_submission(
        template_id=body.template_id,
        template_version=body.template_version,
        field_values=body.field_values,
        operator_id=current_user.id,
        org_id=current_user.org_id,
    )

    audit = AuditLogger(client)
    await audit.log_event(
        user_id=str(current_user.id),
        action="FORM_SUBMITTED",
        resource_type="submission",
        resource_id=str(submission.id),
        metadata={
            "template_id": str(body.template_id),
            "template_version": body.template_version,
            "reference_number": submission.reference_number,
        },
        ip_address=request.client.host if request.client else None,
    )

    return submission


@router.get("", response_model=SubmissionListResponse)
async def list_submissions(
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    search: str | None = Query(None, alias="search"),
    template_id: UUID | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_dir: str = Query("desc"),
    scope: str = Query("own"),
):
    client = get_supabase_client()
    service = SubmissionService(client)
    items, total = await service.list_submissions(
        operator_id=current_user.id,
        org_id=current_user.id,
        search=search,
        template_id=template_id,
        status_filter=status_filter,
        date_from=date_from,
        date_to=date_to,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_dir=sort_dir,
        scope=scope,
    )
    submission_items = [SubmissionListItem(**item) for item in items]
    return SubmissionListResponse(
        items=submission_items,
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/{submission_id}", response_model=SubmissionDetailResponse)
async def get_submission(
    submission_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    client = get_supabase_client()
    service = SubmissionService(client)
    data = await service.get_submission(submission_id, org_id=current_user.id)
    if not data:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Submission not found")
    return SubmissionDetailResponse(**data)


@router.post("/{submission_id}/reprint", response_class=StreamingResponse)
async def reprint_submission(
    submission_id: UUID,
    request: Request,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    from fastapi import HTTPException

    client = get_supabase_client()
    service = SubmissionService(client)

    data = await service.get_submission(submission_id, org_id=current_user.id)
    if not data:
        raise HTTPException(status_code=404, detail="Submission not found")

    from app.services.pdf.renderer import render_reprint_pdf

    field_values = data.get("field_values", {})
    template_id = data["template_id"]

    try:
        template_result = (
            client.table("templates")
            .select("id, name, version, country")
            .eq("id", str(template_id))
            .single()
            .execute()
        )
        template_data = template_result.data if template_result.data else {}
    except Exception:
        template_data = {}

    pdf_bytes = await render_reprint_pdf(
        client=client,
        template_id=str(template_id),
        field_values=field_values,
        reference_number=data["reference_number"],
        original_date=data["created_at"],
    )

    audit = AuditLogger(client)
    await audit.log_event(
        user_id=str(current_user.id),
        action="FORM_REPRINTED",
        resource_type="submission",
        resource_id=str(submission_id),
        metadata={
            "reference_number": data["reference_number"],
            "template_id": str(template_id),
        },
        ip_address=request.client.host if request.client else None,
    )

    filename = f"{data['reference_number']}-reprint.pdf"
    headers = {
        "Content-Disposition": f'inline; filename="{filename}"',
        "Content-Type": "application/pdf",
    }
    return StreamingResponse(io.BytesIO(pdf_bytes), headers=headers)


@router.get("/{submission_id}/export")
async def export_submission(
    submission_id: UUID,
    format: str = Query("json", regex="^(json|csv)$"),
    request: Request = None,
    current_user: Annotated[UserProfile, Depends(get_current_user)] = None,
):
    from fastapi import HTTPException

    client = get_supabase_client()
    service = SubmissionService(client)

    data = await service.get_submission(submission_id, org_id=current_user.id)
    if not data:
        raise HTTPException(status_code=404, detail="Submission not found")

    export_data = await service.export_submission(submission_id, fmt=format)

    ref = data["reference_number"]

    audit = AuditLogger(client)
    await audit.log_event(
        user_id=str(current_user.id),
        action="SUBMISSION_EXPORTED",
        resource_type="submission",
        resource_id=str(submission_id),
        metadata={"format": format, "reference_number": ref},
        ip_address=request.client.host if request and request.client else None,
    )

    if format == "csv":
        from fastapi.responses import Response
        return Response(
            content=export_data,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{ref}.csv"'},
        )

    return JSONResponse(
        content=export_data,
        headers={"Content-Disposition": f'attachment; filename="{ref}.json"'},
    )