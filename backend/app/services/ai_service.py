"""AI service."""

import logging
from datetime import datetime
from uuid import UUID

from app.models.ai_analysis import AIAnalysis
from app.repositories.ai_repository import AIRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.project_repository import ProjectRepository
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class AIService:
    """AI service class."""

    def __init__(
        self,
        ai_repository: AIRepository,
        project_repository: ProjectRepository,
        professional_repository: ProfessionalRepository,
        embedding_service: EmbeddingService | None = None,
    ):
        """Initialize service."""
        self.ai_repository = ai_repository
        self.project_repository = project_repository
        self.professional_repository = professional_repository
        self.embedding_service = embedding_service or EmbeddingService()

    async def recommend_professionals_for_project(
        self, project_id: UUID, limit: int = 10
    ) -> list[dict]:
        """
        Recommend professionals for a project based on skills and ratings.
        Returns list of recommended professionals with compatibility scores.
        """
        # Get project
        project = self.project_repository.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found")

        # Get all professionals
        all_professionals = self.professional_repository.list_professionals(
            skip=0, limit=1000
        )

        # Calculate compatibility scores for each professional
        recommendations = []
        for professional in all_professionals:
            score, factors = await self._calculate_compatibility_score(
                project_id, professional.id
            )

            # Determine model version based on whether embeddings were used
            model_version = (
                "v2.0-semantic"
                if (self.embedding_service and self.embedding_service.api_key)
                else "v1.0-basic"
            )

            # Store AI analysis
            self.ai_repository.create(
                project_id=project_id,
                professional_id=professional.id,
                compatibility_score=score,
                positive_factors=factors["positive"],
                negative_factors=factors["negative"],
                recommendation=self._generate_recommendation(score),
                model_version=model_version,
                analysis_date=datetime.utcnow().isoformat(),
            )

            recommendations.append(
                {
                    "professional_id": professional.id,
                    "professional_name": professional.title,
                    "compatibility_score": score,
                    "hourly_rate": professional.hourly_rate,
                    "average_rating": professional.average_rating,
                    "total_reviews": professional.total_reviews,
                    "positive_factors": factors["positive"],
                    "negative_factors": factors["negative"],
                    "recommendation": self._generate_recommendation(score),
                }
            )

        # Sort by compatibility score
        recommendations.sort(key=lambda x: x["compatibility_score"], reverse=True)

        return recommendations[:limit]

    async def recommend_projects_for_professional(
        self, professional_id: UUID, limit: int = 10
    ) -> list[dict]:
        """
        Recommend projects for a professional based on skills and preferences.
        Returns list of recommended projects with compatibility scores.
        """
        # Get professional
        professional = self.professional_repository.get_by_id(professional_id)
        if not professional:
            raise ValueError("Professional not found")

        # Get all open projects
        from app.models.project import ProjectStatus

        all_projects = self.project_repository.get_projects_by_status(
            ProjectStatus.OPEN, skip=0, limit=1000
        )

        # Calculate compatibility scores for each project
        recommendations = []
        for project in all_projects:
            score, factors = await self._calculate_compatibility_score(
                project.id, professional_id
            )

            recommendations.append(
                {
                    "project_id": project.id,
                    "project_title": project.title,
                    "compatibility_score": score,
                    "budget": project.budget,
                    "deadline": project.deadline,
                    "client_id": project.client_id,
                    "positive_factors": factors["positive"],
                    "negative_factors": factors["negative"],
                    "recommendation": self._generate_recommendation(score),
                }
            )

        # Sort by compatibility score
        recommendations.sort(key=lambda x: x["compatibility_score"], reverse=True)

        return recommendations[:limit]

    async def calculate_compatibility_score(
        self, project_id: UUID, professional_id: UUID
    ) -> float:
        """
        Calculate compatibility score between a project and a professional.
        Returns a score between 0 and 100.
        """
        score, _ = await self._calculate_compatibility_score(
            project_id, professional_id
        )
        return score

    async def _calculate_compatibility_score(
        self, project_id: UUID, professional_id: UUID
    ) -> tuple[float, dict]:
        """
        Internal method to calculate compatibility score with detailed factors.
        Uses semantic embeddings when available, falls back to basic scoring.
        """
        # Get project
        project = self.project_repository.get_by_id(project_id)
        if not project:
            return 0.0, {"positive": {}, "negative": {}}

        # Get professional and their skills
        professional = self.professional_repository.get_by_id(professional_id)
        if not professional:
            return 0.0, {"positive": {}, "negative": {}}

        professional_skills = self.professional_repository.get_professional_skills(
            professional_id
        )

        # Try semantic matching if embedding service is available and has API key
        use_semantic = self.embedding_service and self.embedding_service.api_key

        if use_semantic:
            try:
                return await self._calculate_compatibility_score_with_embeddings(
                    project, professional, professional_skills
                )
            except Exception as e:
                logger.warning(
                    f"Semantic matching failed, falling back to basic algorithm: {str(e)}"
                )
                # Fall through to basic algorithm

        # Fallback to basic algorithm
        return await self._calculate_compatibility_score_basic(
            project, professional, professional_skills
        )

    async def _calculate_compatibility_score_with_embeddings(
        self, project: any, professional: any, professional_skills: list
    ) -> tuple[float, dict]:
        """
        Calculate compatibility score using semantic embeddings.
        """
        positive_factors = {}
        negative_factors = {}

        # Component 1: Description semantic match (40% weight)
        description_score = 0.0
        if project.description and professional.description:
            description_score = await self._calculate_semantic_description_match(
                project.description, professional.description
            )
            if description_score > 70:
                positive_factors["description_match"] = (
                    f"Excellent semantic match ({description_score:.1f}%)"
                )
            elif description_score > 50:
                positive_factors["description_match"] = (
                    f"Good semantic match ({description_score:.1f}%)"
                )
            else:
                negative_factors["description_mismatch"] = (
                    f"Low description match ({description_score:.1f}%)"
                )

        # Component 2: Skills semantic match (30% weight)
        skills_score, matched_skills = await self._calculate_skills_semantic_match(
            project, professional_skills
        )
        if matched_skills:
            positive_factors["matched_skills"] = (
                f"Matched skills: {', '.join(matched_skills[:5])}"
            )
        if skills_score > 70:
            positive_factors["skills_match"] = (
                f"Strong skills match ({skills_score:.1f}%)"
            )
        elif skills_score > 50:
            positive_factors["skills_match"] = (
                f"Moderate skills match ({skills_score:.1f}%)"
            )
        else:
            negative_factors["skills_mismatch"] = (
                f"Weak skills match ({skills_score:.1f}%)"
            )

        # Component 3: Experience/Rating (20% weight)
        experience_score = 50.0
        if professional.average_rating:
            rating = float(professional.average_rating)
            experience_score = (rating / 5.0) * 100
            if rating >= 4.5:
                positive_factors["rating"] = f"Excellent rating ({rating:.1f}/5)"
            elif rating >= 4.0:
                positive_factors["rating"] = f"Good rating ({rating:.1f}/5)"
            elif rating < 3.0:
                negative_factors["low_rating"] = f"Low rating ({rating:.1f}/5)"

        # Component 4: Review count bonus (10% weight)
        review_score = 0.0
        if professional.total_reviews >= 10:
            review_score = min((professional.total_reviews / 50) * 100, 100)
            positive_factors["reviews"] = (
                f"{professional.total_reviews} reviews (experienced professional)"
            )

        # Weighted final score
        final_score = (
            description_score * 0.40
            + skills_score * 0.30
            + experience_score * 0.20
            + review_score * 0.10
        )

        # Ensure score is between 0 and 100
        final_score = max(0.0, min(100.0, final_score))

        logger.info(
            f"Semantic match score: {final_score:.1f} (desc: {description_score:.1f}, "
            f"skills: {skills_score:.1f}, exp: {experience_score:.1f}, reviews: {review_score:.1f})"
        )

        return final_score, {"positive": positive_factors, "negative": negative_factors}

    async def _calculate_compatibility_score_basic(
        self, project: any, professional: any, professional_skills: list
    ) -> tuple[float, dict]:
        """
        Basic compatibility scoring without semantic embeddings (fallback).
        """
        # Base score starts at 50
        base_score = 50.0
        positive_factors = {}
        negative_factors = {}

        # Factor 1: Professional has skills (up to +20 points)
        if professional_skills:
            skill_bonus = min(len(professional_skills) * 2, 20)
            base_score += skill_bonus
            positive_factors["skills_count"] = (
                f"Has {len(professional_skills)} skills (+{skill_bonus} points)"
            )

            # Factor 2: High proficiency levels (up to +10 points)
            avg_proficiency = sum(
                skill.proficiency_level for skill in professional_skills
            ) / len(professional_skills)
            if avg_proficiency >= 4:
                proficiency_bonus = 10
                base_score += proficiency_bonus
                positive_factors["proficiency"] = (
                    f"High average proficiency ({avg_proficiency:.1f}/5) (+{proficiency_bonus} points)"
                )

            # Factor 3: Certified skills (up to +10 points)
            certified_count = sum(1 for skill in professional_skills if skill.certified)
            if certified_count > 0:
                cert_bonus = min(certified_count * 5, 10)
                base_score += cert_bonus
                positive_factors["certifications"] = (
                    f"{certified_count} certified skills (+{cert_bonus} points)"
                )
        else:
            negative_factors["no_skills"] = "No skills listed (-10 points)"
            base_score -= 10

        # Factor 4: Professional rating (up to +15 points or -10 points)
        if professional.average_rating:
            rating = float(professional.average_rating)
            if rating >= 4.5:
                rating_bonus = 15
                base_score += rating_bonus
                positive_factors["rating"] = (
                    f"Excellent rating ({rating:.1f}/5) (+{rating_bonus} points)"
                )
            elif rating >= 4.0:
                rating_bonus = 10
                base_score += rating_bonus
                positive_factors["rating"] = (
                    f"Good rating ({rating:.1f}/5) (+{rating_bonus} points)"
                )
            elif rating < 3.0:
                rating_penalty = 10
                base_score -= rating_penalty
                negative_factors["low_rating"] = (
                    f"Low rating ({rating:.1f}/5) (-{rating_penalty} points)"
                )

        # Factor 5: Number of reviews (up to +5 points)
        if professional.total_reviews >= 10:
            review_bonus = 5
            base_score += review_bonus
            positive_factors["reviews"] = (
                f"{professional.total_reviews} reviews (+{review_bonus} points)"
            )

        # Ensure score is between 0 and 100
        final_score = max(0.0, min(100.0, base_score))

        return final_score, {"positive": positive_factors, "negative": negative_factors}

    async def _calculate_semantic_description_match(
        self, project_description: str, professional_description: str
    ) -> float:
        """
        Calculate semantic similarity between project and professional descriptions.
        Returns a score between 0 and 100.
        """
        if not project_description or not professional_description:
            logger.warning("Missing descriptions for semantic matching")
            return 0.0

        try:
            similarity = await self.embedding_service.semantic_similarity(
                project_description, professional_description
            )
            # Convert 0-1 similarity to 0-100 score
            return similarity * 100

        except Exception as e:
            logger.error(f"Error in semantic description match: {str(e)}")
            return 0.0

    async def _calculate_skills_semantic_match(
        self, project: any, professional_skills: list
    ) -> tuple[float, list[str]]:
        """
        Calculate how well professional skills match project requirements using embeddings.
        Returns (score 0-100, list of matched skill names).
        """
        if not professional_skills:
            return 0.0, []

        # Check if project has requirements with required skills
        if not project.requirements or "required_skills" not in project.requirements:
            # Fallback: use basic count-based scoring
            skill_count = len(professional_skills)
            base_score = min(skill_count * 10, 50)
            skill_names = [
                skill.skill.name
                for skill in professional_skills
                if hasattr(skill, "skill")
            ]
            return base_score, skill_names

        required_skills = project.requirements.get("required_skills", [])
        if not required_skills:
            return 0.0, []

        try:
            # Get embeddings for all skills
            required_skill_names = [
                req.get("skill_name", "") for req in required_skills
            ]
            professional_skill_names = [
                skill.skill.name
                for skill in professional_skills
                if hasattr(skill, "skill")
            ]

            # Generate embeddings
            required_embeddings = await self.embedding_service.embed_texts(
                required_skill_names
            )
            professional_embeddings = await self.embedding_service.embed_texts(
                professional_skill_names
            )

            # Calculate best matches for each required skill
            matches = []
            matched_skills = []

            for req_emb in required_embeddings:
                if req_emb is None:
                    continue

                best_similarity = 0.0
                best_match_idx = -1

                for j, prof_emb in enumerate(professional_embeddings):
                    if prof_emb is None:
                        continue

                    similarity = self.embedding_service.cosine_similarity(
                        req_emb, prof_emb
                    )

                    if similarity and similarity > best_similarity:
                        best_similarity = similarity
                        best_match_idx = j

                if best_similarity > 0.7:  # Threshold for considering a match
                    matches.append(best_similarity)
                    if best_match_idx >= 0:
                        matched_skills.append(professional_skill_names[best_match_idx])

            # Calculate score based on match quality
            if not matches:
                return 0.0, []

            avg_match_quality = sum(matches) / len(required_skills)
            score = avg_match_quality * 100

            return score, matched_skills

        except Exception as e:
            logger.error(f"Error in skills semantic match: {str(e)}")
            return 0.0, []

    def _generate_recommendation(self, score: float) -> str:
        """Generate a text recommendation based on score."""
        if score >= 80:
            return "Highly Recommended - Excellent match"
        elif score >= 65:
            return "Recommended - Good match"
        elif score >= 50:
            return "Consider - Moderate match"
        else:
            return "Not Recommended - Low match"

    async def get_analysis_by_id(self, analysis_id: UUID) -> AIAnalysis:
        """Get AI analysis by ID."""
        return self.ai_repository.get_by_id(analysis_id)

    async def get_analyses_by_project(
        self, project_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[AIAnalysis]:
        """Get all AI analyses for a project."""
        return self.ai_repository.get_analyses_by_project(
            project_id, skip=skip, limit=limit
        )

    async def get_analyses_by_professional(
        self, professional_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[AIAnalysis]:
        """Get all AI analyses for a professional."""
        return self.ai_repository.get_analyses_by_professional(
            professional_id, skip=skip, limit=limit
        )

    async def get_top_matches_for_project(
        self, project_id: UUID, limit: int = 10
    ) -> list[AIAnalysis]:
        """Get top AI matches for a project."""
        return self.ai_repository.get_top_matches_for_project(project_id, limit=limit)
