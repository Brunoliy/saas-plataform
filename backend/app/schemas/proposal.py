"""Proposal schemas."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProposalStatus(str, Enum):
    """Proposal status enumeration."""

    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class ProposalBase(BaseModel):
    """Base proposal schema."""

    proposed_amount: Decimal = Field(ge=0)
    estimated_days: int | None = Field(default=None, ge=1)
    description: str


class ProposalCreate(ProposalBase):
    """Create proposal schema."""

    project_id: UUID


class ProposalUpdate(BaseModel):
    """Update proposal schema."""

    proposed_amount: Decimal | None = Field(default=None, ge=0)
    estimated_days: int | None = Field(default=None, ge=1)
    description: str | None = None
    status: ProposalStatus | None = None


class ProposalResponse(ProposalBase):
    """Proposal response schema."""

    id: UUID
    project_id: UUID
    professional_id: UUID
    status: ProposalStatus
    ai_score: Decimal | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
