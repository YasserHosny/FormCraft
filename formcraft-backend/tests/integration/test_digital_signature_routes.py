from uuid import UUID, uuid4

import pytest


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
        response = client.get("/api/sign/badtoken")
        # The route exists but token validation will return 404
        assert response.status_code in (404, 422)

    def test_public_otp_send_no_token_404(self, client):
        response = client.post("/api/sign/badtoken/otp/send")
        assert response.status_code in (404, 422)
