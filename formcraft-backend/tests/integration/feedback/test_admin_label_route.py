"""Integration tests for admin label CRUD routes and feedback search."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import make_supabase_response


@pytest.fixture
def client():
    return TestClient(app)


def _setup_profile_mock(mock_client, profile):
    from tests.conftest import make_supabase_response

    profile_response = make_supabase_response(profile)
    mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = profile_response


class TestListLabels:
    def test_list_labels_200_admin(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)
        from tests.conftest import make_supabase_response

        mock_client.table.return_value.select.return_value.order.return_value.execute.return_value = make_supabase_response(
            [
                {
                    "id": str(uuid4()),
                    "name": "Bug Report",
                    "colour": "red",
                    "created_at": "2026-05-07T00:00:00Z",
                }
            ],
            count=1,
        )
        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.get(
                "/api/admin/labels",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert response.status_code == 200

    def test_list_labels_403_non_admin(
        self, client, valid_viewer_token, viewer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, viewer_profile)
        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.get(
                "/api/admin/labels",
                headers={"Authorization": f"Bearer {valid_viewer_token}"},
            )
        assert response.status_code == 403


class TestCreateLabel:
    def test_create_label_201(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)
        label_id = str(uuid4())
        now = "2026-05-07T00:00:00Z"
        mock_client.table.return_value.insert.return_value.execute.return_value = (
            MagicMock(
                data=[
                    {
                        "id": label_id,
                        "name": "Bug Report",
                        "colour": "red",
                        "created_by": str(uuid4()),
                        "created_at": now,
                    }
                ]
            )
        )
        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/admin/labels",
                json={"name": "Bug Report", "colour": "red"},
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert response.status_code == 201

    def test_create_label_403_non_admin(
        self, client, valid_viewer_token, viewer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, viewer_profile)
        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/admin/labels",
                json={"name": "Bug Report", "colour": "red"},
                headers={"Authorization": f"Bearer {valid_viewer_token}"},
            )
        assert response.status_code == 403


class TestUpdateLabel:
    def test_update_label_200(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)
        label_id = str(uuid4())
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[
                {
                    "id": label_id,
                    "name": "UI Bug",
                    "colour": "orange",
                    "created_at": "2026-05-07T00:00:00Z",
                }
            ]
        )
        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.patch(
                f"/api/admin/labels/{label_id}",
                json={"name": "UI Bug"},
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert response.status_code == 200

    def test_update_label_404(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)
        label_id = str(uuid4())
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[]
        )
        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.patch(
                f"/api/admin/labels/{label_id}",
                json={"name": "UI Bug"},
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert response.status_code == 404


class TestDeleteLabel:
    def test_delete_label_204(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)
        label_id = str(uuid4())
        mock_client.table.return_value.delete.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": label_id}]
        )
        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.delete(
                f"/api/admin/labels/{label_id}",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert response.status_code == 204

    def test_delete_label_404(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)
        label_id = str(uuid4())
        mock_client.table.return_value.delete.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[]
        )
        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.delete(
                f"/api/admin/labels/{label_id}",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert response.status_code == 404


class TestAssignLabels:
    def test_assign_labels_200(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)
        feedback_id = str(uuid4())
        label_id = str(uuid4())

        # Set up a flexible mock that handles multiple table() calls with different tables
        profiles_chain = MagicMock()
        profiles_chain.select.return_value.eq.return_value.single.return_value.execute.return_value = make_supabase_response(
            admin_profile
        )

        # feedback_labels select.in_ for validation
        labels_chain = MagicMock()
        labels_chain.select.return_value.in_.return_value.execute.return_value = (
            MagicMock(data=[{"id": label_id}])
        )

        # feedback_submissions select.eq for existence check
        submissions_chain = MagicMock()
        submissions_chain.select.return_value.eq.return_value.execute.return_value = (
            MagicMock(data=[{"id": feedback_id}])
        )

        # feedback_submission_labels operations
        fsl_chain = MagicMock()
        fsl_chain.delete.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[]
        )
        fsl_chain.insert.return_value.execute.return_value = MagicMock(
            data=[{"feedback_id": feedback_id, "label_id": label_id}]
        )
        fsl_chain.select.return_value.eq.return_value.select.return_value.execute.return_value = MagicMock(
            data=[]
        )

        def table_side_effect(name):
            if name == "profiles":
                return profiles_chain
            elif name == "feedback_labels":
                return labels_chain
            elif name == "feedback_submissions":
                return submissions_chain
            elif name == "feedback_submission_labels":
                return fsl_chain
            return MagicMock()

        mock_client.table.side_effect = table_side_effect

        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.put(
                f"/api/admin/feedback/{feedback_id}/labels",
                json={"label_ids": [label_id]},
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert response.status_code == 200

    def test_assign_labels_400_exceeds_max(
        self, client, valid_admin_token, admin_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)
        feedback_id = str(uuid4())
        label_ids = [str(uuid4()) for _ in range(6)]
        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.put(
                f"/api/admin/feedback/{feedback_id}/labels",
                json={"label_ids": label_ids},
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert response.status_code in (400, 422)

    def test_assign_labels_403_non_admin(
        self, client, valid_viewer_token, viewer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, viewer_profile)
        feedback_id = str(uuid4())
        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.put(
                f"/api/admin/feedback/{feedback_id}/labels",
                json={"label_ids": []},
                headers={"Authorization": f"Bearer {valid_viewer_token}"},
            )
        assert response.status_code == 403


class TestSearchFeedback:
    def test_search_feedback_200(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)
        from tests.conftest import make_supabase_response

        query_chain = MagicMock()
        query_chain.eq.return_value = query_chain
        query_chain.gte.return_value = query_chain
        query_chain.lte.return_value = query_chain
        query_chain.ilike.return_value = query_chain
        query_chain.range.return_value = query_chain
        query_chain.order.return_value = query_chain
        query_chain.execute.return_value = make_supabase_response([], count=0)

        original_table = mock_client.table

        def table_side_effect(name):
            if name == "profiles":
                return original_table.return_value
            mock_query = MagicMock()
            mock_query.select.return_value = query_chain
            return mock_query

        mock_client.table.side_effect = table_side_effect
        mock_client.storage.from_.return_value.create_signed_url.return_value = (
            "https://signed.url"
        )

        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.get(
                "/api/admin/feedback?search=bug",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert response.status_code == 200
