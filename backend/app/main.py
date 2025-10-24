"""Main FastAPI application."""

import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from structlog import get_logger

from app.core.config import settings
from app.core.container import container
from app.core.exceptions import SaaSPlatformException, AuthenticationError, AuthorizationError, NotFoundError, ConflictError
from app.core.logging import setup_logging, CorrelationIdMiddleware, log_request, log_error
from app.core.sentry import init_sentry
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    setup_logging()
    init_sentry()  # Initialize Sentry for error tracking
    logger = get_logger("app")
    logger.info("Starting SaaS Platform API")
    
    # Initialize container
    container.config.from_dict(settings.model_dump())
    container.wire(modules=[
        "app.api.v1.endpoints.auth",
        "app.api.v1.endpoints.users",
        "app.api.v1.endpoints.professionals",
        "app.api.v1.endpoints.clients",
        "app.api.v1.endpoints.projects",
        "app.api.v1.endpoints.proposals",
        "app.api.v1.endpoints.reviews",
        "app.api.v1.endpoints.skills",
    ])
    
    yield
    
    # Shutdown
    logger.info("Shutting down SaaS Platform API")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="SaaS Platform API for connecting professionals with clients",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # Configure appropriately for production
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to response."""
    start_time = time.time()
    
    # Get correlation ID from request scope
    correlation_id = request.scope.get("correlation_id", "unknown")
    logger = get_logger("http").bind(correlation_id=correlation_id)
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Correlation-ID"] = correlation_id
    
    # Log request
    log_request(
        logger=logger,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration=process_time,
    )
    
    return response


@app.exception_handler(AuthenticationError)
async def authentication_exception_handler(request: Request, exc: AuthenticationError):
    """Handle authentication exceptions."""
    logger = get_logger("app")
    log_error(logger, exc, {"path": request.url.path})

    return JSONResponse(
        status_code=401,
        content={
            "error_code": exc.error_code or "AUTHENTICATION_ERROR",
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(AuthorizationError)
async def authorization_exception_handler(request: Request, exc: AuthorizationError):
    """Handle authorization exceptions."""
    logger = get_logger("app")
    log_error(logger, exc, {"path": request.url.path})

    return JSONResponse(
        status_code=403,
        content={
            "error_code": exc.error_code or "AUTHORIZATION_ERROR",
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request: Request, exc: NotFoundError):
    """Handle not found exceptions."""
    logger = get_logger("app")
    log_error(logger, exc, {"path": request.url.path})

    return JSONResponse(
        status_code=404,
        content={
            "error_code": exc.error_code or "NOT_FOUND_ERROR",
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(ConflictError)
async def conflict_exception_handler(request: Request, exc: ConflictError):
    """Handle conflict exceptions."""
    logger = get_logger("app")
    log_error(logger, exc, {"path": request.url.path})

    return JSONResponse(
        status_code=409,
        content={
            "error_code": exc.error_code or "CONFLICT_ERROR",
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(SaaSPlatformException)
async def saas_platform_exception_handler(request: Request, exc: SaaSPlatformException):
    """Handle generic SaaS Platform exceptions."""
    logger = get_logger("app")
    log_error(logger, exc, {"path": request.url.path})

    return JSONResponse(
        status_code=400,
        content={
            "error_code": exc.error_code or "APPLICATION_ERROR",
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger = get_logger("app")
    log_error(logger, exc, {"path": request.url.path})
    
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": {},
        },
    )


# Include API routes
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "SaaS Platform API",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    ) 