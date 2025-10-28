"""Review service."""

from typing import Optional
from uuid import UUID

from app.models.project import ProjectStatus
from app.models.review import Review, ReviewType
from app.repositories.client_repository import ClientRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.user_repository import UserRepository
from app.schemas.review import ReviewCreate, ReviewUpdate


class ReviewService:
    """Review service class."""

    def __init__(
        self,
        review_repository: ReviewRepository,
        project_repository: ProjectRepository,
        user_repository: UserRepository,
        professional_repository: ProfessionalRepository = None,
        client_repository: ClientRepository = None,
    ):
        """Initialize service."""
        self.review_repository = review_repository
        self.project_repository = project_repository
        self.user_repository = user_repository
        self.professional_repository = professional_repository
        self.client_repository = client_repository

    async def create_review(
        self, reviewer_id: UUID, review_data: ReviewCreate
    ) -> Review:
        """Create a new review."""
        # Verify reviewer exists
        reviewer = self.user_repository.get_by_id(reviewer_id)
        if not reviewer:
            raise ValueError("Reviewer not found")

        # Verify reviewed user exists
        reviewed_user = self.user_repository.get_by_id(review_data.reviewed_id)
        if not reviewed_user:
            raise ValueError("Reviewed user not found")

        # Verify project exists
        project = self.project_repository.get_by_id(review_data.project_id)
        if not project:
            raise ValueError("Project not found")

        # Verify project is completed
        if project.status != ProjectStatus.COMPLETED:
            raise ValueError(
                f"Cannot review project that is not completed. Current status: {project.status}"
            )

        # Verify reviewer is part of the project
        if (
            reviewer_id != project.client_id
            and reviewer_id != project.selected_professional_id
        ):
            raise ValueError("You can only review projects you are part of")

        # Verify reviewer hasn't already reviewed this project
        existing_review = self.review_repository.get_review_by_project_and_reviewer(
            review_data.project_id, reviewer_id
        )
        if existing_review:
            raise ValueError("You have already reviewed this project")

        # Validate review type matches project roles
        if review_data.review_type == ReviewType.CLIENT_TO_PROFESSIONAL:
            if reviewer_id != project.client_id:
                raise ValueError("Only the client can review the professional")
            if review_data.reviewed_id != project.selected_professional_id:
                raise ValueError(
                    "You can only review the professional assigned to this project"
                )
        elif review_data.review_type == ReviewType.PROFESSIONAL_TO_CLIENT:
            if reviewer_id != project.selected_professional_id:
                raise ValueError("Only the professional can review the client")
            if review_data.reviewed_id != project.client_id:
                raise ValueError("You can only review the client of this project")

        # Create review
        review = self.review_repository.create(reviewer_id, review_data)

        # Update rating for the reviewed user's profile
        await self._update_user_rating(review_data.reviewed_id)

        return review

    async def _update_user_rating(self, user_id: UUID):
        """Update user's rating based on their reviews."""
        average_rating = self.review_repository.get_average_rating_for_user(user_id)
        total_reviews = self.review_repository.count_reviews_for_user(user_id)

        if average_rating is None:
            return

        # Update professional or client profile
        if self.professional_repository:
            professional = self.professional_repository.get_by_user_id(user_id)
            if professional:
                self.professional_repository.update_rating(
                    professional.id, average_rating, total_reviews
                )

        if self.client_repository:
            client = self.client_repository.get_by_user_id(user_id)
            if client:
                self.client_repository.update_rating(
                    client.id, average_rating, total_reviews
                )

    async def get_review_by_id(self, review_id: UUID) -> Optional[Review]:
        """Get review by ID."""
        return self.review_repository.get_by_id(review_id)

    async def update_review(
        self, review_id: UUID, review_data: ReviewUpdate
    ) -> Optional[Review]:
        """Update review."""
        review = self.review_repository.update(review_id, review_data)

        if review:
            # Update rating for the reviewed user
            await self._update_user_rating(review.reviewed_id)

        return review

    async def delete_review(self, review_id: UUID) -> bool:
        """Delete review."""
        review = self.review_repository.get_by_id(review_id)
        if not review:
            raise ValueError("Review not found")

        deleted = self.review_repository.delete(review_id)

        if deleted:
            # Update rating for the reviewed user
            await self._update_user_rating(review.reviewed_id)

        return deleted

    async def list_reviews(self, skip: int = 0, limit: int = 20) -> list[Review]:
        """List reviews."""
        return self.review_repository.list_reviews(skip=skip, limit=limit)

    async def count_reviews(self) -> int:
        """Count total reviews."""
        return self.review_repository.count_reviews()

    async def get_reviews_by_project(
        self, project_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[Review]:
        """Get reviews by project ID."""
        return self.review_repository.get_reviews_by_project(
            project_id, skip=skip, limit=limit
        )

    async def get_reviews_by_reviewer(
        self, reviewer_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[Review]:
        """Get reviews by reviewer ID."""
        return self.review_repository.get_reviews_by_reviewer(
            reviewer_id, skip=skip, limit=limit
        )

    async def get_reviews_by_reviewed(
        self, reviewed_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[Review]:
        """Get reviews by reviewed user ID."""
        return self.review_repository.get_reviews_by_reviewed(
            reviewed_id, skip=skip, limit=limit
        )

    async def get_reviews_by_type(
        self, review_type: ReviewType, skip: int = 0, limit: int = 20
    ) -> list[Review]:
        """Get reviews by type."""
        return self.review_repository.get_reviews_by_type(
            review_type, skip=skip, limit=limit
        )

    async def get_average_rating_for_user(self, user_id: UUID) -> Optional[float]:
        """Get average rating for a user."""
        return self.review_repository.get_average_rating_for_user(user_id)
