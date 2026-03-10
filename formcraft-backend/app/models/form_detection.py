"""Form detection models for OCR field detection."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class DetectedField(BaseModel):
    """A single detected field from OCR."""

    text: str = Field(description="Detected text content")
    bbox: dict[str, float] = Field(description="Bounding box in mm: {x, y, width, height}")
    confidence: float = Field(ge=0.0, le=1.0, description="OCR confidence score")
    suggested_type: Literal[
        "date", "currency", "text", "number", "signature", "checkbox", "unknown"
    ] = Field(description="Suggested FormCraft element type")
    status: Literal["pending", "accepted", "rejected"] = Field(
        default="pending", description="Review status"
    )


class FormDetectionCreate(BaseModel):
    """Request to create form detection from uploaded image."""

    template_id: UUID
    page_index: int = Field(ge=0, description="Zero-indexed page number")
    image_data: bytes = Field(description="Image file content")


class FormDetectionResponse(BaseModel):
    """Response containing OCR detection results."""

    id: UUID
    template_id: UUID
    page_index: int
    detected_fields: list[DetectedField]
    page_dimensions: dict[str, float]  # {width, height} in mm
    created_at: datetime

    class Config:
        from_attributes = True


class AcceptDetectionRequest(BaseModel):
    """Request to accept detection(s) and create elements."""

    detection_ids: list[int] = Field(
        description="Indices of detections to accept from the detected_fields array"
    )
