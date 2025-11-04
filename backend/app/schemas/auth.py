"""Authentication schemas."""

from pydantic import BaseModel, Field


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes default


class TokenData(BaseModel):
    """Token data schema."""

    user_id: str | None = None
    email: str | None = None
    account_type: str | None = None


class UserLogin(BaseModel):
    """User login schema."""

    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")


class RefreshToken(BaseModel):
    """Refresh token schema."""

    refresh_token: str = Field(..., description="Refresh token")
