"""Professional endpoints."""

from fastapi import APIRouter, Depends

from app.schemas.common import PaginatedResponse
from app.security import require_any_user

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_professionals(
    skip: int = 0,
    limit: int = 20,
    current_user_id: str = Depends(require_any_user)
):
    """List professionals with pagination."""
    # TODO: Implement actual professional listing logic
    return PaginatedResponse(
        items=[],
        total=0,
        page=skip // limit + 1,
        size=limit,
        pages=0
    )


@router.get("/{professional_id}")
async def get_professional(
    professional_id: str,
    current_user_id: str = Depends(require_any_user)
):
    """Get professional by ID."""
    # TODO: Implement actual professional retrieval logic
    return {"message": f"Professional {professional_id} details"} 