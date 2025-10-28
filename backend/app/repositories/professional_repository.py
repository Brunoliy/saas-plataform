"""Professional repository for database operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.professional import (
    ProfessionalLink,
    ProfessionalProfile,
    ProfessionalSkill,
)
from app.schemas.professional import (
    ProfessionalLinkCreate,
    ProfessionalLinkUpdate,
    ProfessionalProfileCreate,
    ProfessionalProfileUpdate,
)


class ProfessionalRepository:
    """Professional repository class."""

    def __init__(self, db: Session):
        """Initialize repository."""
        self.db = db

    def create(
        self, user_id: UUID, profile_data: ProfessionalProfileCreate
    ) -> ProfessionalProfile:
        """Create a new professional profile."""
        db_profile = ProfessionalProfile(
            user_id=user_id,
            title=profile_data.title,
            description=profile_data.description,
            hourly_rate=profile_data.hourly_rate,
            average_rating=None,
            total_reviews=0,
        )

        self.db.add(db_profile)
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def get_by_id(self, profile_id: UUID) -> Optional[ProfessionalProfile]:
        """Get professional profile by ID (only non-deleted profiles)."""
        return (
            self.db.query(ProfessionalProfile)
            .filter(
                and_(
                    ProfessionalProfile.id == profile_id,
                    ProfessionalProfile.deleted_at.is_(None),
                )
            )
            .first()
        )

    def get_by_user_id(self, user_id: UUID) -> Optional[ProfessionalProfile]:
        """Get professional profile by user ID (only non-deleted profiles)."""
        return (
            self.db.query(ProfessionalProfile)
            .filter(
                and_(
                    ProfessionalProfile.user_id == user_id,
                    ProfessionalProfile.deleted_at.is_(None),
                )
            )
            .first()
        )

    def update(
        self, profile_id: UUID, profile_data: ProfessionalProfileUpdate
    ) -> Optional[ProfessionalProfile]:
        """Update professional profile."""
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
        """Soft delete professional profile."""
        db_profile = self.get_by_id(profile_id)
        if not db_profile:
            return False

        db_profile.soft_delete()
        self.db.commit()
        return True

    def list_professionals(
        self, skip: int = 0, limit: int = 20, include_deleted: bool = False
    ) -> list[ProfessionalProfile]:
        """List professional profiles with pagination."""
        query = self.db.query(ProfessionalProfile)

        if not include_deleted:
            query = query.filter(ProfessionalProfile.deleted_at.is_(None))

        return query.offset(skip).limit(limit).all()

    def count_professionals(self, include_deleted: bool = False) -> int:
        """Count total professional profiles."""
        query = self.db.query(ProfessionalProfile)

        if not include_deleted:
            query = query.filter(ProfessionalProfile.deleted_at.is_(None))

        return query.count()

    def update_rating(
        self, profile_id: UUID, average_rating: float, total_reviews: int
    ) -> Optional[ProfessionalProfile]:
        """Update professional rating."""
        db_profile = self.get_by_id(profile_id)
        if not db_profile:
            return None

        db_profile.average_rating = average_rating
        db_profile.total_reviews = total_reviews
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def add_skill(
        self,
        professional_id: UUID,
        skill_id: UUID,
        proficiency_level: int,
        years_experience: Optional[int] = None,
        certified: bool = False,
    ) -> Optional[ProfessionalSkill]:
        """Add a skill to professional profile."""
        db_skill = ProfessionalSkill(
            professional_id=professional_id,
            skill_id=skill_id,
            proficiency_level=proficiency_level,
            years_experience=years_experience,
            certified=1 if certified else 0,
        )

        self.db.add(db_skill)
        self.db.commit()
        self.db.refresh(db_skill)
        return db_skill

    def remove_skill(self, professional_id: UUID, skill_id: UUID) -> bool:
        """Remove a skill from professional profile."""
        db_skill = (
            self.db.query(ProfessionalSkill)
            .filter(
                and_(
                    ProfessionalSkill.professional_id == professional_id,
                    ProfessionalSkill.skill_id == skill_id,
                    ProfessionalSkill.deleted_at.is_(None),
                )
            )
            .first()
        )

        if not db_skill:
            return False

        db_skill.soft_delete()
        self.db.commit()
        return True

    def get_professional_skills(self, professional_id: UUID) -> list[ProfessionalSkill]:
        """Get all skills for a professional."""
        return (
            self.db.query(ProfessionalSkill)
            .filter(
                and_(
                    ProfessionalSkill.professional_id == professional_id,
                    ProfessionalSkill.deleted_at.is_(None),
                )
            )
            .all()
        )

    def add_link(
        self, professional_id: UUID, link_data: ProfessionalLinkCreate
    ) -> ProfessionalLink:
        """Add a social link to professional profile."""
        db_link = ProfessionalLink(
            professional_id=professional_id,
            platform=link_data.platform,
            url=link_data.url,
            label=link_data.label,
        )
        self.db.add(db_link)
        self.db.commit()
        self.db.refresh(db_link)
        return db_link

    def update_link(
        self, link_id: UUID, link_update: ProfessionalLinkUpdate
    ) -> Optional[ProfessionalLink]:
        """Update a social link."""
        db_link = (
            self.db.query(ProfessionalLink)
            .filter(
                and_(
                    ProfessionalLink.id == link_id,
                    ProfessionalLink.deleted_at.is_(None),
                )
            )
            .first()
        )

        if not db_link:
            return None

        if link_update.platform is not None:
            db_link.platform = link_update.platform
        if link_update.url is not None:
            db_link.url = link_update.url
        if link_update.label is not None:
            db_link.label = link_update.label

        self.db.commit()
        self.db.refresh(db_link)
        return db_link

    def remove_link(self, professional_id: UUID, link_id: UUID) -> bool:
        """Remove a social link from professional profile."""
        db_link = (
            self.db.query(ProfessionalLink)
            .filter(
                and_(
                    ProfessionalLink.id == link_id,
                    ProfessionalLink.professional_id == professional_id,
                    ProfessionalLink.deleted_at.is_(None),
                )
            )
            .first()
        )

        if not db_link:
            return False

        db_link.soft_delete()
        self.db.commit()
        return True
