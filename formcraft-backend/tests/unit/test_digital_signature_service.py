from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException

from app.services.digital_signature_service import DigitalSignatureService
from tests.conftest import make_supabase_response

ORG_ID = UUID("44444444-4444-4444-4444-444444444444")
ACTOR_ID = UUID("11111111-1111-1111-1111-111111111111")
WORKFLOW_ID = UUID("55555555-5555-5555-5555-555555555555")
REQUEST_ID = UUID("66666666-6666-6666-6666-666666666666")
RECIPIENT_ID = UUID("77777777-7777-7777-7777-777777777777")


def _workflow(ordered=False):
    return {
        "id": str(WORKFLOW_ID),
        "org_id": str(ORG_ID),
        "template_id": str(uuid4()),
        "name": "Test Workflow",
        "is_ordered": ordered,
        "expiration_days": 7,
        "decline_policy": "stop",
        "require_all_signers": True,
        "is_active": True,
    }


def _client_with_data(data_map):
    client = MagicMock()

    def _table(name):
        t = MagicMock()
        chain = MagicMock()
        chain.eq.return_value = chain
        chain.single.return_value = chain
        chain.execute.return_value = make_supabase_response(data_map.get(name))
        t.select.return_value = chain
        t.insert.return_value = chain
        t.update.return_value = chain
        return t

    client.table.side_effect = _table
    return client


class TestDigitalSignatureService:
    @pytest.mark.asyncio
    async def test_create_workflow_success(self):
        client = _client_with_data({
            "signature_workflows": _workflow(),
        })
        service = DigitalSignatureService(client)
        result = await service.create_workflow(ORG_ID, ACTOR_ID, {
            "name": "Test Workflow",
            "template_id": uuid4(),
            "is_ordered": False,
            "expiration_days": 7,
            "decline_policy": "stop",
            "require_all_signers": True,
        })
        assert result["name"] == "Test Workflow"

    @pytest.mark.asyncio
    async def test_create_request_workflow_not_active_raises_422(self):
        client = _client_with_data({
            "signature_workflows": None,
        })
        service = DigitalSignatureService(client)
        with pytest.raises(HTTPException) as exc:
            await service.create_request(ORG_ID, ACTOR_ID, {
                "workflow_id": WORKFLOW_ID,
                "submission_id": uuid4(),
                "signers": [],
            })
        assert exc.value.status_code == 422

    @pytest.mark.asyncio
    async def test_create_request_too_many_signers_raises_422(self):
        wf = _workflow()
        client = _client_with_data({
            "signature_workflows": wf,
            "signature_requests": {"id": str(REQUEST_ID)},
        })
        service = DigitalSignatureService(client)
        signers = [{"signer_type": "internal", "profile_id": str(uuid4()), "name": f"Signer {i}"} for i in range(11)]
        with pytest.raises(HTTPException) as exc:
            await service.create_request(ORG_ID, ACTOR_ID, {
                "workflow_id": WORKFLOW_ID,
                "submission_id": uuid4(),
                "signers": signers,
            })
        assert exc.value.status_code == 422

    @pytest.mark.asyncio
    async def test_send_request_not_draft_raises_409(self):
        client = _client_with_data({
            "signature_requests": {"id": str(REQUEST_ID), "status": "sent", "workflow_id": str(WORKFLOW_ID), "org_id": str(ORG_ID)},
        })
        service = DigitalSignatureService(client)
        with pytest.raises(HTTPException) as exc:
            await service.send_request(REQUEST_ID, ORG_ID, ACTOR_ID)
        assert exc.value.status_code == 409

    @pytest.mark.asyncio
    async def test_cancel_request_already_canceled_raises_409(self):
        client = _client_with_data({
            "signature_requests": {"id": str(REQUEST_ID), "status": "canceled", "workflow_id": str(WORKFLOW_ID), "org_id": str(ORG_ID)},
        })
        service = DigitalSignatureService(client)
        with pytest.raises(HTTPException) as exc:
            await service.cancel_request(REQUEST_ID, ORG_ID, ACTOR_ID)
        assert exc.value.status_code == 409
