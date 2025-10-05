"""
Consent Schemas
Models for consent management
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConsentCreate(BaseModel):
    """Create a new consent record"""
    consent_type: str  # hipaa, telehealth, financial
    version: str = "1.0"
    content_hash: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class ConsentResponse(BaseModel):
    """Consent record response"""
    id: str
    user_id: str
    consent_type: str
    version: str
    accepted_at: datetime
    revoked_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ConsentStatus(BaseModel):
    """User's consent status"""
    hipaa: bool = False
    telehealth: bool = False
    financial: bool = False
    all_required_consents_given: bool = False

