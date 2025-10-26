"""Proposal service."""

from typing import Optional, List
from uuid import UUID

from app.repositories.proposal_repository import ProposalRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.schemas.proposal import ProposalCreate, ProposalUpdate
from app.models.proposal import Proposal, ProposalStatus
from app.models.project import ProjectStatus


class ProposalService:
    """Proposal service class."""

    def __init__(self, proposal_repository: ProposalRepository, project_repository: ProjectRepository, professional_repository: ProfessionalRepository):
        """Initialize service."""
        self.proposal_repository = proposal_repository
        self.project_repository = project_repository
        self.professional_repository = professional_repository

    async def create_proposal(self, professional_id: UUID, proposal_data: ProposalCreate) -> Proposal:
        """Create a new proposal."""
        # Verify professional exists
        professional = self.professional_repository.get_by_id(professional_id)
        if not professional:
            raise ValueError("Professional profile not found")

        # Verify project exists
        project = self.project_repository.get_by_id(proposal_data.project_id)
        if not project:
            raise ValueError("Project not found")

        # Verify project is open for proposals
        if project.status != ProjectStatus.OPEN:
            raise ValueError(f"Project is not open for proposals. Current status: {project.status}")

        # Check if professional already submitted a proposal for this project
        existing_proposal = self.proposal_repository.get_proposal_by_project_and_professional(
            proposal_data.project_id, professional_id
        )
        if existing_proposal:
            raise ValueError("You have already submitted a proposal for this project")

        return self.proposal_repository.create(professional_id, proposal_data)

    async def get_proposal_by_id(self, proposal_id: UUID) -> Optional[Proposal]:
        """Get proposal by ID."""
        return self.proposal_repository.get_by_id(proposal_id)

    async def update_proposal(self, proposal_id: UUID, proposal_data: ProposalUpdate) -> Optional[Proposal]:
        """Update proposal."""
        # Verify proposal exists
        proposal = self.proposal_repository.get_by_id(proposal_id)
        if not proposal:
            raise ValueError("Proposal not found")

        # Only allow updates if proposal is still submitted
        if proposal.status != ProposalStatus.SUBMITTED:
            raise ValueError(f"Cannot update proposal with status: {proposal.status}")

        return self.proposal_repository.update(proposal_id, proposal_data)

    async def delete_proposal(self, proposal_id: UUID) -> bool:
        """Delete proposal."""
        # Verify proposal exists and is in submitted status
        proposal = self.proposal_repository.get_by_id(proposal_id)
        if not proposal:
            raise ValueError("Proposal not found")

        if proposal.status != ProposalStatus.SUBMITTED:
            raise ValueError(f"Cannot delete proposal with status: {proposal.status}")

        return self.proposal_repository.delete(proposal_id)

    async def list_proposals(self, skip: int = 0, limit: int = 20) -> List[Proposal]:
        """List proposals."""
        return self.proposal_repository.list_proposals(skip=skip, limit=limit)

    async def count_proposals(self) -> int:
        """Count total proposals."""
        return self.proposal_repository.count_proposals()

    async def get_proposals_by_project(self, project_id: UUID, skip: int = 0, limit: int = 20) -> List[Proposal]:
        """Get proposals by project ID."""
        return self.proposal_repository.get_proposals_by_project(project_id, skip=skip, limit=limit)

    async def get_proposals_by_professional(self, professional_id: UUID, skip: int = 0, limit: int = 20) -> List[Proposal]:
        """Get proposals by professional ID."""
        return self.proposal_repository.get_proposals_by_professional(professional_id, skip=skip, limit=limit)

    async def get_proposals_by_status(self, status: ProposalStatus, skip: int = 0, limit: int = 20) -> List[Proposal]:
        """Get proposals by status."""
        return self.proposal_repository.get_proposals_by_status(status, skip=skip, limit=limit)

    async def accept_proposal(self, proposal_id: UUID) -> Optional[Proposal]:
        """Accept a proposal and assign professional to project."""
        # Verify proposal exists
        proposal = self.proposal_repository.get_by_id(proposal_id)
        if not proposal:
            raise ValueError("Proposal not found")

        # Verify proposal is in submitted status
        if proposal.status != ProposalStatus.SUBMITTED:
            raise ValueError(f"Cannot accept proposal with status: {proposal.status}")

        # Verify project is still open
        project = self.project_repository.get_by_id(proposal.project_id)
        if not project:
            raise ValueError("Project not found")

        if project.status != ProjectStatus.OPEN:
            raise ValueError(f"Project is not open. Current status: {project.status}")

        # Accept the proposal
        accepted_proposal = self.proposal_repository.accept_proposal(proposal_id)

        # Assign professional to project
        self.project_repository.assign_professional(proposal.project_id, proposal.professional_id)

        # Reject all other proposals for this project
        all_proposals = self.proposal_repository.get_proposals_by_project(proposal.project_id)
        for other_proposal in all_proposals:
            if other_proposal.id != proposal_id and other_proposal.status == ProposalStatus.SUBMITTED:
                self.proposal_repository.reject_proposal(other_proposal.id)

        return accepted_proposal

    async def reject_proposal(self, proposal_id: UUID) -> Optional[Proposal]:
        """Reject a proposal."""
        # Verify proposal exists
        proposal = self.proposal_repository.get_by_id(proposal_id)
        if not proposal:
            raise ValueError("Proposal not found")

        # Verify proposal is in submitted status
        if proposal.status != ProposalStatus.SUBMITTED:
            raise ValueError(f"Cannot reject proposal with status: {proposal.status}")

        return self.proposal_repository.reject_proposal(proposal_id)

    async def update_ai_score(self, proposal_id: UUID, ai_score: float) -> Optional[Proposal]:
        """Update proposal AI score."""
        return self.proposal_repository.update_ai_score(proposal_id, ai_score)