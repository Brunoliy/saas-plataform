"""Project model."""

from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ProjectStatus(str, Enum):
    """Project status enumeration."""

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Project(BaseModel):
    """Project model."""

    __tablename__ = "projects"

    client_id = Column(
        UUID(as_uuid=True), ForeignKey("client_profiles.id"), nullable=False
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(JSONB, nullable=True)
    budget = Column(Numeric(12, 2), nullable=True)
    deadline = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default=ProjectStatus.OPEN)
    selected_professional_id = Column(
        UUID(as_uuid=True), ForeignKey("professional_profiles.id"), nullable=True
    )

    # Relationships
    client = relationship("ClientProfile", back_populates="projects")
    selected_professional = relationship("ProfessionalProfile")
    proposals = relationship("Proposal", back_populates="project")
    reviews = relationship("Review", back_populates="project")
    ai_analyses = relationship("AIAnalysis", back_populates="project")

    def __repr__(self) -> str:
        """String representation of the project."""
        return f"<Project(id={self.id}, title={self.title}, status={self.status})>"
