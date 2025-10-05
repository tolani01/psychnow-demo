"""
Intake Schemas
Models for intake session and conversation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime


class ChatMessage(BaseModel):
    """Individual chat message"""
    role: str = Field(..., pattern="^(user|model)$")
    content: str
    timestamp: datetime


class IntakeSessionCreate(BaseModel):
    """Create a new intake session"""
    patient_id: Optional[str] = None  # Null for anonymous
    user_name: Optional[str] = None  # Authenticated user's name to skip name question


class IntakeSessionResponse(BaseModel):
    """Intake session response"""
    id: str
    session_token: str
    current_phase: Optional[str] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Request to send a chat message"""
    session_token: str
    prompt: str


class ChatResponse(BaseModel):
    """Response from chat endpoint"""
    role: str
    content: str
    timestamp: datetime
    done: bool = False
    options: Optional[List[Dict[str, Union[str, int]]]] = None  # For clickable buttons
    pdf_report: Optional[str] = None  # Base64 encoded PDF report (legacy/patient)
    patient_pdf: Optional[str] = None  # Base64 encoded patient PDF
    clinician_pdf: Optional[str] = None  # Base64 encoded clinician PDF


class FinishIntakeRequest(BaseModel):
    """Request to finish intake and generate report"""
    session_token: str

