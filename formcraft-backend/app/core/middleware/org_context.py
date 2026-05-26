import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.security import verify_jwt

logger = logging.getLogger(__name__)

PUBLIC_PATHS = {
    "/api/health",
    "/api/auth/login",
    "/api/auth/refresh",
    "/api/branding",
    "/docs",
    "/openapi.json",
    "/redoc",
}


class OrgContextMiddleware(BaseHTTPMiddleware):
    """Set app.current_org_id and app.is_platform_admin session variables
    from JWT claims before each authenticated request."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in PUBLIC_PATHS or path.startswith("/api/auth/invite") or path.startswith("/api/branding/"):
            response = await call_next(request)
            return response

        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            response = await call_next(request)
            return response

        token = auth_header.removeprefix("Bearer ")

        try:
            payload = verify_jwt(token)
        except Exception:
            response = await call_next(request)
            return response

        org_id = payload.get("org_id")
        is_platform_admin = payload.get("is_platform_admin", False)

        if org_id:
            request.state.org_id = org_id
            request.state.is_platform_admin = is_platform_admin
        else:
            request.state.org_id = None
            request.state.is_platform_admin = is_platform_admin

        response = await call_next(request)
        return response


def get_org_id(request: Request) -> str | None:
    return getattr(request.state, "org_id", None)


def is_platform_admin(request: Request) -> bool:
    return getattr(request.state, "is_platform_admin", False)