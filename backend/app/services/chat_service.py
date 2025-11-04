"""AI Chat service for intelligent Q&A about recommendations."""

import logging

from app.services.ai_service import AIService
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class ChatService:
    """Service for AI-powered chat about projects and professionals."""

    def __init__(
        self,
        ai_service: AIService,
        embedding_service: EmbeddingService | None = None,
    ):
        """Initialize chat service."""
        self.ai_service = ai_service
        self.embedding_service = embedding_service or EmbeddingService()

    async def chat(
        self,
        message: str,
        context: dict | None = None,
        user_type: str = "professional",
    ) -> dict:
        """
        Process a chat message and generate an intelligent response.

        Args:
            message: User's question/message
            context: Optional context (project_id, professional_id, recommendations, etc)
            user_type: "professional" or "client"

        Returns:
            dict with 'response', 'suggestions', 'data'
        """
        message_lower = message.lower().strip()

        # Detect intent
        intent = self._detect_intent(message_lower, context)

        # Generate response based on intent
        if intent == "why_recommended":
            return await self._explain_recommendation(message_lower, context)

        elif intent == "compare":
            return await self._compare_options(message_lower, context)

        elif intent == "best_match":
            return await self._find_best_match(message_lower, context, user_type)

        elif intent == "list_recommendations":
            return await self._list_recommendations(context, user_type)

        elif intent == "explain_score":
            return await self._explain_score(message_lower, context)

        else:
            return self._general_response(message_lower, user_type)

    def _detect_intent(self, message: str, context: dict | None) -> str:
        """Detect user intent from message."""
        # Why/explanation questions
        if any(
            word in message
            for word in ["why", "porque", "por que", "reason", "explain"]
        ):
            if context and ("project_id" in context or "professional_id" in context):
                return "why_recommended"
            return "explain_score"

        # Comparison questions
        if any(
            word in message
            for word in [
                "compare",
                "comparar",
                "difference",
                "diferença",
                "versus",
                "vs",
            ]
        ):
            return "compare"

        # Best match questions
        if any(word in message for word in ["best", "melhor", "top", "recommend"]):
            return "best_match"

        # List questions
        if any(
            word in message
            for word in ["list", "show", "listar", "mostrar", "quais", "what"]
        ):
            return "list_recommendations"

        # Score questions
        if any(
            word in message
            for word in ["score", "rating", "nota", "pontuação", "percentage"]
        ):
            return "explain_score"

        return "general"

    async def _explain_recommendation(self, message: str, context: dict | None) -> dict:
        """Explain why something was recommended."""
        if not context:
            return {
                "response": "I need more context to explain a recommendation. Which project or professional are you asking about?",
                "suggestions": [
                    "Show me recommended projects",
                    "Show me recommended professionals",
                ],
            }

        recommendation = context.get("recommendation")

        if not recommendation:
            return {
                "response": "I don't have the recommendation details. Try viewing the recommendations page first.",
                "suggestions": ["Show me my recommended projects"],
            }

        # Build explanation
        score = recommendation.get("compatibility_score", 0)
        positive = recommendation.get("positive_factors", {})
        negative = recommendation.get("negative_factors", {})

        response = f"This match has a compatibility score of **{score:.1f}%**.\n\n"

        if positive:
            response += "**Why it's a good match:**\n"
            for _key, value in list(positive.items())[:3]:
                response += f"• {value}\n"
            response += "\n"

        if negative:
            response += "**Things to consider:**\n"
            for _key, value in list(negative.items())[:2]:
                response += f"• {value}\n"

        return {
            "response": response,
            "suggestions": [
                "What's the best match for me?",
                "Show me more details",
                "Compare this with others",
            ],
            "data": recommendation,
        }

    async def _compare_options(self, message: str, context: dict | None) -> dict:
        """Compare multiple options."""
        if not context or "recommendations" not in context:
            return {
                "response": "I need a list of recommendations to compare. Try viewing the recommendations page first.",
                "suggestions": ["Show me recommended projects"],
            }

        recommendations = context.get("recommendations", [])[:3]

        if len(recommendations) < 2:
            return {
                "response": "I need at least 2 options to compare. Currently, there's only 1 recommendation available.",
                "suggestions": ["Tell me about this recommendation"],
            }

        response = "Here's a comparison of the top matches:\n\n"

        for i, rec in enumerate(recommendations, 1):
            score = rec.get("compatibility_score", 0)
            title = rec.get("project_title") or rec.get("professional_name", "Option")
            response += f"**{i}. {title}** - {score:.1f}% match\n"

            positive = rec.get("positive_factors", {})
            if positive:
                top_factor = list(positive.values())[0]
                response += f"   ✓ {top_factor}\n"

        response += "\n💡 The first option has the highest compatibility score!"

        return {
            "response": response,
            "suggestions": [
                "Why is #1 the best?",
                "Show me more about #1",
                "What about #2?",
            ],
            "data": {"compared": recommendations},
        }

    async def _find_best_match(
        self, message: str, context: dict | None, user_type: str
    ) -> dict:
        """Find the best match for the user."""
        response = ""

        if user_type == "professional":
            response = "Looking for the best projects for you...\n\n"
            response += "I analyze projects based on:\n"
            response += "• Your skills and experience\n"
            response += "• Project requirements\n"
            response += "• Your ratings and reviews\n"
            response += "• Semantic matching of descriptions\n\n"
            response += (
                "💡 Check the 'Recommended Projects' page to see your top matches!"
            )
        else:
            response = "Looking for the best professionals for your project...\n\n"
            response += "I analyze professionals based on:\n"
            response += "• Skills matching your requirements\n"
            response += "• Their ratings and experience\n"
            response += "• Semantic matching of profiles\n"
            response += "• Success rate and reviews\n\n"
            response += "💡 View your project details to see recommended professionals!"

        return {
            "response": response,
            "suggestions": [
                "Show me recommended projects"
                if user_type == "professional"
                else "Show me recommended professionals",
                "How do you calculate the score?",
                "What makes a good match?",
            ],
        }

    async def _list_recommendations(self, context: dict | None, user_type: str) -> dict:
        """List available recommendations."""
        if not context or "recommendations" not in context:
            return {
                "response": "I don't have any recommendations loaded. Navigate to the recommendations page to see your matches!",
                "suggestions": [
                    "How do you find matches?",
                    "What's a good compatibility score?",
                ],
            }

        recommendations = context.get("recommendations", [])[:5]

        response = f"Here are your top {len(recommendations)} recommendations:\n\n"

        for i, rec in enumerate(recommendations, 1):
            score = rec.get("compatibility_score", 0)
            title = rec.get("project_title") or rec.get("professional_name", "Match")
            rating = rec.get("average_rating")

            response += f"{i}. **{title}** - {score:.1f}% match"
            if rating:
                response += f" ⭐ {float(rating):.1f}/5"
            response += "\n"

        return {
            "response": response,
            "suggestions": [
                "Why is #1 recommended?",
                "Compare top 3",
                "Tell me more about #1",
            ],
            "data": {"recommendations": recommendations},
        }

    async def _explain_score(self, message: str, context: dict | None) -> dict:
        """Explain how compatibility scores work."""
        response = """**How Compatibility Scores Work:**

I calculate a score from 0-100% based on multiple factors:

**For Professionals:**
• **Skills Match (30%)** - How well your skills match project requirements
• **Description Match (40%)** - Semantic similarity between your profile and project
• **Rating & Reviews (20%)** - Your average rating and experience level
• **Review Count (10%)** - Bonus for experienced professionals

**Score Ranges:**
• 80-100%: Highly Recommended - Excellent match
• 65-79%: Recommended - Good match
• 50-64%: Consider - Moderate match
• 0-49%: Not Recommended - Low match

The algorithm uses semantic AI to understand the *meaning* of text, not just keywords!
"""

        return {
            "response": response,
            "suggestions": [
                "Show me my best matches",
                "What's semantic AI?",
                "How can I improve my score?",
            ],
        }

    def _general_response(self, message: str, user_type: str) -> dict:
        """Generate a general response."""
        if "hello" in message or "hi" in message or "oi" in message:
            greeting = (
                "Hello! 👋 I'm your AI assistant. I can help you:"
                if "hello" in message or "hi" in message
                else "Olá! 👋 Sou seu assistente de IA. Posso ajudar você a:"
            )

            suggestions = [
                "Find the best projects for you",
                "Explain why something was recommended",
                "Compare different options",
                "Understand compatibility scores",
            ]

            return {"response": greeting, "suggestions": suggestions}

        return {
            "response": "I can help you understand recommendations and find the best matches! Try asking me something like:",
            "suggestions": [
                "Why was this recommended?",
                "What's my best match?",
                "Compare the top 3",
                "How do scores work?",
            ],
        }
