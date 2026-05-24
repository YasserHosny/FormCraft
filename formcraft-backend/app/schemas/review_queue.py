from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ElementComment(BaseModel):
    element_key: str
    comment: str


class ReviewQueueItem(BaseModel):
    template_id: UUID
    template_name: str
    category: str
    status: str
    version: int
    designer_id: UUID
    designer_name: str | None = None
    department_name: str | None = None
    submitted_at: datetime
    days_waiting: int
    is_overdue: bool


class ReviewQueueResponse(BaseModel):
    items: list[ReviewQueueItem]
    total: int
    overdue_count: int


class GovernanceMetrics(BaseModel):
    pending_count: int
    approved_awaiting_publish: int
    avg_turnaround_days: float | None = None
    rejection_rate_pct: float | None = None
    overdue_count: int
    total_reviews: int
    overdue_threshold_days: int = 3


class TimelineEvent(BaseModel):
    event: str
    actor_id: UUID
    actor_name: str | None = None
    actor_role: str | None = None
    timestamp: datetime
    comment: str | None = None
    element_comments: list[ElementComment] | None = None


class TimelineResponse(BaseModel):
    template_id: UUID
    template_name: str
    timeline: list[TimelineEvent]


class DefaultReviewerRequest(BaseModel):
    reviewer_id: UUID


class DefaultReviewerResponse(BaseModel):
    department_id: UUID
    reviewer_id: UUID
    reviewer_name: str | None = None
