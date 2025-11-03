"""Database session management."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.database.base import Base

# Create engine
engine = create_engine(
    settings.database_url,
    poolclass=StaticPool,
    echo=settings.debug,
    pool_pre_ping=False,  # Disabled due to psycopg2 + Python 3.13 compatibility issue
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """Get database session without dependency injection."""
    return SessionLocal()


def create_tables() -> None:
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """Drop all tables."""
    Base.metadata.drop_all(bind=engine)
