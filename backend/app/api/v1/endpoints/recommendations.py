"""AI Recommendations endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.database.session import get_db
from app.repositories.ai_repository import AIRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.project_repository import ProjectRepository
from app.services.ai_service import AIService
from app.services.chat_service import ChatService

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request schema."""

    message: str
    context: dict | None = None
    user_type: str = "professional"


class ChatResponse(BaseModel):
    """Chat response schema."""

    response: str
    suggestions: list[str] = []
    data: dict | None = None


def get_ai_service(db: Session = Depends(get_db)) -> AIService:
    """Dependency to get AI service."""
    ai_repo = AIRepository(db)
    project_repo = ProjectRepository(db)
    professional_repo = ProfessionalRepository(db)
    return AIService(ai_repo, project_repo, professional_repo)


def get_chat_service(ai_service: AIService = Depends(get_ai_service)) -> ChatService:
    """Dependency to get chat service."""
    return ChatService(ai_service)


@router.get("/projects/{project_id}/recommendations")
async def get_professional_recommendations_for_project(
    project_id: UUID,
    limit: int = Query(default=10, ge=1, le=50),
    ai_service: AIService = Depends(get_ai_service),
) -> dict:
    """
    Get AI-powered professional recommendations for a project.

    Returns list of professionals ranked by compatibility score.
    """
    try:
        recommendations = await ai_service.recommend_professionals_for_project(
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
) -> dict:
    """
    Get AI-powered project recommendations for a professional.

    Returns list of open projects ranked by compatibility score.
    """
    try:
        recommendations = await ai_service.recommend_projects_for_professional(
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
) -> dict:
    """
    Calculate compatibility score between a project and a professional.

    Returns detailed compatibility analysis.
    """
    try:
        result = await ai_service.calculate_compatibility_score(
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
) -> dict:
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

        recommendations = await ai_service.recommend_projects_for_professional(
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
) -> dict:
    """Get AI analysis by ID."""
    analysis = await ai_service.get_analysis_by_id(analysis_id)

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "id": str(analysis.id),
        "project_id": str(analysis.project_id) if analysis.project_id else None,
        "professional_id": str(analysis.professional_id)
        if analysis.professional_id
        else None,
        "compatibility_score": float(analysis.compatibility_score)
        if analysis.compatibility_score
        else None,
        "positive_factors": analysis.positive_factors,
        "negative_factors": analysis.negative_factors,
        "recommendation": analysis.recommendation,
        "model_version": analysis.model_version,
        "analysis_date": analysis.analysis_date,
        "created_at": analysis.created_at,
    }


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user_id: str = Depends(get_current_user_id),
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """
    Chat with AI about recommendations and matches.

    Supports intelligent Q&A about:
    - Why something was recommended
    - Comparing options
    - Finding best matches
    - Explaining scores
    - General questions about the system

    Requires authentication.
    """
    try:
        result = await chat_service.chat(
            message=request.message,
            context=request.context,
            user_type=request.user_type,
        )

        return ChatResponse(
            response=result.get("response", "I'm not sure how to answer that."),
            suggestions=result.get("suggestions", []),
            data=result.get("data"),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
