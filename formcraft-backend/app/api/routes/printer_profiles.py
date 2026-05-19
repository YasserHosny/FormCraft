"""Printer profile management routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response
from weasyprint import HTML

from app.api.deps import get_current_user, require_role
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.print_settings import PrinterProfileCreate, PrinterProfileUpdate, PrinterProfileResponse
from app.services.printer_profile_service import PrinterProfileService

router = APIRouter(prefix="/printer-profiles", tags=["Printer Profiles"])


@router.post("", status_code=201)
async def create_profile(
    body: PrinterProfileCreate,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    client = get_supabase_client()
    service = PrinterProfileService(client)
    profile = await service.create_profile(
        body.model_dump(), current_user.org_id, current_user.id
    )
    return profile


@router.get("")
async def list_profiles(
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    include_inactive: bool = Query(False),
):
    client = get_supabase_client()
    service = PrinterProfileService(client)
    items = await service.list_profiles(current_user.org_id, include_inactive)
    return {"items": items, "total": len(items)}


@router.patch("/{profile_id}")
async def update_profile(
    profile_id: UUID,
    body: PrinterProfileUpdate,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    client = get_supabase_client()
    service = PrinterProfileService(client)
    return await service.update_profile(profile_id, body.model_dump(exclude_none=True), current_user.org_id)


@router.delete("/{profile_id}")
async def delete_profile(
    profile_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    client = get_supabase_client()
    service = PrinterProfileService(client)
    return await service.delete_profile(profile_id, current_user.org_id)


@router.post("/{profile_id}/set-default")
async def set_default(
    profile_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    client = get_supabase_client()
    service = PrinterProfileService(client)
    return await service.set_default(profile_id, current_user.org_id)


@router.post("/{profile_id}/calibration-page")
async def calibration_page(
    profile_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    client = get_supabase_client()
    service = PrinterProfileService(client)

    result = (
        client.table("printer_profiles")
        .select("x_offset_mm, y_offset_mm")
        .eq("id", str(profile_id))
        .single()
        .execute()
    )
    if not result.data:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Profile not found")

    html_str = service.generate_calibration_page(
        float(result.data["x_offset_mm"]),
        float(result.data["y_offset_mm"]),
    )
    pdf_bytes = HTML(string=html_str).write_pdf()
    return Response(content=pdf_bytes, media_type="application/pdf")
