from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import require_role
from app.core.middleware.rate_limit import limiter
from app.core.supabase import get_supabase_client
from app.core.audit import AuditLogger
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.ai import SuggestionRequest, SuggestionResponse
from app.services.ai.bedrock import BedrockProvider
from app.services.ai.suggestion import get_suggestion
from app.services.validators import label_matcher, validator_registry

router = APIRouter(prefix="/ai", tags=["AI"])

_llm_provider = None


def _get_provider():
    global _llm_provider
    if _llm_provider is None:
        _llm_provider = BedrockProvider()
    return _llm_provider


@router.post("/suggest-control", response_model=SuggestionResponse)
async def suggest_control(
    body: SuggestionRequest,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN, Role.DESIGNER))
    ],
):
    """Get AI-powered control type suggestion for a field label."""
    provider = _get_provider()
    response = await get_suggestion(
        request=body,
        llm_provider=provider,
        label_matcher=label_matcher,
        validator_registry=validator_registry,
    )

    # Audit log (non-blocking)
    client = get_supabase_client()
    audit = AuditLogger(client)
    await audit.log_event(
        user_id=str(current_user.id),
        action="ai_suggest",
        resource_type="ai_suggestion",
        metadata={
            "label": body.label,
            "language": body.language.value,
            "country": body.country.value,
            "control_type": response.control_type.value,
            "confidence": response.confidence,
            "source": response.source,
        },
    )

    return response
