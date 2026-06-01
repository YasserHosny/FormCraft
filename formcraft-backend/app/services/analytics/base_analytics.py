"""Base analytics utilities for RLS scoping and shared helpers."""

from datetime import date, timedelta
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


def _period_to_dates(period: str) -> tuple[date, date, date, date]:
    """Convert a period string to current and previous date ranges.

    Returns (current_from, current_to, prev_from, prev_to) where
    current_to and prev_to are both today (UTC).
    """
    today = date.today()
    if period == "7d":
        current_from = today - timedelta(days=6)
    elif period == "30d":
        current_from = today - timedelta(days=29)
    elif period == "90d":
        current_from = today - timedelta(days=89)
    elif period == "yearly":
        # 12 months up to and including current month
        month = today.month
        year = today.year
        for _ in range(11):
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        current_from = date(year, month, 1)
        prev_month = month
        prev_year = year - 1
        prev_from = date(prev_year, prev_month, 1)
        prev_to = date(today.year, today.month, 1) - timedelta(days=1)
        return (current_from, today, prev_from, prev_to)
    else:
        raise ValueError(f"Invalid period: {period!r}")

    prev_to = current_from - timedelta(days=1)
    prev_from = prev_to - (today - current_from)
    return (current_from, today, prev_from, prev_to)
