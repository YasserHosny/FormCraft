"""Auth policy routes: org-level MFA, session, and fallback settings."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, require_role
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.identity import AuthPolicyCreateUpdate, AuthPolicyResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/auth-policy", tags=["Auth Policy"])


@router.get("", response_model=AuthPolicyResponse)
async def get_policy(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    client = get_supabase_client()
    row = (
        client.table("auth_policies")
        .select("*")
        .eq("org_id", str(current_user.org_id))
        .maybe_single()
        .execute()
    )
    if not row.data:
        raise HTTPException(status_code=404, detail="Auth policy not found")
    return AuthPolicyResponse(**row.data)


@router.put("", response_model=AuthPolicyResponse)
async def upsert_policy(
    body: AuthPolicyCreateUpdate,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    client = get_supabase_client()
    existing = (
        client.table("auth_policies")
        .select("*")
        .eq("org_id", str(current_user.org_id))
        .maybe_single()
        .execute()
    )
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "org_id": str(current_user.org_id),
        "require_mfa_for": body.require_mfa_for,
        "session_timeout_minutes": body.session_timeout_minutes,
        "idle_timeout_minutes": body.idle_timeout_minutes,
        "max_concurrent_sessions": body.max_concurrent_sessions,
        "trusted_ip_ranges": body.trusted_ip_ranges,
        "fallback_policy": body.fallback_policy.value,
        "updated_at": now,
    }
    if existing.data:
        client.table("auth_policies").update(payload).eq("id", existing.data["id"]).execute()
        return AuthPolicyResponse(**{**existing.data, **payload})
    else:
        from uuid import uuid4
        payload["id"] = str(uuid4())
        payload["created_at"] = now
        payload["created_by"] = str(current_user.id)
        client.table("auth_policies").insert(payload).execute()
        return AuthPolicyResponse(**payload)
