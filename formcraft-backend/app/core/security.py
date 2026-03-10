import time

import httpx
from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.core.config import settings

_JWKS_CACHE: dict[str, object] = {"keys": None, "fetched_at": 0.0}


def _get_jwks_keys() -> list[dict]:
    cached_keys = _JWKS_CACHE.get("keys")
    fetched_at = _JWKS_CACHE.get("fetched_at", 0.0)
    if cached_keys and (time.time() - float(fetched_at)) < 3600:
        return cached_keys  # type: ignore[return-value]

    response = httpx.get(
        f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json",
        headers={"apikey": settings.SUPABASE_ANON_KEY},
        timeout=10.0,
    )
    response.raise_for_status()
    keys = response.json().get("keys", [])
    _JWKS_CACHE["keys"] = keys
    _JWKS_CACHE["fetched_at"] = time.time()
    return keys


def _get_jwk_for_kid(kid: str | None) -> dict:
    if not kid:
        raise JWTError("Missing kid in token header")
    keys = _get_jwks_keys()
    for key in keys:
        if key.get("kid") == kid:
            return key
    raise JWTError("Signing key not found")


def verify_jwt(token: str) -> dict:
    """Verify a Supabase JWT and return the decoded payload.

    Raises HTTPException 401 if the token is invalid or expired.
    """
    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg")
        if alg == "ES256":
            jwk_key = _get_jwk_for_kid(header.get("kid"))
            payload = jwt.decode(
                token,
                jwk_key,
                algorithms=["ES256"],
                audience="authenticated",
                issuer=f"{settings.SUPABASE_URL}/auth/v1",
            )
        else:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
