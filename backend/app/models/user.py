"""User model."""

from enum import Enum
from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class AccountType(str, Enum):
    """Account type enumeration."""
    
    PROFESSIONAL = "professional"
    CLIENT = "client"


class User(BaseModel):
    """User model."""
    
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    account_type = Column(String(20), nullable=False, default=AccountType.CLIENT)
    active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    professional_profile = relationship("ProfessionalProfile", back_populates="user", uselist=False)
    client_profile = relationship("ClientProfile", back_populates="user", uselist=False)
    
    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User(id={self.id}, email={self.email}, account_type={self.account_type})>" 