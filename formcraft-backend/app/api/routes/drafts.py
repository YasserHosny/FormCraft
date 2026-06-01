from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.deps import get_current_user
from app.core.supabase import get_supabase_client
from app.models.user import UserProfile
from app.schemas.submission import (
    CreateDraftRequest,
    UpdateDraftRequest,
    DraftResponse,
)
from app.services.draft_service import DraftService

router = APIRouter(prefix="/desk/drafts", tags=["Drafts"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=DraftResponse)
async def create_draft(
    body: CreateDraftRequest,
    request: Request,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    """Create a new draft."""
    if current_user.org_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User has no organization")
    client = get_supabase_client()
    service = DraftService(client)
    draft = await service.create_draft(
        template_id=body.template_id,
        template_version=body.template_version,
        field_values=body.field_values,
        operator_id=current_user.id,
        org_id=current_user.org_id,
        name=body.name,
        completion_percent=body.completion_percent,
    )
    return draft


@router.patch("/{draft_id}", response_model=DraftResponse)
async def update_draft(
    draft_id: UUID,
    body: UpdateDraftRequest,
    request: Request,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    """Update an existing draft."""
    client = get_supabase_client()
    service = DraftService(client)
    draft = await service.update_draft(
        draft_id=draft_id,
        operator_id=current_user.id,
        field_values=body.field_values,
        name=body.name,
        completion_percent=body.completion_percent,
    )
    return draft


@router.get("/{draft_id}", response_model=DraftResponse)
async def get_draft(
    draft_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    """Get a draft by ID."""
    client = get_supabase_client()
    service = DraftService(client)
    return await service.get_draft(draft_id=draft_id, operator_id=current_user.id)


@router.get("", response_model=list[DraftResponse])
async def list_drafts(
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    """List drafts for the authenticated user."""
    client = get_supabase_client()
    service = DraftService(client)
    return await service.list_drafts(operator_id=current_user.id)


@router.delete("/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_draft(
    draft_id: UUID,
    request: Request,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    """Delete a draft."""
    client = get_supabase_client()
    service = DraftService(client)
    await service.delete_draft(draft_id=draft_id, operator_id=current_user.id)
