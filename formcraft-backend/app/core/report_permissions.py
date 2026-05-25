from enum import StrEnum


class ReportRole(StrEnum):
    ORG_ADMIN = "org_admin"
    BRANCH_MANAGER = "branch_manager"
    OPERATOR = "operator"


REPORT_ACCESS_MATRIX = {
    # User Story 1: Transaction Register
    "transaction_register": [ReportRole.ORG_ADMIN, ReportRole.BRANCH_MANAGER],
    # User Story 2: Daily Reconciliation
    "daily_reconciliation": [ReportRole.ORG_ADMIN, ReportRole.BRANCH_MANAGER],
    # User Story 3: Period Summary
    "period_summary": [ReportRole.ORG_ADMIN],
    # User Story 4: Custom Report Builder
    "custom": [ReportRole.ORG_ADMIN],
    # User Story 5: Financial Reports
    "beneficiary": [ReportRole.ORG_ADMIN],
    "void_reprint": [ReportRole.ORG_ADMIN],
    "signatory_usage": [ReportRole.ORG_ADMIN],
    # Scheduling and archives
    "schedules": [ReportRole.ORG_ADMIN],
    "archives": [ReportRole.ORG_ADMIN],
}


def can_access_report(user_role: str, report_type: str) -> bool:
    """Check if a user role can access a specific report type."""
    allowed_roles = REPORT_ACCESS_MATRIX.get(report_type, [])
    return ReportRole(user_role) in allowed_roles


def get_branch_scope(user_role: str, user_branch_id: str | None) -> str | None:
    """
    Determine branch scope for a user.
    Returns branch_id to filter by, or None for all branches.
    """
    if user_role == ReportRole.BRANCH_MANAGER:
        return user_branch_id
    if user_role == ReportRole.OPERATOR:
        return user_branch_id
    return None


def can_access_aggregate_reports(user_role: str) -> bool:
    """Operators cannot access aggregate reports."""
    return user_role != ReportRole.OPERATOR


def can_schedule_reports(user_role: str) -> bool:
    """Only org admins can schedule reports."""
    return user_role == ReportRole.ORG_ADMIN


def can_view_all_archives(user_role: str) -> bool:
    """Only org admins can view all archives."""
    return user_role == ReportRole.ORG_ADMIN
