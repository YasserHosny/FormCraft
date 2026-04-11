from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from app.api.deps import get_current_user, require_role
from app.core.audit import AuditLogger
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.element import CreateElementRequest, ReorderElementsRequest, UpdateElementRequest
from app.schemas.page import CreatePageRequest, ReorderPagesRequest, UpdatePageRequest
from app.schemas.template import CreateTemplateRequest, UpdateTemplateRequest
from app.services.template_service import TemplateService

router = APIRouter(prefix="/templates", tags=["Templates"])


# --- Template CRUD ---


@router.post("", status_code=201)
async def create_template(
    request: Request,
    body: CreateTemplateRequest,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN, Role.DESIGNER))
    ],
):
    client = get_supabase_client()
    service = TemplateService(client)
    template = await service.create_template(
        data=body.model_dump(), user_id=current_user.id
    )
    audit = AuditLogger(client)
    await audit.log_event(
        user_id=str(current_user.id),
        action="template.create",
        resource_type="template",
        resource_id=template["id"],
        metadata={"name": template.get("name")},
        ip_address=request.client.host if request.client else None,
    )
    return template


@router.get("")
async def list_templates(
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = None,
    category: str | None = None,
    country: str | None = None,
    search: str | None = None,
):
    client = get_supabase_client()
    service = TemplateService(client)
    templates, total = await service.list_templates(
        page=page,
        limit=limit,
        status_filter=status,
        category=category,
        country=country,
        search=search,
    )
    return {"data": templates, "total": total, "page": page, "limit": limit}


@router.get("/{template_id}")
async def get_template(
    template_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    client = get_supabase_client()
    service = TemplateService(client)
    return await service.get_template(template_id)


@router.put("/{template_id}")
async def update_template(
    request: Request,
    template_id: UUID,
    body: UpdateTemplateRequest,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN, Role.DESIGNER))
    ],
):
    client = get_supabase_client()
    service = TemplateService(client)
    data = body.model_dump(exclude={"updated_at"}, exclude_none=True)
    result = await service.update_template(template_id, data, body.updated_at)
    audit = AuditLogger(client)
    await audit.log_event(
        user_id=str(current_user.id),
        action="template.update",
        resource_type="template",
        resource_id=str(template_id),
        metadata={"changes": data},
        ip_address=request.client.host if request.client else None,
    )
    return result


@router.delete("/{template_id}", status_code=204)
async def delete_template(
    request: Request,
    template_id: UUID,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN, Role.DESIGNER))
    ],
):
    client = get_supabase_client()
    service = TemplateService(client)
    await service.delete_template(template_id)
    audit = AuditLogger(client)
    await audit.log_event(
        user_id=str(current_user.id),
        action="template.delete",
        resource_type="template",
        resource_id=str(template_id),
        ip_address=request.client.host if request.client else None,
    )


@router.post("/{template_id}/publish")
async def publish_template(
    request: Request,
    template_id: UUID,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN))
    ],
):
    client = get_supabase_client()
    service = TemplateService(client)
    result = await service.publish_template(template_id)
    audit = AuditLogger(client)
    await audit.log_event(
        user_id=str(current_user.id),
        action="template.publish",
        resource_type="template",
        resource_id=str(template_id),
        metadata={"status_transition": "draft→published"},
        ip_address=request.client.host if request.client else None,
    )
    return result


@router.post("/{template_id}/version")
async def create_new_version(
    request: Request,
    template_id: UUID,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN, Role.DESIGNER))
    ],
):
    client = get_supabase_client()
    service = TemplateService(client)
    new_template = await service.create_new_version(template_id, user_id=current_user.id)
    audit = AuditLogger(client)
    await audit.log_event(
        user_id=str(current_user.id),
        action="template.version",
        resource_type="template",
        resource_id=str(template_id),
        metadata={"new_template_id": new_template["id"]},
        ip_address=request.client.host if request.client else None,
    )
    return new_template


# --- Page CRUD ---


@router.put("/{template_id}/pages/reorder", status_code=204)
async def reorder_pages(
    template_id: UUID,
    body: ReorderPagesRequest,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN, Role.DESIGNER))
    ],
):
    client = get_supabase_client()
    service = TemplateService(client)
    await service.reorder_pages(template_id, body.page_ids)


@router.post("/{template_id}/pages", status_code=201)
async def add_page(
    template_id: UUID,
    body: CreatePageRequest,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN, Role.DESIGNER))
    ],
):
    client = get_supabase_client()
    service = TemplateService(client)
    return await service.add_page(template_id, body.model_dump())


@router.put("/pages/{page_id}")
async def update_page(
    page_id: UUID,
    body: UpdatePageRequest,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN, Role.DESIGNER))
    ],
):
    client = get_supabase_client()
    service = TemplateService(client)
    return await service.update_page(page_id, body.model_dump(exclude_none=True))


@router.delete("/pages/{page_id}", status_code=204)
async def delete_page(
    page_id: UUID,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN, Role.DESIGNER))
    ],
):
    client = get_supabase_client()
    service = TemplateService(client)
    await service.delete_page(page_id)


# --- Element CRUD ---


@router.put("/pages/{page_id}/elements/reorder", status_code=204)
async def reorder_elements(
    page_id: UUID,
    body: ReorderElementsRequest,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN, Role.DESIGNER))
    ],
):
    client = get_supabase_client()
    service = TemplateService(client)
    await service.reorder_elements(page_id, body.element_ids)


@router.post("/pages/{page_id}/elements", status_code=201)
async def add_element(
    page_id: UUID,
    body: CreateElementRequest,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN, Role.DESIGNER))
    ],
):
    client = get_supabase_client()
    service = TemplateService(client)
    return await service.add_element(page_id, body.model_dump())


@router.put("/elements/{element_id}")
async def update_element(
    element_id: UUID,
    body: UpdateElementRequest,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN, Role.DESIGNER))
    ],
):
    client = get_supabase_client()
    service = TemplateService(client)
    return await service.update_element(element_id, body.model_dump(exclude_none=True))


@router.delete("/elements/{element_id}", status_code=204)
async def delete_element(
    element_id: UUID,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN, Role.DESIGNER))
    ],
):
    client = get_supabase_client()
    service = TemplateService(client)
    await service.delete_element(element_id)
