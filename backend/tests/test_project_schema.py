"""Tests for project schemas."""

import pytest
from uuid import uuid4
from datetime import datetime
from decimal import Decimal

from app.schemas.project import ProjectResponse, ProjectStatus
from app.models.project import Project
from app.models.client import ClientProfile
from app.models.professional import ProfessionalProfile
from app.models.user import User, AccountType


class TestProjectResponse:
    """Test ProjectResponse schema."""

    def test_populate_user_ids_with_model_instance(self, db_session):
        """Test that user IDs are populated from model relationships."""
        # Create users
        client_user = User(
            id=uuid4(),
            email="client@example.com",
            password_hash="hashed",
            full_name="Client User",
            account_type=AccountType.COMPANY,
            active=True,
        )
        professional_user = User(
            id=uuid4(),
            email="professional@example.com",
            password_hash="hashed",
            full_name="Professional User",
            account_type=AccountType.PROFESSIONAL,
            active=True,
        )

        db_session.add(client_user)
        db_session.add(professional_user)
        db_session.commit()

        # Create profiles
        client_profile = ClientProfile(
            id=uuid4(),
            user_id=client_user.id,
            company_name="Test Company",
            business_sector="Technology",
        )
        professional_profile = ProfessionalProfile(
            id=uuid4(),
            user_id=professional_user.id,
            title="Senior Developer",
        )

        db_session.add(client_profile)
        db_session.add(professional_profile)
        db_session.commit()

        # Create project
        project = Project(
            id=uuid4(),
            client_id=client_profile.id,
            title="Test Project",
            description="Test Description",
            budget=Decimal("10000.00"),
            status=ProjectStatus.COMPLETED,
            selected_professional_id=professional_profile.id,
        )

        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)

        # Convert to schema
        response = ProjectResponse.model_validate(project)

        # Assert user IDs are populated
        assert response.client_user_id == client_user.id
        assert response.selected_professional_user_id == professional_user.id
        assert response.client_id == client_profile.id
        assert response.selected_professional_id == professional_profile.id

    def test_populate_user_ids_without_selected_professional(self, db_session):
        """Test that schema works when no professional is selected."""
        # Create user and client profile
        client_user = User(
            id=uuid4(),
            email="client@example.com",
            password_hash="hashed",
            full_name="Client User",
            account_type=AccountType.COMPANY,
            active=True,
        )

        db_session.add(client_user)
        db_session.commit()

        client_profile = ClientProfile(
            id=uuid4(),
            user_id=client_user.id,
            company_name="Test Company",
            business_sector="Technology",
        )

        db_session.add(client_profile)
        db_session.commit()

        # Create project without selected professional
        project = Project(
            id=uuid4(),
            client_id=client_profile.id,
            title="Test Project",
            description="Test Description",
            budget=Decimal("10000.00"),
            status=ProjectStatus.OPEN,
            selected_professional_id=None,
        )

        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)

        # Convert to schema
        response = ProjectResponse.model_validate(project)

        # Assert client user ID is populated but professional is None
        assert response.client_user_id == client_user.id
        assert response.selected_professional_user_id is None
        assert response.selected_professional_id is None

    def test_populate_user_ids_with_dict(self):
        """Test that dict data passes through without modification."""
        # Create a dict with already-serialized data
        project_data = {
            "id": uuid4(),
            "client_id": uuid4(),
            "client_user_id": uuid4(),
            "title": "Test Project",
            "description": "Test Description",
            "requirements": None,
            "budget": Decimal("10000.00"),
            "deadline": None,
            "status": ProjectStatus.OPEN,
            "selected_professional_id": None,
            "selected_professional_user_id": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        # This should not raise an error
        response = ProjectResponse(**project_data)

        # Assert data is preserved
        assert response.client_user_id == project_data["client_user_id"]
        assert response.client_id == project_data["client_id"]

    def test_model_validator_handles_missing_relationships(self, db_session):
        """Test that model_validator handles projects with unloaded relationships."""
        # Create user and client profile
        client_user = User(
            id=uuid4(),
            email="client@example.com",
            password_hash="hashed",
            full_name="Client User",
            account_type=AccountType.COMPANY,
            active=True,
        )

        db_session.add(client_user)
        db_session.commit()

        client_profile = ClientProfile(
            id=uuid4(),
            user_id=client_user.id,
            company_name="Test Company",
            business_sector="Technology",
        )

        db_session.add(client_profile)
        db_session.commit()

        # Create project
        project = Project(
            id=uuid4(),
            client_id=client_profile.id,
            title="Test Project",
            description="Test Description",
            budget=Decimal("10000.00"),
            status=ProjectStatus.OPEN,
        )

        db_session.add(project)
        db_session.commit()

        # Query without joinedload (relationships not loaded)
        project_no_relationships = db_session.query(Project).filter_by(id=project.id).first()

        # This should not raise an error even if relationships aren't loaded
        # The validator should handle missing relationships gracefully
        response = ProjectResponse.model_validate(project_no_relationships)

        assert response.id == project.id
        assert response.client_id == client_profile.id

    def test_project_response_all_fields(self, db_session):
        """Test ProjectResponse with all fields populated."""
        # Create users
        client_user = User(
            id=uuid4(),
            email="client@example.com",
            password_hash="hashed",
            full_name="Client User",
            account_type=AccountType.COMPANY,
            active=True,
        )
        professional_user = User(
            id=uuid4(),
            email="professional@example.com",
            password_hash="hashed",
            full_name="Professional User",
            account_type=AccountType.PROFESSIONAL,
            active=True,
        )

        db_session.add(client_user)
        db_session.add(professional_user)
        db_session.commit()

        # Create profiles
        client_profile = ClientProfile(
            id=uuid4(),
            user_id=client_user.id,
            company_name="Test Company",
            business_sector="Technology",
        )
        professional_profile = ProfessionalProfile(
            id=uuid4(),
            user_id=professional_user.id,
            title="Senior Developer",
        )

        db_session.add(client_profile)
        db_session.add(professional_profile)
        db_session.commit()

        # Create project with all fields
        deadline = datetime(2025, 12, 31)
        requirements = {
            "skills": ["Python", "FastAPI"],
            "experience": "5 years",
        }

        project = Project(
            id=uuid4(),
            client_id=client_profile.id,
            title="Full Stack Development",
            description="Build a SaaS platform",
            requirements=requirements,
            budget=Decimal("50000.00"),
            deadline=deadline,
            status=ProjectStatus.IN_PROGRESS,
            selected_professional_id=professional_profile.id,
        )

        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)

        # Convert to schema
        response = ProjectResponse.model_validate(project)

        # Assert all fields
        assert response.id == project.id
        assert response.client_id == client_profile.id
        assert response.client_user_id == client_user.id
        assert response.title == "Full Stack Development"
        assert response.description == "Build a SaaS platform"
        assert response.requirements == requirements
        assert response.budget == Decimal("50000.00")
        assert response.deadline == deadline
        assert response.status == ProjectStatus.IN_PROGRESS
        assert response.selected_professional_id == professional_profile.id
        assert response.selected_professional_user_id == professional_user.id

    def test_project_status_values(self):
        """Test that all ProjectStatus values are valid."""
        statuses = [
            ProjectStatus.OPEN,
            ProjectStatus.IN_PROGRESS,
            ProjectStatus.COMPLETED,
            ProjectStatus.CANCELLED,
        ]

        for status in statuses:
            project_data = {
                "id": uuid4(),
                "client_id": uuid4(),
                "client_user_id": uuid4(),
                "title": "Test Project",
                "description": "Test Description",
                "requirements": None,
                "budget": Decimal("10000.00"),
                "deadline": None,
                "status": status,
                "selected_professional_id": None,
                "selected_professional_user_id": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            response = ProjectResponse(**project_data)
            assert response.status == status
