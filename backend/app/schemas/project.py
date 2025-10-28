"""Project schemas."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectStatus(str, Enum):
    """Project status enumeration."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectBase(BaseModel):
    """Base project schema."""

    title: str = Field(max_length=255)
    description: str
    requirements: Optional[dict[str, Any]] = None
    budget: Optional[Decimal] = Field(default=None, ge=0)
    deadline: Optional[datetime] = None


class ProjectCreate(ProjectBase):
    """Create project schema."""

    pass


class ProjectUpdate(BaseModel):
    """Update project schema."""

    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    requirements: Optional[dict[str, Any]] = None
    budget: Optional[Decimal] = Field(default=None, ge=0)
    deadline: Optional[datetime] = None
    status: Optional[ProjectStatus] = None


class ProjectResponse(ProjectBase):
    """Project response schema."""

    id: UUID
    client_id: UUID
    status: ProjectStatus
    selected_professional_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
