"""Portal OTP service for generation, verification, and lockout."""

import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

logger = logging.getLogger(__name__)

OTP_CODE_LENGTH = 6
OTP_TTL_MINUTES = 10
LOCKOUT_MINUTES = 15
MAX_ATTEMPTS = 3


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _generate_code() -> str:
    return secrets.randbelow(10**OTP_CODE_LENGTH)


def _format_code(num: int) -> str:
    return f"{num:0{OTP_CODE_LENGTH}d}"


class OtpProvider:
    """Interface for OTP delivery providers."""

    async def send(self, contact_mode: str, contact_value: str, code: str) -> tuple[bool, str | None]:
        """Return (success, error_message)."""
        raise NotImplementedError


class MockOtpProvider(OtpProvider):
    """Development mock that always succeeds."""

    async def send(self, contact_mode: str, contact_value: str, code: str) -> tuple[bool, str | None]:
        logger.info("Mock OTP sent to %s (%s): %s", contact_value, contact_mode, code)
        return True, None


class PortalOtpService:
    """Service for OTP generation, sending, verification, and attempt lockout."""

    def __init__(self, client: Client, provider: OtpProvider | None = None):
        self.client = client
        self.provider = provider or MockOtpProvider()

    def _hash_contact(self, contact: str) -> str:
        return _hash(contact.lower().strip())

    def _hash_code(self, code: str) -> str:
        return _hash(code)

    async def send_otp(
        self,
        session_id: UUID,
        contact_mode: str,
        contact_value: str,
        allowed_modes: list[str],
    ) -> dict:
        """Send OTP for a portal session. Returns dict with status and expires_at."""
        if contact_mode not in allowed_modes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contact mode not allowed",
            )

        # Check session not locked
        session_resp = (
            self.client.table("portal_sessions")
            .select("status, org_id")
            .eq("id", str(session_id))
            .limit(1)
            .execute()
        )
        sessions = session_resp.data or []
        if not sessions:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session",
            )
        session = sessions[0]
        if session["status"] == "locked":
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Session locked due to too many failed attempts",
            )

        # Check existing pending not expired
        now = datetime.now(timezone.utc).isoformat()
        existing = (
            self.client.table("portal_otp_verifications")
            .select("*")
            .eq("portal_session_id", str(session_id))
            .eq("status", "pending")
            .gt("expires_at", now)
            .limit(1)
            .execute()
        )
        if existing.data:
            # Reuse expiry of latest pending
            expires_at = existing.data[0]["expires_at"]
            return {"status": "sent", "expires_at": expires_at}

        code = _format_code(_generate_code())
        code_hash = self._hash_code(code)
        contact_hash = self._hash_contact(contact_value)
        expires = datetime.now(timezone.utc) + timedelta(minutes=OTP_TTL_MINUTES)
        org_id = session["org_id"]

        # Send via provider
        success, provider_error = await self.provider.send(contact_mode, contact_value, code)

        data = {
            "org_id": org_id,
            "portal_session_id": str(session_id),
            "contact_mode": contact_mode,
            "contact_hash": contact_hash,
            "code_hash": code_hash,
            "expires_at": expires.isoformat(),
            "sent_at": datetime.now(timezone.utc).isoformat() if success else None,
            "status": "pending" if success else "provider_failed",
            "provider_error": provider_error,
        }
        self.client.table("portal_otp_verifications").insert(data).execute()

        if not success:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OTP provider unavailable; access remains blocked",
            )

        return {"status": "sent", "expires_at": expires.isoformat()}

    async def verify_otp(self, session_id: UUID, code: str) -> dict:
        """Verify OTP for a portal session."""
        now = datetime.now(timezone.utc).isoformat()

        # Fetch latest pending challenge for this session
        resp = (
            self.client.table("portal_otp_verifications")
            .select("*")
            .eq("portal_session_id", str(session_id))
            .eq("status", "pending")
            .gt("expires_at", now)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        rows = resp.data or []
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP",
            )

        challenge = rows[0]
        code_hash = self._hash_code(code)

        if challenge["code_hash"] != code_hash:
            # Increment attempt count
            new_attempts = challenge["attempt_count"] + 1
            update_data: dict = {"attempt_count": new_attempts}
            if new_attempts >= MAX_ATTEMPTS:
                locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_MINUTES)
                update_data["status"] = "locked"
                update_data["locked_until"] = locked_until.isoformat()
                # Also lock the session
                self.client.table("portal_sessions").update({"status": "locked"}).eq(
                    "id", str(session_id)
                ).execute()
            self.client.table("portal_otp_verifications").update(update_data).eq(
                "id", challenge["id"]
            ).execute()

            if new_attempts >= MAX_ATTEMPTS:
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail="OTP locked after too many failures",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP",
            )

        # Verified
        verified_at = datetime.now(timezone.utc)
        self.client.table("portal_otp_verifications").update(
            {"status": "verified", "verified_at": verified_at.isoformat()}
        ).eq("id", challenge["id"]).execute()

        self.client.table("portal_sessions").update(
            {
                "status": "otp_verified",
                "otp_verified_at": verified_at.isoformat(),
                "verified_contact_mode": challenge["contact_mode"],
                "verified_contact_hash": challenge["contact_hash"],
            }
        ).eq("id", str(session_id)).execute()

        return {"status": "verified"}
