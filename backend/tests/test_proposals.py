"""Test proposal (application) endpoints and functionality."""

import pytest
from fastapi.testclient import TestClient

from tests.factories import (
    ProfessionalProfileFactory,
    ProjectFactory,
    ProposalFactory,
    set_sqlalchemy_session,
)


@pytest.fixture(scope="function")
def db_session_with_factories(db_session):
    """Set up database session with factory_boy."""
    set_sqlalchemy_session(db_session)
    yield db_session


def test_create_proposal_success(db_session_with_factories, client: TestClient):
    """Test successful proposal creation (professional applying to project)."""
    # Create professional and open project
    professional = ProfessionalProfileFactory()
    project = ProjectFactory(status="OPEN")
    db_session_with_factories.commit()

    response = client.post(
        "/api/v1/proposals/",
        json={
            "project_id": str(project.id),
            "proposed_amount": 15000.00,
            "estimated_days": 30,
            "description": "I am the perfect fit for this project because...",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["project_id"] == str(project.id)
    assert data["professional_id"] == str(professional.id)
    assert data["proposed_amount"] == 15000.00
    assert data["estimated_days"] == 30
    assert data["status"] == "SUBMITTED"


def test_create_proposal_duplicate(db_session_with_factories, client: TestClient):
    """Test that professional cannot apply to same project twice."""
    proposal = ProposalFactory()
    db_session_with_factories.commit()

    response = client.post(
        "/api/v1/proposals/",
        json={
            "project_id": str(proposal.project_id),
            "proposed_amount": 10000.00,
            "estimated_days": 20,
            "description": "Second application attempt",
        },
    )

    # Should fail because professional already applied
    assert response.status_code in [400, 409]


def test_accept_proposal(db_session_with_factories, client: TestClient):
    """Test company accepting a proposal."""
    proposal = ProposalFactory(status="SUBMITTED")
    db_session_with_factories.commit()

    response = client.post(f"/api/v1/proposals/{proposal.id}/accept")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACCEPTED"
    assert data["id"] == str(proposal.id)


def test_reject_proposal(db_session_with_factories, client: TestClient):
    """Test company rejecting a proposal."""
    proposal = ProposalFactory(status="SUBMITTED")
    db_session_with_factories.commit()

    response = client.post(f"/api/v1/proposals/{proposal.id}/reject")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "REJECTED"


def test_list_proposals_by_project(db_session_with_factories, client: TestClient):
    """Test listing all proposals for a specific project."""
    project = ProjectFactory(status="OPEN")
    _ = [ProposalFactory(project=project) for _ in range(3)]
    db_session_with_factories.commit()

    response = client.get(f"/api/v1/proposals/?project_id={project.id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3


def test_list_proposals_by_professional(db_session_with_factories, client: TestClient):
    """Test listing all proposals by a specific professional."""
    professional = ProfessionalProfileFactory()
    _ = [ProposalFactory(professional=professional) for _ in range(2)]
    db_session_with_factories.commit()

    response = client.get(f"/api/v1/proposals/?professional_id={professional.id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2


def test_proposal_amount_validation(db_session_with_factories, client: TestClient):
    """Test that proposal amount must be positive."""
    project = ProjectFactory(status="OPEN")
    db_session_with_factories.commit()

    response = client.post(
        "/api/v1/proposals/",
        json={
            "project_id": str(project.id),
            "proposed_amount": -1000.00,  # Invalid negative amount
            "description": "Test",
        },
    )

    assert response.status_code == 422  # Validation error


def test_proposal_only_for_open_projects(db_session_with_factories, client: TestClient):
    """Test that proposals can only be created for OPEN projects."""
    project = ProjectFactory(status="COMPLETED")
    db_session_with_factories.commit()

    response = client.post(
        "/api/v1/proposals/",
        json={
            "project_id": str(project.id),
            "proposed_amount": 10000.00,
            "description": "Trying to apply to completed project",
        },
    )

    # Should fail because project is not OPEN
    assert response.status_code in [400, 403]
