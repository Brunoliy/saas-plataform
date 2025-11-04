"""Proposal repository for database operations."""

from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.proposal import Proposal, ProposalStatus
from app.schemas.proposal import ProposalCreate, ProposalUpdate


class ProposalRepository:
    """Proposal repository class."""

    def __init__(self, db: Session):
        """Initialize repository."""
        self.db = db

    def create(self, professional_id: UUID, proposal_data: ProposalCreate) -> Proposal:
        """Create a new proposal."""
        db_proposal = Proposal(
            project_id=proposal_data.project_id,
            professional_id=professional_id,
            proposed_amount=proposal_data.proposed_amount,
            estimated_days=proposal_data.estimated_days,
            description=proposal_data.description,
            status=ProposalStatus.SUBMITTED,
        )

        self.db.add(db_proposal)
        self.db.commit()
        self.db.refresh(db_proposal)
        return db_proposal

    def get_by_id(self, proposal_id: UUID) -> Proposal | None:
        """Get proposal by ID (only non-deleted proposals)."""
        return (
            self.db.query(Proposal)
            .filter(and_(Proposal.id == proposal_id, Proposal.deleted_at.is_(None)))
            .first()
        )

    def update(
        self, proposal_id: UUID, proposal_data: ProposalUpdate
    ) -> Proposal | None:
        """Update proposal."""
        db_proposal = self.get_by_id(proposal_id)
        if not db_proposal:
            return None

        update_data = proposal_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_proposal, field, value)

        self.db.commit()
        self.db.refresh(db_proposal)
        return db_proposal

    def delete(self, proposal_id: UUID) -> bool:
        """Soft delete proposal."""
        db_proposal = self.get_by_id(proposal_id)
        if not db_proposal:
            return False

        db_proposal.soft_delete()
        self.db.commit()
        return True

    def list_proposals(
        self, skip: int = 0, limit: int = 20, include_deleted: bool = False
    ) -> list[Proposal]:
        """List proposals with pagination."""
        query = self.db.query(Proposal)

        if not include_deleted:
            query = query.filter(Proposal.deleted_at.is_(None))

        return query.offset(skip).limit(limit).all()

    def count_proposals(self, include_deleted: bool = False) -> int:
        """Count total proposals."""
        query = self.db.query(Proposal)

        if not include_deleted:
            query = query.filter(Proposal.deleted_at.is_(None))

        return query.count()

    def get_proposals_by_project(
        self, project_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[Proposal]:
        """Get proposals by project ID."""
        return (
            self.db.query(Proposal)
            .filter(
                and_(Proposal.project_id == project_id, Proposal.deleted_at.is_(None))
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_proposals_by_professional(
        self, professional_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[Proposal]:
        """Get proposals by professional ID."""
        return (
            self.db.query(Proposal)
            .filter(
                and_(
                    Proposal.professional_id == professional_id,
                    Proposal.deleted_at.is_(None),
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_proposals_by_status(
        self, status: ProposalStatus, skip: int = 0, limit: int = 20
    ) -> list[Proposal]:
        """Get proposals by status."""
        return (
            self.db.query(Proposal)
            .filter(and_(Proposal.status == status, Proposal.deleted_at.is_(None)))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def accept_proposal(self, proposal_id: UUID) -> Proposal | None:
        """Accept a proposal."""
        db_proposal = self.get_by_id(proposal_id)
        if not db_proposal:
            return None

        db_proposal.status = ProposalStatus.ACCEPTED
        self.db.commit()
        self.db.refresh(db_proposal)
        return db_proposal

    def reject_proposal(self, proposal_id: UUID) -> Proposal | None:
        """Reject a proposal."""
        db_proposal = self.get_by_id(proposal_id)
        if not db_proposal:
            return None

        db_proposal.status = ProposalStatus.REJECTED
        self.db.commit()
        self.db.refresh(db_proposal)
        return db_proposal

    def update_ai_score(self, proposal_id: UUID, ai_score: float) -> Proposal | None:
        """Update proposal AI score."""
        db_proposal = self.get_by_id(proposal_id)
        if not db_proposal:
            return None

        db_proposal.ai_score = ai_score
        self.db.commit()
        self.db.refresh(db_proposal)
        return db_proposal

    def get_proposal_by_project_and_professional(
        self, project_id: UUID, professional_id: UUID
    ) -> Proposal | None:
        """Get active proposal by project and professional (only SUBMITTED status)."""
        return (
            self.db.query(Proposal)
            .filter(
                and_(
                    Proposal.project_id == project_id,
                    Proposal.professional_id == professional_id,
                    Proposal.status == ProposalStatus.SUBMITTED,
                    Proposal.deleted_at.is_(None),
                )
            )
            .first()
        )
