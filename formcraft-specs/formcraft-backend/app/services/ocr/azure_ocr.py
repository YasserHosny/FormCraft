"""Azure Document Intelligence OCR client."""

import logging
from typing import Any

from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

from app.core.config import settings

logger = logging.getLogger(__name__)


class AzureOCRClient:
    """Client for Azure Document Intelligence OCR service."""

    def __init__(self):
        """Initialize Azure OCR client with credentials from settings."""
        if not settings.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT:
            raise ValueError("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT not configured")
        if not settings.AZURE_DOCUMENT_INTELLIGENCE_KEY:
            raise ValueError("AZURE_DOCUMENT_INTELLIGENCE_KEY not configured")

        self.client = DocumentAnalysisClient(
            endpoint=settings.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT,
            credential=AzureKeyCredential(settings.AZURE_DOCUMENT_INTELLIGENCE_KEY),
        )

    def analyze_layout(self, image_bytes: bytes) -> dict[str, Any]:
        """
        Analyze document layout and extract text with bounding boxes.

        Args:
            image_bytes: Image file content as bytes

        Returns:
            Dictionary containing:
            - words: List of detected words with bbox, text, confidence
            - lines: List of detected lines with bbox, text
            - page_dimensions: {width, height} in pixels
        """
        logger.info("Starting Azure OCR layout analysis")

        poller = self.client.begin_analyze_document(
            model_id="prebuilt-layout", document=image_bytes
        )
        result = poller.result()

        if not result.pages:
            logger.warning("No pages detected in document")
            return {"words": [], "lines": [], "page_dimensions": None}

        # Extract first page (support multi-page later)
        page = result.pages[0]
        page_width = page.width
        page_height = page.height

        logger.info(
            f"Detected page dimensions: {page_width}x{page_height} (unit: {page.unit})"
        )

        # Extract words with bounding boxes
        words = []
        for word in page.words or []:
            if word.polygon and len(word.polygon) >= 4:
                # Azure returns polygon points; extract bounding box (x, y, width, height)
                x_coords = [p.x for p in word.polygon]
                y_coords = [p.y for p in word.polygon]
                x = min(x_coords)
                y = min(y_coords)
                width = max(x_coords) - x
                height = max(y_coords) - y

                words.append(
                    {
                        "text": word.content,
                        "bbox": {"x": x, "y": y, "width": width, "height": height},
                        "confidence": word.confidence or 0.0,
                    }
                )

        # Extract lines (groups of words)
        lines = []
        for line in page.lines or []:
            if line.polygon and len(line.polygon) >= 4:
                x_coords = [p.x for p in line.polygon]
                y_coords = [p.y for p in line.polygon]
                x = min(x_coords)
                y = min(y_coords)
                width = max(x_coords) - x
                height = max(y_coords) - y

                lines.append(
                    {
                        "text": line.content,
                        "bbox": {"x": x, "y": y, "width": width, "height": height},
                    }
                )

        logger.info(f"Extracted {len(words)} words and {len(lines)} lines")

        return {
            "words": words,
            "lines": lines,
            "page_dimensions": {"width": page_width, "height": page_height},
        }
