"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.auth import Token, UserLogin, RefreshToken
from app.schemas.user import UserCreate
from app.core.exceptions import AuthenticationError, ConflictError
from app.database.session import get_db
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository

router = APIRouter()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Get auth service dependency."""
    user_repository = UserRepository(db)
    return AuthService(user_repository)


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user."""
    try:
        return await auth_service.register(user_data)
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login endpoint."""
    try:
        return await auth_service.login(user_credentials)
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token_data: RefreshToken,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Refresh access token."""
    try:
        return await auth_service.refresh_token(refresh_token_data.refresh_token)
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/logout")
async def logout():
    """Logout endpoint."""
    # Token-based logout is handled client-side by discarding the token
    # For more advanced scenarios, implement token blacklisting here
    return {"message": "Successfully logged out"} 