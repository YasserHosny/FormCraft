from io import BytesIO
from typing import Annotated
from uuid import UUID
from zipfile import ZipFile

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_user
from app.core.supabase import get_supabase_client
from app.models.user import UserProfile
from app.schemas.print_settings import PdfGenerationRequest
from app.services.pdf.renderer import render_template_pdf
from app.services.print_settings_service import PrintSettingsService
from app.services.template_service import TemplateService

router = APIRouter(prefix="/pdf", tags=["PDF"])


def _get_profile_offsets(client, profile_id: UUID) -> tuple[float, float]:
    result = (
        client.table("printer_profiles")
        .select("x_offset_mm, y_offset_mm")
        .eq("id", str(profile_id))
        .single()
        .execute()
    )
    row = result.data
    return (row["x_offset_mm"], row["y_offset_mm"]) if row else (0.0, 0.0)


@router.post("/render/{template_id}")
async def render_pdf(
    template_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    body: PdfGenerationRequest | None = None,
):
    client = get_supabase_client()
    service = TemplateService(client)
    template = await service.get_template(template_id)

    print_mode = "full"
    x_offset = 0.0
    y_offset = 0.0

    if body:
        if body.print_mode_override:
            print_mode = body.print_mode_override
        else:
            try:
                ps_service = PrintSettingsService(client)
                settings = await ps_service.get_settings(template_id)
                if settings:
                    print_mode = settings.get("print_mode", "full")
            except Exception:
                # print_settings table may not exist yet (migration pending)
                pass

        if body.printer_profile_id:
            try:
                x_offset, y_offset = _get_profile_offsets(client, body.printer_profile_id)
            except Exception:
                # printer_profiles table may not exist yet (migration pending)
                pass

    if print_mode == "both":
        buf = BytesIO()
        with ZipFile(buf, "w") as zf:
            full_pdf = render_template_pdf(template, overlay_mode=False)
            zf.writestr(f"{template['name']}_full.pdf", full_pdf)
            overlay_pdf = render_template_pdf(
                template, overlay_mode=True, x_offset_mm=x_offset, y_offset_mm=y_offset
            )
            zf.writestr(f"{template['name']}_overlay.pdf", overlay_pdf)
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{template["name"]}_prints.zip"'
            },
        )

    overlay_mode = print_mode == "overlay"
    pdf_bytes = render_template_pdf(
        template,
        overlay_mode=overlay_mode,
        x_offset_mm=x_offset,
        y_offset_mm=y_offset,
    )

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{template["name"]}.pdf"'
        },
    )


@router.get("/preview/{template_id}")
async def preview_pdf(
    template_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    client = get_supabase_client()
    service = TemplateService(client)
    template = await service.get_template(template_id)

    pdf_bytes = render_template_pdf(template)

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{template["name"]}.pdf"'
        },
    )
