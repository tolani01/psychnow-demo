"""
Feedback Schemas
Pydantic models for feedback submission
"""
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class FeedbackSubmissionCreate(BaseModel):
    """Schema for submitting feedback"""
    session_id: str = Field(..., description="Session ID from assessment")
    
    # Ratings (1-5)
    conversation_rating: int = Field(..., ge=1, le=5, description="Conversation flow rating")
    patient_report_rating: int = Field(..., ge=1, le=5, description="Patient report quality rating")
    clinician_report_rating: int = Field(..., ge=1, le=5, description="Clinician report quality rating")
    
    # Practice adoption
    would_use: str = Field(..., description="Would you use this in practice?")
    
    # Open-ended feedback (optional)
    strength: Optional[str] = Field(None, max_length=2000, description="Biggest strength")
    concern: Optional[str] = Field(None, max_length=2000, description="Biggest concern")
    missing_patient: Optional[str] = Field(None, max_length=2000, description="Missing from patient report")
    missing_clinician: Optional[str] = Field(None, max_length=2000, description="Missing from clinician report")
    additional_comments: Optional[str] = Field(None, max_length=5000, description="Additional comments")
    
    # Optional tester info
    tester_email: Optional[EmailStr] = None
    tester_name: Optional[str] = Field(None, max_length=255)
    
    @field_validator('would_use')
    @classmethod
    def validate_would_use(cls, v):
        valid_options = ['yes_definitely', 'yes_probably', 'maybe', 'probably_not', 'no']
        if v not in valid_options:
            raise ValueError(f"must be one of: {', '.join(valid_options)}")
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "abc123",
                "conversation_rating": 5,
                "patient_report_rating": 4,
                "clinician_report_rating": 5,
                "would_use": "yes_probably",
                "strength": "Very natural conversation flow",
                "concern": "Need more trauma history",
                "tester_email": "dr.smith@hospital.com",
                "tester_name": "Dr. Jane Smith"
            }
        }
    }


class FeedbackSubmissionResponse(BaseModel):
    """Response after feedback submission"""
    id: str
    session_id: str
    submitted_at: datetime
    message: str = "Thank you for your feedback!"
    
    model_config = {"from_attributes": True}

