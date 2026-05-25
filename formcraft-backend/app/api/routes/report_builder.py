from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.report_permissions import can_access_report
from app.schemas.report import CustomReportPreviewRequest, CustomReportSaveRequest

router = APIRouter(prefix="/reports/custom", tags=["report-builder"])

async def get_current_user(request: Request):
    return getattr(request.state, "user", {})


@router.post("/preview")
async def preview_custom_report(
    request: Request,
    body: CustomReportPreviewRequest,
    user: dict = Depends(get_current_user),
):
    if not can_access_report(user.get("role", ""), "custom"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    # Placeholder: integrate with custom builder service
    return {
        "columns": [{"key": "branch_name", "label": "Branch", "type": "text"}],
        "rows": [],
        "total_matching": 0,
        "preview_limited": True,
    }


@router.post("/save")
async def save_custom_report(
    request: Request,
    body: CustomReportSaveRequest,
    user: dict = Depends(get_current_user),
):
    if not can_access_report(user.get("role", ""), "custom"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    # Placeholder: integrate with report template service
    return {"id": "placeholder", **body.model_dump()}
