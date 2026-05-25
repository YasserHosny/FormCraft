from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID, uuid4

from fastapi import HTTPException, status

from app.core.audit import AuditLogger


class InternalPaymentProvider:
    """MVP provider that completes payments inside FormCraft transaction records."""

    def charge(self, amount: Decimal, currency: str, idempotency_key: str | None = None) -> dict:
        return {
            "status": "completed",
            "provider": "internal",
            "provider_reference": idempotency_key or str(uuid4()),
            "amount": amount,
            "currency": currency,
        }


class MarketplaceService:
    def __init__(self, client, payment_provider: InternalPaymentProvider | None = None):
        self.client = client
        self.payment_provider = payment_provider or InternalPaymentProvider()

    async def list_listings(
        self,
        *,
        page: int = 1,
        page_size: int = 24,
        search: str | None = None,
        country: str | None = None,
        category: str | None = None,
        language: str | None = None,
        compliance: str | None = None,
        price_type: str | None = None,
        sort_by: str = "quality_score",
        sort_dir: str = "desc",
    ) -> tuple[list[dict], int]:
        offset = (page - 1) * page_size
        query = self.client.table("marketplace_listings").select("*", count="exact").eq("status", "active")
        if country:
            query = query.eq("country", country)
        if category:
            query = query.eq("category", category)
        if language:
            query = query.eq("language", language)
        if price_type:
            query = query.eq("price_type", price_type)
        if search:
            query = query.ilike("name", f"%{search}%")
        if compliance:
            for badge in [item.strip() for item in compliance.split(",") if item.strip()]:
                query = query.contains("compliance_badges", [badge])
        sort_column = sort_by if sort_by in {"quality_score", "download_count", "average_rating", "created_at"} else "quality_score"
        result = (
            query.order(sort_column, desc=sort_dir != "asc")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        return result.data or [], result.count or len(result.data or [])

    async def get_listing_detail(self, listing_id: UUID) -> dict:
        listing = self._get_listing(listing_id, active_only=True)
        template_id = listing.get("template_id")
        template_preview = {}
        if template_id:
            template_preview = await self._build_template_preview(UUID(str(template_id)))
        listing["template_preview"] = template_preview
        listing["sample_pdf_url"] = listing.get("sample_pdf_path")
        listing["dependency_warnings"] = self._dependency_warnings(template_preview.get("elements", []))
        return listing

    async def publish_listing(self, *, org_id: UUID, actor_id: UUID, data: dict) -> dict:
        template = self._get_template(UUID(str(data["template_id"])))
        if str(template.get("org_id")) != str(org_id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Template belongs to another organization")
        if template.get("status") != "published":
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Only published templates can be listed")

        row = {
            "template_id": str(data["template_id"]),
            "publisher_org_id": str(org_id),
            "created_by": str(actor_id),
            "name": template.get("name"),
            "description": data.get("description", ""),
            "tags": data.get("tags", []),
            "preview_image_urls": data.get("preview_image_urls", []),
            "category": template.get("category", "general"),
            "country": template.get("country", "EG"),
            "language": template.get("language", "ar"),
            "compliance_badges": data.get("compliance_badges", []),
            "price_type": data.get("price_type", "free"),
            "price_amount": str(data["price_amount"]) if data.get("price_amount") is not None else None,
            "currency": data.get("currency", "USD"),
            "status": "submitted",
            "review_status": "pending",
            "published_version": template.get("version", 1),
        }
        result = self.client.table("marketplace_listings").insert(row).execute()
        listing = result.data[0]
        await self._audit(actor_id, "MARKETPLACE_LISTING_SUBMITTED", "marketplace_listing", listing["id"], {"template_id": row["template_id"]})
        return listing

    async def moderate_listing(self, *, listing_id: UUID, actor_id: UUID, action: str, comment: str | None = None) -> dict:
        status_by_action = {
            "approve": {"status": "active", "review_status": "approved"},
            "reject": {"status": "rejected", "review_status": "rejected"},
            "suspend": {"status": "suspended"},
            "reactivate": {"status": "active"},
            "archive": {"status": "archived"},
        }
        update = status_by_action[action]
        result = (
            self.client.table("marketplace_listings")
            .update(update)
            .eq("id", str(listing_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Marketplace listing not found")
        await self._audit(actor_id, f"MARKETPLACE_LISTING_{action.upper()}", "marketplace_listing", str(listing_id), {"comment": comment})
        return result.data[0]

    async def purchase_listing(
        self,
        *,
        listing_id: UUID,
        consumer_org_id: UUID,
        actor_id: UUID,
        provider: str = "internal",
        idempotency_key: str | None = None,
    ) -> dict:
        listing = self._get_listing(listing_id, active_only=True)
        if listing.get("price_type") != "premium":
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Listing is free")

        amount = Decimal(str(listing.get("price_amount") or "0")).quantize(Decimal("0.01"))
        platform_share = (amount * Decimal("0.30")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        publisher_share = amount - platform_share
        payment = self.payment_provider.charge(amount, listing.get("currency", "USD"), idempotency_key)
        row = {
            "listing_id": str(listing_id),
            "consumer_org_id": str(consumer_org_id),
            "publisher_org_id": listing["publisher_org_id"],
            "amount": str(amount),
            "currency": listing.get("currency", "USD"),
            "platform_share": str(platform_share),
            "publisher_share": str(publisher_share),
            "payment_status": payment["status"],
            "provider": provider,
            "provider_reference": payment["provider_reference"],
        }
        result = self.client.table("marketplace_transactions").insert(row).execute()
        transaction = result.data[0]
        await self._audit(actor_id, "MARKETPLACE_TEMPLATE_PURCHASED", "marketplace_transaction", transaction["id"], {"listing_id": str(listing_id)})
        return {
            "transaction_id": transaction["id"],
            "payment_status": transaction["payment_status"],
            "amount": amount,
            "currency": row["currency"],
            "publisher_share": publisher_share,
            "platform_share": platform_share,
        }

    async def import_listing(
        self,
        *,
        listing_id: UUID,
        consumer_org_id: UUID,
        actor_id: UUID,
        draft_name: str | None = None,
        reference_mappings: dict[str, str] | None = None,
        accept_disabled_dependencies: bool = False,
    ) -> dict:
        listing = self._get_listing(listing_id, active_only=True)
        if listing.get("price_type") == "premium" and not self._has_completed_transaction(listing_id, consumer_org_id):
            raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, "Premium listing purchase required before import")

        template = self._get_template(UUID(str(listing["template_id"])))
        pages = self._get_pages(UUID(str(listing["template_id"])))
        elements = self._get_elements([page["id"] for page in pages])
        warnings = self._dependency_warnings(elements)
        if warnings and not reference_mappings and not accept_disabled_dependencies:
            raise HTTPException(status.HTTP_409_CONFLICT, {"detail": "Reference remapping required", "warnings": warnings})

        new_template_id = str(uuid4())
        template_row = {
            "id": new_template_id,
            "org_id": str(consumer_org_id),
            "created_by": str(actor_id),
            "name": draft_name or f"{listing['name']} (Marketplace)",
            "description": template.get("description", ""),
            "category": template.get("category", "general"),
            "language": template.get("language", "ar"),
            "country": template.get("country", "EG"),
            "status": "draft",
            "version": 1,
            "lineage_id": new_template_id,
        }
        self.client.table("templates").insert(template_row).execute()

        page_id_map: dict[str, str] = {}
        for page in pages:
            page_id = str(uuid4())
            page_id_map[str(page["id"])] = page_id
            self.client.table("pages").insert(
                {
                    "id": page_id,
                    "template_id": new_template_id,
                    "width_mm": page.get("width_mm", 210),
                    "height_mm": page.get("height_mm", 297),
                    "background_asset": page.get("background_asset"),
                    "sort_order": page.get("sort_order", 0),
                }
            ).execute()

        for element in elements:
            clean = dict(element)
            clean.pop("id", None)
            clean["page_id"] = page_id_map.get(str(element.get("page_id")))
            clean["created_by"] = str(actor_id)
            clean["validation"] = self._sanitize_validation(clean.get("validation"), reference_mappings or {}, warnings)
            self.client.table("elements").insert(clean).execute()

        import_row = {
            "listing_id": str(listing_id),
            "consumer_org_id": str(consumer_org_id),
            "imported_template_id": new_template_id,
            "imported_by": str(actor_id),
            "listing_version": listing.get("published_version", 1),
            "remapping_status": "completed" if reference_mappings else ("pending" if warnings else "not_required"),
            "disabled_dependency_warnings": warnings,
            "source_snapshot": {"listing_id": str(listing_id), "name": listing.get("name"), "version": listing.get("published_version", 1)},
        }
        import_result = self.client.table("marketplace_imports").insert(import_row).execute()
        self.client.table("marketplace_listings").update({"download_count": int(listing.get("download_count") or 0) + 1}).eq("id", str(listing_id)).execute()
        await self._audit(actor_id, "MARKETPLACE_TEMPLATE_IMPORTED", "marketplace_import", import_result.data[0]["id"], {"listing_id": str(listing_id), "template_id": new_template_id})
        return {
            "import_id": import_result.data[0]["id"],
            "template_id": new_template_id,
            "remapping_status": import_row["remapping_status"],
            "disabled_dependency_warnings": warnings,
        }

    async def create_or_update_review(self, *, listing_id: UUID, consumer_org_id: UUID, actor_id: UUID, import_id: UUID, rating: int, review_text: str) -> dict:
        import_row = self._get_import(import_id)
        if str(import_row.get("listing_id")) != str(listing_id) or str(import_row.get("consumer_org_id")) != str(consumer_org_id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Review requires a verified import")
        row = {
            "listing_id": str(listing_id),
            "consumer_org_id": str(consumer_org_id),
            "reviewer_id": str(actor_id),
            "import_id": str(import_id),
            "rating": rating,
            "review_text": review_text,
            "verified_import": True,
            "status": "active",
        }
        existing = self._find_review(listing_id, consumer_org_id)
        if existing:
            result = self.client.table("marketplace_reviews").update(row).eq("id", existing["id"]).execute()
            review = result.data[0]
        else:
            result = self.client.table("marketplace_reviews").insert(row).execute()
            review = result.data[0]
        await self.recalculate_rating(listing_id)
        await self._audit(actor_id, "MARKETPLACE_REVIEW_SUBMITTED", "marketplace_review", review["id"], {"listing_id": str(listing_id), "rating": rating})
        return review

    async def list_reviews(self, listing_id: UUID) -> tuple[list[dict], int]:
        result = (
            self.client.table("marketplace_reviews")
            .select("*", count="exact")
            .eq("listing_id", str(listing_id))
            .eq("status", "active")
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or [], result.count or len(result.data or [])

    async def recalculate_rating(self, listing_id: UUID) -> None:
        reviews, _ = await self.list_reviews(listing_id)
        count = len(reviews)
        average = None
        if count:
            average = round(sum(int(review["rating"]) for review in reviews) / count, 2)
        self.client.table("marketplace_listings").update({"average_rating": average, "review_count": count}).eq("id", str(listing_id)).execute()

    def _get_listing(self, listing_id: UUID, *, active_only: bool = False) -> dict:
        query = self.client.table("marketplace_listings").select("*").eq("id", str(listing_id))
        if active_only:
            query = query.eq("status", "active")
        result = query.single().execute()
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Marketplace listing not found")
        return result.data

    def _get_template(self, template_id: UUID) -> dict:
        result = self.client.table("templates").select("*").eq("id", str(template_id)).single().execute()
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Template not found")
        return result.data

    def _get_pages(self, template_id: UUID) -> list[dict]:
        result = self.client.table("pages").select("*").eq("template_id", str(template_id)).order("sort_order").execute()
        return result.data or []

    def _get_elements(self, page_ids: list[str]) -> list[dict]:
        if not page_ids:
            return []
        result = self.client.table("elements").select("*").in_("page_id", page_ids).execute()
        return result.data or []

    async def _build_template_preview(self, template_id: UUID) -> dict:
        template = self._get_template(template_id)
        pages = self._get_pages(template_id)
        elements = self._get_elements([page["id"] for page in pages])
        return {"template": template, "pages": pages, "elements": elements}

    def _has_completed_transaction(self, listing_id: UUID, org_id: UUID) -> bool:
        result = (
            self.client.table("marketplace_transactions")
            .select("id")
            .eq("listing_id", str(listing_id))
            .eq("consumer_org_id", str(org_id))
            .eq("payment_status", "completed")
            .execute()
        )
        return bool(result.data)

    def _get_import(self, import_id: UUID) -> dict:
        result = self.client.table("marketplace_imports").select("*").eq("id", str(import_id)).single().execute()
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Marketplace import not found")
        return result.data

    def _find_review(self, listing_id: UUID, org_id: UUID) -> dict | None:
        result = (
            self.client.table("marketplace_reviews")
            .select("*")
            .eq("listing_id", str(listing_id))
            .eq("consumer_org_id", str(org_id))
            .execute()
        )
        return (result.data or [None])[0]

    def _dependency_warnings(self, elements: list[dict]) -> list[str]:
        warnings = []
        for element in elements:
            validation = element.get("validation") or {}
            if isinstance(validation, dict) and validation.get("reference_list_id"):
                warnings.append(f"Element {element.get('key')} requires reference remapping")
            if isinstance(validation, dict) and validation.get("custom_validator_id"):
                warnings.append(f"Element {element.get('key')} uses an unsupported custom validator")
        return warnings

    def _sanitize_validation(self, validation, reference_mappings: dict[str, str], warnings: list[str]):
        if not isinstance(validation, dict):
            return validation
        clean = dict(validation)
        reference_id = clean.get("reference_list_id")
        if reference_id:
            mapped = reference_mappings.get(str(reference_id))
            if mapped:
                clean["reference_list_id"] = mapped
            else:
                clean.pop("reference_list_id", None)
                clean["disabled_reason"] = "reference_remapping_required"
        if clean.get("custom_validator_id"):
            clean.pop("custom_validator_id", None)
            clean["disabled_reason"] = "unsupported_custom_validator"
        return clean

    async def _audit(self, actor_id: UUID, action: str, resource_type: str, resource_id: str, metadata: dict) -> None:
        await AuditLogger(self.client).log_event(
            user_id=str(actor_id),
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            metadata=metadata,
        )
