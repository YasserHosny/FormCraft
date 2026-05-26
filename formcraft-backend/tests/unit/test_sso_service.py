"""Unit tests for sso_service."""

from uuid import uuid4

import pytest

from app.models.identity import ProviderType
from app.services.sso_service import SsoService


class TestSsoService:
    def test_get_provider_by_domain_no_match(self):
        result = SsoService.get_provider_by_domain("nonexistent.com")
        assert result is None

    def test_apply_jit_mappings_no_match(self):
        user_id = uuid4()
        org_id = uuid4()
        result = SsoService.apply_jit_mappings(user_id, org_id, {"groups": []})
        assert result.get("fallback") == "strip_access"
