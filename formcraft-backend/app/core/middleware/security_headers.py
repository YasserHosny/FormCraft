from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


DOCS_PATH_PREFIXES = ("/docs",)
DOCS_ALLOWED_PATHS = {"/openapi.json"}
DOCS_CSP = "; ".join(
    [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
        "img-src 'self' data: https://fastapi.tiangolo.com",
        "font-src 'self' https://cdn.jsdelivr.net",
    ]
)
DEFAULT_CSP = "default-src 'self'"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds security headers to all responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        path = request.url.path
        if path.startswith(DOCS_PATH_PREFIXES) or path in DOCS_ALLOWED_PATHS:
            response.headers["Content-Security-Policy"] = DOCS_CSP
        else:
            response.headers["Content-Security-Policy"] = DEFAULT_CSP

        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response
