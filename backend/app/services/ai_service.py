"""AI service."""

from app.repositories.ai_repository import AIRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.professional_repository import ProfessionalRepository


class AIService:
    """AI service class."""
    
    def __init__(self, ai_repository: AIRepository, project_repository: ProjectRepository, professional_repository: ProfessionalRepository):
        """Initialize service."""
        self.ai_repository = ai_repository
        self.project_repository = project_repository
        self.professional_repository = professional_repository