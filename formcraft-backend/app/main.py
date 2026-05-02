import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.middleware.rate_limit import limiter
from app.core.middleware.security_headers import SecurityHeadersMiddleware
from app.api.routes import auth, users, templates, ai, pdf, health, admin, forms, tafqeet

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

    logger.info("FormCraft API v%s started", settings.APP_VERSION)
    return app


app = create_app()
