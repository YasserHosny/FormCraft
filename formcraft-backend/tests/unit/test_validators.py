"""Unit tests for Arabic-specific validators."""

import pytest

from app.services.validators.egypt import (
    EgyptIbanValidator,
    EgyptNationalIdValidator,
    EgyptPhoneValidator,
)
from app.services.validators.saudi import (
    SaudiIbanValidator,
    SaudiNationalIdValidator,
    SaudiVatValidator,
)
from app.services.validators.uae import UaeIbanValidator, UaeTrnValidator


class TestEgyptNationalId:
    def setup_method(self):
        self.validator = EgyptNationalIdValidator()

    def test_valid_id_starting_with_2(self):
        result = self.validator.validate("29901011234567")
        assert result.valid is True

    def test_valid_id_starting_with_3(self):
        result = self.validator.validate("30001011234567")
        assert result.valid is True

    def test_invalid_starts_with_1(self):
        result = self.validator.validate("19901011234567")
        assert result.valid is False

    def test_invalid_too_short(self):
        result = self.validator.validate("2990101123456")
        assert result.valid is False

    def test_invalid_too_long(self):
        result = self.validator.validate("299010112345678")
        assert result.valid is False

    def test_strips_spaces_and_dashes(self):
        result = self.validator.validate("2990-1011-234567")
        assert result.valid is True


class TestEgyptIban:
    def setup_method(self):
        self.validator = EgyptIbanValidator()

    def test_valid_iban(self):
        result = self.validator.validate("EG" + "0" * 27)
        assert result.valid is True

    def test_invalid_prefix(self):
        result = self.validator.validate("SA" + "0" * 27)
        assert result.valid is False

    def test_invalid_length(self):
        result = self.validator.validate("EG" + "0" * 26)
        assert result.valid is False


class TestEgyptPhone:
    def setup_method(self):
        self.validator = EgyptPhoneValidator()

    def test_valid_local(self):
        result = self.validator.validate("01012345678")
        assert result.valid is True

    def test_valid_international(self):
        result = self.validator.validate("+2001012345678")
        assert result.valid is True


class TestSaudiNationalId:
    def setup_method(self):
        self.validator = SaudiNationalIdValidator()

    def test_valid_citizen(self):
        result = self.validator.validate("1234567890")
        assert result.valid is True

    def test_valid_iqama(self):
        result = self.validator.validate("2123456789")
        assert result.valid is True

    def test_invalid_starts_with_3(self):
        result = self.validator.validate("3123456789")
        assert result.valid is False


class TestSaudiVat:
    def setup_method(self):
        self.validator = SaudiVatValidator()

    def test_valid(self):
        result = self.validator.validate("310000000000003")
        assert result.valid is True

    def test_invalid_not_starting_with_3(self):
        result = self.validator.validate("110000000000003")
        assert result.valid is False

    def test_invalid_not_ending_with_3(self):
        result = self.validator.validate("310000000000001")
        assert result.valid is False


class TestUaeIban:
    def setup_method(self):
        self.validator = UaeIbanValidator()

    def test_valid(self):
        result = self.validator.validate("AE" + "0" * 21)
        assert result.valid is True

    def test_invalid_prefix(self):
        result = self.validator.validate("EG" + "0" * 21)
        assert result.valid is False


class TestUaeTrn:
    def setup_method(self):
        self.validator = UaeTrnValidator()

    def test_valid(self):
        result = self.validator.validate("123456789012345")
        assert result.valid is True

    def test_invalid_too_short(self):
        result = self.validator.validate("12345678901234")
        assert result.valid is False
