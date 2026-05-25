from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.api.deps import get_current_user, require_role
from app.core.audit import AuditLogger
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.element import (
    CreateElementRequest,
    ReorderElementsRequest,
    UpdateElementRequest,
)
from app.schemas.page import CreatePageRequest, ReorderPagesRequest, UpdatePageRequest
from app.schemas.template import (
    CloneRequest,
    CreateTemplateRequest,
    TransitionRequest,
    UpdateTemplateRequest,
)
from app.schemas.print_settings import PrintSettingsUpdate
from app.services.dependency_validator import DependencyValidator
from app.services.print_settings_service import PrintSettingsService
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
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization to create templates",
        )

    client = get_supabase_client()
    service = TemplateService(client)
    template = await service.create_template(
        data=body.model_dump(), user_id=current_user.id, org_id=current_user.org_id
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
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
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


@router.post("/{template_id}/transition")
async def transition_template_status(
    request: Request,
    template_id: UUID,
    body: TransitionRequest,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    client = get_supabase_client()
    service = TemplateService(client)
    result = await service.transition_status(
        template_id=template_id,
        new_status=body.status,
        actor_id=current_user.id,
        comment=body.comment,
        element_comments=[c.model_dump() for c in body.element_comments]
        if body.element_comments
        else None,
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
    new_template = await service.create_new_version(
        template_id, user_id=current_user.id
    )
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


@router.post("/{template_id}/clone", status_code=201)
async def clone_template(
    request: Request,
    template_id: UUID,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN, Role.DESIGNER))
    ],
    body: CloneRequest | None = None,
):
    client = get_supabase_client()
    service = TemplateService(client)
    name = body.name if body else None
    result = await service.clone_template(
        template_id, name=name, user_id=current_user.id
    )
    return result


@router.get("/{template_id}/history")
async def get_version_history(
    template_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    client = get_supabase_client()
    service = TemplateService(client)
    return await service.get_version_history(template_id)


@router.get("/{template_id}/diff")
async def get_version_diff(
    template_id: UUID,
    compare_to: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    client = get_supabase_client()
    service = TemplateService(client)
    return await service.compute_diff(template_id, compare_to)


@router.get("/{template_id}/reviews")
async def get_template_reviews(
    template_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    client = get_supabase_client()
    service = TemplateService(client)
    reviews = await service.get_reviews(template_id)
    return {"reviews": reviews}


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

    # FR-023: validate tafqeet sourceElementKey references a number/currency element on same page
    if body.formatting:
        source_key = body.formatting.get("sourceElementKey")
        if source_key is not None:
            element_result = (
                client.table("elements")
                .select("id, type, page_id")
                .eq("id", str(element_id))
                .single()
                .execute()
            )
            element_row = element_result.data
            if element_row and element_row.get("type") == "tafqeet":
                page_id = element_row.get("page_id")
                siblings = (
                    client.table("elements")
                    .select("key, type")
                    .eq("page_id", str(page_id))
                    .neq("id", str(element_id))
                    .execute()
                    .data
                    or []
                )
                valid_keys = {
                    el["key"]
                    for el in siblings
                    if el.get("type") in ("number", "currency")
                }
                if source_key not in valid_keys:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=(
                            f"sourceElementKey '{source_key}' does not reference a "
                            "number or currency element on the same page"
                        ),
                    )

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


# --- Dependency Validation ---


@router.post("/{template_id}/validate-dependencies")
async def validate_dependencies(
    template_id: UUID,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN, Role.DESIGNER))
    ],
):
    client = get_supabase_client()
    # Elements are keyed by page_id, not template_id — fetch pages first
    pages_result = (
        client.table("pages").select("id").eq("template_id", str(template_id)).execute()
    )
    page_ids = [p["id"] for p in (pages_result.data or [])]
    elements: list[dict] = []
    for pid in page_ids:
        result = (
            client.table("elements")
            .select("key, visible_when, required_when, computed_value")
            .eq("page_id", pid)
            .execute()
        )
        elements.extend(result.data or [])

    validator = DependencyValidator()
    cycle = validator.detect_cycles(elements)
    if cycle:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "valid": False,
                "detail": "Circular dependency detected",
                "cycle": cycle,
            },
        )

    stats = validator.get_stats(elements)
    return {"valid": True, **stats}


# --- Print Settings ---


@router.get("/{template_id}/print-settings")
async def get_print_settings(
    template_id: UUID,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN, Role.DESIGNER))
    ],
):
    client = get_supabase_client()
    service = PrintSettingsService(client)
    settings = await service.get_settings(template_id)
    if not settings:
        return {"template_id": str(template_id), "print_mode": "full"}
    return settings


@router.put("/{template_id}/print-settings")
async def update_print_settings(
    template_id: UUID,
    body: PrintSettingsUpdate,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN, Role.DESIGNER))
    ],
):
    client = get_supabase_client()
    service = PrintSettingsService(client)
    return await service.upsert_settings(
        template_id=template_id,
        print_mode=body.print_mode,
        org_id=current_user.org_id,
    )
