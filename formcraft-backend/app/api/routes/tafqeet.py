"""Tafqeet API routes.

POST /api/tafqeet/preview — stateless amount-to-words conversion for canvas preview.
"""

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.user import UserProfile
from app.schemas.tafqeet import TafqeetPreviewRequest, TafqeetPreviewResponse
from app.services.tafqeet.converter import TafqeetConverter

router = APIRouter(prefix="/tafqeet", tags=["Tafqeet"])

_converter = TafqeetConverter()


@router.post(
    "/preview",
    response_model=TafqeetPreviewResponse,
    summary="Convert numeric amount to words (canvas preview)",
    description=(
        "Stateless endpoint — no DB access. Used by Design Studio canvas for live preview "
        "of tafqeet element output. Returns null result for out-of-range or invalid amounts. "
        "Requires valid JWT. Canvas should debounce calls by 300ms (target: <500ms total)."
    ),
    responses={
        200: {
            "description": "Conversion result",
            "content": {
                "application/json": {
                    "examples": {
                        "arabic_only": {
                            "summary": "Arabic output with suffix",
                            "value": {"result": "خمسة آلاف وخمسمائة ريال سعودي وخمسة وسبعون هللة فقط لا غير"},
                        },
                        "both_modes": {
                            "summary": "Both Arabic and English lines",
                            "value": {
                                "result": (
                                    "اثنا عشر ألفاً وخمسمائة جنيه مصري وخمسون قرشاً فقط لا غير\n"
                                    "Twelve Thousand Five Hundred Egyptian Pounds and Fifty Piastres Only"
                                )
                            },
                        },
                        "out_of_range": {
                            "summary": "Out-of-range amount",
                            "value": {"result": None},
                        },
                    }
                }
            },
        },
        401: {"description": "Unauthorized — missing or invalid JWT"},
        422: {"description": "Validation error — e.g. suffix='only' with language='ar'"},
    },
)
async def preview_tafqeet(
    body: TafqeetPreviewRequest,
    _: Annotated[UserProfile, Depends(get_current_user)],
) -> TafqeetPreviewResponse:
    # FR-024: reject suffix="only" when language="ar"
    if body.suffix == "only" and body.language == "ar":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="suffix 'only' is not valid when output language is 'ar'",
        )

    result = _converter.convert(
        amount=body.amount,
        currency_code=body.currency_code,
        language=body.language,
        show_currency=body.show_currency,
        prefix=body.prefix,
        suffix=body.suffix,
    )
    # In canvas preview context, conversion failure returns null — no audit log (FR-009b)
    return TafqeetPreviewResponse(result=result)
