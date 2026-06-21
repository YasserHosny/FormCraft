"""Unit tests for mfa_service."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.models.identity import MfaMethodType
from app.services.mfa_service import MfaService

_SUPA_PATCH = "app.services.mfa_service.get_supabase_client"


def _mock_supa_empty():
    m = MagicMock()
    m.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    m.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{}])
    return m


class TestMfaService:
    def test_begin_enrollment_totp(self):
        user_id = uuid4()
        with patch(_SUPA_PATCH, return_value=_mock_supa_empty()):
            result = MfaService.begin_enrollment(user_id, MfaMethodType.TOTP)
        assert result["method_type"] == MfaMethodType.TOTP
        assert result["qr_code_uri"] is not None

    def test_begin_enrollment_sms(self):
        user_id = uuid4()
        with patch(_SUPA_PATCH, return_value=_mock_supa_empty()):
            result = MfaService.begin_enrollment(user_id, MfaMethodType.SMS, phone_number="+966500000000")
        assert result["method_type"] == MfaMethodType.SMS
        assert result["qr_code_uri"] is None
