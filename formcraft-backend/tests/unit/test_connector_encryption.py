"""Phase 1 .T tests for encryption-at-rest + HMAC signing (Feature 049 FR-6)."""

import hashlib
import hmac
import json
import os
from uuid import uuid4

import pytest

# Ensure deterministic master key for the entire test module
os.environ.setdefault("INTEGRATION_MASTER_KEY", "test-master-key-do-not-use-in-prod-32chars-min")

# Import AFTER env is set so lru_cache picks up the right master
from app.services.connectors.encryption_service import (  # noqa: E402
    decrypt_dict_for_org,
    decrypt_for_org,
    encrypt_dict_for_org,
    encrypt_for_org,
    mask_dict,
)
from app.services.connectors.api_key_service import ApiKeyService  # noqa: E402
from app.services.connectors.webhook_dispatcher import _sign_payload, _mask_sensitive  # noqa: E402


# ----------------------------------------------------------------------
# Encryption round-trips
# ----------------------------------------------------------------------

class TestEncryptionRoundTrip:
    def test_encrypt_then_decrypt_returns_plaintext(self):
        org_id = uuid4()
        plaintext = "Bearer eyJhbGciOiJIUzI1NiJ9.xxx.yyy"
        ct = encrypt_for_org(plaintext, org_id)
        assert ct.startswith("v1:")
        assert plaintext not in ct  # never appears in ciphertext
        pt = decrypt_for_org(ct, org_id)
        assert pt == plaintext

    def test_different_orgs_get_different_ciphertexts(self):
        org_a, org_b = uuid4(), uuid4()
        plaintext = "shared-secret-value"
        ct_a = encrypt_for_org(plaintext, org_a)
        ct_b = encrypt_for_org(plaintext, org_b)
        assert ct_a != ct_b
        # Cross-org decryption must fail
        assert decrypt_for_org(ct_a, org_b) is None
        assert decrypt_for_org(ct_b, org_a) is None

    def test_corrupted_ciphertext_returns_none(self):
        org_id = uuid4()
        ct = encrypt_for_org("hello", org_id)
        tampered = ct[:-5] + "ZZZZZ"
        assert decrypt_for_org(tampered, org_id) is None

    def test_empty_string_is_safe(self):
        org_id = uuid4()
        ct = encrypt_for_org("", org_id)
        assert decrypt_for_org(ct, org_id) == ""


class TestDictHelpers:
    def test_dict_round_trip(self):
        org_id = uuid4()
        plain = {"Authorization": "Bearer xyz", "X-Custom": "val"}
        enc = encrypt_dict_for_org(plain, org_id)
        assert all(v.startswith("v1:") for v in enc.values())
        assert set(enc.keys()) == set(plain.keys())
        out = decrypt_dict_for_org(enc, org_id)
        assert out == plain

    def test_mask_returns_dots_for_each_key(self):
        masked = mask_dict({"Authorization": "secret", "X-Other": "val"})
        assert masked == {"Authorization": "●●●●●", "X-Other": "●●●●●"}
        # Original secrets must not appear
        assert "secret" not in str(masked)


# ----------------------------------------------------------------------
# API key secret hashing
# ----------------------------------------------------------------------

class TestApiKeyHashing:
    def test_same_secret_hashes_identically(self):
        h1 = ApiKeyService.hash_for_lookup("fck_abc123")
        h2 = ApiKeyService.hash_for_lookup("fck_abc123")
        assert h1 == h2

    def test_different_secrets_hash_differently(self):
        assert ApiKeyService.hash_for_lookup("fck_a") != ApiKeyService.hash_for_lookup("fck_b")

    def test_hash_is_64_hex_chars(self):
        # SHA-256 → 32 bytes → 64 hex chars
        h = ApiKeyService.hash_for_lookup("any")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_hash_does_not_contain_secret(self):
        secret = "fck_supersecret"
        assert secret not in ApiKeyService.hash_for_lookup(secret)


# ----------------------------------------------------------------------
# HMAC signature contract (must match what receivers verify)
# ----------------------------------------------------------------------

class TestPayloadSigning:
    def test_signature_is_hex_sha256(self):
        sig = _sign_payload(b'{"a":1}', "secret")
        assert len(sig) == 64
        assert all(c in "0123456789abcdef" for c in sig)

    def test_signature_matches_external_verifier(self):
        """Receivers will verify with hmac.new(secret, body, sha256).hexdigest()."""
        secret = "shared-secret-12345"
        body = b'{"event":"form_submitted","resource_id":"abc"}'
        ours = _sign_payload(body, secret)
        theirs = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        assert ours == theirs

    def test_signature_is_sensitive_to_payload(self):
        sig1 = _sign_payload(b'{"a":1}', "secret")
        sig2 = _sign_payload(b'{"a":2}', "secret")
        assert sig1 != sig2

    def test_signature_is_sensitive_to_secret(self):
        sig1 = _sign_payload(b'{"a":1}', "secret-A")
        sig2 = _sign_payload(b'{"a":1}', "secret-B")
        assert sig1 != sig2


# ----------------------------------------------------------------------
# Banking PAN-mask helper (Constitution compliance + spec FR-6)
# ----------------------------------------------------------------------

class TestPanMasking:
    def test_mask_visible_16_digit_pan(self):
        body = '{"card":"4111111111111111","name":"Test"}'
        masked = _mask_sensitive(body)
        assert "4111111111111111" not in masked
        # First 8 and last 4 are preserved per implementation
        assert "1111" in masked  # last-4

    def test_mask_visible_iban_like_run(self):
        body = "transfer to AE070331234567890123456 succeeded"
        masked = _mask_sensitive(body)
        # IBAN body should not appear in full
        assert "070331234567890123456" not in masked

    def test_short_numbers_unchanged(self):
        body = "code 1234 verified"
        assert _mask_sensitive(body) == body
