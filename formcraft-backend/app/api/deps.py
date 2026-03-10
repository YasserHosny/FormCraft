import logging
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status

from app.core.security import verify_jwt
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile

logger = logging.getLogger(__name__)


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> UserProfile:
    """Extract and verify JWT, then load the user profile from Supabase."""
    logger.debug(f"get_current_user called, authorization: {authorization}")
    if not authorization:
        logger.warning("Missing Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )
    if not authorization.startswith("Bearer "):
        logger.warning(f"Invalid auth header format: {authorization[:50]}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )
    token = authorization.removeprefix("Bearer ")
    payload = verify_jwt(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject claim",
        )

    client = get_supabase_client()
    result = (
        client.table("profiles")
        .select("*")
        .eq("id", user_id)
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    profile = UserProfile(**result.data)
    if not profile.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    return profile


def require_role(*roles: Role):
    """Factory for role-based access control dependency."""

    async def _check_role(
        current_user: Annotated[UserProfile, Depends(get_current_user)],
    ) -> UserProfile:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of: {', '.join(r.value for r in roles)}",
            )
        return current_user

    return _check_role
