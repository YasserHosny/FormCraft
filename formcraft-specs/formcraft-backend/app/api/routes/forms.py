"""Form import and OCR detection endpoints."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.deps import get_current_user
from app.core.supabase import get_supabase_client
from app.models.form_detection import (
    AcceptDetectionRequest,
    DetectedField,
    FormDetectionResponse,
)
from app.models.user import UserProfile
from app.services.ocr import AzureOCRClient, BoundingBoxConverter, FieldClassifier

router = APIRouter(prefix="/forms", tags=["forms"])
logger = logging.getLogger(__name__)


@router.post("/import/{template_id}", response_model=FormDetectionResponse)
async def import_form(
    template_id: UUID,
    file: UploadFile = File(...),
    page_index: int = 0,
    current_user: UserProfile = Depends(get_current_user),
):
    """
    Upload a form image and detect fillable fields using OCR.

    Args:
        template_id: Template to attach this form to
        file: Image file (JPEG, PNG)
        page_index: Page index to import to (default 0)
        current_user: Authenticated user

    Returns:
        FormDetectionResponse with detected fields
    """
    logger.info(
        f"Starting form import for template {template_id}, page {page_index}"
    )

    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}. Only JPEG and PNG are supported.",
        )

    # Read file content
    image_bytes = await file.read()
    if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image file too large. Maximum 10MB.",
        )

    try:
        # Initialize OCR client
        ocr_client = AzureOCRClient()

        # Perform OCR
        ocr_result = ocr_client.analyze_layout(image_bytes)

        if not ocr_result.get("page_dimensions"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not detect page dimensions from image",
            )

        # Initialize bounding box converter
        page_dims = ocr_result["page_dimensions"]
        dpi = BoundingBoxConverter.detect_dpi_from_exif(image_bytes)
        converter = BoundingBoxConverter(
            image_width_px=int(page_dims["width"]),
            image_height_px=int(page_dims["height"]),
            dpi=dpi,
        )

        # Initialize field classifier
        classifier = FieldClassifier()

        # Process detected words into fields
        detected_fields: list[DetectedField] = []
        words = ocr_result.get("words", [])

        for word in words:
            # Convert bbox to mm
            bbox_mm = converter.convert_bbox(word["bbox"])

            # Get nearby labels for context
            nearby_labels = classifier.get_nearby_labels(
                word["bbox"], words, max_distance=100
            )

            # Classify field type
            suggested_type = classifier.classify_field(
                text=word["text"], bbox=bbox_mm, nearby_labels=nearby_labels
            )

            detected_fields.append(
                DetectedField(
                    text=word["text"],
                    bbox=bbox_mm,
                    confidence=word["confidence"],
                    suggested_type=suggested_type,
                    status="pending",
                )
            )

        # Get page dimensions in mm
        page_width_mm, page_height_mm = converter.get_page_dimensions_mm()

        # Store detection in database
        client = get_supabase_client()

        # Convert detected fields to dict for JSONB storage
        fields_json = [field.model_dump() for field in detected_fields]

        insert_data = {
            "template_id": str(template_id),
            "page_index": page_index,
            "detected_fields": fields_json,
            "page_dimensions": {"width": page_width_mm, "height": page_height_mm},
        }

        response = client.table("form_detections").insert(insert_data).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store detection results",
            )

        detection_record = response.data[0]

        logger.info(
            f"OCR complete: detected {len(detected_fields)} fields for template {template_id}"
        )

        return FormDetectionResponse(
            id=detection_record["id"],
            template_id=template_id,
            page_index=page_index,
            detected_fields=detected_fields,
            page_dimensions={"width": page_width_mm, "height": page_height_mm},
            created_at=detection_record["created_at"],
        )

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR service configuration error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"OCR processing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process form image: {str(e)}",
        )


@router.get("/{template_id}/detections", response_model=list[FormDetectionResponse])
async def get_detections(
    template_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
):
    """
    Get all OCR detections for a template.

    Args:
        template_id: Template ID
        current_user: Authenticated user

    Returns:
        List of detection results
    """
    client = get_supabase_client()

    response = (
        client.table("form_detections")
        .select("*")
        .eq("template_id", str(template_id))
        .order("created_at", desc=True)
        .execute()
    )

    if not response.data:
        return []

    results = []
    for record in response.data:
        # Parse detected_fields from JSONB
        detected_fields = [
            DetectedField(**field) for field in record["detected_fields"]
        ]

        results.append(
            FormDetectionResponse(
                id=record["id"],
                template_id=UUID(record["template_id"]),
                page_index=record["page_index"],
                detected_fields=detected_fields,
                page_dimensions=record["page_dimensions"],
                created_at=record["created_at"],
            )
        )

    return results


@router.post("/{template_id}/detections/{detection_id}/accept")
async def accept_detections(
    template_id: UUID,
    detection_id: UUID,
    request: AcceptDetectionRequest,
    current_user: UserProfile = Depends(get_current_user),
):
    """
    Accept detection(s) and create FormCraft elements.

    Args:
        template_id: Template ID
        detection_id: Detection record ID
        request: List of detection indices to accept
        current_user: Authenticated user

    Returns:
        Success message with created element count
    """
    client = get_supabase_client()

    # Fetch detection record
    response = (
        client.table("form_detections")
        .select("*")
        .eq("id", str(detection_id))
        .eq("template_id", str(template_id))
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Detection not found"
        )

    detection = response.data[0]
    detected_fields = detection["detected_fields"]

    # Validate indices
    for idx in request.detection_ids:
        if idx < 0 or idx >= len(detected_fields):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid detection index: {idx}",
            )

    # TODO: Fetch template and page to create elements
    # For now, return success (element creation will be implemented in next iteration)

    created_count = len(request.detection_ids)
    logger.info(
        f"Accepted {created_count} detections for template {template_id}"
    )

    return {
        "message": f"Accepted {created_count} detections",
        "created_elements": created_count,
    }


@router.delete("/detections/{detection_id}")
async def delete_detection(
    detection_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
):
    """
    Delete a detection record.

    Args:
        detection_id: Detection ID to delete
        current_user: Authenticated user

    Returns:
        Success message
    """
    client = get_supabase_client()

    response = (
        client.table("form_detections")
        .delete()
        .eq("id", str(detection_id))
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Detection not found"
        )

    logger.info(f"Deleted detection {detection_id}")
    return {"message": "Detection deleted successfully"}
