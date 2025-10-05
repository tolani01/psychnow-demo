"""
SQLAlchemy Base
Base class for all ORM models
"""
from sqlalchemy.ext.declarative import declarative_base

# Create base class for models
Base = declarative_base()

# Note: Models are imported in alembic/env.py for migration detection
# Do NOT import models here to avoid circular imports

