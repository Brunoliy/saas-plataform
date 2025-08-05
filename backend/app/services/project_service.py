"""Project service."""

from app.repositories.project_repository import ProjectRepository
from app.repositories.client_repository import ClientRepository
from app.repositories.professional_repository import ProfessionalRepository


class ProjectService:
    """Project service class."""
    
    def __init__(self, project_repository: ProjectRepository, client_repository: ClientRepository, professional_repository: ProfessionalRepository):
        """Initialize service."""
        self.project_repository = project_repository
        self.client_repository = client_repository
        self.professional_repository = professional_repository