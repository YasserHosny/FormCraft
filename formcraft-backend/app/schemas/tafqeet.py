from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class TafqeetPreviewRequest(BaseModel):
    amount: Decimal
    currency_code: Literal["EGP", "SAR", "AED", "USD"]
    language: Literal["ar", "en", "both"]
    show_currency: bool = True
    prefix: Literal["none", "faqat"] = "none"
    suffix: Literal["none", "la_ghair", "faqat_la_ghair", "only"] = "none"


class TafqeetPreviewResponse(BaseModel):
    result: str | None  # None when amount is out of range or conversion fails
