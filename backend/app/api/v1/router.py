"""Main API router for v1 endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, professionals, clients, projects, proposals, reviews, skills

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(professionals.router, prefix="/professionals", tags=["Professionals"])
api_router.include_router(clients.router, prefix="/clients", tags=["Clients"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(proposals.router, prefix="/proposals", tags=["Proposals"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(skills.router, prefix="/skills", tags=["Skills"]) 