"""Unified global search service across templates, submissions, and customers."""

from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client


class SearchService:
    def __init__(self, client: Client):
        self.client = client

    async def search_global(
        self,
        query: str,
        org_id: UUID,
        types: list[str] | None = None,
        limit_per_type: int = 5,
        branch_id: UUID | None = None,
        department_id: UUID | None = None,
    ) -> list[dict]:
        """Search across templates, submissions, and customers using full-text search and trigram similarity."""
        if not query or len(query.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query must be at least 2 characters",
            )

        clean_query = query.strip()
        types_filter = types or ["template", "submission", "customer"]
        results: list[dict] = []

        # Use materialized view for templates and customers; direct table for submissions if needed
        for entity_type in types_filter:
            if entity_type == "template":
                items = await self._search_templates(clean_query, org_id, limit_per_type)
                results.extend(items)
            elif entity_type == "submission":
                items = await self._search_submissions(
                    clean_query, org_id, limit_per_type, branch_id, department_id
                )
                results.extend(items)
            elif entity_type == "customer":
                items = await self._search_customers(clean_query, org_id, limit_per_type)
                results.extend(items)

        return results

    async def _search_templates(self, query: str, org_id: UUID, limit: int) -> list[dict]:
        # Full-text search on materialized view
        fts_results = (
            self.client.rpc(
                "search_mv_global",
                {
                    "p_query": query,
                    "p_org_id": str(org_id),
                    "p_entity_type": "template",
                    "p_limit": limit,
                },
            ).execute()
        )

        # Fallback to direct similarity if RPC not available
        if not fts_results.data:
            similarity_results = (
                self.client.table("mv_global_search")
                .select("id, entity_type, title, subtitle, metadata")
                .eq("org_id", str(org_id))
                .eq("entity_type", "template")
                .ilike("title", f"%{query}%")
                .limit(limit)
                .execute()
            )
            data = similarity_results.data or []
        else:
            data = fts_results.data

        return [
            {
                "type": "template",
                "id": item["id"],
                "title": item["title"],
                "subtitle": item["subtitle"],
                "metadata": item.get("metadata", {}),
            }
            for item in data
        ]

    async def _search_submissions(
        self,
        query: str,
        org_id: UUID,
        limit: int,
        branch_id: UUID | None,
        department_id: UUID | None,
    ) -> list[dict]:
        # Exact reference number match first
        exact = (
            self.client.table("mv_global_search")
            .select("id, entity_type, title, subtitle, metadata")
            .eq("org_id", str(org_id))
            .eq("entity_type", "submission")
            .eq("title", query)
            .limit(limit)
            .execute()
        )
        data = exact.data or []

        # If no exact match, try fts on materialized view
        if not data:
            fts = (
                self.client.table("mv_global_search")
                .select("id, entity_type, title, subtitle, metadata")
                .eq("org_id", str(org_id))
                .eq("entity_type", "submission")
                .ilike("title", f"%{query}%")
                .limit(limit)
                .execute()
            )
            data = fts.data or []

        # Apply branch/department filters if provided
        if branch_id or department_id:
            # Fetch matching IDs from direct table with RLS
            direct = self.client.table("form_submissions").select("id")
            direct = direct.eq("org_id", str(org_id))
            if branch_id:
                direct = direct.eq("branch_id", str(branch_id))
            if department_id:
                direct = direct.eq("department_id", str(department_id))
            direct = direct.ilike("reference_number", f"%{query}%").limit(limit)
            direct_ids = {row["id"] for row in (direct.execute().data or [])}
            data = [item for item in data if item["id"] in direct_ids]

        return [
            {
                "type": "submission",
                "id": item["id"],
                "title": item["title"],
                "subtitle": item["subtitle"],
                "metadata": item.get("metadata", {}),
            }
            for item in data
        ]

    async def _search_customers(self, query: str, org_id: UUID, limit: int) -> list[dict]:
        # Use direct customers table with similarity and ilike for best fuzzy matching
        # unaccent and pg_trgm are handled in the query via RPC or direct select
        rpc_result = (
            self.client.rpc(
                "search_customers_fuzzy",
                {
                    "p_query": query,
                    "p_org_id": str(org_id),
                    "p_limit": limit,
                },
            ).execute()
        )

        if rpc_result.data:
            data = rpc_result.data
        else:
            # Fallback: direct query using ilike on identifier/phone and similarity on name
            # Note: Supabase client does not expose similarity() directly, so we use ilike fallbacks
            direct = (
                self.client.table("customers")
                .select(
                    "id, name_ar, name_en, identifier, contact_phone, "
                    "(SELECT COUNT(*) FROM form_submissions WHERE customer_id = customers.id) as recent_submissions_count"
                )
                .eq("org_id", str(org_id))
                .eq("is_active", True)
                .or_(f"identifier.ilike.%{query}%,contact_phone.ilike.%{query}%,name_ar.ilike.%{query}%,name_en.ilike.%{query}%")
                .limit(limit)
                .execute()
            )
            data = direct.data or []

        return [
            {
                "type": "customer",
                "id": item["id"],
                "title": item.get("name_ar") or item.get("name_en") or "",
                "subtitle": f"ID: {item.get('identifier', '')}",
                "metadata": {
                    "identifier": item.get("identifier"),
                    "contact_phone": item.get("contact_phone"),
                    "recent_submissions_count": item.get("recent_submissions_count", 0),
                },
            }
            for item in data
        ]

    async def search_by_reference_number(
        self,
        reference_number: str,
        org_id: UUID,
        branch_id: UUID | None = None,
        department_id: UUID | None = None,
    ) -> dict | None:
        """Exact-match search for a submission by reference number."""
        query = (
            self.client.table("form_submissions")
            .select(
                "id, reference_number, template_id, templates(name), "
                "customer_id, customers(name_ar), status, created_at"
            )
            .eq("org_id", str(org_id))
            .eq("reference_number", reference_number)
        )

        if branch_id:
            query = query.eq("branch_id", str(branch_id))
        if department_id:
            query = query.eq("department_id", str(department_id))

        result = query.maybe_single().execute()
        if not result.data:
            return None

        sub = result.data
        return {
            "found": True,
            "submission": {
                "id": sub["id"],
                "reference_number": sub["reference_number"],
                "template_name": sub.get("templates", {}).get("name") if isinstance(sub.get("templates"), dict) else "",
                "customer_name": sub.get("customers", {}).get("name_ar") if isinstance(sub.get("customers"), dict) else "",
                "status": sub.get("status"),
                "created_at": sub.get("created_at"),
            },
        }
