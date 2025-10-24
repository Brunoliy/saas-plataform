"""Skill endpoints."""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.skill import SkillCreate, SkillUpdate, SkillResponse
from app.schemas.common import PaginatedResponse
from app.core.security import get_current_user_id
from app.database.session import get_db
from app.services.skill_service import SkillService
from app.repositories.skill_repository import SkillRepository

router = APIRouter()


def get_skill_service(db: Session = Depends(get_db)) -> SkillService:
    """Get skill service dependency."""
    skill_repository = SkillRepository(db)
    return SkillService(skill_repository)


@router.post("/", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill_data: SkillCreate,
    current_user_id: str = Depends(get_current_user_id),
    skill_service: SkillService = Depends(get_skill_service)
):
    """Create a new skill (authenticated users only)."""
    try:
        return await skill_service.create_skill(skill_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=PaginatedResponse[SkillResponse])
async def list_skills(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    search: Optional[str] = None,
    only_active: bool = True,
    skill_service: SkillService = Depends(get_skill_service)
):
    """List skills with pagination and filters (public endpoint)."""
    try:
        if search:
            skills = await skill_service.search_skills(search, skip=skip, limit=limit)
        elif category:
            skills = await skill_service.get_skills_by_category(category, skip=skip, limit=limit)
        elif only_active:
            skills = await skill_service.get_active_skills(skip=skip, limit=limit)
        else:
            skills = await skill_service.list_skills(skip=skip, limit=limit)

        total = await skill_service.count_skills()

        pages = (total + limit - 1) // limit if limit > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1

        return PaginatedResponse(
            items=skills,
            total=total,
            page=current_page,
            size=limit,
            pages=pages
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid parameters")


@router.get("/categories", response_model=List[str])
async def get_skill_categories(
    skill_service: SkillService = Depends(get_skill_service)
):
    """Get all skill categories (public endpoint)."""
    return await skill_service.get_categories()


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(
    skill_id: str,
    skill_service: SkillService = Depends(get_skill_service)
):
    """Get skill by ID (public endpoint)."""
    try:
        skill_uuid = UUID(skill_id)
        skill = await skill_service.get_skill_by_id(skill_uuid)
        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skill not found"
            )
        return skill
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid skill ID format")


@router.put("/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: str,
    skill_update: SkillUpdate,
    current_user_id: str = Depends(get_current_user_id),
    skill_service: SkillService = Depends(get_skill_service)
):
    """Update skill (authenticated users only)."""
    try:
        skill_uuid = UUID(skill_id)

        # Verify skill exists
        skill = await skill_service.get_skill_by_id(skill_uuid)
        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skill not found"
            )

        return await skill_service.update_skill(skill_uuid, skill_update)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: str,
    current_user_id: str = Depends(get_current_user_id),
    skill_service: SkillService = Depends(get_skill_service)
):
    """Delete skill (authenticated users only)."""
    try:
        skill_uuid = UUID(skill_id)

        # Verify skill exists
        skill = await skill_service.get_skill_by_id(skill_uuid)
        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skill not found"
            )

        await skill_service.delete_skill(skill_uuid)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")


@router.patch("/{skill_id}/activate", response_model=SkillResponse)
async def activate_skill(
    skill_id: str,
    current_user_id: str = Depends(get_current_user_id),
    skill_service: SkillService = Depends(get_skill_service)
):
    """Activate skill (authenticated users only)."""
    try:
        skill_uuid = UUID(skill_id)
        return await skill_service.activate_skill(skill_uuid)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{skill_id}/deactivate", response_model=SkillResponse)
async def deactivate_skill(
    skill_id: str,
    current_user_id: str = Depends(get_current_user_id),
    skill_service: SkillService = Depends(get_skill_service)
):
    """Deactivate skill (authenticated users only)."""
    try:
        skill_uuid = UUID(skill_id)
        return await skill_service.deactivate_skill(skill_uuid)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) 