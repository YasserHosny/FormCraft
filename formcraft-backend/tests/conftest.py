"""Shared test fixtures for FormCraft backend tests."""

import os
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest
from jose import jwt

# Set test environment variables before importing app modules
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "test-anon-key")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-service-key")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test-jwt-secret-at-least-32-chars-long")

from app.core.config import settings


@pytest.fixture
def jwt_secret() -> str:
    return settings.SUPABASE_JWT_SECRET


@pytest.fixture
def admin_user_id() -> UUID:
    return UUID("11111111-1111-1111-1111-111111111111")


@pytest.fixture
def designer_user_id() -> UUID:
    return UUID("22222222-2222-2222-2222-222222222222")


@pytest.fixture
def viewer_user_id() -> UUID:
    return UUID("33333333-3333-3333-3333-333333333333")


def _make_token(user_id: UUID, secret: str, expired: bool = False) -> str:
    """Create a valid or expired JWT token for testing."""
    import time

    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "aud": "authenticated",
        "role": "authenticated",
        "iat": now - 3600,
        "exp": now - 10 if expired else now + 3600,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


@pytest.fixture
def valid_admin_token(admin_user_id, jwt_secret) -> str:
    return _make_token(admin_user_id, jwt_secret)


@pytest.fixture
def valid_designer_token(designer_user_id, jwt_secret) -> str:
    return _make_token(designer_user_id, jwt_secret)


@pytest.fixture
def valid_viewer_token(viewer_user_id, jwt_secret) -> str:
    return _make_token(viewer_user_id, jwt_secret)


@pytest.fixture
def expired_token(admin_user_id, jwt_secret) -> str:
    return _make_token(admin_user_id, jwt_secret, expired=True)


@pytest.fixture
def admin_profile(admin_user_id) -> dict:
    return {
        "id": str(admin_user_id),
        "role": "admin",
        "language": "ar",
        "display_name": "Test Admin",
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "created_by": None,
    }


@pytest.fixture
def designer_profile(designer_user_id) -> dict:
    return {
        "id": str(designer_user_id),
        "role": "designer",
        "language": "ar",
        "display_name": "Test Designer",
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "created_by": str(UUID("11111111-1111-1111-1111-111111111111")),
    }


@pytest.fixture
def viewer_profile(viewer_user_id) -> dict:
    return {
        "id": str(viewer_user_id),
        "role": "viewer",
        "language": "en",
        "display_name": "Test Viewer",
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "created_by": None,
    }


@pytest.fixture
def deactivated_profile(viewer_user_id) -> dict:
    return {
        "id": str(viewer_user_id),
        "role": "viewer",
        "language": "ar",
        "display_name": "Deactivated User",
        "is_active": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "created_by": None,
    }


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client."""
    client = MagicMock()
    return client


def make_supabase_response(data, count=None):
    """Helper to create mock Supabase query responses."""
    response = MagicMock()
    response.data = data
    response.count = count
    return response
