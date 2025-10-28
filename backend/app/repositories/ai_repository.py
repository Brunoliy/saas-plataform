"""AI Analysis repository for database operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.ai_analysis import AIAnalysis


class AIRepository:
    """AI Analysis repository class."""

    def __init__(self, db: Session):
        """Initialize repository."""
        self.db = db

    def create(
        self,
        project_id: UUID,
        professional_id: UUID,
        compatibility_score: float,
        positive_factors: Optional[dict] = None,
        negative_factors: Optional[dict] = None,
        recommendation: Optional[str] = None,
        model_version: str = "v1.0",
        analysis_date: str = "",
    ) -> AIAnalysis:
        """Create a new AI analysis."""
        db_analysis = AIAnalysis(
            project_id=project_id,
            professional_id=professional_id,
            compatibility_score=compatibility_score,
            positive_factors=positive_factors,
            negative_factors=negative_factors,
            recommendation=recommendation,
            model_version=model_version,
            analysis_date=analysis_date,
        )

        self.db.add(db_analysis)
        self.db.commit()
        self.db.refresh(db_analysis)
        return db_analysis

    def get_by_id(self, analysis_id: UUID) -> Optional[AIAnalysis]:
        """Get AI analysis by ID (only non-deleted analyses)."""
        return (
            self.db.query(AIAnalysis)
            .filter(and_(AIAnalysis.id == analysis_id, AIAnalysis.deleted_at.is_(None)))
            .first()
        )

    def update(
        self,
        analysis_id: UUID,
        compatibility_score: Optional[float] = None,
        positive_factors: Optional[dict] = None,
        negative_factors: Optional[dict] = None,
        recommendation: Optional[str] = None,
    ) -> Optional[AIAnalysis]:
        """Update AI analysis."""
        db_analysis = self.get_by_id(analysis_id)
        if not db_analysis:
            return None

        if compatibility_score is not None:
            db_analysis.compatibility_score = compatibility_score
        if positive_factors is not None:
            db_analysis.positive_factors = positive_factors
        if negative_factors is not None:
            db_analysis.negative_factors = negative_factors
        if recommendation is not None:
            db_analysis.recommendation = recommendation

        self.db.commit()
        self.db.refresh(db_analysis)
        return db_analysis

    def delete(self, analysis_id: UUID) -> bool:
        """Soft delete AI analysis."""
        db_analysis = self.get_by_id(analysis_id)
        if not db_analysis:
            return False

        db_analysis.soft_delete()
        self.db.commit()
        return True

    def list_analyses(
        self, skip: int = 0, limit: int = 20, include_deleted: bool = False
    ) -> list[AIAnalysis]:
        """List AI analyses with pagination."""
        query = self.db.query(AIAnalysis)

        if not include_deleted:
            query = query.filter(AIAnalysis.deleted_at.is_(None))

        return query.offset(skip).limit(limit).all()

    def count_analyses(self, include_deleted: bool = False) -> int:
        """Count total AI analyses."""
        query = self.db.query(AIAnalysis)

        if not include_deleted:
            query = query.filter(AIAnalysis.deleted_at.is_(None))

        return query.count()

    def get_analyses_by_project(
        self, project_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[AIAnalysis]:
        """Get AI analyses by project ID."""
        return (
            self.db.query(AIAnalysis)
            .filter(
                and_(
                    AIAnalysis.project_id == project_id, AIAnalysis.deleted_at.is_(None)
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_analyses_by_professional(
        self, professional_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[AIAnalysis]:
        """Get AI analyses by professional ID."""
        return (
            self.db.query(AIAnalysis)
            .filter(
                and_(
                    AIAnalysis.professional_id == professional_id,
                    AIAnalysis.deleted_at.is_(None),
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_analysis_by_project_and_professional(
        self, project_id: UUID, professional_id: UUID
    ) -> Optional[AIAnalysis]:
        """Get AI analysis by project and professional."""
        return (
            self.db.query(AIAnalysis)
            .filter(
                and_(
                    AIAnalysis.project_id == project_id,
                    AIAnalysis.professional_id == professional_id,
                    AIAnalysis.deleted_at.is_(None),
                )
            )
            .first()
        )

    def get_top_matches_for_project(
        self, project_id: UUID, limit: int = 10
    ) -> list[AIAnalysis]:
        """Get top AI matches for a project ordered by compatibility score."""
        return (
            self.db.query(AIAnalysis)
            .filter(
                and_(
                    AIAnalysis.project_id == project_id, AIAnalysis.deleted_at.is_(None)
                )
            )
            .order_by(AIAnalysis.compatibility_score.desc())
            .limit(limit)
            .all()
        )

    def get_by_model_version(
        self, model_version: str, skip: int = 0, limit: int = 20
    ) -> list[AIAnalysis]:
        """Get AI analyses by model version."""
        return (
            self.db.query(AIAnalysis)
            .filter(
                and_(
                    AIAnalysis.model_version == model_version,
                    AIAnalysis.deleted_at.is_(None),
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_high_compatibility_analyses(
        self, min_score: float = 80.0, skip: int = 0, limit: int = 20
    ) -> list[AIAnalysis]:
        """Get AI analyses with high compatibility scores."""
        return (
            self.db.query(AIAnalysis)
            .filter(
                and_(
                    AIAnalysis.compatibility_score >= min_score,
                    AIAnalysis.deleted_at.is_(None),
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
