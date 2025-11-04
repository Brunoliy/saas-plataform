"""Review schemas."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReviewType(str, Enum):
    """Review type enumeration."""

    PROFESSIONAL_TO_CLIENT = "professional_to_client"
    CLIENT_TO_PROFESSIONAL = "client_to_professional"


class ReviewBase(BaseModel):
    """Base review schema."""

    rating: int = Field(ge=1, le=5, description="Rating (1-5)")
    comment: str | None = None
    review_type: ReviewType


class ReviewCreate(ReviewBase):
    """Create review schema."""

    project_id: UUID
    reviewed_id: UUID


class ReviewUpdate(BaseModel):
    """Update review schema."""

    rating: int | None = Field(default=None, ge=1, le=5)
    comment: str | None = None


class ReviewResponse(ReviewBase):
    """Review response schema."""

    id: UUID
    project_id: UUID
    reviewer_id: UUID
    reviewed_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
