"""Analytics API routes for F040 Enhanced Analytics Dashboard."""

import logging
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from supabase import Client

from app.api.deps import get_current_user
from app.core.supabase import get_supabase_client
from app.models.user import UserProfile as User
from app.schemas.analytics import (
    BusiestHoursResponse,
    ComplianceScorecardResponse,
    ExportRequest,
    ExportResponse,
    FieldAnalyticsResponse,
    OperatorAnalyticsResponse,
    TemplatesNeedingAttentionResponse,
    TemplateUsageResponse,
    VersionAdoptionResponse,
)
from app.services.analytics.compliance_analytics import ComplianceAnalyticsService
from app.services.analytics.export_service import AnalyticsExportService
from app.services.analytics.field_analytics import FieldAnalyticsService
from app.services.analytics.operator_analytics import OperatorAnalyticsService
from app.services.analytics.template_analytics import TemplateAnalyticsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/fields", response_model=FieldAnalyticsResponse)
async def get_field_analytics(
    template_id: UUID,
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
    current_user: User = Depends(get_current_user),
    client: Client = Depends(get_supabase_client),
) -> FieldAnalyticsResponse:
    """Return field-level analytics for a specific template."""
    service = FieldAnalyticsService(client)
    return await service.get_field_analytics(
        org_id=current_user.org_id,
        template_id=template_id,
        from_date=from_date,
        to_date=to_date,
    )


@router.get("/operators", response_model=OperatorAnalyticsResponse)
async def get_operator_analytics(
    period_type: str = Query("week", enum=["day", "week", "month"]),
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
    branch_id: UUID | None = None,
    current_user: User = Depends(get_current_user),
    client: Client = Depends(get_supabase_client),
) -> OperatorAnalyticsResponse:
    """Return operator-level performance analytics."""
    service = OperatorAnalyticsService(client)
    return await service.get_operator_analytics(
        org_id=current_user.org_id,
        period_type=period_type,
        from_date=from_date,
        to_date=to_date,
        branch_id=branch_id,
    )


@router.get("/operators/busiest-hours", response_model=BusiestHoursResponse)
async def get_busiest_hours(
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
    branch_id: UUID | None = None,
    current_user: User = Depends(get_current_user),
    client: Client = Depends(get_supabase_client),
) -> BusiestHoursResponse:
    """Return submission volume heatmap by hour and day of week."""
    service = OperatorAnalyticsService(client)
    return await service.get_busiest_hours(
        org_id=current_user.org_id,
        from_date=from_date,
        to_date=to_date,
        branch_id=branch_id,
    )


@router.get("/compliance", response_model=ComplianceScorecardResponse)
async def get_compliance_scorecard(
    current_user: User = Depends(get_current_user),
    client: Client = Depends(get_supabase_client),
) -> ComplianceScorecardResponse:
    """Return organizational compliance scorecard (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required for compliance analytics",
        )
    service = ComplianceAnalyticsService(client)
    return await service.get_compliance_scorecard(org_id=current_user.org_id)


@router.get("/compliance/templates-needing-attention", response_model=TemplatesNeedingAttentionResponse)
async def get_templates_needing_attention(
    current_user: User = Depends(get_current_user),
    client: Client = Depends(get_supabase_client),
) -> TemplatesNeedingAttentionResponse:
    """Return list of non-compliant templates (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    service = ComplianceAnalyticsService(client)
    return await service.get_templates_needing_attention(org_id=current_user.org_id)


@router.get("/templates/usage", response_model=TemplateUsageResponse)
async def get_template_usage(
    template_id: UUID | None = None,
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
    group_by: str | None = Query(None, enum=["department", "branch"]),
    current_user: User = Depends(get_current_user),
    client: Client = Depends(get_supabase_client),
) -> TemplateUsageResponse:
    """Return template usage funnel and optional department/branch breakdown."""
    service = TemplateAnalyticsService(client)
    return await service.get_template_usage(
        org_id=current_user.org_id,
        template_id=template_id,
        from_date=from_date,
        to_date=to_date,
        group_by=group_by,
    )


@router.get("/templates/version-adoption", response_model=VersionAdoptionResponse)
async def get_version_adoption(
    template_id: UUID,
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
    current_user: User = Depends(get_current_user),
    client: Client = Depends(get_supabase_client),
) -> VersionAdoptionResponse:
    """Return version adoption timeline for a template."""
    service = TemplateAnalyticsService(client)
    return await service.get_version_adoption(
        org_id=current_user.org_id,
        template_id=template_id,
        from_date=from_date,
        to_date=to_date,
    )


@router.post("/export", response_model=ExportResponse)
async def export_analytics(
    request: ExportRequest,
    current_user: User = Depends(get_current_user),
    client: Client = Depends(get_supabase_client),
) -> ExportResponse:
    """Export analytics report in CSV, PNG, or PDF format."""
    service = AnalyticsExportService(client.storage)
    result = await service.generate_export(
        org_id=current_user.org_id,
        request=request,
    )
    return ExportResponse(**result)
