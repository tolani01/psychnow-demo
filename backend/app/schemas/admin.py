"""
Admin Schemas
Administrative action requests
"""
from pydantic import BaseModel


class AssignReportRequest(BaseModel):
    """Request to assign a report to a provider"""
    report_id: str
    provider_id: str
    notes: str = ""


class ApproveProviderRequest(BaseModel):
    """Request to approve a provider"""
    provider_id: str
    notes: str = ""

