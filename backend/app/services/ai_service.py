"""AI service."""

from typing import List, Dict, Tuple
from uuid import UUID
from datetime import datetime

from app.repositories.ai_repository import AIRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.models.ai_analysis import AIAnalysis


class AIService:
    """AI service class."""

    def __init__(self, ai_repository: AIRepository, project_repository: ProjectRepository, professional_repository: ProfessionalRepository):
        """Initialize service."""
        self.ai_repository = ai_repository
        self.project_repository = project_repository
        self.professional_repository = professional_repository

    async def recommend_professionals_for_project(self, project_id: UUID, limit: int = 10) -> List[Dict]:
        """
        Recommend professionals for a project based on skills and ratings.
        Returns list of recommended professionals with compatibility scores.
        """
        # Get project
        project = self.project_repository.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found")

        # Get all professionals
        all_professionals = self.professional_repository.list_professionals(skip=0, limit=1000)

        # Calculate compatibility scores for each professional
        recommendations = []
        for professional in all_professionals:
            score, factors = await self._calculate_compatibility_score(project_id, professional.id)

            # Store AI analysis
            analysis = self.ai_repository.create(
                project_id=project_id,
                professional_id=professional.id,
                compatibility_score=score,
                positive_factors=factors['positive'],
                negative_factors=factors['negative'],
                recommendation=self._generate_recommendation(score),
                model_version="v1.0-basic",
                analysis_date=datetime.utcnow().isoformat()
            )

            recommendations.append({
                'professional_id': professional.id,
                'professional_name': professional.title,
                'compatibility_score': score,
                'hourly_rate': professional.hourly_rate,
                'average_rating': professional.average_rating,
                'total_reviews': professional.total_reviews,
                'positive_factors': factors['positive'],
                'negative_factors': factors['negative'],
                'recommendation': self._generate_recommendation(score)
            })

        # Sort by compatibility score
        recommendations.sort(key=lambda x: x['compatibility_score'], reverse=True)

        return recommendations[:limit]

    async def recommend_projects_for_professional(self, professional_id: UUID, limit: int = 10) -> List[Dict]:
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
        all_projects = self.project_repository.get_projects_by_status(ProjectStatus.OPEN, skip=0, limit=1000)

        # Calculate compatibility scores for each project
        recommendations = []
        for project in all_projects:
            score, factors = await self._calculate_compatibility_score(project.id, professional_id)

            recommendations.append({
                'project_id': project.id,
                'project_title': project.title,
                'compatibility_score': score,
                'budget': project.budget,
                'deadline': project.deadline,
                'client_id': project.client_id,
                'positive_factors': factors['positive'],
                'negative_factors': factors['negative'],
                'recommendation': self._generate_recommendation(score)
            })

        # Sort by compatibility score
        recommendations.sort(key=lambda x: x['compatibility_score'], reverse=True)

        return recommendations[:limit]

    async def calculate_compatibility_score(self, project_id: UUID, professional_id: UUID) -> float:
        """
        Calculate compatibility score between a project and a professional.
        Returns a score between 0 and 100.
        """
        score, _ = await self._calculate_compatibility_score(project_id, professional_id)
        return score

    async def _calculate_compatibility_score(self, project_id: UUID, professional_id: UUID) -> Tuple[float, Dict]:
        """
        Internal method to calculate compatibility score with detailed factors.
        This is a simple implementation that can be enhanced with real AI later.
        """
        # Get professional and their skills
        professional = self.professional_repository.get_by_id(professional_id)
        if not professional:
            return 0.0, {'positive': {}, 'negative': {}}

        professional_skills = self.professional_repository.get_professional_skills(professional_id)

        # Base score starts at 50
        base_score = 50.0
        positive_factors = {}
        negative_factors = {}

        # Factor 1: Professional has skills (up to +20 points)
        if professional_skills:
            skill_bonus = min(len(professional_skills) * 2, 20)
            base_score += skill_bonus
            positive_factors['skills_count'] = f"Has {len(professional_skills)} skills (+{skill_bonus} points)"

            # Factor 2: High proficiency levels (up to +10 points)
            avg_proficiency = sum(skill.proficiency_level for skill in professional_skills) / len(professional_skills)
            if avg_proficiency >= 4:
                proficiency_bonus = 10
                base_score += proficiency_bonus
                positive_factors['proficiency'] = f"High average proficiency ({avg_proficiency:.1f}/5) (+{proficiency_bonus} points)"

            # Factor 3: Certified skills (up to +10 points)
            certified_count = sum(1 for skill in professional_skills if skill.certified)
            if certified_count > 0:
                cert_bonus = min(certified_count * 5, 10)
                base_score += cert_bonus
                positive_factors['certifications'] = f"{certified_count} certified skills (+{cert_bonus} points)"
        else:
            negative_factors['no_skills'] = "No skills listed (-10 points)"
            base_score -= 10

        # Factor 4: Professional rating (up to +15 points or -10 points)
        if professional.average_rating:
            rating = float(professional.average_rating)
            if rating >= 4.5:
                rating_bonus = 15
                base_score += rating_bonus
                positive_factors['rating'] = f"Excellent rating ({rating:.1f}/5) (+{rating_bonus} points)"
            elif rating >= 4.0:
                rating_bonus = 10
                base_score += rating_bonus
                positive_factors['rating'] = f"Good rating ({rating:.1f}/5) (+{rating_bonus} points)"
            elif rating < 3.0:
                rating_penalty = 10
                base_score -= rating_penalty
                negative_factors['low_rating'] = f"Low rating ({rating:.1f}/5) (-{rating_penalty} points)"

        # Factor 5: Number of reviews (up to +5 points)
        if professional.total_reviews >= 10:
            review_bonus = 5
            base_score += review_bonus
            positive_factors['reviews'] = f"{professional.total_reviews} reviews (+{review_bonus} points)"

        # Ensure score is between 0 and 100
        final_score = max(0.0, min(100.0, base_score))

        return final_score, {'positive': positive_factors, 'negative': negative_factors}

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

    async def get_analyses_by_project(self, project_id: UUID, skip: int = 0, limit: int = 20) -> List[AIAnalysis]:
        """Get all AI analyses for a project."""
        return self.ai_repository.get_analyses_by_project(project_id, skip=skip, limit=limit)

    async def get_analyses_by_professional(self, professional_id: UUID, skip: int = 0, limit: int = 20) -> List[AIAnalysis]:
        """Get all AI analyses for a professional."""
        return self.ai_repository.get_analyses_by_professional(professional_id, skip=skip, limit=limit)

    async def get_top_matches_for_project(self, project_id: UUID, limit: int = 10) -> List[AIAnalysis]:
        """Get top AI matches for a project."""
        return self.ai_repository.get_top_matches_for_project(project_id, limit=limit)