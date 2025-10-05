"""
Compliance Pydantic schemas
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    """Schema for audit log response"""
    id: int
    event_type: str
    severity: str
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    description: str
    details: Optional[Dict[str, Any]] = None
    endpoint: Optional[str] = None
    http_method: Optional[str] = None
    response_status: Optional[int] = None
    timestamp: str


class AuditLogListResponse(BaseModel):
    """Schema for audit log list response"""
    audit_logs: List[AuditLogResponse]
    total_count: int


class DataAccessLogResponse(BaseModel):
    """Schema for data access log response"""
    id: int
    user_id: int
    user_name: str
    patient_id: int
    patient_name: str
    data_type: str
    data_id: str
    access_type: str
    reason: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    fields_accessed: Optional[List[str]] = None
    access_duration: Optional[int] = None
    accessed_at: str


class DataAccessLogListResponse(BaseModel):
    """Schema for data access log list response"""
    access_logs: List[DataAccessLogResponse]
    total_count: int


class ComplianceSummaryPeriod(BaseModel):
    """Schema for compliance summary period"""
    start_date: str
    end_date: str


class AuditLogSummary(BaseModel):
    """Schema for audit log summary"""
    total_events: int
    by_severity: Dict[str, int]


class ComplianceCheckSummary(BaseModel):
    """Schema for compliance check summary"""
    total_checks: int
    passed: int
    failed: int
    by_type: Dict[str, Dict[str, int]]


class DataAccessSummary(BaseModel):
    """Schema for data access summary"""
    total_accesses: int
    by_type: Dict[str, int]


class SecurityIncidentSummary(BaseModel):
    """Schema for security incident summary"""
    open_incidents: int


class ComplianceSummaryResponse(BaseModel):
    """Schema for compliance summary response"""
    period: ComplianceSummaryPeriod
    audit_logs: AuditLogSummary
    compliance_checks: ComplianceCheckSummary
    data_access: DataAccessSummary
    security_incidents: SecurityIncidentSummary


class SecurityIncidentRequest(BaseModel):
    """Schema for security incident request"""
    incident_type: str = Field(..., description="Type of security incident")
    severity: str = Field(..., description="Severity level")
    title: str = Field(..., description="Incident title")
    description: str = Field(..., description="Incident description")
    affected_users: Optional[List[int]] = Field(None, description="List of affected user IDs")
    affected_data: Optional[Dict[str, Any]] = Field(None, description="Description of affected data")


class SecurityIncidentResponse(BaseModel):
    """Schema for security incident response"""
    success: bool
    incident_id: Optional[int] = None
    message: str


class PrivacyConsentRequest(BaseModel):
    """Schema for privacy consent request"""
    consent_type: str = Field(..., description="Type of consent")
    consent_text: str = Field(..., description="Full consent text")
    consent_method: str = Field(..., description="Method of consent (digital_signature, verbal, written)")
    witnessed_by: Optional[int] = Field(None, description="ID of witness user")
    ip_address: Optional[str] = Field(None, description="IP address of consent")
    user_agent: Optional[str] = Field(None, description="User agent string")


class PrivacyConsentResponse(BaseModel):
    """Schema for privacy consent response"""
    success: bool
    consent_id: Optional[int] = None
    version: Optional[str] = None
    message: str


class PrivacyConsentSummary(BaseModel):
    """Schema for privacy consent summary"""
    id: int
    consent_type: str
    consent_version: str
    given: bool
    given_at: Optional[str] = None
    withdrawn_at: Optional[str] = None
    consent_method: str
    witnessed_by: Optional[int] = None
    created_at: str


class PrivacyConsentListResponse(BaseModel):
    """Schema for privacy consent list response"""
    consents: List[PrivacyConsentSummary]
    total_count: int


class ComplianceCheckResponse(BaseModel):
    """Schema for compliance check response"""
    success: bool
    check_id: Optional[int] = None
    passed: bool
    details: Optional[Dict[str, Any]] = None
    recommendations: Optional[str] = None
    error: Optional[str] = None


class DataRetentionPolicyRequest(BaseModel):
    """Schema for data retention policy request"""
    data_type: str = Field(..., description="Type of data to retain")
    retention_period_days: int = Field(..., ge=1, description="Retention period in days")
    description: Optional[str] = Field(None, description="Policy description")


class DataRetentionPolicyResponse(BaseModel):
    """Schema for data retention policy response"""
    success: bool
    policy_id: Optional[int] = None
    message: str


class ComplianceReportRequest(BaseModel):
    """Schema for compliance report request"""
    report_type: str = Field(..., description="Type of compliance report")
    report_name: str = Field(..., description="Name of the report")
    period_start: str = Field(..., description="Report period start date")
    period_end: str = Field(..., description="Report period end date")
    summary: Optional[str] = Field(None, description="Report summary")
    findings: Optional[Dict[str, Any]] = Field(None, description="Report findings")
    recommendations: Optional[str] = Field(None, description="Report recommendations")


class ComplianceReportResponse(BaseModel):
    """Schema for compliance report response"""
    success: bool
    report_id: Optional[int] = None
    message: str


class DataBreachNotificationRequest(BaseModel):
    """Schema for data breach notification request"""
    breach_type: str = Field(..., description="Type of data breach")
    severity: str = Field(..., description="Severity of the breach")
    description: str = Field(..., description="Description of the breach")
    affected_data_types: List[str] = Field(..., description="Types of data affected")
    affected_users: Optional[List[int]] = Field(None, description="List of affected user IDs")
    discovery_date: str = Field(..., description="Date when breach was discovered")
    containment_date: Optional[str] = Field(None, description="Date when breach was contained")


class DataBreachNotificationResponse(BaseModel):
    """Schema for data breach notification response"""
    success: bool
    incident_id: Optional[int] = None
    message: str


class HIPAAComplianceStatus(BaseModel):
    """Schema for HIPAA compliance status"""
    overall_status: str
    last_assessment_date: str
    compliance_score: float
    areas_of_concern: List[str]
    recommendations: List[str]
    next_assessment_due: str


class SecurityMetrics(BaseModel):
    """Schema for security metrics"""
    total_logins: int
    failed_logins: int
    suspicious_activities: int
    data_access_events: int
    consent_changes: int
    security_incidents: int


class ComplianceMetrics(BaseModel):
    """Schema for compliance metrics"""
    hipaa_compliance: HIPAAComplianceStatus
    security_metrics: SecurityMetrics
    audit_coverage: float
    consent_coverage: float
    data_retention_compliance: float
