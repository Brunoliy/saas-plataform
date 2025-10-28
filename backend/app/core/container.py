"""Dependency injection container configuration."""

from dependency_injector import containers, providers

from app.repositories.ai_repository import AIRepository
from app.repositories.client_repository import ClientRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.proposal_repository import ProposalRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.skill_repository import SkillRepository
from app.repositories.user_repository import UserRepository
from app.services.ai_service import AIService
from app.services.auth_service import AuthService
from app.services.client_service import ClientService
from app.services.kafka_service import KafkaService
from app.services.professional_service import ProfessionalService
from app.services.project_service import ProjectService
from app.services.proposal_service import ProposalService
from app.services.review_service import ReviewService
from app.services.skill_service import SkillService
from app.services.user_service import UserService


class Container(containers.DeclarativeContainer):
    """Application container."""

    # Configuration
    config = providers.Configuration()

    # Repositories
    user_repository = providers.Factory(UserRepository)
    professional_repository = providers.Factory(ProfessionalRepository)
    client_repository = providers.Factory(ClientRepository)
    project_repository = providers.Factory(ProjectRepository)
    proposal_repository = providers.Factory(ProposalRepository)
    review_repository = providers.Factory(ReviewRepository)
    skill_repository = providers.Factory(SkillRepository)
    ai_repository = providers.Factory(AIRepository)

    # Services
    auth_service = providers.Factory(
        AuthService,
        user_repository=user_repository,
    )

    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
    )

    professional_service = providers.Factory(
        ProfessionalService,
        professional_repository=professional_repository,
        skill_repository=skill_repository,
    )

    client_service = providers.Factory(
        ClientService,
        client_repository=client_repository,
    )

    project_service = providers.Factory(
        ProjectService,
        project_repository=project_repository,
        client_repository=client_repository,
        professional_repository=professional_repository,
    )

    proposal_service = providers.Factory(
        ProposalService,
        proposal_repository=proposal_repository,
        project_repository=project_repository,
        professional_repository=professional_repository,
    )

    review_service = providers.Factory(
        ReviewService,
        review_repository=review_repository,
        project_repository=project_repository,
        user_repository=user_repository,
    )

    skill_service = providers.Factory(
        SkillService,
        skill_repository=skill_repository,
    )

    ai_service = providers.Factory(
        AIService,
        ai_repository=ai_repository,
        project_repository=project_repository,
        professional_repository=professional_repository,
    )

    kafka_service = providers.Factory(KafkaService)


# Global container instance
container = Container()
