"""Skill model."""

from sqlalchemy import Boolean, Column, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Skill(BaseModel):
    """Skill model."""
    
    __tablename__ = "skills"
    
    name = Column(String(100), nullable=False, unique=True, index=True)
    category = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    professionals = relationship("ProfessionalSkill", back_populates="skill")
    
    def __repr__(self) -> str:
        """String representation of the skill."""
        return f"<Skill(id={self.id}, name={self.name}, category={self.category})>" 