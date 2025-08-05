"""Database base configuration."""

from app.models.base import Base
from app.models.user import User
from app.models.professional import ProfessionalProfile, ProfessionalSkill
from app.models.client import ClientProfile
from app.models.skill import Skill
from app.models.project import Project
from app.models.proposal import Proposal
from app.models.review import Review
from app.models.ai_analysis import AIAnalysis

# Import all models to ensure they are registered with SQLAlchemy
__all__ = [
    "Base",
    "User",
    "ProfessionalProfile",
    "ProfessionalSkill",
    "ClientProfile",
    "Skill",
    "Project",
    "Proposal",
    "Review",
    "AIAnalysis",
] 