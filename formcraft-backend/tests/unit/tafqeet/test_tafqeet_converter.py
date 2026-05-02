"""Unit tests for TafqeetConverter — written FIRST (TDD Red phase).

These tests MUST fail until app/services/tafqeet/converter.py is implemented.
Run with: pytest tests/unit/tafqeet/test_tafqeet_converter.py -v
"""

from decimal import Decimal

import pytest

from app.services.tafqeet.converter import TafqeetConverter

converter = TafqeetConverter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ar(amount, currency="EGP", show_currency=True, prefix="none", suffix="none"):
    return converter.convert(Decimal(str(amount)), currency, "ar", show_currency, prefix, suffix)


def en(amount, currency="EGP", show_currency=True, prefix="none", suffix="none"):
    return converter.convert(Decimal(str(amount)), currency, "en", show_currency, prefix, suffix)


def both(amount, currency="EGP", show_currency=True, prefix="none", suffix="none"):
    return converter.convert(Decimal(str(amount)), currency, "both", show_currency, prefix, suffix)


# ---------------------------------------------------------------------------
# Zero amounts
# ---------------------------------------------------------------------------

class TestZero:
    def test_zero_arabic(self):
        assert ar(0) == "صفر جنيه مصري"

    def test_zero_arabic_no_currency(self):
        assert ar(0, show_currency=False) == "صفر"

    def test_zero_english(self):
        assert en(0) == "Zero Egyptian Pounds"

    def test_zero_english_no_currency(self):
        assert en(0, show_currency=False) == "Zero"


# ---------------------------------------------------------------------------
# Integers — all four currencies
# ---------------------------------------------------------------------------

class TestIntegersCurrencies:
    @pytest.mark.parametrize("amount,currency,expected_fragment", [
        (1000, "EGP", "جنيه مصري"),
        (1000, "SAR", "ريال سعودي"),
        (1000, "AED", "درهم إماراتي"),
        (1000, "USD", "دولار أمريكي"),
    ])
    def test_arabic_currency_unit_present(self, amount, currency, expected_fragment):
        result = ar(amount, currency)
        assert result is not None
        assert expected_fragment in result

    @pytest.mark.parametrize("amount,currency,expected_fragment", [
        (1000, "EGP", "Egyptian Pound"),
        (1000, "SAR", "Saudi Riyal"),
        (1000, "AED", "UAE Dirham"),
        (1000, "USD", "US Dollar"),
    ])
    def test_english_currency_unit_present(self, amount, currency, expected_fragment):
        result = en(amount, currency)
        assert result is not None
        assert expected_fragment in result

    def test_arabic_whole_number_no_subunit(self):
        result = ar(2000, "SAR")
        assert result is not None
        assert "هللة" not in result

    def test_english_whole_number_no_subunit(self):
        result = en(2000, "SAR")
        assert result is not None
        assert "Halala" not in result


# ---------------------------------------------------------------------------
# Sub-unit (decimal) handling — US5
# ---------------------------------------------------------------------------

class TestSubUnits:
    @pytest.mark.parametrize("amount,currency,ar_subunit,en_subunit", [
        ("1500.25", "EGP", "قرش", "Piastre"),
        ("3000.50", "SAR", "هللة", "Halala"),
        ("750.10", "AED", "فلس", "Fils"),
        ("500.75", "USD", "سنت", "Cent"),
    ])
    def test_arabic_subunit_present(self, amount, currency, ar_subunit, en_subunit):
        result = ar(amount, currency)
        assert result is not None
        assert ar_subunit in result

    @pytest.mark.parametrize("amount,currency,ar_subunit,en_subunit", [
        ("1500.25", "EGP", "قرش", "Piastre"),
        ("3000.50", "SAR", "هللة", "Halala"),
        ("750.10", "AED", "فلس", "Fils"),
        ("500.75", "USD", "سنت", "Cent"),
    ])
    def test_english_subunit_present(self, amount, currency, ar_subunit, en_subunit):
        result = en(amount, currency)
        assert result is not None
        assert en_subunit in result

    def test_whole_number_omits_ar_subunit(self):
        assert "قرش" not in ar("2000.00", "EGP")

    def test_whole_number_omits_en_subunit(self):
        assert "Piastre" not in en("2000.00", "EGP")

    def test_rounding_to_2_decimal_places(self):
        # 1500.255 should round to 1500.26 → sub-unit = 26
        result = ar("1500.255", "EGP")
        assert result is not None  # must not raise


# ---------------------------------------------------------------------------
# Language modes — US3
# ---------------------------------------------------------------------------

class TestLanguageModes:
    def test_ar_only_no_english(self):
        result = ar(100, "EGP")
        assert result is not None
        assert "\n" not in result

    def test_en_only_no_arabic(self):
        result = en(100, "EGP")
        assert result is not None
        assert "\n" not in result
        # Result should be latin characters only
        assert not any("\u0600" <= c <= "\u06FF" for c in result)

    def test_both_two_lines(self):
        result = both(100, "EGP")
        assert result is not None
        lines = result.split("\n")
        assert len(lines) == 2
        # First line Arabic
        assert any("\u0600" <= c <= "\u06FF" for c in lines[0])
        # Second line English (Latin)
        assert not any("\u0600" <= c <= "\u06FF" for c in lines[1])

    def test_both_no_currency(self):
        result = converter.convert(Decimal("100"), "EGP", "both", False, "none", "none")
        assert result is not None
        assert "\n" in result


# ---------------------------------------------------------------------------
# Prefix / Suffix — US4
# ---------------------------------------------------------------------------

class TestPrefixSuffix:
    def test_ar_prefix_faqat(self):
        result = ar(1000, "EGP", prefix="faqat")
        assert result is not None
        assert result.startswith("فقط")

    def test_ar_suffix_la_ghair(self):
        result = ar(1000, "EGP", suffix="la_ghair")
        assert result is not None
        assert result.endswith("لا غير")

    def test_ar_suffix_faqat_la_ghair(self):
        result = ar(1000, "EGP", suffix="faqat_la_ghair")
        assert result is not None
        assert result.endswith("فقط لا غير")

    def test_en_suffix_only(self):
        result = en(1000, "EGP", suffix="only")
        assert result is not None
        assert result.endswith("Only")

    def test_ar_none_prefix_none_suffix(self):
        result = ar(1000, "EGP", prefix="none", suffix="none")
        assert result is not None
        assert not result.startswith("فقط")
        assert not result.endswith("لا غير")

    def test_en_no_prefix_map(self):
        # prefix "faqat" has no English translation — should not appear in English output
        result = en(1000, "EGP", prefix="faqat")
        assert result is not None
        # English prefix entry is empty string, should not prepend "فقط"
        assert "فقط" not in result


# ---------------------------------------------------------------------------
# show_currency = False
# ---------------------------------------------------------------------------

class TestShowCurrencyFalse:
    def test_arabic_no_unit(self):
        result = ar(500, "SAR", show_currency=False)
        assert result is not None
        assert "ريال" not in result
        assert "هللة" not in result

    def test_english_no_unit(self):
        result = en(500, "SAR", show_currency=False)
        assert result is not None
        assert "Riyal" not in result
        assert "Halala" not in result


# ---------------------------------------------------------------------------
# Edge cases — US7
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_negative_returns_none(self):
        assert converter.convert(Decimal("-1"), "EGP", "ar", True, "none", "none") is None

    def test_above_trillion_returns_none(self):
        assert converter.convert(Decimal("1000000000000"), "EGP", "ar", True, "none", "none") is None

    def test_max_valid_amount(self):
        result = converter.convert(Decimal("999999999999"), "EGP", "ar", True, "none", "none")
        assert result is not None

    def test_zero_decimal_no_subunit(self):
        result = ar("5000.00", "EGP")
        assert result is not None
        assert "قرش" not in result


# ---------------------------------------------------------------------------
# Library exception fallback
# ---------------------------------------------------------------------------

class TestExceptionFallback:
    def test_invalid_currency_returns_none(self):
        # CURRENCY_MAP lookup will raise KeyError → converter catches → returns None
        result = converter.convert(Decimal("100"), "XYZ", "ar", True, "none", "none")
        assert result is None


# ---------------------------------------------------------------------------
# Specific acceptance scenario values (from spec.md)
# ---------------------------------------------------------------------------

class TestAcceptanceScenarios:
    def test_sar_5500_75_arabic(self):
        result = ar("5500.75", "SAR")
        assert result is not None
        assert "ريال سعودي" in result
        assert "هللة" in result

    def test_egp_12500_50_both(self):
        result = both("12500.50", "EGP")
        assert result is not None
        lines = result.split("\n")
        assert len(lines) == 2
        assert "جنيه مصري" in lines[0]
        assert "Egyptian Pound" in lines[1]

    def test_sar_7350_arabic_faqat_la_ghair(self):
        result = ar("7350.00", "SAR", prefix="none", suffix="faqat_la_ghair")
        assert result is not None
        assert "ريال سعودي" in result
        assert result.endswith("فقط لا غير")
        assert "هللة" not in result  # whole number

    def test_egp_1500_25_subunit(self):
        result = ar("1500.25", "EGP")
        assert result is not None
        assert "جنيه مصري" in result
        assert "قرش" in result

    def test_aed_750_10_subunit(self):
        result = ar("750.10", "AED")
        assert result is not None
        assert "درهم إماراتي" in result
        assert "فلس" in result
