"""
Screener Schemas
Models for mental health screening tools
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ScreenerQuestion(BaseModel):
    """Individual screener question"""
    number: int
    text: str
    options: List[Dict[str, Any]]  # List of {value: int, label: str}


class ScreenerResponse(BaseModel):
    """Response to a screener question"""
    question_number: int
    value: int


class ScreenerResult(BaseModel):
    """Result of a completed screener"""
    name: str
    score: int
    max_score: int
    interpretation: str
    severity: Optional[str] = None
    clinical_significance: Optional[str] = None
    subscales: Optional[Dict[str, Any]] = None


class ScreenerAdministration(BaseModel):
    """Request to administer a screener"""
    screener_name: str
    responses: List[ScreenerResponse]

