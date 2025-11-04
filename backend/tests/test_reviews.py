"""Test review (feedback) endpoints and functionality."""

import pytest
from fastapi.testclient import TestClient

from tests.factories import (
    ClientProfileFactory,
    ProfessionalProfileFactory,
    ProjectFactory,
    ReviewFactory,
    set_sqlalchemy_session,
)


@pytest.fixture(scope="function")
def db_session_with_factories(db_session):
    """Set up database session with factory_boy."""
    set_sqlalchemy_session(db_session)
    yield db_session


def test_create_review_client_to_professional(
    db_session_with_factories, client: TestClient
):
    """Test company giving feedback to professional."""
    # Create completed project with professional
    client_profile = ClientProfileFactory()
    professional = ProfessionalProfileFactory()
    project = ProjectFactory(
        client=client_profile,
        selected_professional_id=professional.id,
        status="COMPLETED",
    )
    db_session_with_factories.commit()

    response = client.post(
        "/api/v1/reviews/",
        json={
            "project_id": str(project.id),
            "reviewed_id": str(professional.user_id),
            "rating": 5,
            "comment": "Excellent work! Very professional and delivered on time.",
            "review_type": "client_to_professional",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 5
    assert data["project_id"] == str(project.id)
    assert data["reviewed_id"] == str(professional.user_id)
    assert data["review_type"] == "client_to_professional"


def test_create_review_professional_to_client(
    db_session_with_factories, client: TestClient
):
    """Test professional giving feedback to company."""
    client_profile = ClientProfileFactory()
    professional = ProfessionalProfileFactory()
    project = ProjectFactory(
        client=client_profile,
        selected_professional_id=professional.id,
        status="COMPLETED",
    )
    db_session_with_factories.commit()

    response = client.post(
        "/api/v1/reviews/",
        json={
            "project_id": str(project.id),
            "reviewed_id": str(client_profile.user_id),
            "rating": 4,
            "comment": "Great client, clear requirements and prompt payments.",
            "review_type": "professional_to_client",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 4
    assert data["review_type"] == "professional_to_client"


def test_review_rating_validation(db_session_with_factories, client: TestClient):
    """Test that rating must be between 1 and 5."""
    project = ProjectFactory(status="COMPLETED")
    professional = ProfessionalProfileFactory()
    db_session_with_factories.commit()

    # Test rating > 5
    response = client.post(
        "/api/v1/reviews/",
        json={
            "project_id": str(project.id),
            "reviewed_id": str(professional.user_id),
            "rating": 6,  # Invalid rating
            "review_type": "client_to_professional",
        },
    )
    assert response.status_code == 422

    # Test rating < 1
    response = client.post(
        "/api/v1/reviews/",
        json={
            "project_id": str(project.id),
            "reviewed_id": str(professional.user_id),
            "rating": 0,  # Invalid rating
            "review_type": "client_to_professional",
        },
    )
    assert response.status_code == 422


def test_review_comment_optional(db_session_with_factories, client: TestClient):
    """Test that comment is optional in reviews."""
    client_profile = ClientProfileFactory()
    professional = ProfessionalProfileFactory()
    project = ProjectFactory(
        client=client_profile,
        selected_professional_id=professional.id,
        status="COMPLETED",
    )
    db_session_with_factories.commit()

    response = client.post(
        "/api/v1/reviews/",
        json={
            "project_id": str(project.id),
            "reviewed_id": str(professional.user_id),
            "rating": 3,
            "comment": None,  # Optional comment
            "review_type": "client_to_professional",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 3
    assert data["comment"] is None


def test_list_reviews_by_reviewed_user(db_session_with_factories, client: TestClient):
    """Test listing all reviews for a specific user (professional or company)."""
    professional = ProfessionalProfileFactory()
    # Create 3 reviews for this professional
    _ = [ReviewFactory(reviewed=professional.user, rating=i) for i in range(3, 6)]
    db_session_with_factories.commit()

    response = client.get(f"/api/v1/reviews/?reviewed_id={professional.user_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3


def test_list_reviews_by_project(db_session_with_factories, client: TestClient):
    """Test listing all reviews for a specific project."""
    project = ProjectFactory(status="COMPLETED")
    _ = [ReviewFactory(project=project) for _ in range(2)]
    db_session_with_factories.commit()

    response = client.get(f"/api/v1/reviews/?project_id={project.id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2


def test_get_average_rating_for_professional(
    db_session_with_factories, client: TestClient
):
    """Test calculating average rating for a professional."""
    professional = ProfessionalProfileFactory()
    # Create reviews with ratings 3, 4, 5 (average = 4.0)
    _ = [
        ReviewFactory(reviewed=professional.user, rating=3),
        ReviewFactory(reviewed=professional.user, rating=4),
        ReviewFactory(reviewed=professional.user, rating=5),
    ]
    db_session_with_factories.commit()

    response = client.get(f"/api/v1/reviews/users/{professional.user_id}/rating")

    assert response.status_code == 200
    data = response.json()
    assert "average_rating" in data
    # Average should be 4.0
    assert data["average_rating"] == pytest.approx(4.0, rel=0.1)


def test_get_average_rating_for_company(db_session_with_factories, client: TestClient):
    """Test calculating average rating for a company."""
    company = ClientProfileFactory()
    # Create reviews with ratings 4, 5, 5 (average = 4.67)
    _ = [
        ReviewFactory(reviewed=company.user, rating=4),
        ReviewFactory(reviewed=company.user, rating=5),
        ReviewFactory(reviewed=company.user, rating=5),
    ]
    db_session_with_factories.commit()

    response = client.get(f"/api/v1/reviews/users/{company.user_id}/rating")

    assert response.status_code == 200
    data = response.json()
    assert "average_rating" in data
    # Average should be ~4.67
    assert data["average_rating"] == pytest.approx(4.67, rel=0.1)


def test_review_only_for_completed_projects(
    db_session_with_factories, client: TestClient
):
    """Test that reviews can only be created for COMPLETED projects."""
    project = ProjectFactory(status="IN_PROGRESS")
    professional = ProfessionalProfileFactory()
    db_session_with_factories.commit()

    response = client.post(
        "/api/v1/reviews/",
        json={
            "project_id": str(project.id),
            "reviewed_id": str(professional.user_id),
            "rating": 5,
            "review_type": "client_to_professional",
        },
    )

    # Should fail because project is not COMPLETED
    assert response.status_code in [400, 403]


def test_update_review(db_session_with_factories, client: TestClient):
    """Test updating an existing review."""
    review = ReviewFactory(rating=3, comment="Initial comment")
    db_session_with_factories.commit()

    response = client.put(
        f"/api/v1/reviews/{review.id}",
        json={"rating": 5, "comment": "Updated comment - much better!"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == 5
    assert data["comment"] == "Updated comment - much better!"


def test_delete_review(db_session_with_factories, client: TestClient):
    """Test deleting a review."""
    review = ReviewFactory()
    db_session_with_factories.commit()

    response = client.delete(f"/api/v1/reviews/{review.id}")

    assert response.status_code == 204

    # Verify review is deleted
    response = client.get(f"/api/v1/reviews/{review.id}")
    assert response.status_code == 404


def test_both_parties_can_review_completed_project(
    db_session_with_factories, client: TestClient
):
    """Test that both client and professional can review a completed project."""
    # Create completed project with client and professional
    client_profile = ClientProfileFactory()
    professional = ProfessionalProfileFactory()
    project = ProjectFactory(
        client=client_profile,
        selected_professional_id=professional.id,
        status="COMPLETED",
    )
    db_session_with_factories.commit()

    # Client reviews professional
    client_review_response = client.post(
        "/api/v1/reviews/",
        json={
            "project_id": str(project.id),
            "reviewed_id": str(professional.user_id),
            "rating": 5,
            "comment": "Great work!",
            "review_type": "client_to_professional",
        },
    )

    assert client_review_response.status_code == 201
    client_review_data = client_review_response.json()
    assert client_review_data["reviewer_id"] == str(client_profile.user_id)
    assert client_review_data["reviewed_id"] == str(professional.user_id)

    # Professional reviews client
    professional_review_response = client.post(
        "/api/v1/reviews/",
        json={
            "project_id": str(project.id),
            "reviewed_id": str(client_profile.user_id),
            "rating": 4,
            "comment": "Good client!",
            "review_type": "professional_to_client",
        },
    )

    assert professional_review_response.status_code == 201
    professional_review_data = professional_review_response.json()
    assert professional_review_data["reviewer_id"] == str(professional.user_id)
    assert professional_review_data["reviewed_id"] == str(client_profile.user_id)


def test_third_party_cannot_review_project(
    db_session_with_factories, client: TestClient
):
    """Test that users not part of a project cannot review it."""
    # Create completed project with client and professional
    client_profile = ClientProfileFactory()
    professional = ProfessionalProfileFactory()
    _ = ProfessionalProfileFactory()  # Third party professional
    project = ProjectFactory(
        client=client_profile,
        selected_professional_id=professional.id,
        status="COMPLETED",
    )
    db_session_with_factories.commit()

    # Third party tries to review
    response = client.post(
        "/api/v1/reviews/",
        json={
            "project_id": str(project.id),
            "reviewed_id": str(professional.user_id),
            "rating": 5,
            "comment": "I'm not part of this project",
            "review_type": "client_to_professional",
        },
    )

    # Should fail because third party is not part of the project
    assert response.status_code in [400, 403]
    assert "part of" in response.json()["detail"].lower()
