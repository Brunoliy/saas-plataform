"""Professional service."""

from typing import Optional, List
from uuid import UUID

from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.skill_repository import SkillRepository
from app.schemas.professional import (
    ProfessionalProfileCreate,
    ProfessionalProfileUpdate,
    ProfessionalSkillCreate
)
from app.models.professional import ProfessionalProfile, ProfessionalSkill
from app.core.exceptions import AuthenticationError


class ProfessionalService:
    """Professional service class."""

    def __init__(self, professional_repository: ProfessionalRepository, skill_repository: SkillRepository):
        """Initialize service."""
        self.professional_repository = professional_repository
        self.skill_repository = skill_repository

    async def create_profile(self, user_id: UUID, profile_data: ProfessionalProfileCreate) -> ProfessionalProfile:
        """Create a new professional profile."""
        # Check if profile already exists
        existing_profile = self.professional_repository.get_by_user_id(user_id)
        if existing_profile:
            raise ValueError("Professional profile already exists for this user")

        # Create profile
        profile = self.professional_repository.create(user_id, profile_data)

        # Add skills if provided
        if profile_data.skills:
            for skill_data in profile_data.skills:
                # Verify skill exists
                skill = self.skill_repository.get_by_id(skill_data.skill_id)
                if not skill:
                    raise ValueError(f"Skill with ID {skill_data.skill_id} not found")

                self.professional_repository.add_skill(
                    professional_id=profile.id,
                    skill_id=skill_data.skill_id,
                    proficiency_level=skill_data.proficiency_level,
                    years_experience=skill_data.years_experience,
                    certified=skill_data.certified
                )

        return profile

    async def get_profile_by_id(self, profile_id: UUID) -> Optional[ProfessionalProfile]:
        """Get professional profile by ID."""
        return self.professional_repository.get_by_id(profile_id)

    async def get_profile_by_user_id(self, user_id: UUID) -> Optional[ProfessionalProfile]:
        """Get professional profile by user ID."""
        return self.professional_repository.get_by_user_id(user_id)

    async def update_profile(self, profile_id: UUID, profile_data: ProfessionalProfileUpdate) -> Optional[ProfessionalProfile]:
        """Update professional profile."""
        return self.professional_repository.update(profile_id, profile_data)

    async def delete_profile(self, profile_id: UUID) -> bool:
        """Delete professional profile."""
        return self.professional_repository.delete(profile_id)

    async def list_professionals(self, skip: int = 0, limit: int = 20) -> List[ProfessionalProfile]:
        """List professional profiles."""
        return self.professional_repository.list_professionals(skip=skip, limit=limit)

    async def count_professionals(self) -> int:
        """Count total professional profiles."""
        return self.professional_repository.count_professionals()

    async def add_skill(self, professional_id: UUID, skill_data: ProfessionalSkillCreate) -> Optional[ProfessionalSkill]:
        """Add a skill to professional profile."""
        # Verify professional exists
        professional = self.professional_repository.get_by_id(professional_id)
        if not professional:
            raise ValueError("Professional profile not found")

        # Verify skill exists
        skill = self.skill_repository.get_by_id(skill_data.skill_id)
        if not skill:
            raise ValueError(f"Skill with ID {skill_data.skill_id} not found")

        # Check if skill is active
        if not skill.active:
            raise ValueError(f"Skill {skill.name} is not active")

        return self.professional_repository.add_skill(
            professional_id=professional_id,
            skill_id=skill_data.skill_id,
            proficiency_level=skill_data.proficiency_level,
            years_experience=skill_data.years_experience,
            certified=skill_data.certified
        )

    async def remove_skill(self, professional_id: UUID, skill_id: UUID) -> bool:
        """Remove a skill from professional profile."""
        return self.professional_repository.remove_skill(professional_id, skill_id)

    async def get_professional_skills(self, professional_id: UUID) -> List[ProfessionalSkill]:
        """Get all skills for a professional."""
        return self.professional_repository.get_professional_skills(professional_id)

    async def update_rating(self, profile_id: UUID, average_rating: float, total_reviews: int) -> Optional[ProfessionalProfile]:
        """Update professional rating."""
        return self.professional_repository.update_rating(profile_id, average_rating, total_reviews)