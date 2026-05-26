"""MFA service: TOTP and SMS/Email OTP."""

from __future__ import annotations

import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

import pyotp
from app.core.supabase import get_supabase_client
from app.models.identity import MfaEnrollment, MfaMethodType
from app.services.crypto_service import decrypt_value, encrypt_value

logger = logging.getLogger(__name__)

OTP_VALIDITY_MINUTES = 5
MAX_ACTIVE_METHODS = 2


def _encrypt_secret(raw: str) -> str:
    return encrypt_value(raw)


def _decrypt_secret(token: str) -> str:
    return decrypt_value(token)


class MfaService:
    """Business logic for MFA enrollment, challenge, and recovery."""

    @staticmethod
    def begin_enrollment(user_id: UUID, method_type: MfaMethodType, phone_number: str | None = None) -> dict[str, Any]:
        client = get_supabase_client()
        # Enforce max active methods
        existing = (
            client.table("mfa_enrollments")
            .select("*")
            .eq("user_id", str(user_id))
            .eq("is_active", True)
            .execute()
        )
        if len(existing.data or []) >= MAX_ACTIVE_METHODS:
            raise ValueError("Maximum active MFA methods reached")

        enrollment_id = uuid4()
        if method_type == MfaMethodType.TOTP:
            raw_secret = pyotp.random_base32()
            encrypted = _encrypt_secret(raw_secret)
            qr_uri = pyotp.totp.TOTP(raw_secret).provisioning_uri(
                name=str(user_id), issuer_name="FormCraft"
            )
        else:
            raw_secret = secrets.token_hex(16)
            encrypted = _encrypt_secret(raw_secret)
            qr_uri = None

        payload = {
            "id": str(enrollment_id),
            "user_id": str(user_id),
            "method_type": method_type.value,
            "secret": encrypted,
            "phone_number": phone_number,
            "is_verified": False,
            "is_active": False,
            "recovery_codes": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        client.table("mfa_enrollments").insert(payload).execute()
        return {"enrollment_id": enrollment_id, "method_type": method_type, "qr_code_uri": qr_uri}

    @staticmethod
    def verify_enrollment(enrollment_id: UUID, user_id: UUID, code: str) -> dict[str, Any]:
        client = get_supabase_client()
        row = (
            client.table("mfa_enrollments")
            .select("*")
            .eq("id", str(enrollment_id))
            .eq("user_id", str(user_id))
            .single()
            .execute()
        )
        if not row.data:
            raise ValueError("Enrollment not found")

        enrollment = MfaEnrollment(**row.data)
        raw_secret = _decrypt_secret(enrollment.secret)

        if enrollment.method_type == MfaMethodType.TOTP:
            valid = pyotp.totp.TOTP(raw_secret).verify(code, valid_window=1)
        else:
            valid = raw_secret == code  # simplistic; real impl uses stored OTP with expiry

        if not valid:
            raise ValueError("Invalid verification code")

        recovery_codes = [secrets.token_hex(4).upper() for _ in range(5)]
        encrypted_codes = [_encrypt_secret(c) for c in recovery_codes]

        client.table("mfa_enrollments").update({
            "is_verified": True,
            "is_active": True,
            "recovery_codes": encrypted_codes,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", str(enrollment_id)).execute()

        return {"is_verified": True, "recovery_codes": recovery_codes}

    @staticmethod
    def generate_challenge(user_id: UUID) -> dict[str, Any]:
        client = get_supabase_client()
        rows = (
            client.table("mfa_enrollments")
            .select("*")
            .eq("user_id", str(user_id))
            .eq("is_active", True)
            .execute()
        )
        if not rows.data:
            raise ValueError("No active MFA enrollment")

        enrollment = MfaEnrollment(**rows.data[0])
        challenge_id = uuid4()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_VALIDITY_MINUTES)

        # Store challenge in a simple table-less cache (for production use Redis/cache)
        # Here we update last_challenged_at as a proxy
        client.table("mfa_enrollments").update({
            "last_challenged_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", str(enrollment.id)).execute()

        return {
            "challenge_id": challenge_id,
            "method_type": enrollment.method_type,
            "expires_at": expires_at,
        }

    @staticmethod
    def verify_challenge(user_id: UUID, code: str) -> bool:
        client = get_supabase_client()
        rows = (
            client.table("mfa_enrollments")
            .select("*")
            .eq("user_id", str(user_id))
            .eq("is_active", True)
            .execute()
        )
        for raw in rows.data or []:
            enrollment = MfaEnrollment(**raw)
            raw_secret = _decrypt_secret(enrollment.secret)
            if enrollment.method_type == MfaMethodType.TOTP:
                if pyotp.totp.TOTP(raw_secret).verify(code, valid_window=1):
                    return True
            else:
                if raw_secret == code:
                    return True
        return False

    @staticmethod
    def use_recovery_code(user_id: UUID, recovery_code: str) -> dict[str, Any]:
        client = get_supabase_client()
        rows = (
            client.table("mfa_enrollments")
            .select("*")
            .eq("user_id", str(user_id))
            .eq("is_active", True)
            .execute()
        )
        for raw in rows.data or []:
            enrollment = MfaEnrollment(**raw)
            if not enrollment.recovery_codes:
                continue
            decrypted = [_decrypt_secret(c) for c in enrollment.recovery_codes]
            if recovery_code in decrypted:
                decrypted.remove(recovery_code)
                new_codes = [_encrypt_secret(c) for c in decrypted]
                client.table("mfa_enrollments").update({
                    "recovery_codes": new_codes if new_codes else None,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }).eq("id", str(enrollment.id)).execute()
                return {"token": "jwt-with-mfa-verified-claim", "remaining_codes": len(decrypted)}
        raise ValueError("Invalid recovery code")
