"""Schemas for batch OCR onboarding."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


BatchStatus = Literal["queued", "processing", "needs_review", "completed", "failed", "cancelled"]
ItemStatus = Literal[
    "queued",
    "processing",
    "needs_review",
    "accepted",
    "rejected",
    "failed",
    "duplicate",
    "converted",
]
DecisionAction = Literal["accept", "reject", "edit", "defer", "merge", "retry", "bulk_accept"]
DuplicateDecision = Literal["pending", "keep_one", "keep_both", "merge", "exclude"]


class OCRImportBatchResponse(BaseModel):
    id: UUID
    name: str
    status: BatchStatus
    confidence_threshold: float = Field(ge=0.0, le=1.0)
    total_items: int
    processed_items: int = 0
    accepted_items: int = 0
    failed_items: int = 0
    duplicate_items: int = 0
    created_at: datetime
    updated_at: datetime


class OCRImportItemResponse(BaseModel):
    id: UUID
    batch_id: UUID
    file_name: str
    status: ItemStatus
    mime_type: str
    file_size_bytes: int
    confidence: float | None = None
    likely_type: str | None = None
    category: str | None = None
    language: str | None = None
    page_count: int = 1
    retry_count: int = 0
    last_error: str | None = None
    converted_template_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


class OCRImportBatchDetailResponse(OCRImportBatchResponse):
    items: list[OCRImportItemResponse] = []


class OCRImportBatchListResponse(BaseModel):
    items: list[OCRImportBatchResponse]
    total: int


class OCRReviewDecisionRequest(BaseModel):
    action: DecisionAction
    payload: dict = Field(default_factory=dict)


class OCRBulkAcceptRequest(BaseModel):
    item_ids: list[UUID] = Field(default_factory=list)


class OCRBulkAcceptResponse(BaseModel):
    accepted_count: int
    skipped: list[dict] = []


class OCRDuplicateResolveRequest(BaseModel):
    decision: DuplicateDecision


class OCRDuplicateCandidateResponse(BaseModel):
    id: UUID
    batch_id: UUID
    item_id: UUID
    duplicate_item_id: UUID | None = None
    existing_template_id: UUID | None = None
    similarity_score: float
    evidence: dict = {}
    decision: DuplicateDecision = "pending"
    created_at: datetime
    updated_at: datetime
