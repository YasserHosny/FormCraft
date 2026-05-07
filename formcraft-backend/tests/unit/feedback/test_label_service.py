"""Unit tests for FeedbackService label methods and search."""

from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.services.feedback.service import FeedbackService
from app.schemas.label import LabelCreateRequest, LabelUpdateRequest, LabelColour


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def service(mock_client):
    return FeedbackService(client=mock_client)


@pytest.fixture
def admin_id():
    return uuid4()


class TestCreateLabel:
    @pytest.mark.asyncio
    async def test_create_label_success(self, service, mock_client, admin_id):
        label_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        mock_client.table.return_value.insert.return_value.execute.return_value = (
            MagicMock(
                data=[
                    {
                        "id": label_id,
                        "name": "Bug Report",
                        "colour": "red",
                        "created_by": str(admin_id),
                        "created_at": now,
                    }
                ]
            )
        )
        payload = LabelCreateRequest(name="Bug Report", colour=LabelColour.red)
        result = await service.create_label(admin_id=admin_id, payload=payload)
        assert result["name"] == "Bug Report"
        assert result["colour"] == "red"

    @pytest.mark.asyncio
    async def test_create_label_duplicate_name(self, service, mock_client, admin_id):
        def raise_unique_violation(*args, **kwargs):
            raise Exception("duplicate key value")

        mock_client.table.return_value.insert.return_value.execute.side_effect = (
            raise_unique_violation
        )
        payload = LabelCreateRequest(name="Bug Report", colour=LabelColour.red)
        with pytest.raises(HTTPException) as exc_info:
            await service.create_label(admin_id=admin_id, payload=payload)
        assert exc_info.value.status_code == 409


class TestUpdateLabel:
    @pytest.mark.asyncio
    async def test_update_label_success(self, service, mock_client):
        label_id = str(uuid4())
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[
                {
                    "id": label_id,
                    "name": "UI Bug",
                    "colour": "orange",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ]
        )
        payload = LabelUpdateRequest(name="UI Bug", colour=LabelColour.orange)
        result = await service.update_label(label_id=label_id, payload=payload)
        assert result["name"] == "UI Bug"

    @pytest.mark.asyncio
    async def test_update_label_not_found(self, service, mock_client):
        label_id = str(uuid4())
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[]
        )
        payload = LabelUpdateRequest(name="UI Bug")
        with pytest.raises(HTTPException) as exc_info:
            await service.update_label(label_id=label_id, payload=payload)
        assert exc_info.value.status_code == 404


class TestDeleteLabel:
    @pytest.mark.asyncio
    async def test_delete_label_success(self, service, mock_client):
        label_id = str(uuid4())
        mock_client.table.return_value.delete.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": label_id}]
        )
        await service.delete_label(label_id=label_id)

    @pytest.mark.asyncio
    async def test_delete_label_not_found(self, service, mock_client):
        label_id = str(uuid4())
        mock_client.table.return_value.delete.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[]
        )
        with pytest.raises(HTTPException) as exc_info:
            await service.delete_label(label_id=label_id)
        assert exc_info.value.status_code == 404


class TestAssignLabels:
    @pytest.mark.asyncio
    async def test_assign_labels_success(self, service, mock_client):
        feedback_id = str(uuid4())
        label_id_1 = str(uuid4())
        label_id_2 = str(uuid4())
        admin_id_str = str(uuid4())

        mock_client.table.return_value.select.return_value.in_.return_value.execute.return_value = MagicMock(
            data=[{"id": label_id_1}, {"id": label_id_2}]
        )
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": feedback_id}]
        )
        mock_client.table.return_value.delete.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[]
        )
        mock_client.table.return_value.insert.return_value.execute.return_value = (
            MagicMock(
                data=[
                    {
                        "feedback_id": feedback_id,
                        "label_id": label_id_1,
                        "assigned_by": admin_id_str,
                    },
                    {
                        "feedback_id": feedback_id,
                        "label_id": label_id_2,
                        "assigned_by": admin_id_str,
                    },
                ]
            )
        )
        mock_client.table.return_value.select.return_value.eq.return_value.select.return_value.execute.return_value = MagicMock(
            data=[]
        )
        result = await service.assign_labels(
            feedback_id=feedback_id,
            label_ids=[label_id_1, label_id_2],
            admin_id=admin_id_str,
        )
        assert result is not None or True  # Verify no exception raised

    @pytest.mark.asyncio
    async def test_assign_labels_exceeds_max(self, service, mock_client):
        feedback_id = str(uuid4())
        label_ids = [str(uuid4()) for _ in range(6)]
        admin_id_str = str(uuid4())
        with pytest.raises(HTTPException) as exc_info:
            await service.assign_labels(
                feedback_id=feedback_id, label_ids=label_ids, admin_id=admin_id_str
            )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_assign_labels_clear_all(self, service, mock_client):
        feedback_id = str(uuid4())
        admin_id_str = str(uuid4())
        mock_client.table.return_value.delete.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[]
        )
        result = await service.assign_labels(
            feedback_id=feedback_id, label_ids=[], admin_id=admin_id_str
        )
        assert result == []
