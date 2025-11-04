"""Skill schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SkillBase(BaseModel):
    """Base skill schema."""

    name: str = Field(max_length=100)
    category: str = Field(max_length=50)
    description: str | None = None


class SkillCreate(SkillBase):
    """Create skill schema."""

    pass


class SkillUpdate(BaseModel):
    """Update skill schema."""

    name: str | None = Field(default=None, max_length=100)
    category: str | None = Field(default=None, max_length=50)
    description: str | None = None
    active: bool | None = None


class SkillResponse(SkillBase):
    """Skill response schema."""

    id: UUID
    active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
