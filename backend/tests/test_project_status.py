"""Test project status management by professionals."""

import pytest
from fastapi.testclient import TestClient

from tests.factories import (
    ProfessionalProfileFactory,
    ProjectFactory,
    set_sqlalchemy_session,
)


@pytest.fixture(scope="function")
def db_session_with_factories(db_session):
    """Set up database session with factory_boy."""
    set_sqlalchemy_session(db_session)
    yield db_session


def test_professional_start_project(db_session_with_factories, client: TestClient):
    """Test that assigned professional can start a project (OPEN -> IN_PROGRESS)."""
    # Create professional and project
    professional = ProfessionalProfileFactory()
    project = ProjectFactory(
        status="OPEN",
        selected_professional_id=professional.id,
    )
    db_session_with_factories.commit()

    response = client.patch(f"/api/v1/projects/{project.id}/start")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "IN_PROGRESS"
    assert data["id"] == str(project.id)


def test_professional_complete_project(db_session_with_factories, client: TestClient):
    """Test that assigned professional can complete a project (IN_PROGRESS -> COMPLETED)."""
    # Create professional and project in progress
    professional = ProfessionalProfileFactory()
    project = ProjectFactory(
        status="IN_PROGRESS",
        selected_professional_id=professional.id,
    )
    db_session_with_factories.commit()

    response = client.patch(f"/api/v1/projects/{project.id}/complete-by-professional")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["id"] == str(project.id)


def test_professional_cannot_start_unassigned_project(
    db_session_with_factories, client: TestClient
):
    """Test that professional cannot start a project they are not assigned to."""
    # Create professional and project with different professional assigned
    _ = ProfessionalProfileFactory()  # Current user (not assigned)
    other_professional = ProfessionalProfileFactory()
    project = ProjectFactory(
        status="OPEN",
        selected_professional_id=other_professional.id,
    )
    db_session_with_factories.commit()

    response = client.patch(f"/api/v1/projects/{project.id}/start")

    # Should fail because professional is not assigned to this project
    assert response.status_code == 400


def test_professional_cannot_complete_unassigned_project(
    db_session_with_factories, client: TestClient
):
    """Test that professional cannot complete a project they are not assigned to."""
    # Create professional and project with different professional assigned
    _ = ProfessionalProfileFactory()  # Current user (not assigned)
    other_professional = ProfessionalProfileFactory()
    project = ProjectFactory(
        status="IN_PROGRESS",
        selected_professional_id=other_professional.id,
    )
    db_session_with_factories.commit()

    response = client.patch(f"/api/v1/projects/{project.id}/complete-by-professional")

    # Should fail because professional is not assigned to this project
    assert response.status_code == 400


def test_professional_cannot_start_non_open_project(
    db_session_with_factories, client: TestClient
):
    """Test that professional cannot start a project that is not OPEN."""
    # Create professional and project already in progress
    professional = ProfessionalProfileFactory()
    project = ProjectFactory(
        status="IN_PROGRESS",
        selected_professional_id=professional.id,
    )
    db_session_with_factories.commit()

    response = client.patch(f"/api/v1/projects/{project.id}/start")

    # Should fail because project is not OPEN
    assert response.status_code == 400


def test_professional_cannot_complete_non_in_progress_project(
    db_session_with_factories, client: TestClient
):
    """Test that professional cannot complete a project that is not IN_PROGRESS."""
    # Create professional and project still open
    professional = ProfessionalProfileFactory()
    project = ProjectFactory(
        status="OPEN",
        selected_professional_id=professional.id,
    )
    db_session_with_factories.commit()

    response = client.patch(f"/api/v1/projects/{project.id}/complete-by-professional")

    # Should fail because project is not IN_PROGRESS
    assert response.status_code == 400


def test_professional_workflow_full_cycle(
    db_session_with_factories, client: TestClient
):
    """Test full workflow: professional applies, gets accepted, starts, and completes project."""
    # Create professional and open project
    _ = ProfessionalProfileFactory()  # Professional will be created via proposal
    project = ProjectFactory(status="OPEN")
    db_session_with_factories.commit()

    # Professional submits proposal
    proposal_response = client.post(
        "/api/v1/proposals/",
        json={
            "project_id": str(project.id),
            "proposed_amount": 15000.00,
            "estimated_days": 30,
            "description": "I can do this project",
        },
    )
    assert proposal_response.status_code == 201
    proposal_id = proposal_response.json()["id"]

    # Client accepts proposal
    accept_response = client.post(f"/api/v1/proposals/{proposal_id}/accept")
    assert accept_response.status_code == 200

    # Professional starts project
    start_response = client.patch(f"/api/v1/projects/{project.id}/start")
    assert start_response.status_code == 200
    assert start_response.json()["status"] == "IN_PROGRESS"

    # Professional completes project
    complete_response = client.patch(
        f"/api/v1/projects/{project.id}/complete-by-professional"
    )
    assert complete_response.status_code == 200
    assert complete_response.json()["status"] == "COMPLETED"
