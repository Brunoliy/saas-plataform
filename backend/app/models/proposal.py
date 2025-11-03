"""Proposal model."""

from enum import Enum

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ProposalStatus(str, Enum):
    """Proposal status enumeration."""

    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class Proposal(BaseModel):
    """Proposal model."""

    __tablename__ = "proposals"

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    professional_id = Column(
        UUID(as_uuid=True), ForeignKey("professional_profiles.id"), nullable=False
    )
    proposed_amount = Column(Numeric(12, 2), nullable=False)
    estimated_days = Column(Integer, nullable=True)
    description = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default=ProposalStatus.SUBMITTED)
    ai_score = Column(Numeric(5, 2), nullable=True)

    # Relationships
    project = relationship("Project", back_populates="proposals")
    professional = relationship("ProfessionalProfile", back_populates="proposals")

    def __repr__(self) -> str:
        """String representation of the proposal."""
        return f"<Proposal(id={self.id}, project_id={self.project_id}, professional_id={self.professional_id}, status={self.status})>"
