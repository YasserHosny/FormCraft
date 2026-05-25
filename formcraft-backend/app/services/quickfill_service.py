"""QuickFill service for mapping customer data to template fields."""

from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client


DEFAULT_QUICKFILL_MAPPINGS: list[dict] = [
    {"field_key": "full_name", "customer_attribute": "name"},
    {"field_key": "name", "customer_attribute": "name"},
    {"field_key": "national_id", "customer_attribute": "identifier"},
    {"field_key": "id_number", "customer_attribute": "identifier"},
    {"field_key": "phone", "customer_attribute": "contact_phone"},
    {"field_key": "mobile", "customer_attribute": "contact_phone"},
    {"field_key": "address", "customer_attribute": "address"},
]


class QuickFillService:
    def __init__(self, client: Client):
        self.client = client

    async def get_quickfill_mappings(self, org_id: UUID) -> list[dict]:
        """Retrieve configured field mappings for an organization."""
        result = (
            self.client.table("quickfill_mappings")
            .select("field_key, customer_attribute")
            .eq("org_id", str(org_id))
            .execute()
        )
        data = result.data or []
        if not data:
            # Return defaults if none configured
            return DEFAULT_QUICKFILL_MAPPINGS
        return data

    async def update_quickfill_mappings(
        self, org_id: UUID, mappings: list[dict], updated_by: UUID
    ) -> list[dict]:
        """Replace all mappings for an organization."""
        # Delete existing
        self.client.table("quickfill_mappings").delete().eq("org_id", str(org_id)).execute()

        # Insert new
        rows = [
            {
                "org_id": str(org_id),
                "field_key": m["field_key"],
                "customer_attribute": m["customer_attribute"],
            }
            for m in mappings
        ]
        if rows:
            result = self.client.table("quickfill_mappings").insert(rows).execute()
            return result.data or []
        return []

    async def map_customer_to_fields(
        self, customer_id: UUID, template_id: UUID, org_id: UUID
    ) -> dict:
        """Map a customer's attributes to a template's element keys."""
        # Fetch customer
        customer_result = (
            self.client.table("customers")
            .select("name_ar, name_en, identifier, contact_phone, address, custom_fields")
            .eq("id", str(customer_id))
            .eq("org_id", str(org_id))
            .maybe_single()
            .execute()
        )
        if not customer_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found",
            )
        customer = customer_result.data

        # Fetch template elements to know available field keys
        elements_result = (
            self.client.table("elements")
            .select("key, label, type")
            .eq("template_id", str(template_id))
            .execute()
        )
        elements = elements_result.data or []
        element_keys = {e["key"].lower(): e for e in elements}

        # Get mappings
        mappings = await self.get_quickfill_mappings(org_id)
        mapping_dict = {m["field_key"].lower(): m["customer_attribute"] for m in mappings}

        mapped_fields: list[dict] = []
        unmapped_customer_attributes: list[str] = []

        for element in elements:
            key = element["key"].lower()
            attr = mapping_dict.get(key)
            if not attr:
                continue

            value = self._resolve_customer_attribute(customer, attr)
            if value is not None and value != "":
                mapped_fields.append({
                    "field_key": element["key"],
                    "field_label": element.get("label", element["key"]),
                    "value": value,
                    "source_attribute": attr,
                    "confidence": "high",
                })

        # Determine unmapped customer attributes
        all_attrs = {m["customer_attribute"] for m in mappings}
        mapped_attrs = {f["source_attribute"] for f in mapped_fields}
        unmapped_customer_attributes = sorted(list(all_attrs - mapped_attrs))

        return {
            "customer_id": str(customer_id),
            "template_id": str(template_id),
            "mapped_fields": mapped_fields,
            "unmapped_customer_attributes": unmapped_customer_attributes,
            "mapping_count": len(mapped_fields),
        }

    def _resolve_customer_attribute(self, customer: dict, attribute: str) -> str | None:
        """Resolve a customer attribute value, handling special cases like name."""
        if attribute == "name":
            return customer.get("name_ar") or customer.get("name_en") or None
        return customer.get(attribute)

    async def search_customers(
        self,
        query: str,
        org_id: UUID,
        limit: int = 10,
    ) -> list[dict]:
        """Fuzzy search customers across name, identifier, and phone."""
        if not query or len(query.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query must be at least 2 characters",
            )

        clean = query.strip()
        # Direct query with ilike (similarity via pg_trgm requires raw SQL or RPC)
        result = (
            self.client.table("customers")
            .select(
                "id, name_ar, name_en, identifier, contact_phone, "
                "(SELECT COUNT(*) FROM form_submissions WHERE customer_id = customers.id) as recent_submissions_count"
            )
            .eq("org_id", str(org_id))
            .eq("is_active", True)
            .or_(
                f"identifier.ilike.%{clean}%,"
                f"contact_phone.ilike.%{clean}%,"
                f"name_ar.ilike.%{clean}%,"
                f"name_en.ilike.%{clean}%"
            )
            .limit(limit)
            .execute()
        )
        data = result.data or []
        return [
            {
                "id": c["id"],
                "name_ar": c.get("name_ar"),
                "name_en": c.get("name_en"),
                "identifier": c.get("identifier"),
                "contact_phone": c.get("contact_phone"),
                "recent_submissions_count": c.get("recent_submissions_count", 0),
                "match_score": 1.0,  # Best-effort; real similarity needs raw SQL
            }
            for c in data
        ]
