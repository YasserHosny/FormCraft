"""Integration tests for admin template governance routes."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import make_supabase_response


@pytest.fixture
def client():
    return TestClient(app)


def _setup_profile_mock(mock_client, profile):
    # Add org_id if missing
    profile_with_org = dict(profile)
    if "org_id" not in profile_with_org or profile_with_org.get("org_id") is None:
        profile_with_org["org_id"] = str(UUID("44444444-4444-4444-4444-444444444444"))
    profile_response = make_supabase_response(profile_with_org)
    mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = profile_response


def _make_template(template_id=None, org_id=None, status="draft"):
    return {
        "id": str(template_id or uuid4()),
        "name": "Test Template",
        "category": "general",
        "status": status,
        "version": 1,
        "created_by": str(UUID("22222222-2222-2222-2222-222222222222")),
        "department_id": None,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "org_id": str(org_id or UUID("44444444-4444-4444-4444-444444444444")),
    }


def _setup_templates_query(mock_client, templates):
    """Setup mock for templates table queries."""
    query_chain = MagicMock()
    query_chain.eq.return_value = query_chain
    query_chain.gte.return_value = query_chain
    query_chain.lte.return_value = query_chain
    query_chain.range.return_value = query_chain
    query_chain.order.return_value = query_chain
    query_chain.or_.return_value = query_chain
    query_chain.execute.return_value = make_supabase_response(templates)

    mock_table = MagicMock()
    mock_table.select.return_value = query_chain

    def table_side_effect(name):
        if name == "profiles":
            return mock_client.table.return_value
        return mock_table

    mock_client.table.side_effect = table_side_effect


class TestListTemplates:
    def test_list_templates_200_admin(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)

        template = _make_template()
        template["profiles"] = {"display_name": "Test Designer"}
        template["departments"] = None
        _setup_templates_query(mock_client, [template])

        with (
            patch(
                "app.api.routes.admin_templates.get_supabase_client",
                return_value=mock_client,
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.get(
                "/api/admin/templates",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_templates_403_non_admin(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)

        with (
            patch(
                "app.api.routes.admin_templates.get_supabase_client",
                return_value=mock_client,
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.get(
                "/api/admin/templates",
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 403


class TestBulkActions:
    def test_bulk_archive_200(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)

        template_id = uuid4()
        template = _make_template(template_id=template_id, status="draft")

        # Mock templates query
        mock_table = MagicMock()
        mock_select_chain = MagicMock()
        mock_select_chain.in_.return_value = mock_select_chain
        mock_select_chain.eq.return_value = mock_select_chain
        mock_select_chain.execute.return_value = make_supabase_response([template])
        mock_table.select.return_value = mock_select_chain

        # Mock update
        mock_update_chain = MagicMock()
        mock_update_chain.eq.return_value = mock_update_chain
        mock_update_chain.execute.return_value = make_supabase_response(
            [{"id": str(template_id)}]
        )
        mock_table.update.return_value = mock_update_chain

        def table_side_effect(name):
            if name == "profiles":
                return mock_client.table.return_value
            if name == "templates":
                return mock_table
            return MagicMock()

        mock_client.table.side_effect = table_side_effect

        # Mock audit logger (imported inside function)
        import asyncio

        mock_audit = MagicMock()
        mock_audit.log_event = MagicMock(return_value=asyncio.Future())
        mock_audit.log_event.return_value.set_result(None)

        with (
            patch(
                "app.api.routes.admin_templates.get_supabase_client",
                return_value=mock_client,
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
            patch("app.core.audit.AuditLogger", return_value=mock_audit),
        ):
            response = client.post(
                "/api/admin/templates/bulk-actions",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
                json={
                    "action": "archive",
                    "template_ids": [str(template_id)],
                    "dry_run": False,
                },
            )
        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "archive"
        assert data["affected_count"] == 1

    def test_bulk_action_dry_run(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)

        template_id = uuid4()
        template = _make_template(template_id=template_id, status="published")

        mock_table = MagicMock()
        mock_select_chain = MagicMock()
        mock_select_chain.in_.return_value = mock_select_chain
        mock_select_chain.eq.return_value = mock_select_chain
        mock_select_chain.execute.return_value = make_supabase_response([template])
        mock_table.select.return_value = mock_select_chain

        def table_side_effect(name):
            if name == "profiles":
                return mock_client.table.return_value
            if name == "templates":
                return mock_table
            return MagicMock()

        mock_client.table.side_effect = table_side_effect

        with (
            patch(
                "app.api.routes.admin_templates.get_supabase_client",
                return_value=mock_client,
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/admin/templates/bulk-actions",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
                json={
                    "action": "archive",
                    "template_ids": [str(template_id)],
                    "dry_run": True,
                },
            )
        assert response.status_code == 200
        data = response.json()
        assert data["dry_run"] is True
        assert "warnings" in data


class TestComplianceDashboard:
    def test_compliance_dashboard_200(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)

        template = _make_template(status="published")

        # Mock templates query for compliance
        mock_templates_chain = MagicMock()
        mock_templates_chain.eq.return_value = mock_templates_chain
        mock_templates_chain.execute.return_value = make_supabase_response([template])

        # Mock pages query
        mock_pages_chain = MagicMock()
        mock_pages_chain.eq.return_value = mock_pages_chain
        mock_pages_chain.execute.return_value = make_supabase_response([])

        def table_side_effect(name):
            if name == "profiles":
                return mock_client.table.return_value
            if name == "templates":
                mock_table = MagicMock()
                mock_table.select.return_value = mock_templates_chain
                return mock_table
            if name == "pages":
                mock_table = MagicMock()
                mock_table.select.return_value = mock_pages_chain
                return mock_table
            return MagicMock()

        mock_client.table.side_effect = table_side_effect

        with (
            patch(
                "app.api.routes.admin_templates.get_supabase_client",
                return_value=mock_client,
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.get(
                "/api/admin/templates/compliance",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert response.status_code == 200
        data = response.json()
        assert "avg_quality_score" in data
        assert "total_templates" in data


class TestRegulatoryAlerts:
    def test_regulatory_alerts_200(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)

        with (
            patch(
                "app.api.routes.admin_templates.get_supabase_client",
                return_value=mock_client,
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.get(
                "/api/admin/templates/regulatory-alerts",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
