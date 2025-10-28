"""Project service."""

from typing import Optional
from uuid import UUID

from app.models.project import Project, ProjectStatus
from app.repositories.client_repository import ClientRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Project service class."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        client_repository: ClientRepository,
        professional_repository: ProfessionalRepository,
    ):
        """Initialize service."""
        self.project_repository = project_repository
        self.client_repository = client_repository
        self.professional_repository = professional_repository

    async def create_project(
        self, client_id: UUID, project_data: ProjectCreate
    ) -> Project:
        """Create a new project."""
        # Verify client exists
        client = self.client_repository.get_by_id(client_id)
        if not client:
            raise ValueError("Client profile not found")

        return self.project_repository.create(client_id, project_data)

    async def get_project_by_id(self, project_id: UUID) -> Optional[Project]:
        """Get project by ID."""
        return self.project_repository.get_by_id(project_id)

    async def update_project(
        self, project_id: UUID, project_data: ProjectUpdate
    ) -> Optional[Project]:
        """Update project."""
        return self.project_repository.update(project_id, project_data)

    async def delete_project(self, project_id: UUID) -> bool:
        """Delete project."""
        return self.project_repository.delete(project_id)

    async def list_projects(self, skip: int = 0, limit: int = 20) -> list[Project]:
        """List projects."""
        return self.project_repository.list_projects(skip=skip, limit=limit)

    async def count_projects(self) -> int:
        """Count total projects."""
        return self.project_repository.count_projects()

    async def get_projects_by_client(
        self, client_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[Project]:
        """Get projects by client ID."""
        return self.project_repository.get_projects_by_client(
            client_id, skip=skip, limit=limit
        )

    async def get_projects_by_status(
        self, status: ProjectStatus, skip: int = 0, limit: int = 20
    ) -> list[Project]:
        """Get projects by status."""
        return self.project_repository.get_projects_by_status(
            status, skip=skip, limit=limit
        )

    async def get_projects_by_professional(
        self, professional_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[Project]:
        """Get projects by professional ID."""
        return self.project_repository.get_projects_by_professional(
            professional_id, skip=skip, limit=limit
        )

    async def get_open_projects(self, skip: int = 0, limit: int = 20) -> list[Project]:
        """Get all open projects."""
        return self.project_repository.get_open_projects(skip=skip, limit=limit)

    async def assign_professional(
        self, project_id: UUID, professional_id: UUID
    ) -> Optional[Project]:
        """Assign a professional to a project."""
        # Verify project exists
        project = self.project_repository.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found")

        # Verify project is open
        if project.status != ProjectStatus.OPEN:
            raise ValueError(
                f"Project is not open for assignment. Current status: {project.status}"
            )

        # Verify professional exists
        professional = self.professional_repository.get_by_id(professional_id)
        if not professional:
            raise ValueError("Professional profile not found")

        return self.project_repository.assign_professional(project_id, professional_id)

    async def update_status(
        self, project_id: UUID, status: ProjectStatus
    ) -> Optional[Project]:
        """Update project status."""
        # Verify project exists
        project = self.project_repository.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found")

        # Validate status transitions
        if (
            project.status == ProjectStatus.COMPLETED
            and status != ProjectStatus.COMPLETED
        ):
            raise ValueError("Cannot change status of completed project")

        if (
            project.status == ProjectStatus.CANCELLED
            and status != ProjectStatus.CANCELLED
        ):
            raise ValueError("Cannot change status of cancelled project")

        return self.project_repository.update_status(project_id, status)

    async def complete_project(self, project_id: UUID) -> Optional[Project]:
        """Mark project as completed."""
        return await self.update_status(project_id, ProjectStatus.COMPLETED)

    async def cancel_project(self, project_id: UUID) -> Optional[Project]:
        """Mark project as cancelled."""
        return await self.update_status(project_id, ProjectStatus.CANCELLED)
