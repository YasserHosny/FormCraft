"""Form import and OCR detection endpoints."""

import logging
import mimetypes
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.api.deps import get_current_user, require_role
from app.core.config import settings
from app.core.supabase import get_supabase_client
from app.models.enums import ElementType, Role
from app.models.form_detection import (
    AcceptDetectionRequest,
    DetectedField,
    FormDetectionResponse,
)
from app.models.user import UserProfile
from app.services.ocr import AzureOCRClient, BoundingBoxConverter, FieldClassifier
from app.services.template_service import TemplateService

router = APIRouter(prefix="/forms", tags=["Forms"])
logger = logging.getLogger(__name__)


class LocalImportRequest(BaseModel):
    page_index: int = Field(0, ge=0)


def _get_local_import_path() -> Path:
    if not settings.DEV_LOCAL_IMPORT_PATH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Local import path not configured",
        )

    file_path = Path(settings.DEV_LOCAL_IMPORT_PATH)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Local file not found",
        )
    if file_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Only JPEG/PNG allowed.",
        )

    return file_path


def _process_import(template_id: UUID, image_bytes: bytes, page_index: int) -> FormDetectionResponse:
    ocr_client = AzureOCRClient()
    ocr_result = ocr_client.analyze_layout(image_bytes)

    if not ocr_result.get("page_dimensions"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not detect page dimensions from image",
        )

    page_dims = ocr_result["page_dimensions"]
    dpi = BoundingBoxConverter.detect_dpi_from_exif(image_bytes)
    converter = BoundingBoxConverter(
        image_width_px=int(page_dims["width"]),
        image_height_px=int(page_dims["height"]),
        dpi=dpi,
    )

    classifier = FieldClassifier()
    detected_fields: list[DetectedField] = []
    words = ocr_result.get("words", [])

    for word in words:
        bbox_mm = converter.convert_bbox(word["bbox"])
        nearby_labels = classifier.get_nearby_labels(
            word["bbox"], words, max_distance=100
        )
        suggested_type = classifier.classify_field(
            text=word["text"], bbox=bbox_mm, nearby_labels=nearby_labels
        )

        if (
            classifier.is_probable_label(word["text"], bbox_mm)
            and suggested_type == "text"
        ):
            continue

        detected_fields.append(
            DetectedField(
                text=word["text"],
                bbox=bbox_mm,
                confidence=word["confidence"],
                suggested_type=suggested_type,
                status="pending",
            )
        )

    page_width_mm, page_height_mm = converter.get_page_dimensions_mm()
    client = get_supabase_client()

    insert_data = {
        "template_id": str(template_id),
        "page_index": page_index,
        "detected_fields": [field.model_dump() for field in detected_fields],
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
        "OCR complete: detected %s fields for template %s",
        len(detected_fields),
        template_id,
    )

    return FormDetectionResponse(
        id=detection_record["id"],
        template_id=template_id,
        page_index=page_index,
        detected_fields=detected_fields,
        page_dimensions={"width": page_width_mm, "height": page_height_mm},
        created_at=detection_record["created_at"],
    )


@router.post("/import/{template_id}", response_model=FormDetectionResponse)
async def import_form(
    template_id: UUID,
    file: UploadFile = File(...),
    page_index: int = 0,
    current_user: UserProfile = Depends(require_role(Role.ADMIN, Role.DESIGNER)),
):
    """Upload a form image and detect fillable fields using OCR."""
    logger.info(
        "Starting form import for template %s, page %s", template_id, page_index
    )

    if file.content_type not in {"image/jpeg", "image/png", "image/jpg"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported file type: {file.content_type}. Only JPEG and PNG are supported."
            ),
        )

    image_bytes = await file.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image file too large. Maximum 10MB.",
        )

    try:
        return _process_import(template_id, image_bytes, page_index)
    except ValueError as exc:
        logger.error("Configuration error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR service configuration error: {exc}",
        )
    except Exception as exc:
        logger.error("OCR processing error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process form image: {exc}",
        )


@router.post("/import/local/{template_id}", response_model=FormDetectionResponse)
async def import_form_local(
    template_id: UUID,
    body: LocalImportRequest,
    current_user: UserProfile = Depends(require_role(Role.ADMIN, Role.DESIGNER)),
):
    """Dev-only local file import for OCR detection."""
    if not settings.DEV_ALLOW_LOCAL_IMPORT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Local import disabled",
        )

    file_path = _get_local_import_path()

    try:
        image_bytes = file_path.read_bytes()
        return _process_import(template_id, image_bytes, body.page_index)
    except ValueError as exc:
        logger.error("Configuration error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR service configuration error: {exc}",
        )
    except Exception as exc:
        logger.error("OCR processing error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process local form image: {exc}",
        )


@router.get("/import/local/{template_id}/preview")
async def import_form_local_preview(
    template_id: UUID,
    current_user: UserProfile = Depends(require_role(Role.ADMIN, Role.DESIGNER)),
):
    """Dev-only local file preview for Import Cheque automation."""
    if not settings.DEV_ALLOW_LOCAL_IMPORT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Local import disabled",
        )

    file_path = _get_local_import_path()
    media_type, _ = mimetypes.guess_type(file_path)
    return FileResponse(file_path, media_type=media_type or "image/jpeg")


@router.get("/{template_id}/detections", response_model=list[FormDetectionResponse])
async def get_detections(
    template_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
):
    """Get all OCR detections for a template."""
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
    current_user: UserProfile = Depends(require_role(Role.ADMIN, Role.DESIGNER)),
):
    """Accept detection(s) and create FormCraft elements."""
    client = get_supabase_client()

    response = (
        client.table("form_detections")
        .select("*")
        .eq("id", str(detection_id))
        .eq("template_id", str(template_id))
        .single()
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Detection not found"
        )

    detection = response.data
    detected_fields = detection.get("detected_fields", [])

    for idx in request.detection_ids:
        if idx < 0 or idx >= len(detected_fields):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid detection index: {idx}",
            )

    # Resolve page_id by template + page_index
    page_index = detection.get("page_index", 0)
    page_result = (
        client.table("pages")
        .select("id")
        .eq("template_id", str(template_id))
        .order("sort_order")
        .execute()
    )
    if not page_result.data or page_index >= len(page_result.data):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found for template",
        )

    page_id = page_result.data[page_index]["id"]
    service = TemplateService(client)

    def map_type(suggested: str) -> ElementType:
        return {
            "date": ElementType.DATE,
            "currency": ElementType.CURRENCY,
            "number": ElementType.NUMBER,
            "checkbox": ElementType.CHECKBOX,
            "signature": ElementType.IMAGE,
        }.get(suggested, ElementType.TEXT)

    created = []
    for idx in request.detection_ids:
        field = detected_fields[idx]
        resolved_type = request.type_overrides.get(idx) or field.get("suggested_type", "text")
        element_data = {
            "type": map_type(resolved_type),
            "label_ar": field.get("text", ""),
            "label_en": field.get("text", ""),
            "x_mm": field.get("bbox", {}).get("x", 0),
            "y_mm": field.get("bbox", {}).get("y", 0),
            "width_mm": field.get("bbox", {}).get("width", 50),
            "height_mm": field.get("bbox", {}).get("height", 10),
            "required": False,
        }
        created.append(await service.add_element(UUID(page_id), element_data))

    return {"message": "Accepted detections", "created_elements": len(created)}


@router.delete("/detections/{detection_id}")
async def delete_detection(
    detection_id: UUID,
    current_user: UserProfile = Depends(require_role(Role.ADMIN, Role.DESIGNER)),
):
    """Delete a detection record."""
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

    return {"message": "Detection deleted successfully"}
