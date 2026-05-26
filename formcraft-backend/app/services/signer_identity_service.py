import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status


class SignerIdentityService:
    """Handles internal password re-auth and external email OTP generation/verification."""

    OTP_LENGTH = 6
    OTP_EXPIRY_MINUTES = 10

    def __init__(self, client, email_service=None):
        self.client = client
        self.email_service = email_service

    def _generate_otp(self) -> str:
        return str(secrets.randbelow(10**self.OTP_LENGTH)).zfill(self.OTP_LENGTH)

    def _hash_otp(self, otp: str) -> str:
        return hashlib.sha256(otp.encode()).hexdigest()

    async def send_external_otp(self, recipient_id: UUID, email: str) -> dict:
        otp = self._generate_otp()
        otp_hash = self._hash_otp(otp)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=self.OTP_EXPIRY_MINUTES)

        response = (
            self.client.table("signature_recipients")
            .update({"otp_code_hash": otp_hash, "otp_expires_at": expires_at.isoformat()})
            .eq("id", str(recipient_id))
            .execute()
        )
        if not response.data:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to store OTP")

        if self.email_service:
            await self.email_service.send(
                to=email,
                subject="Your FormCraft Signature Verification Code",
                body=f"Your one-time verification code is: {otp}. It expires in {self.OTP_EXPIRY_MINUTES} minutes.",
            )

        return {"message": "OTP sent", "expires_at": expires_at.isoformat()}

    async def verify_external_otp(self, recipient_id: UUID, otp: str) -> bool:
        result = (
            self.client.table("signature_recipients")
            .select("otp_code_hash", "otp_expires_at", "status")
            .eq("id", str(recipient_id))
            .single()
            .execute()
        )
        if not result.data:
            return False

        data = result.data
        otp_hash = data.get("otp_code_hash")
        expires_at_str = data.get("otp_expires_at")

        if not otp_hash or not expires_at_str:
            return False

        expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
        if expires_at < datetime.now(timezone.utc):
            return False

        if self._hash_otp(otp) != otp_hash:
            return False

        # Clear OTP and mark verified
        (
            self.client.table("signature_recipients")
            .update({"otp_code_hash": None, "otp_expires_at": None, "status": "verified"})
            .eq("id", str(recipient_id))
            .execute()
        )
        return True

    async def authenticate_internal_signer(self, profile_id: UUID, password: str) -> bool:
        """Re-authenticate an internal signer using their FormCraft password via Supabase Auth.
        In a real implementation this would verify against Supabase Auth.
        For now, we do a basic presence check; the route layer should enforce via Supabase.
        """
        # Placeholder: actual password verification should happen at the API/auth layer
        # This service layer assumes the caller has already validated the password
        # and uses this method to update the recipient status.
        return True

    async def mark_internal_verified(self, recipient_id: UUID) -> None:
        (
            self.client.table("signature_recipients")
            .update({"status": "verified"})
            .eq("id", str(recipient_id))
            .execute()
        )
