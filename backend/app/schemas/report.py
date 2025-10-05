"""
Report Schemas
Models for intake reports
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class ReportResponse(BaseModel):
    """Intake report response"""
    id: str
    session_id: str
    patient_id: Optional[str] = None
    report_data: Dict[str, Any]
    severity_level: Optional[str] = None
    risk_level: Optional[str] = None
    urgency: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReportListItem(BaseModel):
    """Simplified report for list views"""
    id: str
    patient_id: Optional[str] = None
    severity_level: Optional[str] = None
    risk_level: Optional[str] = None
    urgency: Optional[str] = None
    created_at: datetime
    chief_complaint: Optional[str] = None
    
    class Config:
        from_attributes = True


class AssignReportRequest(BaseModel):
    """Request to assign report to provider"""
    report_id: str
    provider_id: str

