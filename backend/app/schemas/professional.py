"""Professional schemas."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class ProfessionalSkillBase(BaseModel):
    """Base professional skill schema."""

    skill_id: UUID
    proficiency_level: int = Field(ge=1, le=5, description="Proficiency level (1-5)")
    years_experience: int | None = Field(default=None, ge=0)
    certified: bool = Field(default=False)


class ProfessionalSkillCreate(ProfessionalSkillBase):
    """Create professional skill schema."""

    pass


class ProfessionalSkillUpdate(BaseModel):
    """Update professional skill schema."""

    proficiency_level: int | None = Field(default=None, ge=1, le=5)
    years_experience: int | None = Field(default=None, ge=0)
    certified: bool | None = None


class ProfessionalSkillResponse(ProfessionalSkillBase):
    """Professional skill response schema."""

    id: UUID
    professional_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProfessionalLinkBase(BaseModel):
    """Base professional link schema."""

    platform: str = Field(
        max_length=50,
        description="Platform name (github, linkedin, twitter, portfolio, other)",
    )
    url: str = Field(description="Link URL")
    label: str | None = Field(
        default=None, max_length=255, description="Optional custom label"
    )


class ProfessionalLinkCreate(ProfessionalLinkBase):
    """Create professional link schema."""

    pass


class ProfessionalLinkUpdate(BaseModel):
    """Update professional link schema."""

    platform: str | None = Field(default=None, max_length=50)
    url: str | None = None
    label: str | None = Field(default=None, max_length=255)


class ProfessionalLinkResponse(ProfessionalLinkBase):
    """Professional link response schema."""

    id: UUID
    professional_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProfessionalProfileBase(BaseModel):
    """Base professional profile schema."""

    title: str = Field(max_length=255)
    description: str | None = None
    bio: str | None = Field(
        default=None, description="About section for the professional"
    )
    hourly_rate: Decimal | None = Field(default=None, ge=0)


class ProfessionalProfileCreate(ProfessionalProfileBase):
    """Create professional profile schema."""

    skills: list[ProfessionalSkillCreate] | None = Field(default_factory=list)


class ProfessionalProfileUpdate(BaseModel):
    """Update professional profile schema."""

    title: str | None = Field(default=None, max_length=255)
    description: str | None = None
    bio: str | None = None
    hourly_rate: Decimal | None = Field(default=None, ge=0)


class ProfessionalProfileResponse(ProfessionalProfileBase):
    """Professional profile response schema."""

    id: UUID
    user_id: UUID
    average_rating: Decimal | None = None
    total_reviews: int = 0
    skills: list[ProfessionalSkillResponse] = []
    links: list[ProfessionalLinkResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("average_rating", "hourly_rate")
    def serialize_decimal_to_float(self, value: Decimal | None) -> float | None:
        """Convert Decimal to float for JSON serialization."""
        return float(value) if value is not None else None
