"""Routes for reference data lists and entries."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, UploadFile, File, Form

from app.api.deps import get_current_user, require_role
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.reference import (
    ImportConfirmRequest,
    ReferenceEntryCreate,
    ReferenceEntryUpdate,
    ReferenceListCreate,
    ReferenceListUpdate,
)
from app.services.reference_service import ReferenceService

router = APIRouter(prefix="/reference-lists", tags=["Reference Data"])


# --- List CRUD ---


@router.post("", status_code=201)
async def create_list(
    body: ReferenceListCreate,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN))
    ],
):
    client = get_supabase_client()
    service = ReferenceService(client)
    data = {
        "name_ar": body.name_ar,
        "name_en": body.name_en,
        "description": body.description,
        "schema": [c.model_dump() for c in body.schema_def],
    }
    return await service.create_list(data, current_user.id, current_user.org_id)


@router.get("")
async def list_lists(
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    include_archived: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    client = get_supabase_client()
    service = ReferenceService(client)
    items, total = await service.list_lists(
        include_archived=include_archived, page=page, page_size=page_size
    )
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{list_id}")
async def get_list(
    list_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    client = get_supabase_client()
    service = ReferenceService(client)
    return await service.get_list(list_id)


@router.patch("/{list_id}")
async def update_list(
    list_id: UUID,
    body: ReferenceListUpdate,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN))
    ],
):
    client = get_supabase_client()
    service = ReferenceService(client)
    data = body.model_dump(exclude_none=True)
    if "schema_def" in data:
        data["schema"] = data.pop("schema_def")
        data["schema"] = [c if isinstance(c, dict) else c.model_dump() for c in body.schema_def]
    return await service.update_list(list_id, data, current_user.id)


@router.post("/{list_id}/archive")
async def archive_list(
    list_id: UUID,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN))
    ],
):
    client = get_supabase_client()
    service = ReferenceService(client)
    return await service.archive_list(list_id, current_user.id)


@router.post("/{list_id}/unarchive")
async def unarchive_list(
    list_id: UUID,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN))
    ],
):
    client = get_supabase_client()
    service = ReferenceService(client)
    return await service.unarchive_list(list_id, current_user.id)


@router.delete("/{list_id}", status_code=204)
async def delete_list(
    list_id: UUID,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN))
    ],
):
    client = get_supabase_client()
    service = ReferenceService(client)
    await service.delete_list(list_id, current_user.id)


# --- Entry CRUD ---


@router.get("/{list_id}/entries")
async def get_entries(
    list_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    active_only: bool = Query(True),
    q: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
):
    client = get_supabase_client()
    service = ReferenceService(client)
    items, total = await service.get_entries(
        list_id, active_only=active_only, q=q, page=page, page_size=page_size
    )
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("/{list_id}/entries", status_code=201)
async def create_entry(
    list_id: UUID,
    body: ReferenceEntryCreate,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN))
    ],
):
    client = get_supabase_client()
    service = ReferenceService(client)
    return await service.create_entry(
        list_id, body.values, current_user.id, current_user.org_id
    )


@router.patch("/{list_id}/entries/{entry_id}")
async def update_entry(
    list_id: UUID,
    entry_id: UUID,
    body: ReferenceEntryUpdate,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN))
    ],
):
    client = get_supabase_client()
    service = ReferenceService(client)
    return await service.update_entry(list_id, entry_id, body.values, current_user.id)


@router.post("/{list_id}/entries/{entry_id}/deactivate")
async def deactivate_entry(
    list_id: UUID,
    entry_id: UUID,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN))
    ],
):
    client = get_supabase_client()
    service = ReferenceService(client)
    return await service.deactivate_entry(entry_id, current_user.id)


@router.post("/{list_id}/entries/{entry_id}/activate")
async def activate_entry(
    list_id: UUID,
    entry_id: UUID,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN))
    ],
):
    client = get_supabase_client()
    service = ReferenceService(client)
    return await service.activate_entry(entry_id, current_user.id)


# --- Dropdown endpoint (Form Desk) ---


@router.get("/{list_id}/entries/dropdown")
async def get_dropdown_items(
    list_id: UUID,
    display_column: str = Query(...),
    value_column: str = Query(...),
    q: str | None = Query(None),
    current_user: Annotated[UserProfile, Depends(get_current_user)] = None,
):
    client = get_supabase_client()
    service = ReferenceService(client)
    items = await service.get_dropdown_items(list_id, display_column, value_column, q)
    return {"items": items, "total": len(items), "full_entry_available": True}


@router.get("/{list_id}/entries/{entry_id}")
async def get_single_entry(
    list_id: UUID,
    entry_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    client = get_supabase_client()
    service = ReferenceService(client)
    return await service.get_entry(entry_id)


# --- CSV Import ---


@router.post("/{list_id}/import/preview")
async def import_preview(
    list_id: UUID,
    file: UploadFile = File(...),
    mode: str = Form("insert"),
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN))
    ] = None,
):
    from app.services.reference_import_service import ReferenceImportService

    client = get_supabase_client()
    ref_service = ReferenceService(client)
    ref_list = await ref_service.get_list(list_id)
    import_service = ReferenceImportService(client)
    content = await file.read()
    return await import_service.preview(
        list_id=list_id,
        schema=ref_list["schema"],
        csv_content=content.decode("utf-8-sig"),
        mode=mode,
    )


@router.post("/{list_id}/import/confirm")
async def import_confirm(
    list_id: UUID,
    body: ImportConfirmRequest,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN))
    ],
):
    from app.services.reference_import_service import ReferenceImportService

    client = get_supabase_client()
    import_service = ReferenceImportService(client)
    result = await import_service.confirm(
        list_id=list_id,
        preview_token=body.preview_token,
        import_valid_only=body.import_valid_only,
        user_id=current_user.id,
        org_id=current_user.org_id,
    )
    return result
