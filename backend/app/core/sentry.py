"""Sentry integration for error tracking and monitoring."""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.config import settings


def init_sentry():
    """Initialize Sentry for error tracking."""
    if not settings.sentry_dsn_backend:
        # Sentry not configured, skip initialization
        return

    sentry_sdk.init(
        dsn=settings.sentry_dsn_backend,
        environment=settings.sentry_environment,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
        # Set release version
        release=f"saas-platform@{settings.app_version}",
        # Send default PII (Personally Identifiable Information)
        send_default_pii=False,
        # Enable performance monitoring
        enable_tracing=True,
        # Debug mode (set to False in production)
        debug=settings.debug,
    )


def capture_exception(exception: Exception, context: dict = None):
    """
    Capture exception and send to Sentry.

    Args:
        exception: The exception to capture
        context: Additional context data
    """
    if context:
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_context(key, value)
            sentry_sdk.capture_exception(exception)
    else:
        sentry_sdk.capture_exception(exception)


def capture_message(message: str, level: str = "info", context: dict = None):
    """
    Capture message and send to Sentry.

    Args:
        message: The message to capture
        level: Message level (debug, info, warning, error, fatal)
        context: Additional context data
    """
    if context:
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_context(key, value)
            sentry_sdk.capture_message(message, level)
    else:
        sentry_sdk.capture_message(message, level)


def set_user(user_id: str, email: str = None, username: str = None):
    """
    Set user context for Sentry events.

    Args:
        user_id: User ID
        email: User email (optional)
        username: Username (optional)
    """
    sentry_sdk.set_user(
        {
            "id": user_id,
            "email": email,
            "username": username,
        }
    )


def set_tag(key: str, value: str):
    """
    Set tag for Sentry events.

    Args:
        key: Tag key
        value: Tag value
    """
    sentry_sdk.set_tag(key, value)


def set_context(name: str, context: dict):
    """
    Set context for Sentry events.

    Args:
        name: Context name
        context: Context data
    """
    sentry_sdk.set_context(name, context)
