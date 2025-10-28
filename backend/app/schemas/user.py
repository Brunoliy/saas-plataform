"""User schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_serializer

from app.models.user import AccountType


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr = Field(..., description="User email")
    full_name: str = Field(
        ..., min_length=1, max_length=255, description="User full name"
    )
    phone: Optional[str] = Field(None, max_length=20, description="User phone number")
    account_type: AccountType = Field(..., description="User account type")


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8, description="User password")


class UserUpdate(BaseModel):
    """User update schema."""

    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    active: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema."""

    id: UUID
    active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    @field_serializer("id")
    def serialize_id(self, value: UUID, _info):
        """Serialize UUID to string."""
        return str(value)

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class UserLogin(BaseModel):
    """User login schema."""

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")
