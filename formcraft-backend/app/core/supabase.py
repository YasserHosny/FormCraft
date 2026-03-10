import logging

from supabase import Client, create_client

from app.core.config import settings

logger = logging.getLogger(__name__)
_client: Client | None = None


def get_supabase_client() -> Client:
    """Return a singleton Supabase client (service-role key for backend operations)."""
    global _client
    if _client is None:
        logger.info("supabase_client_init")
        _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    return _client
