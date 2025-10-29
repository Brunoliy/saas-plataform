"""Client schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ClientLinkBase(BaseModel):
    """Base client link schema."""

    platform: str = Field(
        max_length=50,
        description="Platform name (github, linkedin, twitter, website, other)",
    )
    url: str = Field(description="Link URL")
    label: Optional[str] = Field(
        default=None, max_length=255, description="Optional custom label"
    )


class ClientLinkCreate(ClientLinkBase):
    """Create client link schema."""

    pass


class ClientLinkUpdate(BaseModel):
    """Update client link schema."""

    platform: Optional[str] = Field(default=None, max_length=50)
    url: Optional[str] = None
    label: Optional[str] = Field(default=None, max_length=255)


class ClientLinkResponse(ClientLinkBase):
    """Client link response schema."""

    id: UUID
    client_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClientProfileBase(BaseModel):
    """Base client profile schema."""

    company_name: Optional[str] = Field(default=None, max_length=255)
    business_sector: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(
        default=None, description="Description of the company"
    )
    bio: Optional[str] = Field(
        default=None, description="About section for the company"
    )


class ClientProfileCreate(ClientProfileBase):
    """Create client profile schema."""

    pass


class ClientProfileUpdate(BaseModel):
    """Update client profile schema."""

    company_name: Optional[str] = Field(default=None, max_length=255)
    business_sector: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    bio: Optional[str] = None


class ClientProfileResponse(ClientProfileBase):
    """Client profile response schema."""

    id: UUID
    user_id: UUID
    average_rating: Optional[Decimal] = None
    total_reviews: int = 0
    links: list[ClientLinkResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
