from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.core.report_permissions import can_access_report
from app.models.enums import Role
from app.schemas.report import (
    ExportAsyncResponse,
    ExportLimitExceededResponse,
    ExportSuccessResponse,
    PaginatedResponse,
    TransactionExportRequest,
)
from app.services.reports.report_exporter import ReportExporter
from app.services.reports.transaction_register import TransactionRegisterService

router = APIRouter(prefix="/reports", tags=["reports"])

# Dependency helpers (simplified; integrate with actual auth system)
async def get_current_user(request: Request):
    return getattr(request.state, "user", {})

async def get_supabase(request: Request):
    return getattr(request.state, "supabase", None)


@router.get("/transactions", response_model=PaginatedResponse)
async def get_transactions(
    request: Request,
    template_id: UUID | None = None,
    date_from: date = Query(...),
    date_to: date = Query(...),
    branch_id: UUID | None = None,
    department_id: UUID | None = None,
    operator_id: UUID | None = None,
    status: str | None = None,
    customer_query: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    sort_by: str = "created_at",
    sort_dir: str = "desc",
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
):
    if not can_access_report(user.get("role", ""), "transaction_register"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    # Apply branch scope for branch managers
    if user.get("role") == Role.BRANCH_MANAGER and user.get("branch_id"):
        branch_id = user.get("branch_id")

    service = TransactionRegisterService(supabase)
    rows, total_count = await service.query(
        org_id=user.get("org_id"),
        date_from=date_from,
        date_to=date_to,
        template_id=template_id,
        branch_id=branch_id,
        department_id=department_id,
        operator_id=operator_id,
        status=status,
        customer_query=customer_query,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )

    total_pages = (total_count + page_size - 1) // page_size
    return PaginatedResponse(
        data=rows,
        pagination={
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
        },
    )


@router.post("/transactions/export")
async def export_transactions(
    request: Request,
    body: TransactionExportRequest,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
):
    if not can_access_report(user.get("role", ""), "transaction_register"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    filters = body.filters
    if user.get("role") == Role.BRANCH_MANAGER and user.get("branch_id"):
        filters.branch_id = user.get("branch_id")

    service = TransactionRegisterService(supabase)
    record_count = await service.count(
        org_id=user.get("org_id"),
        date_from=filters.date_from,
        date_to=filters.date_to,
        template_id=filters.template_id,
        branch_id=filters.branch_id,
        department_id=filters.department_id,
        operator_id=filters.operator_id,
        status=filters.status,
        customer_query=filters.customer_query,
    )

    if record_count > 100_000:
        return ExportLimitExceededResponse(
            message=f"Selected filters match {record_count:,} records. Maximum is 100,000. Please narrow your filters.",
            record_count=record_count,
            max_allowed=100_000,
        )

    exporter = ReportExporter(supabase)

    if record_count >= 10_000:
        job_id = exporter.create_job(filters.model_dump(), body.format.value)
        # In production, offload to background task
        return ExportAsyncResponse(
            job_id=job_id,
            status="generating",
            estimated_seconds=max(15, record_count // 500),
        )

    rows = await service.fetch_all(
        org_id=user.get("org_id"),
        date_from=filters.date_from,
        date_to=filters.date_to,
        template_id=filters.template_id,
        branch_id=filters.branch_id,
        department_id=filters.department_id,
        operator_id=filters.operator_id,
        status=filters.status,
        customer_query=filters.customer_query,
    )

    columns = [
        {"key": "reference_number", "label": "Reference Number"},
        {"key": "template_name", "label": "Template"},
        {"key": "operator_name", "label": "Operator"},
        {"key": "customer_name", "label": "Customer"},
        {"key": "created_at", "label": "Date"},
        {"key": "status", "label": "Status"},
    ]

    file_bytes = exporter.generate_file(columns, rows, body.format.value, title="Transaction Register")
    file_name = f"transactions_{date.today().isoformat()}.{body.format.value}"
    file_path = await exporter.upload_to_storage(file_bytes, file_name, str(user.get("org_id")))

    # Create archive record (simplified)
    archive_id = UUID(int=0)  # Placeholder
    return ExportSuccessResponse(
        download_url=file_path,
        file_name=file_name,
        record_count=record_count,
        archive_id=archive_id,
    )


@router.get("/reconciliation")
async def get_reconciliation(
    request: Request,
    report_date: date = Query(..., alias="date"),
    branch_id: UUID | None = None,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
):
    if not can_access_report(user.get("role", ""), "daily_reconciliation"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    if user.get("role") == Role.BRANCH_MANAGER and user.get("branch_id"):
        branch_id = user.get("branch_id")

    # Placeholder: integrate with reconciliation service
    return {
        "date": report_date.isoformat(),
        "branch": {"id": str(branch_id), "name": "Branch", "name_ar": "الفرع"},
        "summary": {"total_submissions": 0, "total_amount": 0.0, "template_breakdown": []},
        "operators": [],
    }


@router.get("/period-summary")
async def get_period_summary(
    request: Request,
    period: str = Query(...),
    group_by: str = Query(...),
    date_from: date | None = None,
    compare: bool = Query(True),
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
):
    if not can_access_report(user.get("role", ""), "period_summary"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    # Placeholder: integrate with period summary service
    return {
        "period": period,
        "current": {"from": "", "to": ""},
        "previous": {"from": "", "to": ""},
        "groups": [],
    }


@router.get("/financial/beneficiary")
async def get_beneficiary_report(
    request: Request,
    date_from: date = Query(...),
    date_to: date = Query(...),
    beneficiary_query: str | None = None,
    template_id: UUID | None = None,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
):
    if not can_access_report(user.get("role", ""), "beneficiary"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    return {"data": [], "total_count": 0}


@router.get("/financial/void-reprint")
async def get_void_reprint_report(
    request: Request,
    date_from: date = Query(...),
    date_to: date = Query(...),
    branch_id: UUID | None = None,
    min_reprint_count: int = Query(1),
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
):
    if not can_access_report(user.get("role", ""), "void_reprint"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    return {"data": [], "total_count": 0}


@router.get("/financial/signatory-usage")
async def get_signatory_usage_report(
    request: Request,
    date_from: date = Query(...),
    date_to: date = Query(...),
    signatory_id: UUID | None = None,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
):
    if not can_access_report(user.get("role", ""), "signatory_usage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    return {"data": [], "total_count": 0}


@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: UUID,
    supabase = Depends(get_supabase),
):
    exporter = ReportExporter(supabase)
    job = exporter.get_job(str(job_id))
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.get("/archives", response_model=PaginatedResponse)
async def get_archives(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    report_type: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase),
):
    if not can_access_report(user.get("role", ""), "archives"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    # Placeholder: integrate with archive query service
    return PaginatedResponse(data=[], pagination={"page": page, "page_size": page_size, "total_count": 0, "total_pages": 0})
