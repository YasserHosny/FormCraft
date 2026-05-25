import pytest
from uuid import uuid4

from app.services.quickfill_service import QuickFillService, DEFAULT_QUICKFILL_MAPPINGS


class TestQuickFillService:
    def test_service_init(self):
        svc = QuickFillService(client=None)
        assert svc is not None

    def test_default_mappings_cover_expected_keys(self):
        keys = {m["field_key"] for m in DEFAULT_QUICKFILL_MAPPINGS}
        assert "full_name" in keys
        assert "name" in keys
        assert "national_id" in keys
        assert "id_number" in keys
        assert "phone" in keys
        assert "mobile" in keys
        assert "address" in keys

    def test_resolve_customer_attribute_name_prefers_ar(self):
        svc = QuickFillService(client=None)
        customer = {"name_ar": "Ahmed", "name_en": "Ahmed En"}
        assert svc._resolve_customer_attribute(customer, "name") == "Ahmed"

    def test_resolve_customer_attribute_fallback_to_en(self):
        svc = QuickFillService(client=None)
        customer = {"name_ar": None, "name_en": "Ahmed En"}
        assert svc._resolve_customer_attribute(customer, "name") == "Ahmed En"

    def test_resolve_customer_attribute_identifier(self):
        svc = QuickFillService(client=None)
        customer = {"identifier": "1234567890"}
        assert svc._resolve_customer_attribute(customer, "identifier") == "1234567890"

    def test_resolve_customer_attribute_missing(self):
        svc = QuickFillService(client=None)
        customer = {}
        assert svc._resolve_customer_attribute(customer, "contact_phone") is None

    @pytest.mark.asyncio
    async def test_search_customers_short_query_raises(self):
        svc = QuickFillService(client=None)
        with pytest.raises(Exception) as exc:
            await svc.search_customers(query="a", org_id=uuid4())
        assert "400" in str(exc.value) or "Query must be at least 2 characters" in str(exc.value)
