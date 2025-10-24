"""Client repository for database operations."""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.client import ClientProfile
from app.schemas.client import ClientProfileCreate, ClientProfileUpdate


class ClientRepository:
    """Client repository class."""

    def __init__(self, db: Session):
        """Initialize repository."""
        self.db = db

    def create(self, user_id: UUID, profile_data: ClientProfileCreate) -> ClientProfile:
        """Create a new client profile."""
        db_profile = ClientProfile(
            user_id=user_id,
            company_name=profile_data.company_name,
            business_sector=profile_data.business_sector,
            average_rating=None,
            total_reviews=0
        )

        self.db.add(db_profile)
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def get_by_id(self, profile_id: UUID) -> Optional[ClientProfile]:
        """Get client profile by ID (only non-deleted profiles)."""
        return self.db.query(ClientProfile).filter(
            and_(ClientProfile.id == profile_id, ClientProfile.deleted_at.is_(None))
        ).first()

    def get_by_user_id(self, user_id: UUID) -> Optional[ClientProfile]:
        """Get client profile by user ID (only non-deleted profiles)."""
        return self.db.query(ClientProfile).filter(
            and_(ClientProfile.user_id == user_id, ClientProfile.deleted_at.is_(None))
        ).first()

    def update(self, profile_id: UUID, profile_data: ClientProfileUpdate) -> Optional[ClientProfile]:
        """Update client profile."""
        db_profile = self.get_by_id(profile_id)
        if not db_profile:
            return None

        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_profile, field, value)

        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def delete(self, profile_id: UUID) -> bool:
        """Soft delete client profile."""
        db_profile = self.get_by_id(profile_id)
        if not db_profile:
            return False

        db_profile.soft_delete()
        self.db.commit()
        return True

    def list_clients(self, skip: int = 0, limit: int = 20, include_deleted: bool = False) -> List[ClientProfile]:
        """List client profiles with pagination."""
        query = self.db.query(ClientProfile)

        if not include_deleted:
            query = query.filter(ClientProfile.deleted_at.is_(None))

        return query.offset(skip).limit(limit).all()

    def count_clients(self, include_deleted: bool = False) -> int:
        """Count total client profiles."""
        query = self.db.query(ClientProfile)

        if not include_deleted:
            query = query.filter(ClientProfile.deleted_at.is_(None))

        return query.count()

    def update_rating(self, profile_id: UUID, average_rating: float, total_reviews: int) -> Optional[ClientProfile]:
        """Update client rating."""
        db_profile = self.get_by_id(profile_id)
        if not db_profile:
            return None

        db_profile.average_rating = average_rating
        db_profile.total_reviews = total_reviews
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def get_clients_by_sector(self, business_sector: str, skip: int = 0, limit: int = 20) -> List[ClientProfile]:
        """Get clients by business sector."""
        return self.db.query(ClientProfile).filter(
            and_(
                ClientProfile.business_sector == business_sector,
                ClientProfile.deleted_at.is_(None)
            )
        ).offset(skip).limit(limit).all()
