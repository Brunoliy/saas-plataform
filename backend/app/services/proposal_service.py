"""Proposal service."""

from app.repositories.proposal_repository import ProposalRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.professional_repository import ProfessionalRepository


class ProposalService:
    """Proposal service class."""
    
    def __init__(self, proposal_repository: ProposalRepository, project_repository: ProjectRepository, professional_repository: ProfessionalRepository):
        """Initialize service."""
        self.proposal_repository = proposal_repository
        self.project_repository = project_repository
        self.professional_repository = professional_repository