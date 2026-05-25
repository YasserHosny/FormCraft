from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import require_role
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.services.integration_credential_service import IntegrationCredentialService
from app.services.webhook_service import WebhookService

router = APIRouter(prefix="/integrations", tags=["Integrations"])


@router.get("/health")
async def integrations_health(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    """Placeholder endpoint for F32 integrations route registration."""
    return {"status": "ok", "org_id": str(current_user.org_id) if current_user.org_id else None}


# --- Credentials ---


@router.post("/credentials")
async def create_credential(
    request: dict,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    """Create a new integration credential with one-time secret."""
    if not current_user.org_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="User must belong to an organization")

    service = IntegrationCredentialService(get_supabase_client())
    result = await service.create_credential(
        current_user.org_id,
        current_user.id,
        request.get("name", "Unnamed"),
        request.get("scopes", []),
    )
    if not result:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create credential")
    return result


@router.get("/credentials")
async def list_credentials(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    """List integration credentials for the org."""
    if not current_user.org_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="User must belong to an organization")

    service = IntegrationCredentialService(get_supabase_client())
    items = await service.list_credentials(current_user.org_id)
    return {"items": items}


@router.patch("/credentials/{credential_id}/revoke")
async def revoke_credential(
    credential_id: str,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    """Revoke an integration credential."""
    if not current_user.org_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="User must belong to an organization")

    service = IntegrationCredentialService(get_supabase_client())
    result = await service.revoke_credential(current_user.org_id, UUID(credential_id), current_user.id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")
    return result


# --- Webhooks ---


@router.post("/webhooks")
async def create_webhook(
    request: dict,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    """Create a webhook subscription."""
    if not current_user.org_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="User must belong to an organization")

    service = WebhookService(get_supabase_client())
    result = await service.create_subscription(
        current_user.org_id,
        current_user.id,
        request["url"],
        request.get("event_types", []),
        request.get("signing_secret", ""),
    )
    if not result:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create webhook")
    return result


@router.get("/webhooks")
async def list_webhooks(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    """List webhook subscriptions for the org."""
    if not current_user.org_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="User must belong to an organization")

    service = WebhookService(get_supabase_client())
    items = await service.list_subscriptions(current_user.org_id)
    return {"items": items}


@router.patch("/webhooks/{webhook_id}")
async def update_webhook(
    webhook_id: str,
    request: dict,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    """Update a webhook subscription."""
    if not current_user.org_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="User must belong to an organization")

    service = WebhookService(get_supabase_client())
    updates = {k: v for k, v in request.items() if v is not None}
    result = await service.update_subscription(current_user.org_id, UUID(webhook_id), updates)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")
    return result


@router.get("/webhooks/{webhook_id}/deliveries")
async def list_webhook_deliveries(
    webhook_id: str,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    """List webhook deliveries."""
    if not current_user.org_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="User must belong to an organization")

    service = WebhookService(get_supabase_client())
    items = await service.list_deliveries(current_user.org_id, UUID(webhook_id))
    return {"items": items}