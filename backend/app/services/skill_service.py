"""Skill service."""

from uuid import UUID

from app.models.skill import Skill
from app.repositories.skill_repository import SkillRepository
from app.schemas.skill import SkillCreate, SkillUpdate


class SkillService:
    """Skill service class."""

    def __init__(self, skill_repository: SkillRepository):
        """Initialize service."""
        self.skill_repository = skill_repository

    async def create_skill(self, skill_data: SkillCreate) -> Skill:
        """Create a new skill."""
        # Check if skill with same name already exists
        existing_skill = self.skill_repository.get_by_name(skill_data.name)
        if existing_skill:
            raise ValueError(f"Skill with name '{skill_data.name}' already exists")

        return self.skill_repository.create(skill_data)

    async def get_skill_by_id(self, skill_id: UUID) -> Skill | None:
        """Get skill by ID."""
        return self.skill_repository.get_by_id(skill_id)

    async def get_skill_by_name(self, name: str) -> Skill | None:
        """Get skill by name."""
        return self.skill_repository.get_by_name(name)

    async def update_skill(
        self, skill_id: UUID, skill_data: SkillUpdate
    ) -> Skill | None:
        """Update skill."""
        # If updating name, check for duplicates
        if skill_data.name:
            existing_skill = self.skill_repository.get_by_name(skill_data.name)
            if existing_skill and existing_skill.id != skill_id:
                raise ValueError(f"Skill with name '{skill_data.name}' already exists")

        return self.skill_repository.update(skill_id, skill_data)

    async def delete_skill(self, skill_id: UUID) -> bool:
        """Delete skill."""
        return self.skill_repository.delete(skill_id)

    async def list_skills(self, skip: int = 0, limit: int = 20) -> list[Skill]:
        """List skills."""
        return self.skill_repository.list_skills(skip=skip, limit=limit)

    async def count_skills(self) -> int:
        """Count total skills."""
        return self.skill_repository.count_skills()

    async def get_skills_by_category(
        self, category: str, skip: int = 0, limit: int = 20
    ) -> list[Skill]:
        """Get skills by category."""
        return self.skill_repository.get_skills_by_category(
            category, skip=skip, limit=limit
        )

    async def get_active_skills(self, skip: int = 0, limit: int = 20) -> list[Skill]:
        """Get active skills."""
        return self.skill_repository.get_active_skills(skip=skip, limit=limit)

    async def activate_skill(self, skill_id: UUID) -> Skill | None:
        """Activate skill."""
        skill = self.skill_repository.get_by_id(skill_id)
        if not skill:
            raise ValueError("Skill not found")

        return self.skill_repository.activate_skill(skill_id)

    async def deactivate_skill(self, skill_id: UUID) -> Skill | None:
        """Deactivate skill."""
        skill = self.skill_repository.get_by_id(skill_id)
        if not skill:
            raise ValueError("Skill not found")

        return self.skill_repository.deactivate_skill(skill_id)

    async def get_categories(self) -> list[str]:
        """Get all unique skill categories."""
        return self.skill_repository.get_categories()

    async def search_skills(
        self, search_term: str, skip: int = 0, limit: int = 20
    ) -> list[Skill]:
        """Search skills by name or description."""
        return self.skill_repository.search_skills(search_term, skip=skip, limit=limit)
