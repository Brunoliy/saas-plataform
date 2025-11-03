"""Project repository for database operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from app.models.project import Project, ProjectStatus
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectRepository:
    """Project repository class."""

    def __init__(self, db: Session):
        """Initialize repository."""
        self.db = db

    def create(self, client_id: UUID, project_data: ProjectCreate) -> Project:
        """Create a new project."""
        db_project = Project(
            client_id=client_id,
            title=project_data.title,
            description=project_data.description,
            budget=project_data.budget,
            deadline=project_data.deadline,
            status=ProjectStatus.OPEN,
        )

        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def get_by_id(self, project_id: UUID) -> Optional[Project]:
        """Get project by ID (only non-deleted projects)."""
        return (
            self.db.query(Project)
            .options(
                joinedload(Project.client), joinedload(Project.selected_professional)
            )
            .filter(and_(Project.id == project_id, Project.deleted_at.is_(None)))
            .first()
        )

    def update(
        self, project_id: UUID, project_data: ProjectUpdate
    ) -> Optional[Project]:
        """Update project."""
        db_project = self.get_by_id(project_id)
        if not db_project:
            return None

        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_project, field, value)

        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def delete(self, project_id: UUID) -> bool:
        """Soft delete project."""
        db_project = self.get_by_id(project_id)
        if not db_project:
            return False

        db_project.soft_delete()
        self.db.commit()
        return True

    def list_projects(
        self, skip: int = 0, limit: int = 20, include_deleted: bool = False
    ) -> list[Project]:
        """List projects with pagination."""
        query = self.db.query(Project).options(
            joinedload(Project.client), joinedload(Project.selected_professional)
        )

        if not include_deleted:
            query = query.filter(Project.deleted_at.is_(None))

        return query.offset(skip).limit(limit).all()

    def count_projects(self, include_deleted: bool = False) -> int:
        """Count total projects."""
        query = self.db.query(Project)

        if not include_deleted:
            query = query.filter(Project.deleted_at.is_(None))

        return query.count()

    def get_projects_by_client(
        self, client_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[Project]:
        """Get projects by client ID."""
        return (
            self.db.query(Project)
            .options(
                joinedload(Project.client), joinedload(Project.selected_professional)
            )
            .filter(and_(Project.client_id == client_id, Project.deleted_at.is_(None)))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_projects_by_status(
        self, status: ProjectStatus, skip: int = 0, limit: int = 20
    ) -> list[Project]:
        """Get projects by status."""
        return (
            self.db.query(Project)
            .options(
                joinedload(Project.client), joinedload(Project.selected_professional)
            )
            .filter(and_(Project.status == status, Project.deleted_at.is_(None)))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_projects_by_professional(
        self, professional_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[Project]:
        """Get projects by professional ID."""
        return (
            self.db.query(Project)
            .options(
                joinedload(Project.client), joinedload(Project.selected_professional)
            )
            .filter(
                and_(
                    Project.selected_professional_id == professional_id,
                    Project.deleted_at.is_(None),
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def assign_professional(
        self, project_id: UUID, professional_id: UUID
    ) -> Optional[Project]:
        """Assign a professional to a project."""
        db_project = self.get_by_id(project_id)
        if not db_project:
            return None

        db_project.selected_professional_id = professional_id
        db_project.status = ProjectStatus.IN_PROGRESS
        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def update_status(
        self, project_id: UUID, status: ProjectStatus
    ) -> Optional[Project]:
        """Update project status."""
        db_project = self.get_by_id(project_id)
        if not db_project:
            return None

        db_project.status = status
        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def get_open_projects(self, skip: int = 0, limit: int = 20) -> list[Project]:
        """Get all open projects."""
        return self.get_projects_by_status(ProjectStatus.OPEN, skip, limit)
