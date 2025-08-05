"""Professional service."""

from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.skill_repository import SkillRepository


class ProfessionalService:
    """Professional service class."""
    
    def __init__(self, professional_repository: ProfessionalRepository, skill_repository: SkillRepository):
        """Initialize service."""
        self.professional_repository = professional_repository
        self.skill_repository = skill_repository