"""Professional models."""

from enum import Enum

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class LinkPlatform(str, Enum):
    """Link platform enumeration."""

    GITHUB = "github"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    PORTFOLIO = "portfolio"
    OTHER = "other"


class ProfessionalProfile(BaseModel):
    """Professional profile model."""

    __tablename__ = "professional_profiles"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)  # About section for professional profile
    hourly_rate = Column(Numeric(10, 2), nullable=True)
    average_rating = Column(Numeric(3, 2), nullable=True)
    total_reviews = Column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="professional_profile")
    skills = relationship("ProfessionalSkill", back_populates="professional")
    links = relationship(
        "ProfessionalLink", back_populates="professional", cascade="all, delete-orphan"
    )
    proposals = relationship("Proposal", back_populates="professional")
    ai_analyses = relationship("AIAnalysis", back_populates="professional")

    def __repr__(self) -> str:
        """String representation of the professional profile."""
        return f"<ProfessionalProfile(id={self.id}, user_id={self.user_id}, title={self.title})>"


class ProfessionalSkill(BaseModel):
    """Professional skill model (junction table)."""

    __tablename__ = "professional_skills"

    professional_id = Column(
        UUID(as_uuid=True), ForeignKey("professional_profiles.id"), nullable=False
    )
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False)
    proficiency_level = Column(Integer, nullable=False)  # 1-5 scale
    years_experience = Column(Integer, nullable=True)
    certified = Column(Integer, default=0, nullable=False)  # Boolean as integer

    # Relationships
    professional = relationship("ProfessionalProfile", back_populates="skills")
    skill = relationship("Skill", back_populates="professionals")

    def __repr__(self) -> str:
        """String representation of the professional skill."""
        return f"<ProfessionalSkill(professional_id={self.professional_id}, skill_id={self.skill_id})>"


class ProfessionalLink(BaseModel):
    """Professional social link model."""

    __tablename__ = "professional_links"

    professional_id = Column(
        UUID(as_uuid=True), ForeignKey("professional_profiles.id"), nullable=False
    )
    platform = Column(
        String(50), nullable=False
    )  # github, linkedin, twitter, portfolio, other
    url = Column(Text, nullable=False)
    label = Column(String(255), nullable=True)  # Optional custom label

    # Relationships
    professional = relationship("ProfessionalProfile", back_populates="links")

    def __repr__(self) -> str:
        """String representation of the professional link."""
        return f"<ProfessionalLink(id={self.id}, professional_id={self.professional_id}, platform={self.platform})>"
