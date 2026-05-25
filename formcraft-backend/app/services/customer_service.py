"""Customer profile CRUD with search, auto-populate, and audit logging."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.models.enums import IdentifierType
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    def __init__(self, client: Client):
        self.client = client

    # --- CRUD ---

    async def create_customer(
        self, data: CustomerCreate, org_id: UUID, created_by: UUID
    ) -> dict:
        """Create a new customer. Handle duplicate identifier by returning existing."""
        # Pre-check for duplicate identifier
        existing = (
            self.client.table("customers")
            .select("*")
            .eq("org_id", str(org_id))
            .eq("identifier_type", data.identifier_type.value)
            .eq("identifier", data.identifier)
            .maybe_single()
            .execute()
        )
        if existing and existing.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "detail": "Customer already exists",
                    "customer": existing.data,
                },
            )

        customer_data = {
            **data.model_dump(),
            "org_id": str(org_id),
            "created_by": str(created_by),
            "custom_fields": data.custom_fields or {},
        }

        result = self.client.table("customers").insert(customer_data).execute()
        if result.data:
            from app.core.audit import AuditLogger

            await AuditLogger(self.client).log_event(
                user_id=str(created_by),
                action="CUSTOMER_CREATED",
                resource_type="customer",
                resource_id=result.data[0]["id"],
                metadata={"name_ar": data.name_ar, "identifier": data.identifier},
            )
            return result.data[0]

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Failed to create customer",
        )

    async def get_by_id(self, customer_id: UUID, org_id: UUID) -> dict:
        result = (
            self.client.table("customers")
            .select("*")
            .eq("id", str(customer_id))
            .eq("org_id", str(org_id))
            .single()
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Customer not found")
        return result.data

    async def list_customers(
        self,
        org_id: UUID,
        page: int = 1,
        page_size: int = 25,
        is_active: bool | None = None,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
    ) -> tuple[list[dict], int]:
        query = (
            self.client.table("customers")
            .select("*", count="exact")
            .eq("org_id", str(org_id))
        )

        if is_active is not None:
            query = query.eq("is_active", is_active)

        # Validate sort_by to prevent injection
        allowed_sort = {"name_ar", "name_en", "created_at", "updated_at", "identifier"}
        if sort_by not in allowed_sort:
            sort_by = "updated_at"

        sort_dir = True if sort_order.lower() == "desc" else False
        query = query.order(sort_by, desc=sort_dir)

        start = (page - 1) * page_size
        result = query.range(start, start + page_size - 1).execute()

        return result.data or [], result.count or 0

    async def search_customers(
        self, org_id: UUID, query_text: str, page: int = 1, page_size: int = 25
    ) -> tuple[list[dict], int]:
        """Full-text search using search_vector or ILIKE fallback."""
        if len(query_text) < 3:
            # ILIKE fallback for short queries
            search_pattern = f"%{query_text}%"
            result = (
                self.client.table("customers")
                .select("*", count="exact")
                .eq("org_id", str(org_id))
                .or_(
                    f"name_ar.ilike.{search_pattern},name_en.ilike.{search_pattern},identifier.ilike.{search_pattern}"
                )
                .order("updated_at", desc=True)
                .range((page - 1) * page_size, page * page_size - 1)
                .execute()
            )
        else:
            # Full-text search
            result = (
                self.client.table("customers")
                .select("*", count="exact")
                .eq("org_id", str(org_id))
                .text_search("search_vector", query_text)
                .order("updated_at", desc=True)
                .range((page - 1) * page_size, page * page_size - 1)
                .execute()
            )

        return result.data or [], result.count or 0

    async def update_customer(
        self, customer_id: UUID, org_id: UUID, data: CustomerUpdate, actor_id: UUID
    ) -> dict:
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, "No fields to update"
            )

        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

        result = (
            self.client.table("customers")
            .update(update_data)
            .eq("id", str(customer_id))
            .eq("org_id", str(org_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Customer not found")

        from app.core.audit import AuditLogger

        await AuditLogger(self.client).log_event(
            user_id=str(actor_id),
            action="CUSTOMER_UPDATED",
            resource_type="customer",
            resource_id=str(customer_id),
            metadata={"changed_fields": list(update_data.keys())},
        )

        return result.data[0]

    async def deactivate_customer(
        self, customer_id: UUID, org_id: UUID, actor_id: UUID
    ) -> dict:
        return await self.update_customer(
            customer_id, org_id, CustomerUpdate(is_active=False), actor_id
        )

    async def reactivate_customer(
        self, customer_id: UUID, org_id: UUID, actor_id: UUID
    ) -> dict:
        return await self.update_customer(
            customer_id, org_id, CustomerUpdate(is_active=True), actor_id
        )

    async def delete_customer(self, customer_id: UUID, org_id: UUID) -> None:
        result = (
            self.client.table("customers")
            .delete()
            .eq("id", str(customer_id))
            .eq("org_id", str(org_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Customer not found")

    # --- Auto-populate ---

    async def get_auto_populate_data(
        self, customer_id: UUID, template_id: UUID, org_id: UUID
    ) -> list[dict]:
        """Return field mappings for auto-populating a form from customer data."""
        # Fetch customer directly by ID scoped to org (single query)
        result = (
            self.client.table("customers")
            .select("*")
            .eq("id", str(customer_id))
            .eq("org_id", str(org_id))
            .single()
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Customer not found")
        customer = result.data

        # Tier 1: Default mapping based on element key naming conventions
        tier1 = {
            "customer_name": customer.get("name_ar"),
            "customer_name_ar": customer.get("name_ar"),
            "customer_name_en": customer.get("name_en"),
            "applicant_name": customer.get("name_ar"),
            "national_id": customer.get("identifier")
            if customer.get("identifier_type") == "national_id"
            else None,
            "iqama_number": customer.get("identifier")
            if customer.get("identifier_type") == "iqama"
            else None,
            "commercial_register": customer.get("identifier")
            if customer.get("identifier_type") == "commercial_register"
            else None,
            "passport_number": customer.get("identifier")
            if customer.get("identifier_type") == "passport"
            else None,
            "phone": customer.get("contact_phone"),
            "mobile": customer.get("contact_phone"),
            "email": customer.get("contact_email"),
            "address": customer.get("address"),
        }

        # Tier 2: Designer overrides from customer_field_mappings
        tier2_result = (
            self.client.table("customer_field_mappings")
            .select("element_key, customer_field")
            .eq("template_id", str(template_id))
            .execute()
        )

        mappings = []
        used_keys = set()

        # Apply Tier 2 overrides first
        for mapping in tier2_result.data or []:
            element_key = mapping["element_key"]
            customer_field = mapping["customer_field"]
            value = customer.get(customer_field)
            if value is not None:
                mappings.append(
                    {
                        "element_key": element_key,
                        "value": value,
                        "source": "mapping",
                    }
                )
                used_keys.add(element_key)

        # Fill remaining with Tier 1 defaults
        for element_key, value in tier1.items():
            if element_key not in used_keys and value is not None:
                mappings.append(
                    {
                        "element_key": element_key,
                        "value": value,
                        "source": "default",
                    }
                )

        return mappings

    async def get_recent(
        self, user_id: UUID, org_id: UUID, limit: int = 5
    ) -> list[dict]:
        """Return recently used customers based on audit logs."""
        result = (
            self.client.table("audit_logs")
            .select("resource_id, created_at")
            .eq("user_id", str(user_id))
            .eq("action", "CUSTOMER_AUTO_POPULATED")
            .order("created_at", desc=True)
            .limit(100)
            .execute()
        )

        seen = set()
        recent = []
        for row in result.data or []:
            cid = row["resource_id"]
            if cid in seen:
                continue
            seen.add(cid)
            # Fetch customer basic info
            cust = (
                self.client.table("customers")
                .select("id, name_ar, name_en, identifier, identifier_type, is_active")
                .eq("id", cid)
                .eq("org_id", str(org_id))
                .single()
                .execute()
            )
            if cust.data:
                recent.append(
                    {
                        **cust.data,
                        "last_used_at": row["created_at"],
                    }
                )
            if len(recent) >= limit:
                break

        return recent

    # --- Submission history ---

    async def get_submissions(
        self,
        customer_id: UUID,
        org_id: UUID,
        page: int = 1,
        page_size: int = 25,
        template_id: UUID | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> tuple[list[dict], int]:
        query = (
            self.client.table("form_submissions")
            .select(
                "*, templates!inner(name), profiles!inner(display_name)", count="exact"
            )
            .eq("customer_id", str(customer_id))
            .eq("templates.org_id", str(org_id))
            .order("created_at", desc=True)
        )

        if template_id:
            query = query.eq("template_id", str(template_id))
        if date_from:
            query = query.gte("created_at", date_from)
        if date_to:
            query = query.lte("created_at", date_to)

        start = (page - 1) * page_size
        result = query.range(start, start + page_size - 1).execute()

        submissions = []
        for row in result.data or []:
            template = row.get("templates") or {}
            profile = row.get("profiles") or {}
            submissions.append(
                {
                    "id": row["id"],
                    "template_id": row["template_id"],
                    "template_name": template.get("name", ""),
                    "status": row.get("status", ""),
                    "created_at": row["created_at"],
                    "created_by_name": profile.get("display_name", ""),
                }
            )

        return submissions, result.count or 0
