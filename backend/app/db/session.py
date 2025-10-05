"""
Database Session Management
Creates and manages database connections
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine with error handling
engine: Optional[object] = None
SessionLocal: Optional[sessionmaker] = None

try:
    if "sqlite" in settings.DATABASE_URL:
        # SQLite configuration
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=settings.DEBUG,
        )
    else:
        # PostgreSQL configuration with connection pooling
        # Note: SSL connection handled by DATABASE_URL parameters
        engine = create_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=5,  # Reduced for Render free tier
            max_overflow=10,
        )
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database connection established successfully")
    
except Exception as e:
    logger.error(f"Failed to establish database connection: {e}")
    logger.warning("Running in database-less mode - some features may be limited")
    engine = None
    SessionLocal = None


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session
    
    Yields:
        Database session
    """
    if SessionLocal is None:
        # Return a mock session that doesn't do anything
        class MockQuery:
            def filter(self, *args): return self
            def first(self): return None
            def all(self): return []
            def count(self): return 0
        
        class MockSession:
            def add(self, obj): pass
            def commit(self): pass
            def refresh(self, obj): pass
            def close(self): pass
            def query(self, model): return MockQuery()
            def __enter__(self): return self
            def __exit__(self, *args): pass
        yield MockSession()
        return
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

