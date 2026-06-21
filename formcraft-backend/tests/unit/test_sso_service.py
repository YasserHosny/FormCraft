"""Unit tests for sso_service."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.models.identity import ProviderType
from app.services.sso_service import SsoService

_SUPA_PATCH = "app.services.sso_service.get_supabase_client"


def _mock_supa_empty():
    m = MagicMock()
    m.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    m.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(data=[])
    return m


class TestSsoService:
    def test_get_provider_by_domain_no_match(self):
        with patch(_SUPA_PATCH, return_value=_mock_supa_empty()):
            result = SsoService.get_provider_by_domain("nonexistent.com")
        assert result is None

    def test_apply_jit_mappings_no_match(self):
        user_id = uuid4()
        org_id = uuid4()
        with patch(_SUPA_PATCH, return_value=_mock_supa_empty()):
            result = SsoService.apply_jit_mappings(user_id, org_id, {"groups": []})
        assert result.get("fallback") == "strip_access"
