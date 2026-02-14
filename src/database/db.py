"""
Database connection and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from src.utils.config import settings
from src.database.models import Base

# Create database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")


@contextmanager
def get_db() -> Session:
    """
    Context manager for database sessions.
    
    Usage:
        with get_db() as db:
            # perform database operations
            pass
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get a database session (for dependency injection in FastAPI).
    Remember to close the session after use.
    """
    db = SessionLocal()
    try:
        return db
    finally:
        pass
