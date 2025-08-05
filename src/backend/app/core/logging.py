"""Logging configuration for the application."""

import logging
import sys
import uuid
from typing import Any, Dict

import structlog
from structlog.types import Processor

from app.core.config import settings


def setup_logging() -> None:
    """Setup structured logging configuration."""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.log_format == "json" else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def add_correlation_id(logger: structlog.BoundLogger, correlation_id: str) -> structlog.BoundLogger:
    """Add correlation ID to logger context."""
    return logger.bind(correlation_id=correlation_id)


def get_correlation_id() -> str:
    """Generate a new correlation ID."""
    return str(uuid.uuid4())


class CorrelationIdMiddleware:
    """Middleware to add correlation ID to request context."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        """Add correlation ID to request scope."""
        correlation_id = get_correlation_id()
        scope["correlation_id"] = correlation_id
        
        # Add correlation ID to logger context
        logger = get_logger("http")
        logger = add_correlation_id(logger, correlation_id)
        scope["logger"] = logger
        
        await self.app(scope, receive, send)


def log_request(logger: structlog.BoundLogger, method: str, path: str, status_code: int, duration: float) -> None:
    """Log HTTP request details."""
    logger.info(
        "HTTP request",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=round(duration * 1000, 2),
    )


def log_error(logger: structlog.BoundLogger, error: Exception, context: Dict[str, Any] = None) -> None:
    """Log error with context."""
    logger.error(
        "Application error",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {},
        exc_info=True,
    )


def log_database_operation(logger: structlog.BoundLogger, operation: str, table: str, duration: float) -> None:
    """Log database operation."""
    logger.info(
        "Database operation",
        operation=operation,
        table=table,
        duration_ms=round(duration * 1000, 2),
    )


def log_external_service_call(
    logger: structlog.BoundLogger,
    service: str,
    endpoint: str,
    method: str,
    status_code: int,
    duration: float,
) -> None:
    """Log external service call."""
    logger.info(
        "External service call",
        service=service,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        duration_ms=round(duration * 1000, 2),
    ) 