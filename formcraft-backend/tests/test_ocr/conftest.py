"""Test fixtures for OCR service tests."""

import pytest


@pytest.fixture
def sample_ocr_response():
    """Mock Azure OCR response with typical cheque fields."""
    return {
        "words": [
            {
                "text": "25/09/2024",
                "bbox": {"x": 500, "y": 100, "width": 200, "height": 40},
                "confidence": 0.95,
            },
            {
                "text": "EGP",
                "bbox": {"x": 100, "y": 200, "width": 80, "height": 35},
                "confidence": 0.92,
            },
            {
                "text": "12,500.00",
                "bbox": {"x": 200, "y": 200, "width": 180, "height": 35},
                "confidence": 0.98,
            },
            {
                "text": "تاريخ",
                "bbox": {"x": 700, "y": 95, "width": 60, "height": 30},
                "confidence": 0.90,
            },
            {
                "text": "توقيع",
                "bbox": {"x": 50, "y": 400, "width": 55, "height": 25},
                "confidence": 0.88,
            },
            {
                "text": "",
                "bbox": {"x": 120, "y": 390, "width": 200, "height": 50},
                "confidence": 0.30,
            },
            {
                "text": "X",
                "bbox": {"x": 600, "y": 300, "width": 12, "height": 12},
                "confidence": 0.85,
            },
            {
                "text": "Ahmed",
                "bbox": {"x": 300, "y": 150, "width": 120, "height": 35},
                "confidence": 0.97,
            },
            {
                "text": "12345",
                "bbox": {"x": 400, "y": 350, "width": 100, "height": 30},
                "confidence": 0.99,
            },
        ],
        "lines": [],
        "page_dimensions": {"width": 800, "height": 500},
    }


@pytest.fixture
def sample_detected_fields_jsonb():
    """Sample detected_fields JSONB as stored in database."""
    return [
        {
            "text": "25/09/2024",
            "bbox": {"x": 132.29, "y": 26.46, "width": 52.92, "height": 10.58},
            "confidence": 0.95,
            "suggested_type": "date",
            "status": "pending",
        },
        {
            "text": "12,500.00",
            "bbox": {"x": 52.92, "y": 52.92, "width": 47.62, "height": 9.26},
            "confidence": 0.98,
            "suggested_type": "currency",
            "status": "pending",
        },
        {
            "text": "Ahmed",
            "bbox": {"x": 79.37, "y": 39.69, "width": 31.75, "height": 9.26},
            "confidence": 0.97,
            "suggested_type": "text",
            "status": "pending",
        },
    ]


@pytest.fixture
def sample_bbox_px():
    """Sample bounding box in pixel coordinates."""
    return {"x": 100, "y": 200, "width": 300, "height": 50}
