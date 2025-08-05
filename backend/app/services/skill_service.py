"""Skill service."""

from app.repositories.skill_repository import SkillRepository


class SkillService:
    """Skill service class."""
    
    def __init__(self, skill_repository: SkillRepository):
        """Initialize service."""
        self.skill_repository = skill_repository