"""Base analytics utilities for RLS scoping and shared helpers."""

from uuid import UUID

from supabase import Client


def apply_org_scope(client: Client, table: str, org_id: UUID | str) -> any:
    """Return a query builder scoped to the given org_id."""
    return client.table(table).select("*").eq("org_id", str(org_id))


def apply_branch_scope(
    client: Client, table: str, org_id: UUID | str, branch_id: UUID | str | None
) -> any:
    """Return a query builder scoped to org_id and optionally branch_id."""
    query = apply_org_scope(client, table, org_id)
    if branch_id:
        query = query.eq("branch_id", str(branch_id))
    return query
