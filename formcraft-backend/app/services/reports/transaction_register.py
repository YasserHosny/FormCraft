from datetime import date
from uuid import UUID


class TransactionRegisterService:
    """Builds and executes transaction register queries against the submissions table."""

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    async def query(
        self,
        org_id: UUID,
        date_from: date,
        date_to: date,
        template_id: UUID | None = None,
        branch_id: UUID | None = None,
        department_id: UUID | None = None,
        operator_id: UUID | None = None,
        status: str | None = None,
        customer_query: str | None = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> tuple[list[dict], int]:
        """
        Query submissions with filters and pagination.
        Returns (rows, total_count).
        """
        # Base query via Supabase RPC or direct query
        # Using raw SQL via RPC for complex joins
        rpc_params = {
            "p_org_id": str(org_id),
            "p_date_from": date_from.isoformat(),
            "p_date_to": date_to.isoformat(),
            "p_template_id": str(template_id) if template_id else None,
            "p_branch_id": str(branch_id) if branch_id else None,
            "p_department_id": str(department_id) if department_id else None,
            "p_operator_id": str(operator_id) if operator_id else None,
            "p_status": status,
            "p_customer_query": customer_query,
            "p_page": page,
            "p_page_size": page_size,
            "p_sort_by": sort_by,
            "p_sort_dir": sort_dir,
        }

        response = self.supabase.rpc("get_transaction_register", rpc_params).execute()
        if hasattr(response, "data") and response.data:
            data = response.data
            total_count = data[0].get("total_count", 0) if data else 0
            rows = [{k: v for k, v in row.items() if k != "total_count"} for row in data]
            return rows, total_count
        return [], 0

    async def count(
        self,
        org_id: UUID,
        date_from: date,
        date_to: date,
        template_id: UUID | None = None,
        branch_id: UUID | None = None,
        department_id: UUID | None = None,
        operator_id: UUID | None = None,
        status: str | None = None,
        customer_query: str | None = None,
    ) -> int:
        """Count submissions matching filters."""
        rpc_params = {
            "p_org_id": str(org_id),
            "p_date_from": date_from.isoformat(),
            "p_date_to": date_to.isoformat(),
            "p_template_id": str(template_id) if template_id else None,
            "p_branch_id": str(branch_id) if branch_id else None,
            "p_department_id": str(department_id) if department_id else None,
            "p_operator_id": str(operator_id) if operator_id else None,
            "p_status": status,
            "p_customer_query": customer_query,
        }
        response = self.supabase.rpc("count_transaction_register", rpc_params).execute()
        if hasattr(response, "data") and response.data:
            return response.data[0].get("count", 0)
        return 0

    async def fetch_all(
        self,
        org_id: UUID,
        date_from: date,
        date_to: date,
        template_id: UUID | None = None,
        branch_id: UUID | None = None,
        department_id: UUID | None = None,
        operator_id: UUID | None = None,
        status: str | None = None,
        customer_query: str | None = None,
    ) -> list[dict]:
        """Fetch all matching rows for export (no pagination)."""
        rpc_params = {
            "p_org_id": str(org_id),
            "p_date_from": date_from.isoformat(),
            "p_date_to": date_to.isoformat(),
            "p_template_id": str(template_id) if template_id else None,
            "p_branch_id": str(branch_id) if branch_id else None,
            "p_department_id": str(department_id) if department_id else None,
            "p_operator_id": str(operator_id) if operator_id else None,
            "p_status": status,
            "p_customer_query": customer_query,
        }
        response = self.supabase.rpc("export_transaction_register", rpc_params).execute()
        if hasattr(response, "data") and response.data:
            return response.data
        return []
