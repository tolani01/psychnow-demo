"""
Common API response schemas
"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    """Standardized API response wrapper"""
    success: bool = True
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Standardized error response"""
    success: bool = False
    error: str
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Any] = None


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    success: bool = True
    data: Any
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
