"""Client schemas."""

from decimal import Decimal
from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class ClientProfileBase(BaseModel):
    """Base client profile schema."""

    company_name: Optional[str] = Field(default=None, max_length=255)
    business_sector: Optional[str] = Field(default=None, max_length=100)


class ClientProfileCreate(ClientProfileBase):
    """Create client profile schema."""

    pass


class ClientProfileUpdate(BaseModel):
    """Update client profile schema."""

    company_name: Optional[str] = Field(default=None, max_length=255)
    business_sector: Optional[str] = Field(default=None, max_length=100)


class ClientProfileResponse(ClientProfileBase):
    """Client profile response schema."""

    id: UUID
    user_id: UUID
    average_rating: Optional[Decimal] = None
    total_reviews: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
