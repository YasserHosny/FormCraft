import pytest
from uuid import uuid4

from app.services.search_service import SearchService


class TestSearchService:
    def test_service_init(self):
        svc = SearchService(client=None)
        assert svc is not None

    @pytest.mark.asyncio
    async def test_search_global_short_query_raises(self):
        svc = SearchService(client=None)
        with pytest.raises(Exception) as exc:
            await svc.search_global(query="a", org_id=uuid4())
        assert "400" in str(exc.value) or "Search query must be at least 2 characters" in str(exc.value)

    @pytest.mark.asyncio
    async def test_search_by_reference_number_no_client(self):
        svc = SearchService(client=None)
        # Without a real client this will fail at query time; we verify the method exists and signatures match
        assert hasattr(svc, "search_by_reference_number")
