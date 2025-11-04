"""Custom exceptions for the application."""

from typing import Any


class SaaSPlatformException(Exception):
    """Base exception for SaaS Platform."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize exception."""
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ValidationError(SaaSPlatformException):
    """Validation error exception."""

    def __init__(self, message: str, field: str | None = None) -> None:
        """Initialize validation error."""
        super().__init__(message, "VALIDATION_ERROR", {"field": field})


class AuthenticationError(SaaSPlatformException):
    """Authentication error exception."""

    def __init__(self, message: str = "Authentication failed") -> None:
        """Initialize authentication error."""
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(SaaSPlatformException):
    """Authorization error exception."""

    def __init__(self, message: str = "Insufficient permissions") -> None:
        """Initialize authorization error."""
        super().__init__(message, "AUTHORIZATION_ERROR")


class NotFoundError(SaaSPlatformException):
    """Resource not found exception."""

    def __init__(self, resource: str, resource_id: str | None = None) -> None:
        """Initialize not found error."""
        message = f"{resource} not found"
        if resource_id:
            message += f" with id: {resource_id}"
        super().__init__(
            message,
            "NOT_FOUND_ERROR",
            {"resource": resource, "resource_id": resource_id},
        )


class ConflictError(SaaSPlatformException):
    """Resource conflict exception."""

    def __init__(self, message: str, resource: str | None = None) -> None:
        """Initialize conflict error."""
        super().__init__(message, "CONFLICT_ERROR", {"resource": resource})


class DatabaseError(SaaSPlatformException):
    """Database error exception."""

    def __init__(self, message: str, operation: str | None = None) -> None:
        """Initialize database error."""
        super().__init__(message, "DATABASE_ERROR", {"operation": operation})


class ExternalServiceError(SaaSPlatformException):
    """External service error exception."""

    def __init__(self, message: str, service: str | None = None) -> None:
        """Initialize external service error."""
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", {"service": service})


class RateLimitError(SaaSPlatformException):
    """Rate limit exceeded exception."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        """Initialize rate limit error."""
        super().__init__(message, "RATE_LIMIT_ERROR")


class BusinessLogicError(SaaSPlatformException):
    """Business logic error exception."""

    def __init__(self, message: str, business_rule: str | None = None) -> None:
        """Initialize business logic error."""
        super().__init__(
            message, "BUSINESS_LOGIC_ERROR", {"business_rule": business_rule}
        )
