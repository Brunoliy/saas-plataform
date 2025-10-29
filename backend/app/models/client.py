"""Client model."""

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, Text
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
    description = Column(Text, nullable=True)  # Description for company
    bio = Column(Text, nullable=True)  # About section for company profile
    average_rating = Column(Numeric(3, 2), nullable=True)
    total_reviews = Column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="client_profile")
    projects = relationship("Project", back_populates="client")
    links = relationship(
        "ClientLink", back_populates="client", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of the client profile."""
        return f"<ClientProfile(id={self.id}, user_id={self.user_id}, company_name={self.company_name})>"


class ClientLink(BaseModel):
    """Client social link model."""

    __tablename__ = "client_links"

    client_id = Column(
        UUID(as_uuid=True), ForeignKey("client_profiles.id"), nullable=False
    )
    platform = Column(
        String(50), nullable=False
    )  # github, linkedin, twitter, website, other
    url = Column(Text, nullable=False)
    label = Column(String(255), nullable=True)  # Optional custom label

    # Relationships
    client = relationship("ClientProfile", back_populates="links")

    def __repr__(self) -> str:
        """String representation of the client link."""
        return f"<ClientLink(id={self.id}, client_id={self.client_id}, platform={self.platform})>"
