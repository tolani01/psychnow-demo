"""
Compliance Service
HIPAA compliance monitoring and audit trail management
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.models.audit_log import AuditLog
from app.models.compliance import (
    ComplianceCheck, DataAccessLog, SecurityIncident,
    PrivacyConsent, ComplianceReport, DataRetentionPolicy, DataRetentionLog,
    AuditEventType, AuditSeverity, ComplianceStatus
)
from app.models.user import User
from app.services.notification_service import notification_service


class ComplianceService:
    """Service for HIPAA compliance monitoring and audit trails"""
    
    def __init__(self):
        self.notification_service = notification_service
    
    def log_audit_event(
        self,
        event_type: AuditEventType,
        description: str,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None,
        http_method: Optional[str] = None,
        response_status: Optional[int] = None,
        severity: AuditSeverity = AuditSeverity.LOW,
        db: Session = None
    ) -> None:
        """Log an audit event"""
        
        audit_log = AuditLog(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            details=details,
            endpoint=endpoint,
            http_method=http_method,
            response_status=response_status,
            timestamp=datetime.utcnow()
        )
        
        db.add(audit_log)
        db.commit()
        
        # Log high severity events to notification system
        if severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL]:
            self.notification_service.create_notification(
                user_id=user_id,
                type="security_alert",
                title=f"Security Alert: {event_type.value}",
                message=description,
                priority=severity.value,
                data={
                    "event_type": event_type.value,
                    "severity": severity.value,
                    "timestamp": audit_log.timestamp.isoformat(),
                    "details": details
                },
                db=db
            )
    
    def log_data_access(
        self,
        user_id: int,
        patient_id: int,
        data_type: str,
        data_id: str,
        access_type: str,
        reason: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        fields_accessed: Optional[List[str]] = None,
        access_duration: Optional[int] = None,
        db: Session = None
    ) -> None:
        """Log PHI data access"""
        
        access_log = DataAccessLog(
            user_id=user_id,
            patient_id=patient_id,
            data_type=data_type,
            data_id=data_id,
            access_type=access_type,
            reason=reason,
            session_id=session_id,
            ip_address=ip_address,
            fields_accessed=fields_accessed,
            access_duration=access_duration,
            accessed_at=datetime.utcnow()
        )
        
        db.add(access_log)
        db.commit()
        
        # Log audit event
        self.log_audit_event(
            event_type=AuditEventType.PATIENT_DATA_ACCESSED,
            description=f"User {user_id} accessed {data_type} {data_id} for patient {patient_id}",
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            resource_type=data_type,
            resource_id=data_id,
            details={
                "patient_id": patient_id,
                "access_type": access_type,
                "reason": reason,
                "fields_accessed": fields_accessed,
                "access_duration": access_duration
            },
            severity=AuditSeverity.MEDIUM,
            db=db
        )
    
    def run_compliance_check(
        self,
        check_name: str,
        check_type: str,
        check_function: callable,
        db: Session
    ) -> Dict[str, Any]:
        """Run a compliance check"""
        
        try:
            # Run the check
            result = check_function(db)
            
            # Create compliance check record
            compliance_check = ComplianceCheck(
                check_name=check_name,
                check_type=check_type,
                description=f"Automated compliance check: {check_name}",
                passed=result.get('passed', False),
                details=result.get('details', {}),
                recommendations=result.get('recommendations'),
                severity=AuditSeverity(result.get('severity', 'medium')),
                status=ComplianceStatus.COMPLIANT if result.get('passed') else ComplianceStatus.NON_COMPLIANT,
                checked_at=datetime.utcnow()
            )
            
            db.add(compliance_check)
            db.commit()
            
            # Log audit event for failed checks
            if not result.get('passed'):
                self.log_audit_event(
                    event_type=AuditEventType.SECURITY_VIOLATION,
                    description=f"Compliance check failed: {check_name}",
                    details={
                        "check_name": check_name,
                        "check_type": check_type,
                        "result": result
                    },
                    severity=AuditSeverity.HIGH,
                    db=db
                )
            
            return {
                "success": True,
                "check_id": compliance_check.id,
                "passed": result.get('passed', False),
                "details": result.get('details', {}),
                "recommendations": result.get('recommendations')
            }
            
        except Exception as e:
            # Log failed check
            compliance_check = ComplianceCheck(
                check_name=check_name,
                check_type=check_type,
                description=f"Compliance check failed with error: {check_name}",
                passed=False,
                details={"error": str(e)},
                recommendations="Investigate and fix the compliance check",
                severity=AuditSeverity.HIGH,
                status=ComplianceStatus.NON_COMPLIANT,
                checked_at=datetime.utcnow()
            )
            
            db.add(compliance_check)
            db.commit()
            
            return {
                "success": False,
                "error": str(e),
                "passed": False
            }
    
    def get_audit_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[int] = None,
        event_type: Optional[AuditEventType] = None,
        severity: Optional[AuditSeverity] = None,
        limit: int = 100,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Get audit logs with filtering"""
        
        query = db.query(AuditLog)
        
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        if severity:
            query = query.filter(AuditLog.severity == severity)
        
        logs = query.order_by(desc(AuditLog.timestamp)).limit(limit).all()
        
        return [
            {
                "id": log.id,
                "event_type": log.event_type.value,
                "severity": log.severity.value,
                "user_id": log.user_id,
                "user_email": log.user.email if log.user else None,
                "session_id": log.session_id,
                "ip_address": log.ip_address,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "description": log.description,
                "details": log.details,
                "endpoint": log.endpoint,
                "http_method": log.http_method,
                "response_status": log.response_status,
                "timestamp": log.timestamp.isoformat()
            }
            for log in logs
        ]
    
    def get_data_access_logs(
        self,
        patient_id: Optional[int] = None,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Get data access logs"""
        
        query = db.query(DataAccessLog)
        
        if patient_id:
            query = query.filter(DataAccessLog.patient_id == patient_id)
        if user_id:
            query = query.filter(DataAccessLog.user_id == user_id)
        if start_date:
            query = query.filter(DataAccessLog.accessed_at >= start_date)
        if end_date:
            query = query.filter(DataAccessLog.accessed_at <= end_date)
        
        logs = query.order_by(desc(DataAccessLog.accessed_at)).limit(limit).all()
        
        return [
            {
                "id": log.id,
                "user_id": log.user_id,
                "user_name": f"{log.user.first_name} {log.user.last_name}" if log.user else "Unknown",
                "patient_id": log.patient_id,
                "patient_name": f"{log.patient.first_name} {log.patient.last_name}" if log.patient else "Unknown",
                "data_type": log.data_type,
                "data_id": log.data_id,
                "access_type": log.access_type,
                "reason": log.reason,
                "session_id": log.session_id,
                "ip_address": log.ip_address,
                "fields_accessed": log.fields_accessed,
                "access_duration": log.access_duration,
                "accessed_at": log.accessed_at.isoformat()
            }
            for log in logs
        ]
    
    def create_security_incident(
        self,
        incident_type: str,
        severity: AuditSeverity,
        title: str,
        description: str,
        discovered_by: Optional[int] = None,
        affected_users: Optional[List[int]] = None,
        affected_data: Optional[Dict[str, Any]] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Create a security incident record"""
        
        incident = SecurityIncident(
            incident_type=incident_type,
            severity=severity,
            status="open",
            title=title,
            description=description,
            discovered_by=discovered_by,
            affected_users=affected_users,
            affected_data=affected_data,
            discovered_at=datetime.utcnow()
        )
        
        db.add(incident)
        db.commit()
        db.refresh(incident)
        
        # Log audit event
        self.log_audit_event(
            event_type=AuditEventType.SECURITY_VIOLATION,
            description=f"Security incident created: {title}",
            user_id=discovered_by,
            details={
                "incident_id": incident.id,
                "incident_type": incident_type,
                "severity": severity.value,
                "affected_users": affected_users,
                "affected_data": affected_data
            },
            severity=severity,
            db=db
        )
        
        # Send notifications to admins
        admins = db.query(User).filter(User.role == "admin").all()
        for admin in admins:
            self.notification_service.create_notification(
                user_id=admin.id,
                type="security_incident",
                title=f"Security Incident: {title}",
                message=description,
                priority=severity.value,
                data={
                    "incident_id": incident.id,
                    "incident_type": incident_type,
                    "severity": severity.value
                },
                db=db
            )
        
        return {
            "success": True,
            "incident_id": incident.id,
            "message": "Security incident created successfully"
        }
    
    def get_compliance_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Get compliance summary"""
        
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Get audit log counts by severity
        audit_counts = db.query(
            AuditLog.severity,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date
        ).group_by(AuditLog.severity).all()
        
        severity_counts = {severity.value: 0 for severity in AuditSeverity}
        for severity, count in audit_counts:
            severity_counts[severity.value] = count
        
        # Get compliance check results
        recent_checks = db.query(ComplianceCheck).filter(
            ComplianceCheck.checked_at >= start_date,
            ComplianceCheck.checked_at <= end_date
        ).all()
        
        check_summary = {
            "total_checks": len(recent_checks),
            "passed": len([c for c in recent_checks if c.passed]),
            "failed": len([c for c in recent_checks if not c.passed]),
            "by_type": {}
        }
        
        for check in recent_checks:
            if check.check_type not in check_summary["by_type"]:
                check_summary["by_type"][check.check_type] = {"passed": 0, "failed": 0}
            if check.passed:
                check_summary["by_type"][check.check_type]["passed"] += 1
            else:
                check_summary["by_type"][check.check_type]["failed"] += 1
        
        # Get data access summary
        access_counts = db.query(
            DataAccessLog.data_type,
            func.count(DataAccessLog.id).label('count')
        ).filter(
            DataAccessLog.accessed_at >= start_date,
            DataAccessLog.accessed_at <= end_date
        ).group_by(DataAccessLog.data_type).all()
        
        access_summary = {data_type: count for data_type, count in access_counts}
        
        # Get open security incidents
        open_incidents = db.query(SecurityIncident).filter(
            SecurityIncident.status == "open"
        ).count()
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "audit_logs": {
                "total_events": sum(severity_counts.values()),
                "by_severity": severity_counts
            },
            "compliance_checks": check_summary,
            "data_access": {
                "total_accesses": sum(access_summary.values()),
                "by_type": access_summary
            },
            "security_incidents": {
                "open_incidents": open_incidents
            }
        }
    
    def create_privacy_consent(
        self,
        patient_id: int,
        consent_type: str,
        consent_text: str,
        consent_method: str,
        witnessed_by: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Create privacy consent record"""
        
        # Get latest consent version for this type
        latest_consent = db.query(PrivacyConsent).filter(
            PrivacyConsent.patient_id == patient_id,
            PrivacyConsent.consent_type == consent_type
        ).order_by(desc(PrivacyConsent.created_at)).first()
        
        version = "1.0"
        if latest_consent:
            # Increment version
            try:
                current_version = float(latest_consent.consent_version)
                version = str(current_version + 0.1)
            except ValueError:
                version = "1.1"
        
        consent = PrivacyConsent(
            patient_id=patient_id,
            consent_type=consent_type,
            consent_version=version,
            given=True,
            given_at=datetime.utcnow(),
            consent_text=consent_text,
            consent_method=consent_method,
            witnessed_by=witnessed_by,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(consent)
        db.commit()
        
        # Log audit event
        self.log_audit_event(
            event_type=AuditEventType.CONSENT_GIVEN,
            description=f"Privacy consent given by patient {patient_id} for {consent_type}",
            user_id=patient_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type="consent",
            resource_id=str(consent.id),
            details={
                "consent_type": consent_type,
                "consent_version": version,
                "consent_method": consent_method,
                "witnessed_by": witnessed_by
            },
            severity=AuditSeverity.MEDIUM,
            db=db
        )
        
        return {
            "success": True,
            "consent_id": consent.id,
            "version": version,
            "message": "Privacy consent recorded successfully"
        }
    
    def withdraw_privacy_consent(
        self,
        patient_id: int,
        consent_type: str,
        db: Session = None
    ) -> Dict[str, Any]:
        """Withdraw privacy consent"""
        
        # Get latest consent
        consent = db.query(PrivacyConsent).filter(
            PrivacyConsent.patient_id == patient_id,
            PrivacyConsent.consent_type == consent_type,
            PrivacyConsent.given == True
        ).order_by(desc(PrivacyConsent.created_at)).first()
        
        if not consent:
            raise ValueError("No active consent found for this type")
        
        # Withdraw consent
        consent.given = False
        consent.withdrawn_at = datetime.utcnow()
        consent.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Log audit event
        self.log_audit_event(
            event_type=AuditEventType.CONSENT_WITHDRAWN,
            description=f"Privacy consent withdrawn by patient {patient_id} for {consent_type}",
            user_id=patient_id,
            resource_type="consent",
            resource_id=str(consent.id),
            details={
                "consent_type": consent_type,
                "consent_version": consent.consent_version,
                "withdrawn_at": consent.withdrawn_at.isoformat()
            },
            severity=AuditSeverity.MEDIUM,
            db=db
        )
        
        return {
            "success": True,
            "message": "Privacy consent withdrawn successfully"
        }
    
    def get_privacy_consents(
        self,
        patient_id: int,
        consent_type: Optional[str] = None,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Get privacy consents for patient"""
        
        query = db.query(PrivacyConsent).filter(PrivacyConsent.patient_id == patient_id)
        
        if consent_type:
            query = query.filter(PrivacyConsent.consent_type == consent_type)
        
        consents = query.order_by(desc(PrivacyConsent.created_at)).all()
        
        return [
            {
                "id": consent.id,
                "consent_type": consent.consent_type,
                "consent_version": consent.consent_version,
                "given": consent.given,
                "given_at": consent.given_at.isoformat() if consent.given_at else None,
                "withdrawn_at": consent.withdrawn_at.isoformat() if consent.withdrawn_at else None,
                "consent_method": consent.consent_method,
                "witnessed_by": consent.witnessed_by,
                "created_at": consent.created_at.isoformat()
            }
            for consent in consents
        ]


# Global compliance service instance
compliance_service = ComplianceService()
