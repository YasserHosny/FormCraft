from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.supabase import get_supabase_client

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    checks = {}
    status = "ok"

    # Check Supabase connectivity
    try:
        client = get_supabase_client()
        result = client.table("profiles").select("id").limit(1).execute()
        if result.data is not None:
            checks["supabase"] = "healthy"
        else:
            checks["supabase"] = "unreachable"
            status = "degraded"
    except Exception:
        checks["supabase"] = "unreachable"
        status = "degraded"

    status_code = 200 if status == "ok" else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": status,
            "version": settings.APP_VERSION,
            "checks": checks,
        },
    )
