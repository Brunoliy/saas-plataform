"""Review repository for database operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.review import Review, ReviewType
from app.schemas.review import ReviewCreate, ReviewUpdate


class ReviewRepository:
    """Review repository class."""

    def __init__(self, db: Session):
        """Initialize repository."""
        self.db = db

    def create(self, reviewer_id: UUID, review_data: ReviewCreate) -> Review:
        """Create a new review."""
        db_review = Review(
            project_id=review_data.project_id,
            reviewer_id=reviewer_id,
            reviewed_id=review_data.reviewed_id,
            rating=review_data.rating,
            comment=review_data.comment,
            review_type=review_data.review_type,
        )

        self.db.add(db_review)
        self.db.commit()
        self.db.refresh(db_review)
        return db_review

    def get_by_id(self, review_id: UUID) -> Optional[Review]:
        """Get review by ID (only non-deleted reviews)."""
        return (
            self.db.query(Review)
            .filter(and_(Review.id == review_id, Review.deleted_at.is_(None)))
            .first()
        )

    def update(self, review_id: UUID, review_data: ReviewUpdate) -> Optional[Review]:
        """Update review."""
        db_review = self.get_by_id(review_id)
        if not db_review:
            return None

        update_data = review_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_review, field, value)

        self.db.commit()
        self.db.refresh(db_review)
        return db_review

    def delete(self, review_id: UUID) -> bool:
        """Soft delete review."""
        db_review = self.get_by_id(review_id)
        if not db_review:
            return False

        db_review.soft_delete()
        self.db.commit()
        return True

    def list_reviews(
        self, skip: int = 0, limit: int = 20, include_deleted: bool = False
    ) -> list[Review]:
        """List reviews with pagination."""
        query = self.db.query(Review)

        if not include_deleted:
            query = query.filter(Review.deleted_at.is_(None))

        return query.offset(skip).limit(limit).all()

    def count_reviews(self, include_deleted: bool = False) -> int:
        """Count total reviews."""
        query = self.db.query(Review)

        if not include_deleted:
            query = query.filter(Review.deleted_at.is_(None))

        return query.count()

    def get_reviews_by_project(
        self, project_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[Review]:
        """Get reviews by project ID."""
        return (
            self.db.query(Review)
            .filter(and_(Review.project_id == project_id, Review.deleted_at.is_(None)))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_reviews_by_reviewer(
        self, reviewer_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[Review]:
        """Get reviews by reviewer ID."""
        return (
            self.db.query(Review)
            .filter(
                and_(Review.reviewer_id == reviewer_id, Review.deleted_at.is_(None))
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_reviews_by_reviewed(
        self, reviewed_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[Review]:
        """Get reviews by reviewed user ID."""
        return (
            self.db.query(Review)
            .filter(
                and_(Review.reviewed_id == reviewed_id, Review.deleted_at.is_(None))
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_reviews_by_type(
        self, review_type: ReviewType, skip: int = 0, limit: int = 20
    ) -> list[Review]:
        """Get reviews by type."""
        return (
            self.db.query(Review)
            .filter(
                and_(Review.review_type == review_type, Review.deleted_at.is_(None))
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_average_rating_for_user(self, user_id: UUID) -> Optional[float]:
        """Get average rating for a user."""
        from sqlalchemy import func

        result = (
            self.db.query(func.avg(Review.rating))
            .filter(and_(Review.reviewed_id == user_id, Review.deleted_at.is_(None)))
            .scalar()
        )

        return float(result) if result else None

    def count_reviews_for_user(self, user_id: UUID) -> int:
        """Count reviews for a user."""
        return (
            self.db.query(Review)
            .filter(and_(Review.reviewed_id == user_id, Review.deleted_at.is_(None)))
            .count()
        )

    def get_review_by_project_and_reviewer(
        self, project_id: UUID, reviewer_id: UUID
    ) -> Optional[Review]:
        """Get review by project and reviewer."""
        return (
            self.db.query(Review)
            .filter(
                and_(
                    Review.project_id == project_id,
                    Review.reviewer_id == reviewer_id,
                    Review.deleted_at.is_(None),
                )
            )
            .first()
        )
