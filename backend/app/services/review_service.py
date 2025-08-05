"""Review service."""

from app.repositories.review_repository import ReviewRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository


class ReviewService:
    """Review service class."""
    
    def __init__(self, review_repository: ReviewRepository, project_repository: ProjectRepository, user_repository: UserRepository):
        """Initialize service."""
        self.review_repository = review_repository
        self.project_repository = project_repository
        self.user_repository = user_repository