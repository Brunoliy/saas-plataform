"""Security utilities for authentication and authorization."""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.config import settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.schemas.auth import TokenData

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)

    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> TokenData:
    """Verify JWT token and return token data."""
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        token_type_payload = payload.get("type")

        if token_type_payload != token_type:
            raise AuthenticationError("Invalid token type")

        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        account_type: str = payload.get("account_type")

        if user_id is None:
            raise AuthenticationError("Invalid token")

        token_data = TokenData(user_id=user_id, email=email, account_type=account_type)
        return token_data

    except JWTError:
        raise AuthenticationError("Invalid token")
    except ValidationError:
        raise AuthenticationError("Invalid token data")


# OAuth2 scheme for FastAPI
security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Get current user ID from token."""
    token_data = verify_token(credentials.credentials)
    return token_data.user_id


def get_current_user_email(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Get current user email from token."""
    token_data = verify_token(credentials.credentials)
    return token_data.email


def get_current_user_account_type(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Get current user account type from token."""
    token_data = verify_token(credentials.credentials)
    return token_data.account_type


def require_any_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Require any valid user account type and return user ID."""
    token_data = verify_token(credentials.credentials)
    check_permissions(token_data.account_type, ["professional", "company"])
    return token_data.user_id


def check_permissions(
    user_account_type: str, required_account_types: list[str]
) -> None:
    """Check if user has required permissions."""
    if user_account_type not in required_account_types:
        raise AuthorizationError(f"Required account types: {required_account_types}")


def require_professional(user_account_type: str) -> None:
    """Require professional account type."""
    check_permissions(user_account_type, ["professional"])


def require_company(user_account_type: str) -> None:
    """Require company account type."""
    check_permissions(user_account_type, ["company"])


def require_admin(user_account_type: str) -> None:
    """Require admin account type."""
    check_permissions(user_account_type, ["admin"])


def require_any_user(user_account_type: str) -> None:
    """Require any valid user account type."""
    check_permissions(user_account_type, ["professional", "company", "admin"])
