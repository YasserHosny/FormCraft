"""Helpers for database schema compatibility during incremental migrations."""

SCHEMA_ERROR_CODES = ("PGRST204", "PGRST205", "42703", "42P01")


def is_missing_schema_error(exc: Exception) -> bool:
    """Return true when Supabase/PostgREST reports a missing table/column."""
    message = str(exc)
    return any(code in message for code in SCHEMA_ERROR_CODES) or "schema cache" in message
