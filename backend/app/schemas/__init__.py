"""Pydantic schemas for API requests and responses."""

from app.schemas.auth import Token, TokenData
from app.schemas.client import (
    ClientProfileCreate,
    ClientProfileResponse,
    ClientProfileUpdate,
)
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.professional import (
    ProfessionalProfileCreate,
    ProfessionalProfileResponse,
    ProfessionalProfileUpdate,
    ProfessionalSkillCreate,
    ProfessionalSkillResponse,
    ProfessionalSkillUpdate,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectStatus,
    ProjectUpdate,
)
from app.schemas.proposal import (
    ProposalCreate,
    ProposalResponse,
    ProposalStatus,
    ProposalUpdate,
)
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewType, ReviewUpdate
from app.schemas.skill import SkillCreate, SkillResponse, SkillUpdate
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate

__all__ = [
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    # Auth schemas
    "Token",
    "TokenData",
    # Common schemas
    "PaginationParams",
    "PaginatedResponse",
    # Professional schemas
    "ProfessionalProfileCreate",
    "ProfessionalProfileUpdate",
    "ProfessionalProfileResponse",
    "ProfessionalSkillCreate",
    "ProfessionalSkillUpdate",
    "ProfessionalSkillResponse",
    # Client schemas
    "ClientProfileCreate",
    "ClientProfileUpdate",
    "ClientProfileResponse",
    # Project schemas
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectStatus",
    # Proposal schemas
    "ProposalCreate",
    "ProposalUpdate",
    "ProposalResponse",
    "ProposalStatus",
    # Skill schemas
    "SkillCreate",
    "SkillUpdate",
    "SkillResponse",
    # Review schemas
    "ReviewCreate",
    "ReviewUpdate",
    "ReviewResponse",
    "ReviewType",
]
