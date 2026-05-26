from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import make_supabase_response


ORG_ID = UUID("44444444-4444-4444-4444-444444444444")
BRANCH_ID = UUID("55555555-5555-5555-5555-555555555555")


@pytest.fixture
def client():
    return TestClient(app)


def _profile(user_id, role="admin"):
    return {
        "id": str(user_id),
        "role": role,
        "language": "ar",
        "display_name": "Template Admin",
        "is_active": True,
        "org_id": str(ORG_ID),
        "branch_id": str(BRANCH_ID),
        "department_id": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def _chain(data):
    chain = MagicMock()
    chain.select.return_value = chain
    chain.eq.return_value = chain
    chain.single.return_value = chain
    chain.insert.return_value = chain
    chain.update.return_value = chain
    chain.execute.return_value = make_supabase_response(data)
    return chain


def _mock_client(template_id, user_id, role="admin"):
    policy_id = uuid4()
    policy = {
        "id": str(policy_id),
        "org_id": str(ORG_ID),
        "template_id": str(template_id),
        "name": "Branch policy",
        "is_active": True,
        "default_import_policy": "admin_only",
    }
    grant = {
        "id": str(uuid4()),
        "policy_id": str(policy_id),
        "effect": "allow",
        "principal_type": "branch",
        "principal_id": str(BRANCH_ID),
        "capabilities": ["fill"],
        "lifecycle_states": ["published"],
    }
    template = {
        "id": str(template_id),
        "org_id": str(ORG_ID),
        "status": "published",
        "name": "Cheque Template",
    }
    client = MagicMock()
    tables = {
        "profiles": _chain(_profile(user_id, role)),
        "templates": _chain(template),
        "template_access_policies": _chain([policy]),
        "template_access_grants": _chain([grant]),
        "custom_template_role_assignments": _chain([]),
        "template_access_decisions": _chain([{"id": str(uuid4())}]),
    }

    def table(name):
        return tables.get(name, _chain([]))

    client.table.side_effect = table
    return client


def test_user_decision_endpoint_returns_access_diagnostics(
    client, valid_admin_token, admin_user_id
):
    template_id = uuid4()
    mock_client = _mock_client(template_id, admin_user_id)

    with (
        patch("app.api.deps.get_supabase_client", return_value=mock_client),
        patch("app.api.routes.template_permissions.get_supabase_client", return_value=mock_client),
        patch("app.services.template_permission_service.AuditLogger") as audit_cls,
    ):
        audit_cls.return_value.log_event = AsyncMock()
        response = client.get(
            f"/api/template-permissions/templates/{template_id}/decision?capability=fill",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] is True
    assert data["reason"] == "allow_grant_matched"
    assert "branch" in data["scope_matches"]


def test_admin_can_replace_template_policy(client, valid_admin_token, admin_user_id):
    template_id = uuid4()
    mock_client = _mock_client(template_id, admin_user_id)
    inserted_policy = {
        "id": str(uuid4()),
        "org_id": str(ORG_ID),
        "template_id": str(template_id),
        "name": "Branch policy",
        "description": None,
        "is_active": True,
        "default_import_policy": "admin_only",
    }
    mock_client.table("template_access_policies").insert.return_value.execute.return_value = (
        make_supabase_response([inserted_policy])
    )

    with (
        patch("app.api.deps.get_supabase_client", return_value=mock_client),
        patch("app.api.routes.template_permissions.get_supabase_client", return_value=mock_client),
        patch("app.services.template_permission_service.AuditLogger") as audit_cls,
    ):
        audit_cls.return_value.log_event = AsyncMock()
        response = client.put(
            f"/api/admin/template-permissions/templates/{template_id}/policy",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
            json={
                "name": "Branch policy",
                "default_import_policy": "admin_only",
                "grants": [
                    {
                        "effect": "allow",
                        "principal_type": "branch",
                        "principal_id": str(BRANCH_ID),
                        "capabilities": ["fill"],
                        "lifecycle_states": ["published"],
                    }
                ],
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["template_id"] == str(template_id)
    assert data["name"] == "Branch policy"


def test_admin_diagnostics_for_selected_user(client, valid_admin_token, admin_user_id):
    template_id = uuid4()
    selected_user_id = UUID("22222222-2222-2222-2222-222222222222")
    mock_client = _mock_client(template_id, admin_user_id)
    profile_chain = _chain(_profile(admin_user_id, "admin"))
    profile_chain.execute.side_effect = [
        make_supabase_response(_profile(admin_user_id, "admin")),
        make_supabase_response(_profile(selected_user_id, "operator")),
    ]

    def table(name):
        if name == "profiles":
            # First call authenticates admin, second call loads selected user.
            return profile_chain
        return _mock_client(template_id, admin_user_id).table(name)

    mock_client.table.side_effect = table

    with (
        patch("app.api.deps.get_supabase_client", return_value=mock_client),
        patch("app.api.routes.template_permissions.get_supabase_client", return_value=mock_client),
        patch("app.services.template_permission_service.AuditLogger") as audit_cls,
    ):
        audit_cls.return_value.log_event = AsyncMock()
        response = client.get(
            f"/api/admin/template-permissions/templates/{template_id}/diagnostics"
            f"?user_id={selected_user_id}&capability=fill",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(selected_user_id)
    assert data["allowed"] is True
