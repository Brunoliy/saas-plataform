"""Client service."""

from typing import Optional
from uuid import UUID

from app.models.client import ClientLink, ClientProfile
from app.repositories.client_repository import ClientRepository
from app.schemas.client import (
    ClientLinkCreate,
    ClientLinkUpdate,
    ClientProfileCreate,
    ClientProfileUpdate,
)


class ClientService:
    """Client service class."""

    def __init__(self, client_repository: ClientRepository):
        """Initialize service."""
        self.client_repository = client_repository

    async def create_profile(
        self, user_id: UUID, profile_data: ClientProfileCreate
    ) -> ClientProfile:
        """Create a new client profile."""
        # Check if profile already exists
        existing_profile = self.client_repository.get_by_user_id(user_id)
        if existing_profile:
            raise ValueError("Client profile already exists for this user")

        # Create profile
        return self.client_repository.create(user_id, profile_data)

    async def get_profile_by_id(self, profile_id: UUID) -> Optional[ClientProfile]:
        """Get client profile by ID."""
        return self.client_repository.get_by_id(profile_id)

    async def get_profile_by_user_id(self, user_id: UUID) -> Optional[ClientProfile]:
        """Get client profile by user ID."""
        return self.client_repository.get_by_user_id(user_id)

    async def update_profile(
        self, profile_id: UUID, profile_data: ClientProfileUpdate
    ) -> Optional[ClientProfile]:
        """Update client profile."""
        return self.client_repository.update(profile_id, profile_data)

    async def delete_profile(self, profile_id: UUID) -> bool:
        """Delete client profile."""
        return self.client_repository.delete(profile_id)

    async def list_clients(self, skip: int = 0, limit: int = 20) -> list[ClientProfile]:
        """List client profiles."""
        return self.client_repository.list_clients(skip=skip, limit=limit)

    async def count_clients(self) -> int:
        """Count total client profiles."""
        return self.client_repository.count_clients()

    async def get_clients_by_sector(
        self, business_sector: str, skip: int = 0, limit: int = 20
    ) -> list[ClientProfile]:
        """Get clients by business sector."""
        return self.client_repository.get_clients_by_sector(
            business_sector, skip=skip, limit=limit
        )

    async def update_rating(
        self, profile_id: UUID, average_rating: float, total_reviews: int
    ) -> Optional[ClientProfile]:
        """Update client rating."""
        return self.client_repository.update_rating(
            profile_id, average_rating, total_reviews
        )

    async def add_link(
        self, client_id: UUID, link_data: ClientLinkCreate
    ) -> ClientLink:
        """Add a social link to client profile."""
        return self.client_repository.add_link(client_id, link_data)

    async def update_link(
        self, link_id: UUID, link_update: ClientLinkUpdate
    ) -> Optional[ClientLink]:
        """Update a social link."""
        return self.client_repository.update_link(link_id, link_update)

    async def remove_link(self, client_id: UUID, link_id: UUID) -> bool:
        """Remove a social link from client profile."""
        return self.client_repository.remove_link(client_id, link_id)
