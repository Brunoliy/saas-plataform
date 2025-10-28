"""Professional endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.database.session import get_db
from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.skill_repository import SkillRepository
from app.schemas.common import PaginatedResponse
from app.schemas.professional import (
    ProfessionalProfileCreate,
    ProfessionalProfileResponse,
    ProfessionalProfileUpdate,
    ProfessionalSkillCreate,
    ProfessionalSkillResponse,
)
from app.services.professional_service import ProfessionalService

router = APIRouter()


def get_professional_service(db: Session = Depends(get_db)) -> ProfessionalService:
    """Get professional service dependency."""
    professional_repository = ProfessionalRepository(db)
    skill_repository = SkillRepository(db)
    return ProfessionalService(professional_repository, skill_repository)


@router.post(
    "/", response_model=ProfessionalProfileResponse, status_code=status.HTTP_201_CREATED
)
async def create_professional_profile(
    profile_data: ProfessionalProfileCreate,
    current_user_id: str = Depends(get_current_user_id),
    professional_service: ProfessionalService = Depends(get_professional_service),
):
    """Create a new professional profile."""
    try:
        user_uuid = UUID(current_user_id)
        return await professional_service.create_profile(user_uuid, profile_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=PaginatedResponse[ProfessionalProfileResponse])
async def list_professionals(
    skip: int = 0,
    limit: int = 20,
    professional_service: ProfessionalService = Depends(get_professional_service),
):
    """List professionals with pagination (public endpoint)."""
    professionals = await professional_service.list_professionals(
        skip=skip, limit=limit
    )
    total = await professional_service.count_professionals()

    pages = (total + limit - 1) // limit if limit > 0 else 1
    current_page = (skip // limit) + 1 if limit > 0 else 1

    return PaginatedResponse(
        items=professionals, total=total, page=current_page, size=limit, pages=pages
    )


@router.get("/me", response_model=ProfessionalProfileResponse)
async def get_my_professional_profile(
    current_user_id: str = Depends(get_current_user_id),
    professional_service: ProfessionalService = Depends(get_professional_service),
):
    """Get current user's professional profile."""
    try:
        user_uuid = UUID(current_user_id)
        profile = await professional_service.get_profile_by_user_id(user_uuid)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Professional profile not found",
            )
        return profile
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format"
        )


@router.put("/me", response_model=ProfessionalProfileResponse)
async def update_my_professional_profile(
    profile_update: ProfessionalProfileUpdate,
    current_user_id: str = Depends(get_current_user_id),
    professional_service: ProfessionalService = Depends(get_professional_service),
):
    """Update current user's professional profile."""
    try:
        user_uuid = UUID(current_user_id)
        profile = await professional_service.get_profile_by_user_id(user_uuid)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Professional profile not found",
            )
        return await professional_service.update_profile(profile.id, profile_update)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format"
        )


@router.get("/{professional_id}", response_model=ProfessionalProfileResponse)
async def get_professional(
    professional_id: str,
    professional_service: ProfessionalService = Depends(get_professional_service),
):
    """Get professional by ID (public endpoint)."""
    try:
        profile_uuid = UUID(professional_id)
        profile = await professional_service.get_profile_by_id(profile_uuid)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Professional profile not found",
            )
        return profile
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid professional ID format",
        )


@router.delete("/{professional_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_professional_profile(
    professional_id: str,
    current_user_id: str = Depends(get_current_user_id),
    professional_service: ProfessionalService = Depends(get_professional_service),
):
    """Delete professional profile (only owner can delete)."""
    try:
        profile_uuid = UUID(professional_id)
        user_uuid = UUID(current_user_id)

        # Verify ownership
        profile = await professional_service.get_profile_by_id(profile_uuid)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Professional profile not found",
            )

        if profile.user_id != user_uuid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this profile",
            )

        await professional_service.delete_profile(profile_uuid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format"
        )


@router.post(
    "/{professional_id}/skills",
    response_model=ProfessionalSkillResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_skill_to_professional(
    professional_id: str,
    skill_data: ProfessionalSkillCreate,
    current_user_id: str = Depends(get_current_user_id),
    professional_service: ProfessionalService = Depends(get_professional_service),
):
    """Add a skill to professional profile."""
    try:
        profile_uuid = UUID(professional_id)
        user_uuid = UUID(current_user_id)

        # Verify ownership
        profile = await professional_service.get_profile_by_id(profile_uuid)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Professional profile not found",
            )

        if profile.user_id != user_uuid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to modify this profile",
            )

        return await professional_service.add_skill(profile_uuid, skill_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{professional_id}/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_skill_from_professional(
    professional_id: str,
    skill_id: str,
    current_user_id: str = Depends(get_current_user_id),
    professional_service: ProfessionalService = Depends(get_professional_service),
):
    """Remove a skill from professional profile."""
    try:
        profile_uuid = UUID(professional_id)
        skill_uuid = UUID(skill_id)
        user_uuid = UUID(current_user_id)

        # Verify ownership
        profile = await professional_service.get_profile_by_id(profile_uuid)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Professional profile not found",
            )

        if profile.user_id != user_uuid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to modify this profile",
            )

        success = await professional_service.remove_skill(profile_uuid, skill_uuid)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skill not found in professional profile",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format"
        )
