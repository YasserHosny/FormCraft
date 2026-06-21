from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest

_SUPA_PATCH = "app.api.routes.digital_signatures.get_supabase_client"


def _mock_supa_empty():
    """Return a Supabase mock where token lookups find nothing."""
    m = MagicMock()
    empty = MagicMock()
    empty.data = []
    m.table.return_value.select.return_value.eq.return_value.execute.return_value = empty
    m.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = empty
    return m


class TestDigitalSignatureRoutes:
    def test_list_workflows_requires_auth(self, client):
        response = client.get("/api/digital-signatures/workflows")
        assert response.status_code == 401

    def test_create_workflow_requires_auth(self, client):
        response = client.post("/api/digital-signatures/workflows", json={"name": "WF"})
        assert response.status_code == 401

    def test_create_request_requires_auth(self, client):
        response = client.post("/api/digital-signatures/requests", json={})
        assert response.status_code == 401

    def test_public_signer_metadata_no_token_404(self, client):
        with patch(_SUPA_PATCH, return_value=_mock_supa_empty()):
            response = client.get("/api/sign/badtoken")
        assert response.status_code in (404, 422)

    def test_public_otp_send_no_token_404(self, client):
        with patch(_SUPA_PATCH, return_value=_mock_supa_empty()):
            response = client.post("/api/sign/badtoken/otp/send")
        assert response.status_code in (404, 422)
