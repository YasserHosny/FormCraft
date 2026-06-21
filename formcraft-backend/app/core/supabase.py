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


def get_auth_client() -> Client:
    """Return a fresh anon-key client for user auth operations (sign-in, refresh, sign-out).

    Auth operations like sign_in_with_password mutate supabase-py's internal
    PostgREST headers to the user JWT, which would break the service-role singleton.
    Using a dedicated fresh client per auth call keeps the singleton untouched.
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
