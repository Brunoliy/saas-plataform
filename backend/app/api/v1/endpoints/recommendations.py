"""AI Recommendations endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.database.session import get_db
from app.repositories.ai_repository import AIRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.project_repository import ProjectRepository
from app.services.ai_service import AIService

router = APIRouter()


def get_ai_service(db: Session = Depends(get_db)) -> AIService:
    """Dependency to get AI service."""
    ai_repo = AIRepository(db)
    project_repo = ProjectRepository(db)
    professional_repo = ProfessionalRepository(db)
    return AIService(ai_repo, project_repo, professional_repo)


@router.get("/projects/{project_id}/recommendations")
async def get_professional_recommendations_for_project(
    project_id: UUID,
    limit: int = Query(default=10, ge=1, le=50),
    ai_service: AIService = Depends(get_ai_service),
):
    """
    Get AI-powered professional recommendations for a project.

    Returns list of professionals ranked by compatibility score.
    """
    try:
        recommendations = ai_service.recommend_professionals_for_project(
            project_id=project_id, limit=limit
        )

        if not recommendations:
            return {
                "project_id": str(project_id),
                "recommendations": [],
                "message": "No professionals found matching this project requirements",
            }

        return {
            "project_id": str(project_id),
            "recommendations": [
                {
                    "professional_id": str(rec["professional_id"]),
                    "professional_name": rec.get("professional_name"),
                    "compatibility_score": rec["compatibility_score"],
                    "recommendation": rec.get("recommendation", ""),
                    "skills_match": rec.get("skills_match", []),
                    "average_rating": float(rec.get("average_rating", 0))
                    if rec.get("average_rating")
                    else None,
                    "total_reviews": rec.get("total_reviews", 0),
                }
                for rec in recommendations
            ],
            "total": len(recommendations),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/professionals/{professional_id}/recommendations")
async def get_project_recommendations_for_professional(
    professional_id: UUID,
    limit: int = Query(default=10, ge=1, le=50),
    ai_service: AIService = Depends(get_ai_service),
):
    """
    Get AI-powered project recommendations for a professional.

    Returns list of open projects ranked by compatibility score.
    """
    try:
        recommendations = ai_service.recommend_projects_for_professional(
            professional_id=professional_id, limit=limit
        )

        if not recommendations:
            return {
                "professional_id": str(professional_id),
                "recommendations": [],
                "message": "No open projects found matching your skills",
            }

        return {
            "professional_id": str(professional_id),
            "recommendations": [
                {
                    "project_id": str(rec["project_id"]),
                    "project_title": rec.get("project_title"),
                    "compatibility_score": rec["compatibility_score"],
                    "recommendation": rec.get("recommendation", ""),
                    "skills_match": rec.get("skills_match", []),
                    "budget": float(rec.get("budget", 0))
                    if rec.get("budget")
                    else None,
                    "deadline": rec.get("deadline"),
                }
                for rec in recommendations
            ],
            "total": len(recommendations),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compatibility/{project_id}/{professional_id}")
async def calculate_compatibility(
    project_id: UUID,
    professional_id: UUID,
    ai_service: AIService = Depends(get_ai_service),
):
    """
    Calculate compatibility score between a project and a professional.

    Returns detailed compatibility analysis.
    """
    try:
        result = ai_service.calculate_compatibility_score(
            project_id=project_id, professional_id=professional_id
        )

        if not result:
            raise HTTPException(
                status_code=404, detail="Project or professional not found"
            )

        return {
            "project_id": str(project_id),
            "professional_id": str(professional_id),
            "compatibility_score": result["score"],
            "recommendation": result.get("recommendation", ""),
            "analysis": result.get("analysis", {}),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me/recommended-projects")
async def get_my_recommended_projects(
    limit: int = Query(default=10, ge=1, le=50),
    current_user_id: str = Depends(get_current_user_id),
    ai_service: AIService = Depends(get_ai_service),
    db: Session = Depends(get_db),
):
    """
    Get personalized project recommendations for the current professional.

    Requires authentication and professional account.
    """
    try:
        # Get professional profile for current user
        professional_repo = ProfessionalRepository(db)
        professional = professional_repo.get_by_user_id(UUID(current_user_id))

        if not professional:
            raise HTTPException(
                status_code=404,
                detail="Professional profile not found. Please create a professional profile first.",
            )

        recommendations = ai_service.recommend_projects_for_professional(
            professional_id=professional.id, limit=limit
        )

        return {
            "recommendations": [
                {
                    "project_id": str(rec["project_id"]),
                    "project_title": rec.get("project_title"),
                    "compatibility_score": rec["compatibility_score"],
                    "recommendation": rec.get("recommendation", ""),
                    "skills_match": rec.get("skills_match", []),
                    "budget": float(rec.get("budget", 0))
                    if rec.get("budget")
                    else None,
                    "deadline": rec.get("deadline"),
                }
                for rec in recommendations
            ],
            "total": len(recommendations),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyses/{analysis_id}")
async def get_analysis(
    analysis_id: UUID,
    ai_service: AIService = Depends(get_ai_service),
):
    """Get AI analysis by ID."""
    analysis = ai_service.get_analysis_by_id(analysis_id)

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "id": str(analysis.id),
        "project_id": str(analysis.project_id) if analysis.project_id else None,
        "professional_id": str(analysis.professional_id)
        if analysis.professional_id
        else None,
        "analysis_type": analysis.analysis_type,
        "result_data": analysis.result_data,
        "confidence_score": float(analysis.confidence_score)
        if analysis.confidence_score
        else None,
        "model_version": analysis.model_version,
        "created_at": analysis.created_at,
    }
