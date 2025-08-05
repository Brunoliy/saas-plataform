"""Client service."""

from app.repositories.client_repository import ClientRepository


class ClientService:
    """Client service class."""
    
    def __init__(self, client_repository: ClientRepository):
        """Initialize service."""
        self.client_repository = client_repository