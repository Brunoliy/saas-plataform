"""Professional schemas."""

from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class ProfessionalSkillBase(BaseModel):
    """Base professional skill schema."""

    skill_id: UUID
    proficiency_level: int = Field(ge=1, le=5, description="Proficiency level (1-5)")
    years_experience: Optional[int] = Field(default=None, ge=0)
    certified: bool = Field(default=False)


class ProfessionalSkillCreate(ProfessionalSkillBase):
    """Create professional skill schema."""

    pass


class ProfessionalSkillUpdate(BaseModel):
    """Update professional skill schema."""

    proficiency_level: Optional[int] = Field(default=None, ge=1, le=5)
    years_experience: Optional[int] = Field(default=None, ge=0)
    certified: Optional[bool] = None


class ProfessionalSkillResponse(ProfessionalSkillBase):
    """Professional skill response schema."""

    id: UUID
    professional_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProfessionalProfileBase(BaseModel):
    """Base professional profile schema."""

    title: str = Field(max_length=255)
    description: Optional[str] = None
    hourly_rate: Optional[Decimal] = Field(default=None, ge=0)


class ProfessionalProfileCreate(ProfessionalProfileBase):
    """Create professional profile schema."""

    skills: Optional[List[ProfessionalSkillCreate]] = Field(default_factory=list)


class ProfessionalProfileUpdate(BaseModel):
    """Update professional profile schema."""

    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    hourly_rate: Optional[Decimal] = Field(default=None, ge=0)


class ProfessionalProfileResponse(ProfessionalProfileBase):
    """Professional profile response schema."""

    id: UUID
    user_id: UUID
    average_rating: Optional[Decimal] = None
    total_reviews: int = 0
    skills: List[ProfessionalSkillResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
