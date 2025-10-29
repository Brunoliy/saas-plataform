"""Authentication service."""

from app.core.exceptions import AuthenticationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.models.user import AccountType
from app.repositories.client_repository import ClientRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token, UserLogin
from app.schemas.client import ClientProfileCreate
from app.schemas.professional import ProfessionalProfileCreate
from app.schemas.user import UserCreate


class AuthService:
    """Authentication service class."""

    def __init__(
        self,
        user_repository: UserRepository,
        client_repository: ClientRepository,
        professional_repository: ProfessionalRepository,
    ):
        """Initialize service."""
        self.user_repository = user_repository
        self.client_repository = client_repository
        self.professional_repository = professional_repository

    async def register(self, user_data: UserCreate) -> Token:
        """Register a new user."""
        # Check if user already exists
        existing_user = self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise AuthenticationError("User already exists")

        # Hash password and create user
        user_data.password = get_password_hash(user_data.password)
        user = self.user_repository.create(user_data)

        # Auto-create profile based on account type
        account_type = (
            user.account_type.value
            if hasattr(user.account_type, "value")
            else user.account_type
        )

        if account_type == AccountType.PROFESSIONAL:
            # Create professional profile with default title
            professional_data = ProfessionalProfileCreate(
                title=f"{user.full_name}",
                description=None,
                bio=None,
                hourly_rate=None,
                skills=[],
            )
            self.professional_repository.create(user.id, professional_data)  # type: ignore[arg-type]
        elif account_type == AccountType.COMPANY:
            # Create client profile with default company name
            client_data = ClientProfileCreate(
                company_name=user.full_name,  # type: ignore[arg-type]
                business_sector=None,
                description=None,
                bio=None,
            )
            self.client_repository.create(user.id, client_data)  # type: ignore[arg-type]

        # Create tokens
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "account_type": account_type,
        }
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60,  # 30 minutes
        )

    async def login(self, credentials: UserLogin) -> Token:
        """Login user."""
        user = self.user_repository.get_by_email(credentials.email)
        if not user or not verify_password(credentials.password, user.password_hash):  # type: ignore[arg-type]
            raise AuthenticationError("Invalid credentials")

        if not user.active:
            raise AuthenticationError("Account is disabled")

        # Create tokens
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "account_type": user.account_type.value
            if hasattr(user.account_type, "value")
            else user.account_type,
        }
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60,  # 30 minutes
        )

    async def refresh_token(self, refresh_token: str) -> Token:
        """Refresh access token using refresh token."""
        from app.core.security import verify_token

        # Verify refresh token
        token_data = verify_token(refresh_token, token_type="refresh")

        # Get user to ensure they still exist and are active
        user = self.user_repository.get_by_email(token_data.email)  # type: ignore[arg-type]
        if not user:
            raise AuthenticationError("User not found")

        if not user.active:
            raise AuthenticationError("Account is disabled")

        # Create new tokens
        new_token_data = {
            "sub": str(user.id),
            "email": user.email,
            "account_type": user.account_type.value
            if hasattr(user.account_type, "value")
            else user.account_type,
        }
        access_token = create_access_token(data=new_token_data)
        new_refresh_token = create_refresh_token(data=new_token_data)

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=30 * 60,  # 30 minutes
        )
