"""Review endpoints."""

from fastapi import APIRouter, Depends

from app.schemas.common import PaginatedResponse
from app.core.security import require_any_user

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_reviews(
    skip: int = 0,
    limit: int = 20,
    current_user_id: str = Depends(require_any_user)
):
    """List reviews with pagination."""
    # TODO: Implement actual review listing logic
    return PaginatedResponse(
        items=[],
        total=0,
        page=skip // limit + 1,
        size=limit,
        pages=0
    )


@router.get("/{review_id}")
async def get_review(
    review_id: str,
    current_user_id: str = Depends(require_any_user)
):
    """Get review by ID."""
    # TODO: Implement actual review retrieval logic
    return {"message": f"Review {review_id} details"}


@router.post("/")
async def create_review(current_user_id: str = Depends(require_any_user)):
    """Create a new review."""
    # TODO: Implement actual review creation logic
    return {"message": "Review created successfully"}


@router.put("/{review_id}")
async def update_review(
    review_id: str,
    current_user_id: str = Depends(require_any_user)
):
    """Update review."""
    # TODO: Implement actual review update logic
    return {"message": f"Review {review_id} updated successfully"}


@router.delete("/{review_id}")
async def delete_review(
    review_id: str,
    current_user_id: str = Depends(require_any_user)
):
    """Delete review."""
    # TODO: Implement actual review deletion logic
    return {"message": f"Review {review_id} deleted successfully"} 