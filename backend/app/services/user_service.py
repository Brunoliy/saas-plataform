"""User service."""

from typing import Optional, List, Tuple
from uuid import UUID

from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.models.user import User
from app.core.exceptions import ConflictError, NotFoundError


class UserService:
    """User service class."""

    def __init__(self, user_repository: UserRepository):
        """Initialize service."""
        self.user_repository = user_repository

    def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        # Check if user with email already exists
        existing_user = self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise ConflictError(f"User with email {user_data.email} already exists")

        # Create user
        db_user = self.user_repository.create(user_data)
        return UserResponse.model_validate(db_user)

    def get_user_by_id(self, user_id: UUID) -> UserResponse:
        """Get user by ID."""
        db_user = self.user_repository.get_by_id(user_id)
        if not db_user:
            raise NotFoundError(f"User with ID {user_id} not found")

        return UserResponse.model_validate(db_user)

    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email."""
        db_user = self.user_repository.get_by_email(email)
        if not db_user:
            return None

        return UserResponse.model_validate(db_user)

    def update_user(self, user_id: UUID, user_data: UserUpdate) -> UserResponse:
        """Update user."""
        db_user = self.user_repository.update(user_id, user_data)
        if not db_user:
            raise NotFoundError(f"User with ID {user_id} not found")

        return UserResponse.model_validate(db_user)

    def delete_user(self, user_id: UUID) -> bool:
        """Soft delete user."""
        success = self.user_repository.delete(user_id)
        if not success:
            raise NotFoundError(f"User with ID {user_id} not found")

        return success

    def list_users(self, skip: int = 0, limit: int = 20) -> Tuple[List[UserResponse], int]:
        """List users with pagination."""
        users = self.user_repository.list_users(skip=skip, limit=limit)
        total = self.user_repository.count_users()

        user_responses = [UserResponse.model_validate(user) for user in users]
        return user_responses, total

    def activate_user(self, user_id: UUID) -> UserResponse:
        """Activate user."""
        db_user = self.user_repository.activate_user(user_id)
        if not db_user:
            raise NotFoundError(f"User with ID {user_id} not found")

        return UserResponse.model_validate(db_user)

    def deactivate_user(self, user_id: UUID) -> UserResponse:
        """Deactivate user."""
        db_user = self.user_repository.deactivate_user(user_id)
        if not db_user:
            raise NotFoundError(f"User with ID {user_id} not found")

        return UserResponse.model_validate(db_user)