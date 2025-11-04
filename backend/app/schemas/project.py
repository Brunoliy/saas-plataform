"""Project schemas."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProjectStatus(str, Enum):
    """Project status enumeration."""

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ProjectBase(BaseModel):
    """Base project schema."""

    title: str = Field(max_length=255)
    description: str
    requirements: dict[str, Any] | None = None
    budget: Decimal | None = Field(default=None, ge=0)
    deadline: datetime | None = None


class ProjectCreate(ProjectBase):
    """Create project schema."""

    pass


class ProjectUpdate(BaseModel):
    """Update project schema."""

    title: str | None = Field(default=None, max_length=255)
    description: str | None = None
    requirements: dict[str, Any] | None = None
    budget: Decimal | None = Field(default=None, ge=0)
    deadline: datetime | None = None
    status: ProjectStatus | None = None


class ProjectResponse(ProjectBase):
    """Project response schema."""

    id: UUID
    client_id: UUID
    client_user_id: UUID | None = None  # User ID of the client who created the project
    status: ProjectStatus
    selected_professional_id: UUID | None = None
    selected_professional_user_id: UUID | None = (
        None  # User ID of the selected professional
    )
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def populate_user_ids(cls, data: Any) -> Any:
        """Populate user IDs from relationships."""
        # If data is a dict, it's already serialized, return as-is
        if isinstance(data, dict):
            return data

        # If it's a model instance, populate the user IDs from relationships
        if hasattr(data, "client") and data.client and hasattr(data.client, "user_id"):
            data.client_user_id = data.client.user_id
        if (
            hasattr(data, "selected_professional")
            and data.selected_professional
            and hasattr(data.selected_professional, "user_id")
        ):
            data.selected_professional_user_id = data.selected_professional.user_id
        return data
