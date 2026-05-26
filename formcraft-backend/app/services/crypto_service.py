"""AES-256-GCM encryption service for IdP secrets."""

from __future__ import annotations

import base64
import logging
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings

logger = logging.getLogger(__name__)


def _get_master_key() -> bytes:
    """Derive a 32-byte AES key from the configured secret."""
    raw = getattr(settings, "SSO_ENCRYPTION_KEY", "")
    if not raw:
        logger.warning("SSO_ENCRYPTION_KEY not set; using fallback (NOT FOR PRODUCTION)")
        raw = settings.SUPABASE_JWT_SECRET
    key = raw.encode("utf-8")
    # Pad or truncate to 32 bytes
    if len(key) < 32:
        key = key + b"\0" * (32 - len(key))
    return key[:32]


def encrypt_value(plaintext: str) -> str:
    """Encrypt plaintext and return base64-encoded 'nonce:ciphertext'."""
    key = _get_master_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    combined = nonce + ciphertext
    return base64.b64encode(combined).decode("utf-8")


def decrypt_value(token: str) -> str:
    """Decrypt a base64-encoded 'nonce:ciphertext' token."""
    key = _get_master_key()
    aesgcm = AESGCM(key)
    combined = base64.b64decode(token.encode("utf-8"))
    nonce, ciphertext = combined[:12], combined[12:]
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")
