"""Client repository for database operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.client import ClientLink, ClientProfile
from app.schemas.client import (
    ClientLinkCreate,
    ClientLinkUpdate,
    ClientProfileCreate,
    ClientProfileUpdate,
)


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
            description=profile_data.description,
            bio=profile_data.bio,
            average_rating=None,
            total_reviews=0,
        )

        self.db.add(db_profile)
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def get_by_id(self, profile_id: UUID) -> Optional[ClientProfile]:
        """Get client profile by ID (only non-deleted profiles)."""
        return (
            self.db.query(ClientProfile)
            .filter(
                and_(ClientProfile.id == profile_id, ClientProfile.deleted_at.is_(None))
            )
            .first()
        )

    def get_by_user_id(self, user_id: UUID) -> Optional[ClientProfile]:
        """Get client profile by user ID (only non-deleted profiles)."""
        return (
            self.db.query(ClientProfile)
            .filter(
                and_(
                    ClientProfile.user_id == user_id, ClientProfile.deleted_at.is_(None)
                )
            )
            .first()
        )

    def update(
        self, profile_id: UUID, profile_data: ClientProfileUpdate
    ) -> Optional[ClientProfile]:
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

    def list_clients(
        self, skip: int = 0, limit: int = 20, include_deleted: bool = False
    ) -> list[ClientProfile]:
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

    def update_rating(
        self, profile_id: UUID, average_rating: float, total_reviews: int
    ) -> Optional[ClientProfile]:
        """Update client rating."""
        db_profile = self.get_by_id(profile_id)
        if not db_profile:
            return None

        db_profile.average_rating = average_rating
        db_profile.total_reviews = total_reviews
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def get_clients_by_sector(
        self, business_sector: str, skip: int = 0, limit: int = 20
    ) -> list[ClientProfile]:
        """Get clients by business sector."""
        return (
            self.db.query(ClientProfile)
            .filter(
                and_(
                    ClientProfile.business_sector == business_sector,
                    ClientProfile.deleted_at.is_(None),
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def add_link(self, client_id: UUID, link_data: ClientLinkCreate) -> ClientLink:
        """Add a social link to client profile."""
        db_link = ClientLink(
            client_id=client_id,
            platform=link_data.platform,
            url=link_data.url,
            label=link_data.label,
        )
        self.db.add(db_link)
        self.db.commit()
        self.db.refresh(db_link)
        return db_link

    def update_link(
        self, link_id: UUID, link_update: ClientLinkUpdate
    ) -> Optional[ClientLink]:
        """Update a social link."""
        db_link = (
            self.db.query(ClientLink)
            .filter(
                and_(
                    ClientLink.id == link_id,
                    ClientLink.deleted_at.is_(None),
                )
            )
            .first()
        )

        if not db_link:
            return None

        update_data = link_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_link, field, value)

        self.db.commit()
        self.db.refresh(db_link)
        return db_link

    def remove_link(self, client_id: UUID, link_id: UUID) -> bool:
        """Remove a social link from client profile."""
        db_link = (
            self.db.query(ClientLink)
            .filter(
                and_(
                    ClientLink.id == link_id,
                    ClientLink.client_id == client_id,
                    ClientLink.deleted_at.is_(None),
                )
            )
            .first()
        )

        if not db_link:
            return False

        db_link.soft_delete()
        self.db.commit()
        return True
