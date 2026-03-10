"""Unit tests for label matcher."""

import pytest

from app.services.validators.label_matcher import LabelMatcher


class TestLabelMatcher:
    def setup_method(self):
        self.matcher = LabelMatcher()

    def test_egyptian_national_id_arabic(self):
        result = self.matcher.match("الرقم القومي", "EG")
        assert result == ("EG", "national_id")

    def test_saudi_vat_arabic(self):
        result = self.matcher.match("الرقم الضريبي", "SA")
        assert result == ("SA", "vat_number")

    def test_uae_iban_english(self):
        result = self.matcher.match("IBAN Number", "AE")
        assert result == ("AE", "iban")

    def test_unknown_label_returns_none(self):
        result = self.matcher.match("favorite color", "EG")
        assert result is None

    def test_case_insensitive(self):
        result = self.matcher.match("IBAN", "SA")
        assert result == ("SA", "iban")

    def test_unknown_country_returns_none(self):
        result = self.matcher.match("الرقم القومي", "US")
        assert result is None
