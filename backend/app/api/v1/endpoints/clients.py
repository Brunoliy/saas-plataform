"""Client endpoints."""

from fastapi import APIRouter, Depends

from app.schemas.common import PaginatedResponse
from app.security import require_any_user

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_clients(
    skip: int = 0,
    limit: int = 20,
    current_user_id: str = Depends(require_any_user)
):
    """List clients with pagination."""
    # TODO: Implement actual client listing logic
    return PaginatedResponse(
        items=[],
        total=0,
        page=skip // limit + 1,
        size=limit,
        pages=0
    )


@router.get("/{client_id}")
async def get_client(
    client_id: str,
    current_user_id: str = Depends(require_any_user)
):
    """Get client by ID."""
    # TODO: Implement actual client retrieval logic
    return {"message": f"Client {client_id} details"} 