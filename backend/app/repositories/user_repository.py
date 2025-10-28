"""User repository for database operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository:
    """User repository class."""

    def __init__(self, db: Session):
        """Initialize repository."""
        self.db = db

    def create(self, user_data: UserCreate) -> User:
        """Create a new user."""
        db_user = User(
            email=user_data.email,
            password_hash=user_data.password,  # Password should already be hashed by service layer
            full_name=user_data.full_name,
            phone=user_data.phone,
            account_type=user_data.account_type,
            active=True,
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID (only non-deleted users)."""
        return (
            self.db.query(User)
            .filter(and_(User.id == user_id, User.deleted_at.is_(None)))
            .first()
        )

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email (only non-deleted users)."""
        return (
            self.db.query(User)
            .filter(and_(User.email == email, User.deleted_at.is_(None)))
            .first()
        )

    def update(self, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
        """Update user."""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete(self, user_id: UUID) -> bool:
        """Soft delete user."""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return False

        db_user.soft_delete()
        self.db.commit()
        return True

    def list_users(
        self, skip: int = 0, limit: int = 20, include_deleted: bool = False
    ) -> list[User]:
        """List users with pagination."""
        query = self.db.query(User)

        if not include_deleted:
            query = query.filter(User.deleted_at.is_(None))

        return query.offset(skip).limit(limit).all()

    def count_users(self, include_deleted: bool = False) -> int:
        """Count total users."""
        query = self.db.query(User)

        if not include_deleted:
            query = query.filter(User.deleted_at.is_(None))

        return query.count()

    def activate_user(self, user_id: UUID) -> Optional[User]:
        """Activate user."""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None

        db_user.active = True
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def deactivate_user(self, user_id: UUID) -> Optional[User]:
        """Deactivate user."""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None

        db_user.active = False
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
