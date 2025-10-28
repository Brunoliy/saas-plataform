"""Project endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.database.session import get_db
from app.repositories.client_repository import ClientRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.common import PaginatedResponse
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectStatus,
    ProjectUpdate,
)
from app.services.client_service import ClientService
from app.services.project_service import ProjectService

router = APIRouter()


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    """Get project service dependency."""
    project_repository = ProjectRepository(db)
    client_repository = ClientRepository(db)
    professional_repository = ProfessionalRepository(db)
    return ProjectService(
        project_repository, client_repository, professional_repository
    )


def get_client_service(db: Session = Depends(get_db)) -> ClientService:
    """Get client service dependency."""
    client_repository = ClientRepository(db)
    return ClientService(client_repository)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user_id: str = Depends(get_current_user_id),
    project_service: ProjectService = Depends(get_project_service),
    client_service: ClientService = Depends(get_client_service),
):
    """Create a new project (only clients can create projects)."""
    try:
        user_uuid = UUID(current_user_id)

        # Get client profile for the current user
        client_profile = await client_service.get_profile_by_user_id(user_uuid)
        if not client_profile:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only clients can create projects. Please create a client profile first.",
            )

        return await project_service.create_project(client_profile.id, project_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=PaginatedResponse[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[ProjectStatus] = None,
    client_id: Optional[str] = None,
    professional_id: Optional[str] = None,
    only_open: bool = False,
    project_service: ProjectService = Depends(get_project_service),
):
    """List projects with pagination and filters (public endpoint)."""
    try:
        if only_open:
            projects = await project_service.get_open_projects(skip=skip, limit=limit)
        elif status_filter:
            projects = await project_service.get_projects_by_status(
                status_filter, skip=skip, limit=limit
            )
        elif client_id:
            client_uuid = UUID(client_id)
            projects = await project_service.get_projects_by_client(
                client_uuid, skip=skip, limit=limit
            )
        elif professional_id:
            professional_uuid = UUID(professional_id)
            projects = await project_service.get_projects_by_professional(
                professional_uuid, skip=skip, limit=limit
            )
        else:
            projects = await project_service.list_projects(skip=skip, limit=limit)

        total = await project_service.count_projects()

        pages = (total + limit - 1) // limit if limit > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1

        return PaginatedResponse(
            items=projects, total=total, page=current_page, size=limit, pages=pages
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format"
        )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str, project_service: ProjectService = Depends(get_project_service)
):
    """Get project by ID (public endpoint)."""
    try:
        project_uuid = UUID(project_id)
        project = await project_service.get_project_by_id(project_uuid)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )
        return project
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format"
        )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user_id: str = Depends(get_current_user_id),
    project_service: ProjectService = Depends(get_project_service),
    client_service: ClientService = Depends(get_client_service),
):
    """Update project (only owner can update)."""
    try:
        project_uuid = UUID(project_id)
        user_uuid = UUID(current_user_id)

        # Verify project exists
        project = await project_service.get_project_by_id(project_uuid)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        # Verify ownership
        client_profile = await client_service.get_profile_by_user_id(user_uuid)
        if not client_profile or project.client_id != client_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this project",
            )

        return await project_service.update_project(project_uuid, project_update)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user_id: str = Depends(get_current_user_id),
    project_service: ProjectService = Depends(get_project_service),
    client_service: ClientService = Depends(get_client_service),
):
    """Delete project (only owner can delete)."""
    try:
        project_uuid = UUID(project_id)
        user_uuid = UUID(current_user_id)

        # Verify project exists
        project = await project_service.get_project_by_id(project_uuid)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        # Verify ownership
        client_profile = await client_service.get_profile_by_user_id(user_uuid)
        if not client_profile or project.client_id != client_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this project",
            )

        await project_service.delete_project(project_uuid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format"
        )


@router.patch("/{project_id}/assign/{professional_id}", response_model=ProjectResponse)
async def assign_professional_to_project(
    project_id: str,
    professional_id: str,
    current_user_id: str = Depends(get_current_user_id),
    project_service: ProjectService = Depends(get_project_service),
    client_service: ClientService = Depends(get_client_service),
):
    """Assign a professional to a project (only project owner can assign)."""
    try:
        project_uuid = UUID(project_id)
        professional_uuid = UUID(professional_id)
        user_uuid = UUID(current_user_id)

        # Verify project exists
        project = await project_service.get_project_by_id(project_uuid)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        # Verify ownership
        client_profile = await client_service.get_profile_by_user_id(user_uuid)
        if not client_profile or project.client_id != client_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to assign professionals to this project",
            )

        return await project_service.assign_professional(
            project_uuid, professional_uuid
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{project_id}/complete", response_model=ProjectResponse)
async def complete_project(
    project_id: str,
    current_user_id: str = Depends(get_current_user_id),
    project_service: ProjectService = Depends(get_project_service),
    client_service: ClientService = Depends(get_client_service),
):
    """Mark project as completed (only owner can complete)."""
    try:
        project_uuid = UUID(project_id)
        user_uuid = UUID(current_user_id)

        # Verify project exists
        project = await project_service.get_project_by_id(project_uuid)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        # Verify ownership
        client_profile = await client_service.get_profile_by_user_id(user_uuid)
        if not client_profile or project.client_id != client_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to complete this project",
            )

        return await project_service.complete_project(project_uuid)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{project_id}/cancel", response_model=ProjectResponse)
async def cancel_project(
    project_id: str,
    current_user_id: str = Depends(get_current_user_id),
    project_service: ProjectService = Depends(get_project_service),
    client_service: ClientService = Depends(get_client_service),
):
    """Mark project as cancelled (only owner can cancel)."""
    try:
        project_uuid = UUID(project_id)
        user_uuid = UUID(current_user_id)

        # Verify project exists
        project = await project_service.get_project_by_id(project_uuid)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        # Verify ownership
        client_profile = await client_service.get_profile_by_user_id(user_uuid)
        if not client_profile or project.client_id != client_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to cancel this project",
            )

        return await project_service.cancel_project(project_uuid)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
