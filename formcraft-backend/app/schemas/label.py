from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class LabelColour(str, Enum):
    red = "red"
    orange = "orange"
    yellow = "yellow"
    green = "green"
    teal = "teal"
    blue = "blue"
    purple = "purple"
    pink = "pink"
    grey = "grey"
    brown = "brown"


class LabelCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    colour: LabelColour | None = None


class LabelUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    colour: LabelColour | None = None


class LabelResponse(BaseModel):
    id: UUID
    name: str
    colour: str | None
    created_at: datetime


class SubmissionLabelAssignRequest(BaseModel):
    label_ids: list[UUID] = Field(..., max_length=5)
