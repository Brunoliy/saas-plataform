"""Skill repository for database operations."""

from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.skill import Skill
from app.schemas.skill import SkillCreate, SkillUpdate


class SkillRepository:
    """Skill repository class."""

    def __init__(self, db: Session):
        """Initialize repository."""
        self.db = db

    def create(self, skill_data: SkillCreate) -> Skill:
        """Create a new skill."""
        db_skill = Skill(
            name=skill_data.name,
            category=skill_data.category,
            description=skill_data.description,
            active=True,
        )

        self.db.add(db_skill)
        self.db.commit()
        self.db.refresh(db_skill)
        return db_skill

    def get_by_id(self, skill_id: UUID) -> Skill | None:
        """Get skill by ID (only non-deleted skills)."""
        return (
            self.db.query(Skill)
            .filter(and_(Skill.id == skill_id, Skill.deleted_at.is_(None)))
            .first()
        )

    def get_by_name(self, name: str) -> Skill | None:
        """Get skill by name (only non-deleted skills)."""
        return (
            self.db.query(Skill)
            .filter(and_(Skill.name == name, Skill.deleted_at.is_(None)))
            .first()
        )

    def update(self, skill_id: UUID, skill_data: SkillUpdate) -> Skill | None:
        """Update skill."""
        db_skill = self.get_by_id(skill_id)
        if not db_skill:
            return None

        update_data = skill_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_skill, field, value)

        self.db.commit()
        self.db.refresh(db_skill)
        return db_skill

    def delete(self, skill_id: UUID) -> bool:
        """Soft delete skill."""
        db_skill = self.get_by_id(skill_id)
        if not db_skill:
            return False

        db_skill.soft_delete()
        self.db.commit()
        return True

    def list_skills(
        self, skip: int = 0, limit: int = 20, include_deleted: bool = False
    ) -> list[Skill]:
        """List skills with pagination."""
        query = self.db.query(Skill)

        if not include_deleted:
            query = query.filter(Skill.deleted_at.is_(None))

        return query.offset(skip).limit(limit).all()

    def count_skills(self, include_deleted: bool = False) -> int:
        """Count total skills."""
        query = self.db.query(Skill)

        if not include_deleted:
            query = query.filter(Skill.deleted_at.is_(None))

        return query.count()

    def get_skills_by_category(
        self, category: str, skip: int = 0, limit: int = 20
    ) -> list[Skill]:
        """Get skills by category."""
        return (
            self.db.query(Skill)
            .filter(and_(Skill.category == category, Skill.deleted_at.is_(None)))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_skills(self, skip: int = 0, limit: int = 20) -> list[Skill]:
        """Get active skills."""
        return (
            self.db.query(Skill)
            .filter(and_(Skill.active.is_(True), Skill.deleted_at.is_(None)))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def activate_skill(self, skill_id: UUID) -> Skill | None:
        """Activate skill."""
        db_skill = self.get_by_id(skill_id)
        if not db_skill:
            return None

        db_skill.active = True
        self.db.commit()
        self.db.refresh(db_skill)
        return db_skill

    def deactivate_skill(self, skill_id: UUID) -> Skill | None:
        """Deactivate skill."""
        db_skill = self.get_by_id(skill_id)
        if not db_skill:
            return None

        db_skill.active = False
        self.db.commit()
        self.db.refresh(db_skill)
        return db_skill

    def get_categories(self) -> list[str]:
        """Get all unique skill categories."""
        result = (
            self.db.query(Skill.category)
            .filter(Skill.deleted_at.is_(None))
            .distinct()
            .all()
        )

        return [category[0] for category in result]

    def search_skills(
        self, search_term: str, skip: int = 0, limit: int = 20
    ) -> list[Skill]:
        """Search skills by name or description."""
        search_pattern = f"%{search_term}%"
        return (
            self.db.query(Skill)
            .filter(
                and_(
                    (
                        Skill.name.ilike(search_pattern)
                        | Skill.description.ilike(search_pattern)
                    ),
                    Skill.deleted_at.is_(None),
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
