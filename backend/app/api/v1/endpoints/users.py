"""User endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.common import PaginatedResponse
from app.security import get_current_user_id, require_any_user
from app.core.exceptions import NotFoundError

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user_id: str = Depends(get_current_user_id)):
    """Get current user information."""
    # TODO: Implement actual user retrieval logic
    # This is a placeholder implementation
    return UserResponse(
        id=current_user_id,
        email="user@example.com",
        full_name="Test User",
        phone="+1234567890",
        account_type="PROFESSIONAL",
        active=True
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user_id: str = Depends(get_current_user_id)
):
    """Update current user information."""
    # TODO: Implement actual user update logic
    # This is a placeholder implementation
    return UserResponse(
        id=current_user_id,
        email="user@example.com",
        full_name=user_update.full_name or "Test User",
        phone=user_update.phone or "+1234567890",
        account_type="PROFESSIONAL",
        active=True
    )


@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 20,
    current_user_id: str = Depends(require_any_user)
):
    """List users with pagination."""
    # TODO: Implement actual user listing logic
    # This is a placeholder implementation
    users = [
        UserResponse(
            id="user-1",
            email="user1@example.com",
            full_name="User One",
            phone="+1234567890",
            account_type="PROFESSIONAL",
            active=True
        ),
        UserResponse(
            id="user-2",
            email="user2@example.com",
            full_name="User Two",
            phone="+1234567891",
            account_type="CLIENT",
            active=True
        )
    ]
    
    return PaginatedResponse(
        items=users,
        total=len(users),
        page=skip // limit + 1,
        size=limit,
        pages=1
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user_id: str = Depends(require_any_user)
):
    """Get user by ID."""
    # TODO: Implement actual user retrieval logic
    # This is a placeholder implementation
    if user_id == "user-1":
        return UserResponse(
            id=user_id,
            email="user1@example.com",
            full_name="User One",
            phone="+1234567890",
            account_type="PROFESSIONAL",
            active=True
        )
    
    raise NotFoundError(f"User with ID {user_id} not found") 