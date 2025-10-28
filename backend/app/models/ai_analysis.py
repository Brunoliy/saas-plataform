"""AI Analysis model."""

from sqlalchemy import JSON, Column, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class AIAnalysis(BaseModel):
    """AI Analysis model."""

    __tablename__ = "ai_analyses"

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    professional_id = Column(
        UUID(as_uuid=True), ForeignKey("professional_profiles.id"), nullable=False
    )
    compatibility_score = Column(Numeric(5, 2), nullable=False)
    positive_factors = Column(JSON, nullable=True)
    negative_factors = Column(JSON, nullable=True)
    recommendation = Column(Text, nullable=True)
    model_version = Column(String(20), nullable=False)
    analysis_date = Column(String(20), nullable=False)  # Using string for timestamp

    # Relationships
    project = relationship("Project", back_populates="ai_analyses")
    professional = relationship("ProfessionalProfile", back_populates="ai_analyses")

    def __repr__(self) -> str:
        """String representation of the AI analysis."""
        return f"<AIAnalysis(id={self.id}, project_id={self.project_id}, professional_id={self.professional_id}, compatibility_score={self.compatibility_score})>"
