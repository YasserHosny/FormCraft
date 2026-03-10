"""Unit tests for JWT verification and role extraction."""

import time

import pytest
from fastapi import HTTPException
from jose import jwt as jose_jwt

from app.core.security import verify_jwt


class TestVerifyJWT:
    def test_valid_token_decodes_successfully(self, valid_admin_token, admin_user_id):
        payload = verify_jwt(valid_admin_token)
        assert payload["sub"] == str(admin_user_id)
        assert payload["aud"] == "authenticated"

    def test_expired_token_raises_401(self, expired_token):
        with pytest.raises(HTTPException) as exc_info:
            verify_jwt(expired_token)
        assert exc_info.value.status_code == 401
        assert "Invalid or expired token" in exc_info.value.detail

    def test_tampered_token_raises_401(self, valid_admin_token):
        tampered = valid_admin_token[:-5] + "XXXXX"
        with pytest.raises(HTTPException) as exc_info:
            verify_jwt(tampered)
        assert exc_info.value.status_code == 401

    def test_wrong_secret_raises_401(self, admin_user_id):
        now = int(time.time())
        payload = {
            "sub": str(admin_user_id),
            "aud": "authenticated",
            "iat": now,
            "exp": now + 3600,
        }
        token = jose_jwt.encode(payload, "wrong-secret-key-that-is-long-enough", algorithm="HS256")
        with pytest.raises(HTTPException) as exc_info:
            verify_jwt(token)
        assert exc_info.value.status_code == 401

    def test_wrong_audience_raises_401(self, jwt_secret, admin_user_id):
        now = int(time.time())
        payload = {
            "sub": str(admin_user_id),
            "aud": "wrong_audience",
            "iat": now,
            "exp": now + 3600,
        }
        token = jose_jwt.encode(payload, jwt_secret, algorithm="HS256")
        with pytest.raises(HTTPException) as exc_info:
            verify_jwt(token)
        assert exc_info.value.status_code == 401

    def test_valid_token_contains_sub_claim(self, valid_designer_token, designer_user_id):
        payload = verify_jwt(valid_designer_token)
        assert "sub" in payload
        assert payload["sub"] == str(designer_user_id)

    def test_completely_invalid_string_raises_401(self):
        with pytest.raises(HTTPException) as exc_info:
            verify_jwt("not-a-jwt-at-all")
        assert exc_info.value.status_code == 401

    def test_empty_token_raises_401(self):
        with pytest.raises(HTTPException) as exc_info:
            verify_jwt("")
        assert exc_info.value.status_code == 401
