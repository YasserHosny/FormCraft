"""Encryption-at-rest helper for Feature 049 connector framework.

Implements FR-6 from spec: webhook custom_headers values and connector secret
config fields are encrypted at rest using a per-org Data Encryption Key (DEK)
derived from a master key stored in environment configuration.

Cleartext only exists in two places:
  1. Inside the dispatcher worker, immediately before the outbound HTTP call.
  2. Inside the admin POST/PUT/regenerate response body (one-time display).

Storage layer (DB columns suffixed `_enc`) NEVER contains cleartext.

KMS Design Choice:
  We use a deterministic per-org sub-key derived from a master key. The master key
  is loaded from `INTEGRATION_MASTER_KEY` env var. In production this should be
  rotated via key versioning (deferred until ≥3 customer requests per Constitution
  YAGNI; for Phase 1, a single master key with version=1 is sufficient).
"""

from __future__ import annotations

import base64
import hashlib
import os
from functools import lru_cache
from uuid import UUID

from cryptography.fernet import Fernet, InvalidToken


_KEY_VERSION_PREFIX = "v1:"


class EncryptionConfigError(RuntimeError):
    """Raised when the master key is missing or malformed."""


def _load_master_key() -> bytes:
    raw = os.environ.get("INTEGRATION_MASTER_KEY")
    if not raw:
        raise EncryptionConfigError(
            "INTEGRATION_MASTER_KEY environment variable is not set. "
            "Generate one with `python -c 'import secrets; print(secrets.token_urlsafe(32))'`."
        )
    if len(raw) < 32:
        raise EncryptionConfigError("INTEGRATION_MASTER_KEY must be at least 32 chars")
    return raw.encode("utf-8")


@lru_cache(maxsize=256)
def _org_fernet(org_id_str: str) -> Fernet:
    """Derive a per-org Fernet key from the master key + org_id (HKDF-like)."""
    master = _load_master_key()
    # HMAC-SHA256(master_key, org_id) → 32 bytes → urlsafe b64 for Fernet
    digest = hashlib.pbkdf2_hmac("sha256", master, org_id_str.encode("utf-8"), iterations=10_000, dklen=32)
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_for_org(plaintext: str, org_id: UUID | str) -> str:
    """Encrypt a string value for storage. Returns 'v1:<token>' so we can rotate keys later."""
    if plaintext is None:
        return ""
    if not isinstance(plaintext, str):
        plaintext = str(plaintext)
    token = _org_fernet(str(org_id)).encrypt(plaintext.encode("utf-8")).decode("ascii")
    return f"{_KEY_VERSION_PREFIX}{token}"


def decrypt_for_org(ciphertext: str, org_id: UUID | str) -> str | None:
    """Decrypt a value previously encrypted with encrypt_for_org. Returns None on failure."""
    if not ciphertext:
        return None
    if not ciphertext.startswith(_KEY_VERSION_PREFIX):
        # Tolerate legacy un-versioned tokens during migrations
        token = ciphertext
    else:
        token = ciphertext[len(_KEY_VERSION_PREFIX):]
    try:
        return _org_fernet(str(org_id)).decrypt(token.encode("ascii")).decode("utf-8")
    except (InvalidToken, ValueError):
        return None


def encrypt_dict_for_org(values: dict[str, str], org_id: UUID | str) -> dict[str, str]:
    """Encrypt every value in a {header_name: value} or {config_key: secret} dict."""
    return {k: encrypt_for_org(v, org_id) for k, v in (values or {}).items() if v is not None}


def decrypt_dict_for_org(values: dict[str, str], org_id: UUID | str) -> dict[str, str]:
    """Decrypt every value in a previously encrypted dict. Failed entries are dropped."""
    out: dict[str, str] = {}
    for k, v in (values or {}).items():
        plaintext = decrypt_for_org(v, org_id)
        if plaintext is not None:
            out[k] = plaintext
    return out


def mask_dict(values: dict[str, str]) -> dict[str, str]:
    """Return {header_name: '●●●●●'} for display in admin UI / API responses."""
    return {k: "●●●●●" for k in (values or {})}
