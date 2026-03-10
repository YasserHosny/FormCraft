"""Unit tests for API dependency injection (get_current_user, require_role)."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from app.api.deps import get_current_user, require_role
from app.models.enums import Role
from app.models.user import UserProfile
from tests.conftest import make_supabase_response


class TestGetCurrentUser:
    @pytest.mark.asyncio
    async def test_missing_bearer_prefix_raises_401(self):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(authorization="InvalidToken")
        assert exc_info.value.status_code == 401
        assert "Invalid authorization header format" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_valid_token_returns_profile(
        self, valid_admin_token, admin_profile
    ):
        mock_response = make_supabase_response(admin_profile)
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        with patch("app.api.deps.get_supabase_client", return_value=mock_client):
            user = await get_current_user(
                authorization=f"Bearer {valid_admin_token}"
            )
        assert str(user.id) == admin_profile["id"]
        assert user.role == Role.ADMIN

    @pytest.mark.asyncio
    async def test_expired_token_raises_401(self, expired_token):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(authorization=f"Bearer {expired_token}")
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_profile_not_found_raises_404(self, valid_admin_token):
        mock_response = make_supabase_response(None)
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        with patch("app.api.deps.get_supabase_client", return_value=mock_client):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(
                    authorization=f"Bearer {valid_admin_token}"
                )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_deactivated_user_raises_403(
        self, valid_viewer_token, deactivated_profile
    ):
        mock_response = make_supabase_response(deactivated_profile)
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        with patch("app.api.deps.get_supabase_client", return_value=mock_client):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(
                    authorization=f"Bearer {valid_viewer_token}"
                )
        assert exc_info.value.status_code == 403
        assert "deactivated" in exc_info.value.detail


class TestRequireRole:
    @pytest.mark.asyncio
    async def test_admin_passes_admin_check(
        self, valid_admin_token, admin_profile
    ):
        mock_response = make_supabase_response(admin_profile)
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        check_fn = require_role(Role.ADMIN)
        with patch("app.api.deps.get_supabase_client", return_value=mock_client):
            user = await get_current_user(
                authorization=f"Bearer {valid_admin_token}"
            )
            result = await check_fn(current_user=user)
        assert result.role == Role.ADMIN

    @pytest.mark.asyncio
    async def test_viewer_fails_admin_check(
        self, valid_viewer_token, viewer_profile
    ):
        mock_response = make_supabase_response(viewer_profile)
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        check_fn = require_role(Role.ADMIN)
        with patch("app.api.deps.get_supabase_client", return_value=mock_client):
            user = await get_current_user(
                authorization=f"Bearer {valid_viewer_token}"
            )
            with pytest.raises(HTTPException) as exc_info:
                await check_fn(current_user=user)
        assert exc_info.value.status_code == 403
        assert "admin" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_designer_passes_designer_or_admin_check(
        self, valid_designer_token, designer_profile
    ):
        mock_response = make_supabase_response(designer_profile)
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        check_fn = require_role(Role.ADMIN, Role.DESIGNER)
        with patch("app.api.deps.get_supabase_client", return_value=mock_client):
            user = await get_current_user(
                authorization=f"Bearer {valid_designer_token}"
            )
            result = await check_fn(current_user=user)
        assert result.role == Role.DESIGNER
