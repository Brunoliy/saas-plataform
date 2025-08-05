"""Authentication schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Token(BaseModel):
    """Token response schema."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes default


class TokenData(BaseModel):
    """Token data schema."""
    
    user_id: Optional[str] = None
    email: Optional[str] = None
    account_type: Optional[str] = None


class UserLogin(BaseModel):
    """User login schema."""
    
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")


class RefreshToken(BaseModel):
    """Refresh token schema."""
    
    refresh_token: str = Field(..., description="Refresh token") 