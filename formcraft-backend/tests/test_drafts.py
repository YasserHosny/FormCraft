import sys
from datetime import datetime, timezone
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

openpyxl_module = ModuleType("openpyxl")
openpyxl_styles_module = ModuleType("openpyxl.styles")
openpyxl_utils_module = ModuleType("openpyxl.utils")
openpyxl_styles_module.Alignment = SimpleNamespace
openpyxl_styles_module.Font = SimpleNamespace
openpyxl_utils_module.get_column_letter = lambda idx: str(idx)
openpyxl_module.styles = openpyxl_styles_module
openpyxl_module.utils = openpyxl_utils_module
sys.modules.setdefault("openpyxl", openpyxl_module)
sys.modules.setdefault("openpyxl.styles", openpyxl_styles_module)
sys.modules.setdefault("openpyxl.utils", openpyxl_utils_module)

from app.main import app
from tests.conftest import make_supabase_response


def _profile(user_id: UUID, role: str = "operator") -> dict:
    return {
        "id": str(user_id),
        "role": role,
        "language": "ar",
        "display_name": "Test Operator",
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "created_by": None,
        "org_id": str(UUID("44444444-4444-4444-4444-444444444444")),
    }


def test_list_drafts_returns_only_authenticated_user_drafts(valid_designer_token):
    client = TestClient(app)
    auth_user_id = UUID("22222222-2222-2222-2222-222222222222")
    other_user_id = uuid4()

    owned_draft = {
        "id": str(uuid4()),
        "template_id": str(uuid4()),
        "template_version": 1,
        "operator_id": str(auth_user_id),
        "org_id": str(UUID("44444444-4444-4444-4444-444444444444")),
        "field_values": {"field_a": "value"},
        "completion_percent": 50,
        "name": "Owned Draft",
        "expires_at": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    foreign_draft = {
        **owned_draft,
        "id": str(uuid4()),
        "operator_id": str(other_user_id),
        "name": "Foreign Draft",
    }

    mock_client = MagicMock()
    profile_query = MagicMock()
    profile_query.select.return_value.eq.return_value.single.return_value.execute.return_value = make_supabase_response(
        _profile(auth_user_id, role="designer")
    )

    drafts_query = MagicMock()
    drafts_query.select.return_value.eq.return_value.order.return_value.execute.return_value = make_supabase_response(
        [owned_draft]
    )

    def table_side_effect(name: str):
        if name == "profiles":
            return profile_query
        if name == "drafts":
            return drafts_query
        return MagicMock()

    mock_client.table.side_effect = table_side_effect

    with (
        patch("app.api.routes.drafts.get_supabase_client", return_value=mock_client),
        patch("app.api.deps.get_supabase_client", return_value=mock_client),
    ):
        response = client.get(
            "/api/desk/drafts",
            headers={"Authorization": f"Bearer {valid_designer_token}"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) == 1
    assert payload[0]["id"] == owned_draft["id"]
    assert payload[0]["name"] == owned_draft["name"]
    assert payload[0]["id"] != foreign_draft["id"]
