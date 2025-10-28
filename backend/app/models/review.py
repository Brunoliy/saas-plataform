"""Review model."""

from enum import Enum

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ReviewType(str, Enum):
    """Review type enumeration."""

    PROFESSIONAL_TO_CLIENT = "professional_to_client"
    CLIENT_TO_PROFESSIONAL = "client_to_professional"


class Review(BaseModel):
    """Review model."""

    __tablename__ = "reviews"

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reviewed_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 scale
    comment = Column(Text, nullable=True)
    review_type = Column(String(30), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="reviews")
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    reviewed = relationship("User", foreign_keys=[reviewed_id])

    def __repr__(self) -> str:
        """String representation of the review."""
        return f"<Review(id={self.id}, project_id={self.project_id}, rating={self.rating}, review_type={self.review_type})>"
