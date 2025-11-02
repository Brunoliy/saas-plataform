"""Factories for testing using factory_boy and faker."""

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal, FuzzyInteger
from faker import Faker
from sqlalchemy.orm import Session

from app.models.client import ClientProfile
from app.models.professional import ProfessionalProfile
from app.models.project import Project, ProjectStatus
from app.models.proposal import Proposal, ProposalStatus
from app.models.review import Review, ReviewType
from app.models.skill import Skill
from app.models.user import AccountType, User

fake = Faker()


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for User model."""

    class Meta:
        model = User
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    email = factory.LazyAttribute(lambda _: fake.email())
    password_hash = factory.LazyAttribute(lambda _: fake.password())
    full_name = factory.LazyAttribute(lambda _: fake.name())
    phone = factory.LazyAttribute(lambda _: fake.phone_number())
    account_type = FuzzyChoice([AccountType.PROFESSIONAL, AccountType.COMPANY])
    active = True


class ProfessionalProfileFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for ProfessionalProfile model."""

    class Meta:
        model = ProfessionalProfile
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    user = factory.SubFactory(UserFactory, account_type=AccountType.PROFESSIONAL)
    title = factory.LazyAttribute(lambda _: fake.job())
    description = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=200))
    bio = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=300))
    hourly_rate = FuzzyDecimal(50.0, 500.0, precision=2)
    average_rating = None
    total_reviews = 0


class ClientProfileFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for ClientProfile model."""

    class Meta:
        model = ClientProfile
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    user = factory.SubFactory(UserFactory, account_type=AccountType.COMPANY)
    company_name = factory.LazyAttribute(lambda _: fake.company())
    business_sector = factory.LazyAttribute(lambda _: fake.bs())
    description = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=200))
    bio = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=300))
    average_rating = None
    total_reviews = 0


class SkillFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for Skill model."""

    class Meta:
        model = Skill
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    name = factory.LazyAttribute(lambda _: fake.word())
    category = factory.LazyAttribute(lambda _: fake.word())


class ProjectFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for Project model."""

    class Meta:
        model = Project
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    client = factory.SubFactory(ClientProfileFactory)
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=6))
    description = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=500))
    requirements = factory.LazyAttribute(
        lambda _: {
            "skills": [fake.word() for _ in range(3)],
            "experience": f"{fake.random_int(1, 10)} years",
        }
    )
    budget = FuzzyDecimal(1000.0, 50000.0, precision=2)
    deadline = factory.LazyAttribute(lambda _: fake.future_date())
    status = FuzzyChoice(
        [ProjectStatus.OPEN, ProjectStatus.IN_PROGRESS, ProjectStatus.COMPLETED]
    )
    selected_professional_id = None


class ProposalFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for Proposal model."""

    class Meta:
        model = Proposal
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    project = factory.SubFactory(ProjectFactory, status=ProjectStatus.OPEN)
    professional = factory.SubFactory(ProfessionalProfileFactory)
    proposed_amount = FuzzyDecimal(1000.0, 50000.0, precision=2)
    estimated_days = FuzzyInteger(7, 90)
    description = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=500))
    status = ProposalStatus.SUBMITTED
    ai_score = None


class ReviewFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for Review model."""

    class Meta:
        model = Review
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    project = factory.SubFactory(ProjectFactory, status=ProjectStatus.COMPLETED)
    reviewer = factory.SubFactory(UserFactory)
    reviewed = factory.SubFactory(UserFactory)
    rating = FuzzyInteger(1, 5)
    comment = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=300))
    review_type = FuzzyChoice(
        [ReviewType.PROFESSIONAL_TO_CLIENT, ReviewType.CLIENT_TO_PROFESSIONAL]
    )


def set_sqlalchemy_session(session: Session):
    """Set SQLAlchemy session for all factories."""
    UserFactory._meta.sqlalchemy_session = session
    ProfessionalProfileFactory._meta.sqlalchemy_session = session
    ClientProfileFactory._meta.sqlalchemy_session = session
    SkillFactory._meta.sqlalchemy_session = session
    ProjectFactory._meta.sqlalchemy_session = session
    ProposalFactory._meta.sqlalchemy_session = session
    ReviewFactory._meta.sqlalchemy_session = session
