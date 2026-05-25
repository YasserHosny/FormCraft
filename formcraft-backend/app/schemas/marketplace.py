from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


PriceType = Literal["free", "premium"]
ListingStatus = Literal["draft", "submitted", "approved", "rejected", "active", "suspended", "archived"]
PaymentStatus = Literal["pending", "completed", "failed", "refunded", "reversed"]


class MarketplaceListingBase(BaseModel):
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    preview_image_urls: list[str] = Field(default_factory=list)
    compliance_badges: list[str] = Field(default_factory=list)
    price_type: PriceType = "free"
    price_amount: Decimal | None = None
    currency: str = "USD"

    @model_validator(mode="after")
    def validate_price(self):
        if self.price_type == "premium" and (self.price_amount is None or self.price_amount <= 0):
            raise ValueError("Premium listings require a positive price_amount")
        if self.price_type == "free":
            self.price_amount = None
        return self


class MarketplaceListingCreate(MarketplaceListingBase):
    template_id: UUID


class MarketplaceListingResponse(MarketplaceListingBase):
    id: UUID
    template_id: UUID
    publisher_org_id: UUID
    publisher_org_name: str | None = None
    name: str
    category: str
    country: str
    language: str
    quality_score: float = 0
    status: ListingStatus
    review_status: str = "pending"
    download_count: int = 0
    average_rating: float | None = None
    review_count: int = 0
    published_version: int = 1
    created_at: str | None = None
    updated_at: str | None = None


class MarketplaceListResponse(BaseModel):
    items: list[MarketplaceListingResponse]
    total: int
    page: int
    page_size: int


class MarketplaceListingDetail(MarketplaceListingResponse):
    template_preview: dict = Field(default_factory=dict)
    sample_pdf_url: str | None = None
    dependency_warnings: list[str] = Field(default_factory=list)


class MarketplaceImportRequest(BaseModel):
    draft_name: str | None = None
    reference_mappings: dict[str, str] = Field(default_factory=dict)
    accept_disabled_dependencies: bool = False


class MarketplaceImportResponse(BaseModel):
    import_id: UUID
    template_id: UUID
    remapping_status: str
    disabled_dependency_warnings: list[str] = Field(default_factory=list)


class MarketplacePurchaseRequest(BaseModel):
    provider: str = "internal"
    idempotency_key: str | None = None


class MarketplaceTransactionResponse(BaseModel):
    transaction_id: UUID
    payment_status: PaymentStatus
    amount: Decimal
    currency: str
    publisher_share: Decimal
    platform_share: Decimal


class MarketplaceModerationRequest(BaseModel):
    action: Literal["approve", "reject", "suspend", "reactivate", "archive"]
    comment: str | None = None


class MarketplaceReviewCreate(BaseModel):
    import_id: UUID
    rating: int = Field(ge=1, le=5)
    review_text: str = ""


class MarketplaceReviewResponse(BaseModel):
    id: UUID
    listing_id: UUID
    consumer_org_id: UUID
    reviewer_id: UUID
    import_id: UUID
    rating: int
    review_text: str
    verified_import: bool = True
    status: str = "active"
    created_at: str | None = None
    updated_at: str | None = None


class MarketplaceReviewListResponse(BaseModel):
    items: list[MarketplaceReviewResponse]
    total: int
