from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.models.user import UserProfile
from app.schemas.offline_desk import RegisterDeviceRequest, SyncOperationType, SyncRequest, SyncStatus
from app.services.offline_desk_service import OfflineDeskService


class Result:
    def __init__(self, data=None):
        self.data = data or []


class Table:
    def __init__(self, client, name):
        self.client = client
        self.name = name
        self.filters = []

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, key, value):
        self.filters.append((key, value))
        return self

    def limit(self, _limit):
        return self

    def insert(self, payload):
        self.client.inserts.append((self.name, payload))
        return self

    def update(self, payload):
        self.client.updates.append((self.name, payload))
        return self

    def execute(self):
        rows = list(self.client.tables.get(self.name, []))
        for key, value in self.filters:
            rows = [row for row in rows if str(row.get(key)) == str(value)]
        return Result(rows)


class Client:
    def __init__(self, tables=None):
        self.tables = tables or {}
        self.inserts = []
        self.updates = []

    def table(self, name):
        return Table(self, name)


def make_user():
    return UserProfile(id=uuid4(), role="operator", language="ar", org_id=uuid4(), created_at=datetime.now(UTC), updated_at=datetime.now(UTC))


def make_sync(device_id, template_id, version=1):
    return SyncRequest(
        device_id=device_id,
        idempotency_key="queue-key-1",
        operation_type=SyncOperationType.SUBMISSION,
        template_id=template_id,
        template_version=version,
        payload_digest="sha256:test",
        client_created_at=datetime.now(UTC),
        encrypted_payload="ciphertext",
    )


@pytest.mark.asyncio
async def test_register_device_uses_default_policy():
    user = make_user()
    service = OfflineDeskService(Client())

    result = await service.register_device(
        RegisterDeviceRequest(device_fingerprint="fingerprint-123", display_name="Tablet", public_key="public-key-material"),
        user,
    )

    assert result.policy.max_offline_age_hours == 168
    assert result.policy.max_storage_mb == 250
    assert result.policy.wipe_on_revocation is True


@pytest.mark.asyncio
async def test_sync_blocks_stale_template_version():
    user = make_user()
    device_id = uuid4()
    template_id = uuid4()
    client = Client(
        {
            "offline_devices": [{"id": str(device_id), "org_id": str(user.org_id), "user_id": str(user.id), "status": "active"}],
            "templates": [{"id": str(template_id), "version": 2, "status": "published"}],
        }
    )

    result = await OfflineDeskService(client).sync(make_sync(device_id, template_id), user)

    assert result.status == SyncStatus.CONFLICT
    assert result.conflicts[0].conflict_type == "template_version"
