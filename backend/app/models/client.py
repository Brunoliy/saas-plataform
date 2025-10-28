"""Client model."""

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ClientProfile(BaseModel):
    """Client profile model."""

    __tablename__ = "client_profiles"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True
    )
    company_name = Column(String(255), nullable=True)
    business_sector = Column(String(100), nullable=True)
    average_rating = Column(Numeric(3, 2), nullable=True)
    total_reviews = Column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="client_profile")
    projects = relationship("Project", back_populates="client")

    def __repr__(self) -> str:
        """String representation of the client profile."""
        return f"<ClientProfile(id={self.id}, user_id={self.user_id}, company_name={self.company_name})>"
