"""Field classifier to suggest FormCraft element types from OCR results."""

import logging
import re
from typing import Literal

from app.models.enums import ElementType

logger = logging.getLogger(__name__)

# Arabic date indicators
DATE_INDICATORS_AR = ["تاريخ", "التاريخ", "اليوم", "Date"]
# Arabic currency/amount indicators
CURRENCY_INDICATORS_AR = ["مبلغ", "المبلغ", "القيمة", "Amount", "EGP", "ر.س", "SAR", "AED"]
# Arabic name indicators
NAME_INDICATORS_AR = ["اسم", "الاسم", "Name", "Pay to"]
# Arabic signature indicators
SIGNATURE_INDICATORS_AR = ["توقيع", "التوقيع", "Signature"]

# Date regex patterns
DATE_PATTERNS = [
    r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}",  # DD/MM/YYYY or DD-MM-YYYY
    r"\d{4}[-/]\d{1,2}[-/]\d{1,2}",  # YYYY/MM/DD
    r"\d{1,2}\s+\d{1,2}\s+\d{2,4}",  # DD MM YYYY with spaces
]

# Currency/amount patterns
CURRENCY_PATTERNS = [
    r"\d{1,3}(,\d{3})*(\.\d+)?",  # 12,345.67
    r"\d+\.\d{2,3}",  # 12345.67
]


class FieldClassifier:
    """Classifies detected OCR regions into FormCraft element types."""

    def classify_field(
        self, text: str, bbox: dict, nearby_labels: list[str] | None = None
    ) -> Literal[
        "date", "currency", "text", "number", "signature", "checkbox", "unknown"
    ]:
        """
        Classify a detected field into an element type.

        Args:
            text: Detected text content
            bbox: Bounding box {x, y, width, height}
            nearby_labels: Optional list of nearby label texts for context

        Returns:
            Suggested element type
        """
        text_lower = text.lower().strip()
        nearby_text = " ".join(nearby_labels or []).lower()

        # Check for date patterns
        if self._is_date_field(text, nearby_text):
            logger.debug(f"Classified as date: {text}")
            return "date"

        # Check for currency/amount patterns
        if self._is_currency_field(text, nearby_text):
            logger.debug(f"Classified as currency: {text}")
            return "currency"

        # Check for signature field (usually empty with nearby "signature" label)
        if self._is_signature_field(text, nearby_text, bbox):
            logger.debug(f"Classified as signature: {text}")
            return "signature"

        # Check for checkbox (small square regions, usually empty)
        if self._is_checkbox_field(text, bbox):
            logger.debug(f"Classified as checkbox: {text}")
            return "checkbox"

        # Check if numeric
        if self._is_number_field(text):
            logger.debug(f"Classified as number: {text}")
            return "number"

        # Default to text
        logger.debug(f"Classified as text: {text}")
        return "text"

    def _is_date_field(self, text: str, nearby_text: str) -> bool:
        """Check if field is a date."""
        # Check nearby labels for date indicators
        for indicator in DATE_INDICATORS_AR:
            if indicator.lower() in nearby_text:
                return True

        # Check text content for date patterns
        for pattern in DATE_PATTERNS:
            if re.search(pattern, text):
                return True

        return False

    def _is_currency_field(self, text: str, nearby_text: str) -> bool:
        """Check if field is a currency/amount."""
        # Check nearby labels for currency indicators
        for indicator in CURRENCY_INDICATORS_AR:
            if indicator.lower() in nearby_text:
                return True

        # Check for currency symbols in text
        if any(symbol in text for symbol in ["EGP", "ر.س", "SAR", "AED", "USD", "$"]):
            return True

        # Check for amount patterns with commas/decimals
        for pattern in CURRENCY_PATTERNS:
            if re.search(pattern, text):
                # If nearby text mentions amount/currency, classify as currency
                if any(
                    ind.lower() in nearby_text for ind in CURRENCY_INDICATORS_AR
                ):
                    return True

        return False

    def _is_signature_field(self, text: str, nearby_text: str, bbox: dict) -> bool:
        """Check if field is a signature area."""
        # Check nearby labels for signature indicators
        for indicator in SIGNATURE_INDICATORS_AR:
            if indicator.lower() in nearby_text:
                return True

        # Signature fields are usually empty or have minimal text
        if len(text.strip()) < 3 and bbox.get("width", 0) > 30:
            # Check if there's a signature label nearby
            if any(ind.lower() in nearby_text for ind in SIGNATURE_INDICATORS_AR):
                return True

        return False

    def _is_checkbox_field(self, text: str, bbox: dict) -> bool:
        """Check if field is a checkbox."""
        # Checkbox: small square, usually empty or with X/✓
        width = bbox.get("width", 0)
        height = bbox.get("height", 0)

        # Aspect ratio close to 1:1 (square)
        if width > 0 and height > 0:
            aspect_ratio = width / height
            is_square = 0.8 <= aspect_ratio <= 1.2

            # Small size (typically 5-15mm)
            is_small = width < 15 and height < 15

            # Empty or single character
            is_empty_or_check = len(text.strip()) <= 1

            if is_square and is_small and is_empty_or_check:
                return True

        return False

    def _is_number_field(self, text: str) -> bool:
        """Check if field contains only numbers."""
        # Remove common separators
        cleaned = text.replace(",", "").replace(".", "").replace(" ", "")
        return cleaned.isdigit() and len(cleaned) > 0

    def get_nearby_labels(
        self, target_bbox: dict, all_words: list[dict], max_distance: float = 50
    ) -> list[str]:
        """
        Find nearby label words for context.

        Args:
            target_bbox: Target field bounding box
            all_words: List of all detected words with bbox
            max_distance: Maximum distance in pixels to consider as "nearby"

        Returns:
            List of nearby word texts
        """
        nearby = []
        target_x = target_bbox["x"]
        target_y = target_bbox["y"]

        for word in all_words:
            word_bbox = word.get("bbox", {})
            word_x = word_bbox.get("x", 0)
            word_y = word_bbox.get("y", 0)

            # Calculate distance (simple Manhattan distance)
            distance = abs(target_x - word_x) + abs(target_y - word_y)

            if distance < max_distance:
                nearby.append(word.get("text", ""))

        return nearby
