import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.middleware.rate_limit import limiter
from app.core.middleware.security_headers import SecurityHeadersMiddleware
from app.api.routes import (
    auth,
    users,
    templates,
    ai,
    pdf,
    health,
    admin,
    forms,
    tafqeet,
    feedback,
    template_feedback,
    printer_profiles,
    reference,
    organizations,
    org_settings,
    departments,
    branches,
    invitations,
    desk,
    drafts,
    submissions,
    review_queue,
)

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title="FormCraft API",
        description="Universal Form Designer & Print Studio",
        version=settings.APP_VERSION,
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SecurityHeadersMiddleware)

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Routes
    app.include_router(health.router, prefix="/api")
    app.include_router(auth.router, prefix="/api")
    app.include_router(users.router, prefix="/api")
    app.include_router(templates.router, prefix="/api")
    app.include_router(forms.router, prefix="/api")
    app.include_router(ai.router, prefix="/api")
    app.include_router(pdf.router, prefix="/api")
    app.include_router(admin.router, prefix="/api")
    app.include_router(tafqeet.router, prefix="/api")
    app.include_router(feedback.router, prefix="/api")
    app.include_router(feedback.user_router, prefix="/api")
    app.include_router(template_feedback.router, prefix="/api")
    app.include_router(template_feedback.admin_router, prefix="/api")
    app.include_router(printer_profiles.router, prefix="/api")
    app.include_router(reference.router, prefix="/api")
    app.include_router(organizations.router, prefix="/api")
    app.include_router(org_settings.router, prefix="/api")
    app.include_router(departments.router, prefix="/api")
    app.include_router(branches.router, prefix="/api")
    app.include_router(invitations.router, prefix="/api")
    app.include_router(invitations.public_router, prefix="/api")
    app.include_router(desk.router, prefix="/api")
    app.include_router(drafts.router, prefix="/api")
    app.include_router(submissions.router, prefix="/api")
    app.include_router(review_queue.router, prefix="/api/admin")

    # Global handler for Supabase/PostgREST errors (missing tables/columns
    # from unapplied migrations) — returns a clear 503 instead of 500.
    _SCHEMA_CODES = ("PGRST204", "PGRST205", "42703", "42P01")

    def _is_schema_error(exc: Exception) -> bool:
        msg = str(exc)
        if any(code in msg for code in _SCHEMA_CODES):
            return True
        # Check nested exceptions in ExceptionGroups
        if hasattr(exc, "exceptions"):
            return any(_is_schema_error(e) for e in exc.exceptions)
        if exc.__cause__:
            return _is_schema_error(exc.__cause__)
        return False

    @app.exception_handler(Exception)
    async def _supabase_schema_error_handler(request: Request, exc: Exception):
        if _is_schema_error(exc):
            msg = str(exc)[:300]
            logger.warning("Schema error (migration pending): %s", msg[:200])
            return JSONResponse(
                status_code=503,
                content={
                    "detail": "This feature requires a database migration that has not been applied yet.",
                    "error": msg[:200],
                },
            )
        # Re-raise anything else so default handling applies
        raise exc

    logger.info("FormCraft API v%s started", settings.APP_VERSION)
    return app


app = create_app()
