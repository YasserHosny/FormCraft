"""Unit tests for AI suggestion schema validation."""

import pytest
from pydantic import ValidationError

from app.schemas.ai import SuggestionResponse


class TestSuggestionResponse:
    def test_valid_response(self):
        resp = SuggestionResponse(
            control_type="text",
            confidence=0.9,
            source="llm",
        )
        assert resp.control_type == "text"
        assert resp.confidence == 0.9

    def test_invalid_control_type_rejected(self):
        with pytest.raises(ValidationError):
            SuggestionResponse(
                control_type="unknown_type",
                confidence=0.5,
            )

    def test_confidence_out_of_range_rejected(self):
        with pytest.raises(ValidationError):
            SuggestionResponse(
                control_type="text",
                confidence=1.5,
            )

    def test_all_element_types_accepted(self):
        types = [
            "text", "number", "date", "currency", "dropdown",
            "radio", "checkbox", "image", "qr", "barcode",
        ]
        for t in types:
            resp = SuggestionResponse(control_type=t, confidence=0.8)
            assert resp.control_type == t
