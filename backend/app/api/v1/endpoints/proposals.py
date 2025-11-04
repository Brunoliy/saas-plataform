"""Proposal endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.database.session import get_db
from app.repositories.client_repository import ClientRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.proposal_repository import ProposalRepository
from app.repositories.skill_repository import SkillRepository
from app.schemas.common import PaginatedResponse
from app.schemas.proposal import (
    ProposalCreate,
    ProposalResponse,
    ProposalStatus,
    ProposalUpdate,
)
from app.services.client_service import ClientService
from app.services.professional_service import ProfessionalService
from app.services.proposal_service import ProposalService

router = APIRouter()


def get_proposal_service(db: Session = Depends(get_db)) -> ProposalService:
    """Get proposal service dependency."""
    proposal_repository = ProposalRepository(db)
    project_repository = ProjectRepository(db)
    professional_repository = ProfessionalRepository(db)
    return ProposalService(
        proposal_repository, project_repository, professional_repository
    )


def get_professional_service(db: Session = Depends(get_db)) -> ProfessionalService:
    """Get professional service dependency."""
    professional_repository = ProfessionalRepository(db)
    skill_repository = SkillRepository(db)
    return ProfessionalService(professional_repository, skill_repository)


def get_client_service(db: Session = Depends(get_db)) -> ClientService:
    """Get client service dependency."""
    client_repository = ClientRepository(db)
    return ClientService(client_repository)


@router.post("/", response_model=ProposalResponse, status_code=status.HTTP_201_CREATED)
async def create_proposal(
    proposal_data: ProposalCreate,
    current_user_id: str = Depends(get_current_user_id),
    proposal_service: ProposalService = Depends(get_proposal_service),
    professional_service: ProfessionalService = Depends(get_professional_service),
) -> ProposalResponse:
    """Create a new proposal (only professionals can create proposals)."""
    try:
        user_uuid = UUID(current_user_id)

        # Get professional profile for the current user
        professional_profile = await professional_service.get_profile_by_user_id(
            user_uuid
        )
        if not professional_profile:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only professionals can create proposals. Please create a professional profile first.",
            )

        return await proposal_service.create_proposal(
            professional_profile.id, proposal_data
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=PaginatedResponse[ProposalResponse])
async def list_proposals(
    skip: int = 0,
    limit: int = 20,
    project_id: str | None = None,
    professional_id: str | None = None,
    status_filter: ProposalStatus | None = None,
    current_user_id: str = Depends(get_current_user_id),
    proposal_service: ProposalService = Depends(get_proposal_service),
) -> PaginatedResponse[ProposalResponse]:
    """List proposals with pagination and filters (authenticated endpoint)."""
    try:
        if project_id:
            project_uuid = UUID(project_id)
            proposals = await proposal_service.get_proposals_by_project(
                project_uuid, skip=skip, limit=limit
            )
        elif professional_id:
            professional_uuid = UUID(professional_id)
            proposals = await proposal_service.get_proposals_by_professional(
                professional_uuid, skip=skip, limit=limit
            )
        elif status_filter:
            proposals = await proposal_service.get_proposals_by_status(
                status_filter, skip=skip, limit=limit
            )
        else:
            proposals = await proposal_service.list_proposals(skip=skip, limit=limit)

        total = await proposal_service.count_proposals()

        pages = (total + limit - 1) // limit if limit > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1

        return PaginatedResponse(
            items=proposals, total=total, page=current_page, size=limit, pages=pages
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format"
        )


@router.get("/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(
    proposal_id: str,
    current_user_id: str = Depends(get_current_user_id),
    proposal_service: ProposalService = Depends(get_proposal_service),
) -> ProposalResponse:
    """Get proposal by ID (authenticated endpoint)."""
    try:
        proposal_uuid = UUID(proposal_id)
        proposal = await proposal_service.get_proposal_by_id(proposal_uuid)
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found"
            )
        return proposal
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid proposal ID format"
        )


@router.put("/{proposal_id}", response_model=ProposalResponse)
async def update_proposal(
    proposal_id: str,
    proposal_update: ProposalUpdate,
    current_user_id: str = Depends(get_current_user_id),
    proposal_service: ProposalService = Depends(get_proposal_service),
    professional_service: ProfessionalService = Depends(get_professional_service),
) -> ProposalResponse:
    """Update proposal (only proposal owner can update)."""
    try:
        proposal_uuid = UUID(proposal_id)
        user_uuid = UUID(current_user_id)

        # Verify proposal exists
        proposal = await proposal_service.get_proposal_by_id(proposal_uuid)
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found"
            )

        # Verify ownership
        professional_profile = await professional_service.get_profile_by_user_id(
            user_uuid
        )
        if (
            not professional_profile
            or proposal.professional_id != professional_profile.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this proposal",
            )

        return await proposal_service.update_proposal(proposal_uuid, proposal_update)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{proposal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_proposal(
    proposal_id: str,
    current_user_id: str = Depends(get_current_user_id),
    proposal_service: ProposalService = Depends(get_proposal_service),
    professional_service: ProfessionalService = Depends(get_professional_service),
) -> None:
    """Delete proposal (only proposal owner can delete)."""
    try:
        proposal_uuid = UUID(proposal_id)
        user_uuid = UUID(current_user_id)

        # Verify proposal exists
        proposal = await proposal_service.get_proposal_by_id(proposal_uuid)
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found"
            )

        # Verify ownership
        professional_profile = await professional_service.get_profile_by_user_id(
            user_uuid
        )
        if (
            not professional_profile
            or proposal.professional_id != professional_profile.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this proposal",
            )

        await proposal_service.delete_proposal(proposal_uuid)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{proposal_id}/accept", response_model=ProposalResponse)
async def accept_proposal(
    proposal_id: str,
    current_user_id: str = Depends(get_current_user_id),
    proposal_service: ProposalService = Depends(get_proposal_service),
    client_service: ClientService = Depends(get_client_service),
) -> ProposalResponse:
    """Accept a proposal (only project owner can accept)."""
    try:
        proposal_uuid = UUID(proposal_id)
        user_uuid = UUID(current_user_id)

        # Verify proposal exists
        proposal = await proposal_service.get_proposal_by_id(proposal_uuid)
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found"
            )

        # Verify user is the project owner
        from app.repositories.project_repository import ProjectRepository

        db = next(get_db())
        project_repository = ProjectRepository(db)
        project = project_repository.get_by_id(proposal.project_id)

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        # Verify ownership
        client_profile = await client_service.get_profile_by_user_id(user_uuid)
        if not client_profile or project.client_id != client_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to accept proposals for this project",
            )

        return await proposal_service.accept_proposal(proposal_uuid)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{proposal_id}/reject", response_model=ProposalResponse)
async def reject_proposal(
    proposal_id: str,
    current_user_id: str = Depends(get_current_user_id),
    proposal_service: ProposalService = Depends(get_proposal_service),
    client_service: ClientService = Depends(get_client_service),
) -> ProposalResponse:
    """Reject a proposal (only project owner can reject)."""
    try:
        proposal_uuid = UUID(proposal_id)
        user_uuid = UUID(current_user_id)

        # Verify proposal exists
        proposal = await proposal_service.get_proposal_by_id(proposal_uuid)
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found"
            )

        # Verify user is the project owner
        from app.repositories.project_repository import ProjectRepository

        db = next(get_db())
        project_repository = ProjectRepository(db)
        project = project_repository.get_by_id(proposal.project_id)

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        # Verify ownership
        client_profile = await client_service.get_profile_by_user_id(user_uuid)
        if not client_profile or project.client_id != client_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to reject proposals for this project",
            )

        return await proposal_service.reject_proposal(proposal_uuid)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
