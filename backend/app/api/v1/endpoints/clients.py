"""Client endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from app.core.security import get_current_user_id
from app.database.session import get_db
from app.repositories.client_repository import ClientRepository
from app.schemas.client import (
    ClientProfileCreate,
    ClientProfileResponse,
    ClientProfileUpdate,
)
from app.schemas.common import PaginatedResponse
from app.services.client_service import ClientService

router = APIRouter()


def get_client_service(db: Session = Depends(get_db)) -> ClientService:
    """Get client service dependency."""
    client_repository = ClientRepository(db)
    return ClientService(client_repository)


@router.post(
    "/", response_model=ClientProfileResponse, status_code=status.HTTP_201_CREATED
)
async def create_client_profile(
    profile_data: ClientProfileCreate,
    current_user_id: str = Depends(get_current_user_id),
    client_service: ClientService = Depends(get_client_service),
) -> ClientProfileResponse:
    """Create a new client profile."""
    try:
        user_uuid = UUID(current_user_id)
        return await client_service.create_profile(user_uuid, profile_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=PaginatedResponse[ClientProfileResponse])
async def list_clients(
    skip: int = 0,
    limit: int = 20,
    business_sector: Optional[str] = None,
    client_service: ClientService = Depends(get_client_service),
) -> PaginatedResponse[ClientProfileResponse]:
    """List clients with pagination (public endpoint)."""
    if business_sector:
        clients = await client_service.get_clients_by_sector(
            business_sector, skip=skip, limit=limit
        )
    else:
        clients = await client_service.list_clients(skip=skip, limit=limit)

    total = await client_service.count_clients()

    pages = (total + limit - 1) // limit if limit > 0 else 1
    current_page = (skip // limit) + 1 if limit > 0 else 1

    return PaginatedResponse(
        items=clients, total=total, page=current_page, size=limit, pages=pages
    )


@router.get("/me", response_model=ClientProfileResponse)
async def get_my_client_profile(
    current_user_id: str = Depends(get_current_user_id),
    client_service: ClientService = Depends(get_client_service),
) -> ClientProfileResponse:
    """Get current user's client profile."""
    try:
        user_uuid = UUID(current_user_id)
        profile = await client_service.get_profile_by_user_id(user_uuid)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Client profile not found"
            )
        return profile
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format"
        )


@router.put("/me", response_model=ClientProfileResponse)
async def update_my_client_profile(
    profile_update: ClientProfileUpdate,
    current_user_id: str = Depends(get_current_user_id),
    client_service: ClientService = Depends(get_client_service),
) -> ClientProfileResponse:
    """Update current user's client profile."""
    try:
        user_uuid = UUID(current_user_id)
        profile = await client_service.get_profile_by_user_id(user_uuid)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Client profile not found"
            )
        return await client_service.update_profile(profile.id, profile_update)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format"
        )


@router.get("/{client_id}", response_model=ClientProfileResponse)
async def get_client(
    client_id: str, client_service: ClientService = Depends(get_client_service)
) -> ClientProfileResponse:
    """Get client by ID (public endpoint)."""
    try:
        client_uuid = UUID(client_id)
        profile = await client_service.get_profile_by_id(client_uuid)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Client profile not found"
            )
        return profile
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid client ID format"
        )


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client_profile(
    client_id: str,
    current_user_id: str = Depends(get_current_user_id),
    client_service: ClientService = Depends(get_client_service),
) -> None:
    """Delete client profile (only owner can delete)."""
    try:
        profile_uuid = UUID(client_id)
        user_uuid = UUID(current_user_id)

        # Verify ownership
        profile = await client_service.get_profile_by_id(profile_uuid)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Client profile not found"
            )

        if profile.user_id != user_uuid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this profile",
            )

        await client_service.delete_profile(profile_uuid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format"
        )
