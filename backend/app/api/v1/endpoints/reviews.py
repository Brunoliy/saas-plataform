"""Review endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.database.session import get_db
from app.repositories.client_repository import ClientRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.user_repository import UserRepository
from app.schemas.common import PaginatedResponse
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewType, ReviewUpdate
from app.services.review_service import ReviewService

router = APIRouter()


def get_review_service(db: Session = Depends(get_db)) -> ReviewService:
    """Get review service dependency."""
    review_repository = ReviewRepository(db)
    project_repository = ProjectRepository(db)
    user_repository = UserRepository(db)
    professional_repository = ProfessionalRepository(db)
    client_repository = ClientRepository(db)
    return ReviewService(
        review_repository,
        project_repository,
        user_repository,
        professional_repository,
        client_repository,
    )


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user_id: str = Depends(get_current_user_id),
    review_service: ReviewService = Depends(get_review_service),
):
    """Create a new review (authenticated users only)."""
    try:
        user_uuid = UUID(current_user_id)
        return await review_service.create_review(user_uuid, review_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=PaginatedResponse[ReviewResponse])
async def list_reviews(
    skip: int = 0,
    limit: int = 20,
    project_id: Optional[str] = None,
    reviewer_id: Optional[str] = None,
    reviewed_id: Optional[str] = None,
    review_type: Optional[ReviewType] = None,
    review_service: ReviewService = Depends(get_review_service),
):
    """List reviews with pagination and filters (public endpoint)."""
    try:
        if project_id:
            project_uuid = UUID(project_id)
            reviews = await review_service.get_reviews_by_project(
                project_uuid, skip=skip, limit=limit
            )
        elif reviewer_id:
            reviewer_uuid = UUID(reviewer_id)
            reviews = await review_service.get_reviews_by_reviewer(
                reviewer_uuid, skip=skip, limit=limit
            )
        elif reviewed_id:
            reviewed_uuid = UUID(reviewed_id)
            reviews = await review_service.get_reviews_by_reviewed(
                reviewed_uuid, skip=skip, limit=limit
            )
        elif review_type:
            reviews = await review_service.get_reviews_by_type(
                review_type, skip=skip, limit=limit
            )
        else:
            reviews = await review_service.list_reviews(skip=skip, limit=limit)

        total = await review_service.count_reviews()

        pages = (total + limit - 1) // limit if limit > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1

        return PaginatedResponse(
            items=reviews, total=total, page=current_page, size=limit, pages=pages
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format"
        )


@router.get("/users/{user_id}/rating")
async def get_user_rating(
    user_id: str, review_service: ReviewService = Depends(get_review_service)
):
    """Get average rating for a user (public endpoint)."""
    try:
        user_uuid = UUID(user_id)
        average_rating = await review_service.get_average_rating_for_user(user_uuid)
        if average_rating is None:
            return {"user_id": user_id, "average_rating": 0.0, "total_reviews": 0}
        return {"user_id": user_id, "average_rating": average_rating}
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format"
        )


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: str, review_service: ReviewService = Depends(get_review_service)
):
    """Get review by ID (public endpoint)."""
    try:
        review_uuid = UUID(review_id)
        review = await review_service.get_review_by_id(review_uuid)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
            )
        return review
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid review ID format"
        )


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: str,
    review_update: ReviewUpdate,
    current_user_id: str = Depends(get_current_user_id),
    review_service: ReviewService = Depends(get_review_service),
):
    """Update review (only reviewer can update)."""
    try:
        review_uuid = UUID(review_id)
        user_uuid = UUID(current_user_id)

        # Verify review exists
        review = await review_service.get_review_by_id(review_uuid)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
            )

        # Verify ownership
        if review.reviewer_id != user_uuid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this review",
            )

        return await review_service.update_review(review_uuid, review_update)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: str,
    current_user_id: str = Depends(get_current_user_id),
    review_service: ReviewService = Depends(get_review_service),
):
    """Delete review (only reviewer can delete)."""
    try:
        review_uuid = UUID(review_id)
        user_uuid = UUID(current_user_id)

        # Verify review exists
        review = await review_service.get_review_by_id(review_uuid)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
            )

        # Verify ownership
        if review.reviewer_id != user_uuid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this review",
            )

        await review_service.delete_review(review_uuid)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
