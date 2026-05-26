from datetime import datetime, timezone
from io import BytesIO
from uuid import uuid4

import pytest
from fastapi import UploadFile

from app.services.ocr_onboarding_service import (
    MAX_BATCH_ITEMS,
    OCRBatchValidationError,
    OCROnboardingService,
)


class FakeResult:
    def __init__(self, data=None, count=None):
        self.data = data
        self.count = count


class FakeQuery:
    def __init__(self, db, table_name):
        self.db = db
        self.table_name = table_name
        self.action = "select"
        self.payload = None
        self.filters = []
        self.count_mode = None
        self.single_mode = False

    def select(self, *_args, count=None):
        self.action = "select"
        self.count_mode = count
        return self

    def insert(self, payload):
        self.action = "insert"
        self.payload = payload
        return self

    def update(self, payload):
        self.action = "update"
        self.payload = payload
        return self

    def eq(self, key, value):
        self.filters.append((key, str(value)))
        return self

    def single(self):
        self.single_mode = True
        return self

    def order(self, *_args, **_kwargs):
        return self

    def range(self, *_args):
        return self

    def execute(self):
        rows = self.db.setdefault(self.table_name, [])
        if self.action == "insert":
            payloads = self.payload if isinstance(self.payload, list) else [self.payload]
            rows.extend(payloads)
            return FakeResult(payloads, len(rows))
        matched = [
            row for row in rows
            if all(str(row.get(key)) == value for key, value in self.filters)
        ]
        if self.action == "update":
            for row in matched:
                row.update(self.payload)
            return FakeResult(matched, len(matched))
        return FakeResult(matched[0] if self.single_mode and matched else matched, len(matched))


class FakeSupabase:
    def __init__(self):
        self.db = {
            "ocr_import_batches": [],
            "ocr_import_items": [],
            "ocr_review_decisions": [],
            "audit_logs": [],
        }

    def table(self, name):
        return FakeQuery(self.db, name)


def upload(name="scan.png", content_type="image/png", content=b"scan"):
    return UploadFile(filename=name, file=BytesIO(content), headers={"content-type": content_type})


async def noop_audit(*_args, **_kwargs):
    return None


@pytest.mark.asyncio
async def test_create_batch_validates_files_and_keeps_supported_items(monkeypatch):
    client = FakeSupabase()
    service = OCROnboardingService(client)
    monkeypatch.setattr(service, "_audit", noop_audit)

    result = await service.create_batch(
        org_id=uuid4(),
        created_by=uuid4(),
        name="Legacy library",
        confidence_threshold=0.85,
        files=[upload(), upload("notes.txt", "text/plain")],
    )

    assert result.total_items == 1
    assert result.failed_items == 1
    assert client.db["ocr_import_items"][0]["status"] == "queued"


@pytest.mark.asyncio
async def test_create_batch_rejects_more_than_200_items():
    service = OCROnboardingService(FakeSupabase())
    files = [upload(f"scan-{idx}.png") for idx in range(MAX_BATCH_ITEMS + 1)]

    with pytest.raises(OCRBatchValidationError):
        await service.create_batch(
            org_id=uuid4(),
            created_by=uuid4(),
            name="Too large",
            confidence_threshold=0.85,
            files=files,
        )


@pytest.mark.asyncio
async def test_bulk_accept_skips_below_threshold(monkeypatch):
    client = FakeSupabase()
    service = OCROnboardingService(client)
    monkeypatch.setattr(service, "_audit", noop_audit)
    template_id = uuid4()

    async def fake_create_template(*_args, **_kwargs):
        return template_id

    monkeypatch.setattr(service, "_create_draft_template", fake_create_template)

    batch_id = uuid4()
    org_id = uuid4()
    now = datetime.now(timezone.utc).isoformat()
    high_id = uuid4()
    low_id = uuid4()
    client.db["ocr_import_batches"].append({
        "id": str(batch_id),
        "org_id": str(org_id),
        "name": "Batch",
        "status": "needs_review",
        "confidence_threshold": 0.85,
        "total_items": 2,
        "processed_items": 2,
        "accepted_items": 0,
        "failed_items": 0,
        "duplicate_items": 0,
        "created_at": now,
        "updated_at": now,
    })
    for item_id, confidence in ((high_id, 0.91), (low_id, 0.5)):
        client.db["ocr_import_items"].append({
            "id": str(item_id),
            "batch_id": str(batch_id),
            "org_id": str(org_id),
            "file_name": f"{item_id}.png",
            "status": "needs_review",
            "mime_type": "image/png",
            "file_size_bytes": 4,
            "confidence": confidence,
            "page_count": 1,
            "retry_count": 0,
            "created_at": now,
            "updated_at": now,
        })

    result = await service.bulk_accept(
        batch_id=batch_id,
        org_id=org_id,
        decided_by=uuid4(),
        item_ids=[high_id, low_id],
    )

    assert result.accepted_count == 1
    assert result.skipped == [{"item_id": str(low_id), "reason": "below_threshold"}]


@pytest.mark.asyncio
async def test_retry_item_resets_failed_state(monkeypatch):
    client = FakeSupabase()
    service = OCROnboardingService(client)
    monkeypatch.setattr(service, "_audit", noop_audit)
    batch_id = uuid4()
    org_id = uuid4()
    item_id = uuid4()
    now = datetime.now(timezone.utc).isoformat()
    client.db["ocr_import_items"].append({
        "id": str(item_id),
        "batch_id": str(batch_id),
        "org_id": str(org_id),
        "file_name": "bad.png",
        "status": "failed",
        "mime_type": "image/png",
        "file_size_bytes": 4,
        "page_count": 1,
        "retry_count": 1,
        "last_error": "timeout",
        "created_at": now,
        "updated_at": now,
    })

    result = await service.retry_item(
        batch_id=batch_id,
        item_id=item_id,
        org_id=org_id,
        decided_by=uuid4(),
    )

    assert result.status == "queued"
    assert result.retry_count == 2
    assert result.last_error is None
