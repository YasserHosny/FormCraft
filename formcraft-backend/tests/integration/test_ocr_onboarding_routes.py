from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.routes import ocr_onboarding
from app.models.user import UserProfile


class DummyService:
    def __init__(self):
        self.calls = []

    async def list_batches(self, **kwargs):
        self.calls.append(("list", kwargs))
        return [], 0

    async def get_batch(self, **kwargs):
        self.calls.append(("get", kwargs))
        return {
            "id": kwargs["batch_id"],
            "name": "Batch",
            "status": "queued",
            "confidence_threshold": 0.85,
            "total_items": 0,
            "processed_items": 0,
            "accepted_items": 0,
            "failed_items": 0,
            "duplicate_items": 0,
            "created_at": "2026-05-26T00:00:00Z",
            "updated_at": "2026-05-26T00:00:00Z",
            "items": [],
        }

    async def bulk_accept(self, **kwargs):
        self.calls.append(("bulk_accept", kwargs))
        return {"accepted_count": len(kwargs["item_ids"]), "skipped": []}

    async def retry_item(self, **kwargs):
        self.calls.append(("retry", kwargs))
        return {
            "id": kwargs["item_id"],
            "batch_id": kwargs["batch_id"],
            "file_name": "scan.png",
            "status": "queued",
            "mime_type": "image/png",
            "file_size_bytes": 10,
            "confidence": None,
            "likely_type": None,
            "category": None,
            "language": None,
            "page_count": 1,
            "retry_count": 1,
            "last_error": None,
            "converted_template_id": None,
            "created_at": "2026-05-26T00:00:00Z",
            "updated_at": "2026-05-26T00:00:00Z",
        }


def user(org_id="default"):
    return UserProfile(
        id=uuid4(),
        role="admin",
        language="ar",
        org_id=uuid4() if org_id == "default" else org_id,
        created_at="2026-05-26T00:00:00Z",
        updated_at="2026-05-26T00:00:00Z",
    )


@pytest.mark.asyncio
async def test_list_batches_route_delegates_to_service():
    service = DummyService()

    result = await ocr_onboarding.list_batches(
        current_user=user(),
        service=service,
    )

    assert result.total == 0
    assert service.calls[0][0] == "list"


@pytest.mark.asyncio
async def test_get_batch_route_requires_org_context():
    with pytest.raises(HTTPException) as exc:
        await ocr_onboarding.get_batch(
            batch_id=uuid4(),
            current_user=user(org_id=None),
            service=DummyService(),
        )

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_bulk_accept_route_delegates_selected_items():
    service = DummyService()
    batch_id = uuid4()
    item_id = uuid4()

    result = await ocr_onboarding.bulk_accept(
        batch_id=batch_id,
        payload=ocr_onboarding.OCRBulkAcceptRequest(item_ids=[item_id]),
        current_user=user(),
        service=service,
    )

    assert result["accepted_count"] == 1
    assert service.calls[0][1]["item_ids"] == [item_id]


@pytest.mark.asyncio
async def test_retry_route_delegates_item():
    service = DummyService()
    batch_id = uuid4()
    item_id = uuid4()

    result = await ocr_onboarding.retry_item(
        batch_id=batch_id,
        item_id=item_id,
        current_user=user(),
        service=service,
    )

    assert result["status"] == "queued"
    assert service.calls[0][0] == "retry"
