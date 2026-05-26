"""Unit tests for mfa_service."""

from uuid import uuid4

import pytest

from app.models.identity import MfaMethodType
from app.services.mfa_service import MfaService


class TestMfaService:
    def test_begin_enrollment_totp(self):
        user_id = uuid4()
        result = MfaService.begin_enrollment(user_id, MfaMethodType.TOTP)
        assert result["method_type"] == MfaMethodType.TOTP
        assert result["qr_code_uri"] is not None

    def test_begin_enrollment_sms(self):
        user_id = uuid4()
        result = MfaService.begin_enrollment(user_id, MfaMethodType.SMS, phone_number="+966500000000")
        assert result["method_type"] == MfaMethodType.SMS
        assert result["qr_code_uri"] is None
