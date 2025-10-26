"""Proposal schemas."""

from decimal import Decimal
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class ProposalStatus(str, Enum):
    """Proposal status enumeration."""

    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ProposalBase(BaseModel):
    """Base proposal schema."""

    proposed_amount: Decimal = Field(ge=0)
    estimated_days: Optional[int] = Field(default=None, ge=1)
    description: str


class ProposalCreate(ProposalBase):
    """Create proposal schema."""

    project_id: UUID


class ProposalUpdate(BaseModel):
    """Update proposal schema."""

    proposed_amount: Optional[Decimal] = Field(default=None, ge=0)
    estimated_days: Optional[int] = Field(default=None, ge=1)
    description: Optional[str] = None
    status: Optional[ProposalStatus] = None


class ProposalResponse(ProposalBase):
    """Proposal response schema."""

    id: UUID
    project_id: UUID
    professional_id: UUID
    status: ProposalStatus
    ai_score: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
