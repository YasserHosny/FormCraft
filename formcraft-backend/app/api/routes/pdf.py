from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_user
from app.core.supabase import get_supabase_client
from app.models.user import UserProfile
from app.services.pdf.renderer import render_template_pdf
from app.services.template_service import TemplateService

router = APIRouter(prefix="/pdf", tags=["PDF"])


@router.post("/render/{template_id}")
async def render_pdf(
    template_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    """Render a template as a PDF and return it for download."""
    client = get_supabase_client()
    service = TemplateService(client)
    template = await service.get_template(template_id)

    pdf_bytes = render_template_pdf(template)

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
    """Render a template as a PDF and return it for inline preview."""
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
