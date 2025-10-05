"""
Compliance API endpoints
HIPAA compliance monitoring and audit trails
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.compliance import AuditEventType, AuditSeverity
from app.schemas.compliance import (
    AuditLogResponse,
    AuditLogListResponse,
    DataAccessLogResponse,
    DataAccessLogListResponse,
    ComplianceSummaryResponse,
    SecurityIncidentRequest,
    SecurityIncidentResponse,
    PrivacyConsentRequest,
    PrivacyConsentResponse,
    PrivacyConsentListResponse,
    ComplianceCheckResponse
)
from app.services.compliance_service import compliance_service

router = APIRouter()


@router.get("/audit-logs", response_model=AuditLogListResponse)
async def get_audit_logs(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(100, ge=1, le=1000, description="Number of logs to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit logs with filtering"""
    
    if current_user.role not in ["admin", "provider"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or provider role required."
        )
    
    try:
        # Parse dates
        start_dt = None
        end_dt = None
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        
        # Parse enums
        event_type_enum = None
        if event_type:
            try:
                event_type_enum = AuditEventType(event_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid event type: {event_type}"
                )
        
        severity_enum = None
        if severity:
            try:
                severity_enum = AuditSeverity(severity)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid severity: {severity}"
                )
        
        logs = compliance_service.get_audit_logs(
            start_date=start_dt,
            end_date=end_dt,
            user_id=user_id,
            event_type=event_type_enum,
            severity=severity_enum,
            limit=limit,
            db=db
        )
        
        return AuditLogListResponse(
            audit_logs=logs,
            total_count=len(logs)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audit logs: {str(e)}"
        )


@router.get("/data-access-logs", response_model=DataAccessLogListResponse)
async def get_data_access_logs(
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000, description="Number of logs to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get data access logs"""
    
    if current_user.role not in ["admin", "provider"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or provider role required."
        )
    
    try:
        # Parse dates
        start_dt = None
        end_dt = None
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        
        logs = compliance_service.get_data_access_logs(
            patient_id=patient_id,
            user_id=user_id,
            start_date=start_dt,
            end_date=end_dt,
            limit=limit,
            db=db
        )
        
        return DataAccessLogListResponse(
            access_logs=logs,
            total_count=len(logs)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get data access logs: {str(e)}"
        )


@router.get("/compliance-summary", response_model=ComplianceSummaryResponse)
async def get_compliance_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get compliance summary"""
    
    if current_user.role not in ["admin", "provider"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or provider role required."
        )
    
    try:
        # Parse dates
        start_dt = None
        end_dt = None
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        
        summary = compliance_service.get_compliance_summary(
            start_date=start_dt,
            end_date=end_dt,
            db=db
        )
        
        return ComplianceSummaryResponse(**summary)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get compliance summary: {str(e)}"
        )


@router.post("/security-incidents", response_model=SecurityIncidentResponse)
async def create_security_incident(
    incident_request: SecurityIncidentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a security incident"""
    
    if current_user.role not in ["admin", "provider"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or provider role required."
        )
    
    try:
        result = compliance_service.create_security_incident(
            incident_type=incident_request.incident_type,
            severity=AuditSeverity(incident_request.severity),
            title=incident_request.title,
            description=incident_request.description,
            discovered_by=current_user.id,
            affected_users=incident_request.affected_users,
            affected_data=incident_request.affected_data,
            db=db
        )
        
        return SecurityIncidentResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create security incident: {str(e)}"
        )


@router.post("/privacy-consents", response_model=PrivacyConsentResponse)
async def create_privacy_consent(
    consent_request: PrivacyConsentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create privacy consent record"""
    
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Patient role required."
        )
    
    try:
        result = compliance_service.create_privacy_consent(
            patient_id=current_user.id,
            consent_type=consent_request.consent_type,
            consent_text=consent_request.consent_text,
            consent_method=consent_request.consent_method,
            witnessed_by=consent_request.witnessed_by,
            ip_address=consent_request.ip_address,
            user_agent=consent_request.user_agent,
            db=db
        )
        
        return PrivacyConsentResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create privacy consent: {str(e)}"
        )


@router.get("/privacy-consents", response_model=PrivacyConsentListResponse)
async def get_privacy_consents(
    consent_type: Optional[str] = Query(None, description="Filter by consent type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get privacy consents for current user"""
    
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Patient role required."
        )
    
    try:
        consents = compliance_service.get_privacy_consents(
            patient_id=current_user.id,
            consent_type=consent_type,
            db=db
        )
        
        return PrivacyConsentListResponse(
            consents=consents,
            total_count=len(consents)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get privacy consents: {str(e)}"
        )


@router.post("/privacy-consents/{consent_type}/withdraw", response_model=PrivacyConsentResponse)
async def withdraw_privacy_consent(
    consent_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Withdraw privacy consent"""
    
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Patient role required."
        )
    
    try:
        result = compliance_service.withdraw_privacy_consent(
            patient_id=current_user.id,
            consent_type=consent_type,
            db=db
        )
        
        return PrivacyConsentResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to withdraw privacy consent: {str(e)}"
        )


@router.post("/compliance-checks/{check_name}/run", response_model=ComplianceCheckResponse)
async def run_compliance_check(
    check_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run a specific compliance check"""
    
    if current_user.role not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    
    try:
        # Define available compliance checks
        compliance_checks = {
            "user_access_review": {
                "type": "security",
                "function": lambda db: _check_user_access_review(db)
            },
            "data_retention_compliance": {
                "type": "hipaa",
                "function": lambda db: _check_data_retention_compliance(db)
            },
            "audit_log_integrity": {
                "type": "security",
                "function": lambda db: _check_audit_log_integrity(db)
            },
            "consent_management": {
                "type": "hipaa",
                "function": lambda db: _check_consent_management(db)
            }
        }
        
        if check_name not in compliance_checks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Compliance check '{check_name}' not found"
            )
        
        check_config = compliance_checks[check_name]
        result = compliance_service.run_compliance_check(
            check_name=check_name,
            check_type=check_config["type"],
            check_function=check_config["function"],
            db=db
        )
        
        return ComplianceCheckResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run compliance check: {str(e)}"
        )


@router.get("/compliance-checks")
async def get_available_compliance_checks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available compliance checks"""
    
    if current_user.role not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    
    return {
        "compliance_checks": [
            {
                "name": "user_access_review",
                "type": "security",
                "description": "Review user access permissions and inactive accounts"
            },
            {
                "name": "data_retention_compliance",
                "type": "hipaa",
                "description": "Check data retention policy compliance"
            },
            {
                "name": "audit_log_integrity",
                "type": "security",
                "description": "Verify audit log integrity and completeness"
            },
            {
                "name": "consent_management",
                "type": "hipaa",
                "description": "Review consent management and withdrawal processes"
            }
        ]
    }


# Compliance check functions
def _check_user_access_review(db: Session) -> Dict[str, Any]:
    """Check user access review compliance"""
    from app.models.user import User
    
    # Check for inactive users
    inactive_users = db.query(User).filter(
        User.is_active == False
    ).count()
    
    # Check for users without recent activity
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    users_without_recent_activity = db.query(User).filter(
        User.last_login < thirty_days_ago,
        User.is_active == True
    ).count()
    
    passed = inactive_users == 0 and users_without_recent_activity < 10
    
    return {
        "passed": passed,
        "details": {
            "inactive_users": inactive_users,
            "users_without_recent_activity": users_without_recent_activity
        },
        "recommendations": "Review inactive users and users without recent activity" if not passed else None,
        "severity": "medium"
    }


def _check_data_retention_compliance(db: Session) -> Dict[str, Any]:
    """Check data retention compliance"""
    from app.models.compliance import DataRetentionPolicy, AuditLog
    
    # Check if retention policies exist
    policies = db.query(DataRetentionPolicy).filter(
        DataRetentionPolicy.is_active == True
    ).count()
    
    # Check for old audit logs
    old_audit_logs = db.query(AuditLog).filter(
        AuditLog.timestamp < datetime.utcnow() - timedelta(days=2555)  # 7 years
    ).count()
    
    passed = policies > 0 and old_audit_logs == 0
    
    return {
        "passed": passed,
        "details": {
            "active_retention_policies": policies,
            "old_audit_logs": old_audit_logs
        },
        "recommendations": "Implement data retention policies and archive old data" if not passed else None,
        "severity": "high"
    }


def _check_audit_log_integrity(db: Session) -> Dict[str, Any]:
    """Check audit log integrity"""
    from app.models.compliance import AuditLog
    
    # Check for missing audit logs in last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_logs = db.query(AuditLog).filter(
        AuditLog.timestamp >= yesterday
    ).count()
    
    # Check for high severity events
    high_severity_events = db.query(AuditLog).filter(
        AuditLog.severity == AuditSeverity.HIGH,
        AuditLog.timestamp >= yesterday
    ).count()
    
    passed = recent_logs > 0
    
    return {
        "passed": passed,
        "details": {
            "recent_logs": recent_logs,
            "high_severity_events": high_severity_events
        },
        "recommendations": "Investigate missing audit logs" if not passed else None,
        "severity": "high"
    }


def _check_consent_management(db: Session) -> Dict[str, Any]:
    """Check consent management compliance"""
    from app.models.compliance import PrivacyConsent
    
    # Check for patients without consent
    total_patients = db.query(User).filter(User.role == "patient").count()
    patients_with_consent = db.query(PrivacyConsent.patient_id).distinct().count()
    
    # Check for withdrawn consents
    withdrawn_consents = db.query(PrivacyConsent).filter(
        PrivacyConsent.given == False
    ).count()
    
    passed = patients_with_consent >= total_patients * 0.9  # 90% threshold
    
    return {
        "passed": passed,
        "details": {
            "total_patients": total_patients,
            "patients_with_consent": patients_with_consent,
            "withdrawn_consents": withdrawn_consents
        },
        "recommendations": "Ensure all patients have provided necessary consents" if not passed else None,
        "severity": "high"
    }
