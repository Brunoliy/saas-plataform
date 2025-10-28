"""User endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import get_current_user_id, require_any_user
from app.database.session import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.common import PaginatedResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Get user service dependency."""
    user_repository = UserRepository(db)
    return UserService(user_repository)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate, user_service: UserService = Depends(get_user_service)
):
    """Create a new user."""
    try:
        return user_service.create_user(user_data)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
):
    """Get current user information."""
    try:
        print(
            f"DEBUG: current_user_id = {current_user_id!r}, type = {type(current_user_id)}"
        )
        user_uuid = UUID(current_user_id)
        print(f"DEBUG: user_uuid = {user_uuid}")
        result = user_service.get_user_by_id(user_uuid)
        print(f"DEBUG: user found = {result is not None}")
        return result
    except ValueError as e:
        print(
            f"DEBUG: ValueError when converting to UUID: {e}, input was: {current_user_id!r}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user ID format: {current_user_id!r}",
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
):
    """Update current user information."""
    try:
        user_uuid = UUID(current_user_id)
        return user_service.update_user(user_uuid, user_update)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format"
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 20,
    current_user_id: str = Depends(require_any_user),
    user_service: UserService = Depends(get_user_service),
):
    """List users with pagination."""
    users, total = user_service.list_users(skip=skip, limit=limit)

    pages = (total + limit - 1) // limit if limit > 0 else 1
    current_page = (skip // limit) + 1 if limit > 0 else 1

    return PaginatedResponse(
        items=users, total=total, page=current_page, size=limit, pages=pages
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user_id: str = Depends(require_any_user),
    user_service: UserService = Depends(get_user_service),
):
    """Get user by ID."""
    try:
        user_uuid = UUID(user_id)
        return user_service.get_user_by_id(user_uuid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format"
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user_id: str = Depends(require_any_user),
    user_service: UserService = Depends(get_user_service),
):
    """Update user by ID."""
    try:
        user_uuid = UUID(user_id)
        return user_service.update_user(user_uuid, user_update)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format"
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user_id: str = Depends(require_any_user),
    user_service: UserService = Depends(get_user_service),
):
    """Soft delete user by ID."""
    try:
        user_uuid = UUID(user_id)
        user_service.delete_user(user_uuid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format"
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: str,
    current_user_id: str = Depends(require_any_user),
    user_service: UserService = Depends(get_user_service),
):
    """Activate user by ID."""
    try:
        user_uuid = UUID(user_id)
        return user_service.activate_user(user_uuid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format"
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: str,
    current_user_id: str = Depends(require_any_user),
    user_service: UserService = Depends(get_user_service),
):
    """Deactivate user by ID."""
    try:
        user_uuid = UUID(user_id)
        return user_service.deactivate_user(user_uuid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format"
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
