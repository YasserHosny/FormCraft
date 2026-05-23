"""Unit tests for FieldClassifier."""

import pytest

from app.services.ocr.field_classifier import FieldClassifier


@pytest.fixture
def classifier():
    return FieldClassifier()


# --- T006: classify_field tests ---


class TestClassifyFieldDate:
    def test_date_pattern_dd_mm_yyyy(self, classifier):
        result = classifier.classify_field("25/09/2024", {"x": 0, "y": 0, "width": 50, "height": 10})
        assert result == "date"

    def test_date_pattern_dd_dash_mm_dash_yyyy(self, classifier):
        result = classifier.classify_field("25-09-2024", {"x": 0, "y": 0, "width": 50, "height": 10})
        assert result == "date"

    def test_date_pattern_yyyy_mm_dd(self, classifier):
        result = classifier.classify_field("2024/09/25", {"x": 0, "y": 0, "width": 50, "height": 10})
        assert result == "date"

    def test_date_from_nearby_label_arabic(self, classifier):
        result = classifier.classify_field(
            "some text", {"x": 0, "y": 0, "width": 50, "height": 10},
            nearby_labels=["تاريخ"]
        )
        assert result == "date"


class TestClassifyFieldCurrency:
    def test_currency_egp_symbol(self, classifier):
        result = classifier.classify_field("EGP 500", {"x": 0, "y": 0, "width": 50, "height": 10})
        assert result == "currency"

    def test_currency_sar_symbol(self, classifier):
        result = classifier.classify_field("SAR 1000", {"x": 0, "y": 0, "width": 50, "height": 10})
        assert result == "currency"

    def test_currency_aed_symbol(self, classifier):
        result = classifier.classify_field("AED 250", {"x": 0, "y": 0, "width": 50, "height": 10})
        assert result == "currency"

    def test_currency_from_nearby_label(self, classifier):
        result = classifier.classify_field(
            "12,500.00", {"x": 0, "y": 0, "width": 50, "height": 10},
            nearby_labels=["مبلغ"]
        )
        assert result == "currency"


class TestClassifyFieldSignature:
    def test_signature_nearby_label_arabic(self, classifier):
        result = classifier.classify_field(
            "", {"x": 0, "y": 0, "width": 50, "height": 15},
            nearby_labels=["توقيع"]
        )
        assert result == "signature"

    def test_signature_nearby_label_english(self, classifier):
        result = classifier.classify_field(
            "x", {"x": 0, "y": 0, "width": 50, "height": 15},
            nearby_labels=["Signature"]
        )
        assert result == "signature"


class TestClassifyFieldCheckbox:
    def test_checkbox_small_square_empty(self, classifier):
        result = classifier.classify_field(
            "", {"x": 0, "y": 0, "width": 10, "height": 10}
        )
        assert result == "checkbox"

    def test_checkbox_small_square_with_x(self, classifier):
        result = classifier.classify_field(
            "X", {"x": 0, "y": 0, "width": 12, "height": 12}
        )
        assert result == "checkbox"

    def test_not_checkbox_large_square(self, classifier):
        """Large square regions should not be classified as checkbox."""
        result = classifier.classify_field(
            "", {"x": 0, "y": 0, "width": 50, "height": 50}
        )
        assert result != "checkbox"


class TestClassifyFieldNumber:
    def test_number_digits_only(self, classifier):
        result = classifier.classify_field("12345", {"x": 0, "y": 0, "width": 50, "height": 10})
        assert result == "number"

    def test_number_with_commas(self, classifier):
        result = classifier.classify_field("1,234", {"x": 0, "y": 0, "width": 50, "height": 10})
        assert result == "number"


class TestClassifyFieldText:
    def test_text_default(self, classifier):
        result = classifier.classify_field("Ahmed Mohamed", {"x": 0, "y": 0, "width": 100, "height": 10})
        assert result == "text"

    def test_text_arabic_name(self, classifier):
        result = classifier.classify_field("أحمد محمد", {"x": 0, "y": 0, "width": 100, "height": 10})
        assert result == "text"


# --- T007: is_probable_label tests ---


class TestIsProbableLabel:
    def test_arabic_date_indicator_is_label(self, classifier):
        assert classifier.is_probable_label("تاريخ", {"x": 0, "y": 0, "width": 20, "height": 8}) is True

    def test_arabic_amount_indicator_is_label(self, classifier):
        assert classifier.is_probable_label("مبلغ", {"x": 0, "y": 0, "width": 20, "height": 8}) is True

    def test_arabic_signature_indicator_is_label(self, classifier):
        assert classifier.is_probable_label("توقيع", {"x": 0, "y": 0, "width": 20, "height": 8}) is True

    def test_english_name_indicator_is_label(self, classifier):
        assert classifier.is_probable_label("Name", {"x": 0, "y": 0, "width": 20, "height": 8}) is True

    def test_short_alpha_text_is_label(self, classifier):
        assert classifier.is_probable_label("Date", {"x": 0, "y": 0, "width": 15, "height": 6}) is True

    def test_empty_text_is_label(self, classifier):
        assert classifier.is_probable_label("", {"x": 0, "y": 0, "width": 10, "height": 5}) is True

    def test_long_text_not_label(self, classifier):
        assert classifier.is_probable_label(
            "Ahmed Mohamed Ibrahim Hassan",
            {"x": 0, "y": 0, "width": 150, "height": 12}
        ) is False

    def test_numeric_text_not_label(self, classifier):
        assert classifier.is_probable_label(
            "12345.67",
            {"x": 0, "y": 0, "width": 50, "height": 10}
        ) is False


# --- T044: Arabic-specific classification (Phase 6, added here for file consolidation) ---


class TestArabicClassification:
    """T044: Arabic-specific classification tests."""

    # --- Hijri dates ---

    def test_hijri_date_yyyy_mm_dd(self, classifier):
        result = classifier.classify_field("1445/06/15", {"x": 0, "y": 0, "width": 50, "height": 10})
        assert result == "date"

    def test_hijri_date_with_dash(self, classifier):
        result = classifier.classify_field("1446-03-21", {"x": 0, "y": 0, "width": 50, "height": 10})
        assert result == "date"

    def test_hijri_month_name_in_text(self, classifier):
        result = classifier.classify_field("15 رمضان 1445", {"x": 0, "y": 0, "width": 80, "height": 10})
        assert result == "date"

    def test_hijri_month_shawwal(self, classifier):
        result = classifier.classify_field("شوال", {"x": 0, "y": 0, "width": 30, "height": 10})
        assert result == "date"

    def test_hijri_nearby_label(self, classifier):
        result = classifier.classify_field(
            "15/06/1445", {"x": 0, "y": 0, "width": 50, "height": 10},
            nearby_labels=["هجري"]
        )
        assert result == "date"

    def test_arabic_day_name(self, classifier):
        result = classifier.classify_field("الخميس", {"x": 0, "y": 0, "width": 40, "height": 10})
        assert result == "date"

    def test_gregorian_month_arabic(self, classifier):
        result = classifier.classify_field("يناير", {"x": 0, "y": 0, "width": 40, "height": 10})
        assert result == "date"

    # --- Arabic currency ---

    def test_arabic_currency_nearby_label_egp(self, classifier):
        result = classifier.classify_field(
            "500.00", {"x": 0, "y": 0, "width": 50, "height": 10},
            nearby_labels=["المبلغ"]
        )
        assert result == "currency"

    def test_arabic_currency_name_guineh(self, classifier):
        """جنيه (Egyptian pound) in text."""
        result = classifier.classify_field(
            "500 جنيه", {"x": 0, "y": 0, "width": 60, "height": 10}
        )
        assert result == "currency"

    def test_arabic_currency_name_riyal(self, classifier):
        """ريال (Riyal) in text."""
        result = classifier.classify_field(
            "1000 ريال", {"x": 0, "y": 0, "width": 60, "height": 10}
        )
        assert result == "currency"

    def test_arabic_currency_name_dirham(self, classifier):
        """درهم (Dirham) in text."""
        result = classifier.classify_field(
            "250 درهم", {"x": 0, "y": 0, "width": 60, "height": 10}
        )
        assert result == "currency"

    def test_arabic_amount_in_words_faqat(self, classifier):
        """فقط (only) nearby indicates amount-in-words."""
        result = classifier.classify_field(
            "500.00", {"x": 0, "y": 0, "width": 50, "height": 10},
            nearby_labels=["فقط"]
        )
        assert result == "currency"

    def test_three_decimal_currency(self, classifier):
        """Three-decimal format common in KWD, BHD, OMR."""
        result = classifier.classify_field(
            "1,250.500", {"x": 0, "y": 0, "width": 50, "height": 10},
            nearby_labels=["المبلغ"]
        )
        assert result == "currency"

    def test_gulf_currency_code_qar(self, classifier):
        result = classifier.classify_field(
            "QAR 500", {"x": 0, "y": 0, "width": 50, "height": 10}
        )
        assert result == "currency"

    # --- Arabic signatures ---

    def test_arabic_signature_nearby_label(self, classifier):
        result = classifier.classify_field(
            "", {"x": 0, "y": 0, "width": 60, "height": 20},
            nearby_labels=["التوقيع"]
        )
        assert result == "signature"

    def test_arabic_signature_wide_empty_region(self, classifier):
        """Wide empty region near توقيع label = signature."""
        result = classifier.classify_field(
            "", {"x": 0, "y": 0, "width": 80, "height": 15},
            nearby_labels=["توقيع"]
        )
        assert result == "signature"

    def test_arabic_calligraphic_signature_aspect(self, classifier):
        """Very wide, shallow empty box = likely signature even without nearby label."""
        result = classifier.classify_field(
            "", {"x": 0, "y": 0, "width": 80, "height": 12},
        )
        assert result == "signature"

    # --- Mixed Arabic/English ---

    def test_mixed_form_date_english_nearby(self, classifier):
        result = classifier.classify_field(
            "25/12/2024", {"x": 0, "y": 0, "width": 50, "height": 10},
            nearby_labels=["Date"]
        )
        assert result == "date"

    def test_mixed_form_currency_arabic_nearby(self, classifier):
        result = classifier.classify_field(
            "1,500.00", {"x": 0, "y": 0, "width": 50, "height": 10},
            nearby_labels=["القيمة"]
        )
        assert result == "currency"

    def test_rtl_nearby_label_distance(self, classifier):
        """Labels to the right of fields in RTL should still be found."""
        # Target at x=200, label at x=350 (150px to the right)
        target_bbox = {"x": 200, "y": 100, "width": 100, "height": 10}
        words = [
            {"text": "التاريخ", "bbox": {"x": 350, "y": 100, "width": 30, "height": 10}},
        ]
        nearby = classifier.get_nearby_labels(target_bbox, words, max_distance=100)
        # Right edge of target (200+100=300) is only 50px from label at 350
        assert "التاريخ" in nearby
