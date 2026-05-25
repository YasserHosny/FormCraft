"""Integration and migration checks for F32 data export/integration."""

import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import make_supabase_response


MIGRATION = (
    Path(__file__).resolve().parents[2]
    / "migrations"
    / "034_data_export_integration.sql"
)


@pytest.fixture
def client():
    return TestClient(app)


def _setup_profile_mock(mock_client, profile):
    profile_with_org = dict(profile)
    if "org_id" not in profile_with_org or profile_with_org.get("org_id") is None:
        profile_with_org["org_id"] = str(UUID("44444444-4444-4444-4444-444444444444"))
    profile_response = make_supabase_response(profile_with_org)
    mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = profile_response


def _make_submission(submission_id=None, template_id=None, org_id=None, field_values=None):
    return {
        "id": str(submission_id or uuid4()),
        "template_id": str(template_id or uuid4()),
        "template_version": 1,
        "org_id": str(org_id or UUID("44444444-4444-4444-4444-444444444444")),
        "operator_id": str(UUID("22222222-2222-2222-2222-222222222222")),
        "branch_id": None,
        "department_id": None,
        "status": "completed",
        "field_values": field_values or {"name": "Test", "amount": 100},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


# --- Migration Tests ---


def test_data_export_integration_migration_defines_required_tables():
    sql = MIGRATION.read_text(encoding="utf-8")

    for table in (
        "export_requests",
        "export_schedules",
        "export_deliveries",
        "integration_credentials",
        "webhook_subscriptions",
        "webhook_deliveries",
    ):
        assert f"CREATE TABLE IF NOT EXISTS {table}" in sql
        assert f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY" in sql
        assert f"{table}_org_isolation" in sql


def test_data_export_integration_migration_has_audit_and_status_guards():
    sql = MIGRATION.read_text(encoding="utf-8")

    assert "created_by UUID" in sql
    assert "updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()" in sql
    assert "CHECK (status IN ('previewed', 'completed', 'rejected', 'failed'))" in sql
    assert "CHECK (format IN ('csv', 'xlsx', 'json'))" in sql
    assert "CHECK (frequency IN ('daily', 'weekly'))" in sql
    assert "CHECK (event_type IN (" in sql


def test_data_export_integration_migration_has_lookup_indexes():
    sql = MIGRATION.read_text(encoding="utf-8")

    for index in (
        "idx_export_requests_org_created",
        "idx_export_schedules_org_status_next_run",
        "idx_export_deliveries_schedule",
        "idx_integration_credentials_org_status",
        "idx_webhook_subscriptions_org_event_status",
        "idx_webhook_deliveries_subscription_created",
    ):
        assert f"CREATE INDEX IF NOT EXISTS {index}" in sql


# --- US1: Export Preview ---


class TestExportPreview:
    def test_preview_export_count_and_can_download(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)

        submission = _make_submission()
        rows = [submission]
        count = 1

        # Build a single table mock that handles both submissions and export_requests
        select_chain = MagicMock()
        select_chain.eq.return_value = select_chain
        select_chain.gte.return_value = select_chain
        select_chain.lte.return_value = select_chain
        select_chain.order.return_value = select_chain
        select_chain.range.return_value = select_chain
        select_chain.execute.return_value = make_supabase_response(rows, count=count)

        insert_chain = MagicMock()
        insert_chain.execute.return_value = make_supabase_response([{"id": str(uuid4())}])

        def table_side_effect(name):
            if name == "profiles":
                return mock_client.table.return_value
            if name == "submissions":
                mock_table = MagicMock()
                mock_table.select.return_value = select_chain
                return mock_table
            if name == "export_requests":
                mock_table = MagicMock()
                mock_table.insert.return_value = insert_chain
                return mock_table
            return MagicMock()

        mock_client.table.side_effect = table_side_effect

        with (
            patch("app.api.routes.admin_export.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/admin/export/preview",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
                json={
                    "filters": {},
                    "format": "csv",
                    "scope": "flattened",
                },
            )
        assert response.status_code == 200
        data = response.json()
        assert data["matching_count"] == 1
        assert data["can_download"] is True
        assert data["rejection_reason"] is None
        assert "estimated_file_size_bytes" in data

    def test_preview_export_oversized_rejection(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)

        count = 15_000
        select_chain = MagicMock()
        select_chain.eq.return_value = select_chain
        select_chain.order.return_value = select_chain
        select_chain.range.return_value = select_chain
        select_chain.execute.return_value = make_supabase_response([], count=count)

        insert_chain = MagicMock()
        insert_chain.execute.return_value = make_supabase_response([{"id": str(uuid4())}])

        def table_side_effect(name):
            if name == "profiles":
                return mock_client.table.return_value
            if name == "submissions":
                mock_table = MagicMock()
                mock_table.select.return_value = select_chain
                return mock_table
            if name == "export_requests":
                mock_table = MagicMock()
                mock_table.insert.return_value = insert_chain
                return mock_table
            return MagicMock()

        mock_client.table.side_effect = table_side_effect

        with (
            patch("app.api.routes.admin_export.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/admin/export/preview",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
                json={
                    "filters": {},
                    "format": "csv",
                    "scope": "flattened",
                },
            )
        assert response.status_code == 200
        data = response.json()
        assert data["matching_count"] == 15_000
        assert data["can_download"] is False
        assert data["rejection_reason"] == "row_limit_exceeded"

    def test_preview_export_admin_only(self, client, valid_designer_token, designer_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)

        with (
            patch("app.api.routes.admin_export.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/admin/export/preview",
                headers={"Authorization": f"Bearer {valid_designer_token}"},
                json={
                    "filters": {},
                    "format": "csv",
                    "scope": "flattened",
                },
            )
        assert response.status_code == 403


# --- US1: Export Download ---


class TestExportDownload:
    def test_download_csv_success(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)

        submission = _make_submission(field_values={"name": "Test Arabic النص", "amount": 100})
        rows = [submission]
        count = 1

        select_chain = MagicMock()
        select_chain.eq.return_value = select_chain
        select_chain.order.return_value = select_chain
        select_chain.range.return_value = select_chain
        select_chain.execute.return_value = make_supabase_response(rows, count=count)

        insert_chain = MagicMock()
        insert_chain.execute.return_value = make_supabase_response([{"id": str(uuid4())}])

        def table_side_effect(name):
            if name == "profiles":
                return mock_client.table.return_value
            if name == "submissions":
                mock_table = MagicMock()
                mock_table.select.return_value = select_chain
                return mock_table
            if name == "export_requests":
                mock_table = MagicMock()
                mock_table.insert.return_value = insert_chain
                return mock_table
            return MagicMock()

        mock_client.table.side_effect = table_side_effect

        import asyncio
        mock_audit = MagicMock()
        mock_audit.log_event = MagicMock(return_value=asyncio.Future())
        mock_audit.log_event.return_value.set_result(None)

        with (
            patch("app.api.routes.admin_export.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
            patch("app.services.export_service.AuditLogger", return_value=mock_audit),
        ):
            response = client.post(
                "/api/admin/export/download",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
                json={
                    "filters": {},
                    "format": "csv",
                    "scope": "flattened",
                },
            )
        assert response.status_code == 200
        content_disposition = response.headers.get("content-disposition", "")
        assert "attachment" in content_disposition
        assert ".csv" in content_disposition
        assert "Test Arabic النص" in response.text

    def test_download_json_success(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)

        submission = _make_submission(field_values={"name": "Test", "amount": 100})
        rows = [submission]
        count = 1

        select_chain = MagicMock()
        select_chain.eq.return_value = select_chain
        select_chain.order.return_value = select_chain
        select_chain.range.return_value = select_chain
        select_chain.execute.return_value = make_supabase_response(rows, count=count)

        insert_chain = MagicMock()
        insert_chain.execute.return_value = make_supabase_response([{"id": str(uuid4())}])

        def table_side_effect(name):
            if name == "profiles":
                return mock_client.table.return_value
            if name == "submissions":
                mock_table = MagicMock()
                mock_table.select.return_value = select_chain
                return mock_table
            if name == "export_requests":
                mock_table = MagicMock()
                mock_table.insert.return_value = insert_chain
                return mock_table
            return MagicMock()

        mock_client.table.side_effect = table_side_effect

        import asyncio
        mock_audit = MagicMock()
        mock_audit.log_event = MagicMock(return_value=asyncio.Future())
        mock_audit.log_event.return_value.set_result(None)

        with (
            patch("app.api.routes.admin_export.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
            patch("app.services.export_service.AuditLogger", return_value=mock_audit),
        ):
            response = client.post(
                "/api/admin/export/download",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
                json={
                    "filters": {},
                    "format": "json",
                    "scope": "structured",
                },
            )
        assert response.status_code == 200
        data = json.loads(response.text)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["field_values"]["name"] == "Test"

    def test_download_empty_export(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)

        count = 0
        select_chain = MagicMock()
        select_chain.eq.return_value = select_chain
        select_chain.order.return_value = select_chain
        select_chain.range.return_value = select_chain
        select_chain.execute.return_value = make_supabase_response([], count=count)

        insert_chain = MagicMock()
        insert_chain.execute.return_value = make_supabase_response([{"id": str(uuid4())}])

        def table_side_effect(name):
            if name == "profiles":
                return mock_client.table.return_value
            if name == "submissions":
                mock_table = MagicMock()
                mock_table.select.return_value = select_chain
                return mock_table
            if name == "export_requests":
                mock_table = MagicMock()
                mock_table.insert.return_value = insert_chain
                return mock_table
            return MagicMock()

        mock_client.table.side_effect = table_side_effect

        import asyncio
        mock_audit = MagicMock()
        mock_audit.log_event = MagicMock(return_value=asyncio.Future())
        mock_audit.log_event.return_value.set_result(None)

        with (
            patch("app.api.routes.admin_export.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
            patch("app.services.export_service.AuditLogger", return_value=mock_audit),
        ):
            response = client.post(
                "/api/admin/export/download",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
                json={
                    "filters": {},
                    "format": "csv",
                    "scope": "flattened",
                },
            )
        assert response.status_code == 200

    def test_download_oversized_rejected(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)

        count = 15_000
        select_chain = MagicMock()
        select_chain.eq.return_value = select_chain
        select_chain.order.return_value = select_chain
        select_chain.range.return_value = select_chain
        select_chain.execute.return_value = make_supabase_response([], count=count)

        insert_chain = MagicMock()
        insert_chain.execute.return_value = make_supabase_response([{"id": str(uuid4())}])

        def table_side_effect(name):
            if name == "profiles":
                return mock_client.table.return_value
            if name == "submissions":
                mock_table = MagicMock()
                mock_table.select.return_value = select_chain
                return mock_table
            if name == "export_requests":
                mock_table = MagicMock()
                mock_table.insert.return_value = insert_chain
                return mock_table
            return MagicMock()

        mock_client.table.side_effect = table_side_effect

        import asyncio
        mock_audit = MagicMock()
        mock_audit.log_event = MagicMock(return_value=asyncio.Future())
        mock_audit.log_event.return_value.set_result(None)

        with (
            patch("app.api.routes.admin_export.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
            patch("app.services.export_service.AuditLogger", return_value=mock_audit),
        ):
            response = client.post(
                "/api/admin/export/download",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
                json={
                    "filters": {},
                    "format": "csv",
                    "scope": "flattened",
                },
            )
        assert response.status_code == 413


# --- US1: Export History ---


class TestExportHistory:
    def test_export_history_list(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)

        export_request = {
            "id": str(uuid4()),
            "dataset": "submissions",
            "format": "csv",
            "scope": "flattened",
            "status": "completed",
            "matching_count": 100,
            "rejection_reason": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        select_chain = MagicMock()
        select_chain.eq.return_value = select_chain
        select_chain.order.return_value = select_chain
        select_chain.range.return_value = select_chain
        select_chain.execute.return_value = make_supabase_response([export_request], count=1)

        def table_side_effect(name):
            if name == "profiles":
                return mock_client.table.return_value
            if name == "export_requests":
                mock_table = MagicMock()
                mock_table.select.return_value = select_chain
                return mock_table
            return MagicMock()

        mock_client.table.side_effect = table_side_effect

        with (
            patch("app.api.routes.admin_export.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.get(
                "/api/admin/export/history",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["format"] == "csv"