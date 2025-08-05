"""User service."""

from app.repositories.user_repository import UserRepository


class UserService:
    """User service class."""
    
    def __init__(self, user_repository: UserRepository):
        """Initialize service."""
        self.user_repository = user_repository