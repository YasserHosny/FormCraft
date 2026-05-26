"""Unit tests for crypto_service."""

import pytest

from app.services.crypto_service import decrypt_value, encrypt_value


def test_encrypt_decrypt_roundtrip():
    plaintext = "my-secret-value"
    token = encrypt_value(plaintext)
    assert token != plaintext
    recovered = decrypt_value(token)
    assert recovered == plaintext


def test_encrypt_produces_different_tokens():
    plaintext = "my-secret-value"
    t1 = encrypt_value(plaintext)
    t2 = encrypt_value(plaintext)
    assert t1 != t2  # nonce should be random
