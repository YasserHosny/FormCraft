import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status


class SignatureTokenService:
    """Handles opaque token generation and validation for public signer endpoints."""

    def __init__(self, client):
        self.client = client

    def generate_token(self) -> str:
        return secrets.token_urlsafe(32)

    def hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    async def create_signer_token(self, recipient_id: UUID, expires_in_hours: int = 168) -> str:
        token = self.generate_token()
        token_hash = self.hash_token(token)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)

        response = (
            self.client.table("signature_recipients")
            .update({"signature_token": token_hash, "token_expires_at": expires_at.isoformat()})
            .eq("id", str(recipient_id))
            .execute()
        )
        if not response.data:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to store signer token")
        return token

    async def validate_token(self, token: str) -> dict:
        token_hash = self.hash_token(token)
        result = (
            self.client.table("signature_recipients")
            .select("*, signature_requests!inner(*)")
            .eq("signature_token", token_hash)
            .single()
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Invalid or expired token")

        recipient = result.data
        expires_at = recipient.get("token_expires_at")
        if expires_at and datetime.fromisoformat(expires_at.replace("Z", "+00:00")) < datetime.now(timezone.utc):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Token expired")

        request_status = recipient.get("signature_requests", {}).get("status")
        if request_status in ("expired", "canceled", "failed"):
            raise HTTPException(status.HTTP_410_GONE, "Request is no longer active")

        return recipient
