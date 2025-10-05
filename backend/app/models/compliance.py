"""
Compliance Models
HIPAA compliance monitoring and audit trail
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class AuditEventType(str, enum.Enum):
    """Audit event type enumeration"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    
    PATIENT_DATA_ACCESSED = "patient_data_accessed"
    PATIENT_DATA_CREATED = "patient_data_created"
    PATIENT_DATA_UPDATED = "patient_data_updated"
    PATIENT_DATA_DELETED = "patient_data_deleted"
    PATIENT_DATA_EXPORTED = "patient_data_exported"
    
    INTAKE_STARTED = "intake_started"
    INTAKE_COMPLETED = "intake_completed"
    INTAKE_PAUSED = "intake_paused"
    INTAKE_RESUMED = "intake_resumed"
    
    REPORT_GENERATED = "report_generated"
    REPORT_VIEWED = "report_viewed"
    REPORT_SHARED = "report_shared"
    REPORT_DOWNLOADED = "report_downloaded"
    
    APPOINTMENT_CREATED = "appointment_created"
    APPOINTMENT_UPDATED = "appointment_updated"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    
    PAYMENT_PROCESSED = "payment_processed"
    PAYMENT_FAILED = "payment_failed"
    
    CONSENT_GIVEN = "consent_given"
    CONSENT_WITHDRAWN = "consent_withdrawn"
    
    SYSTEM_CONFIG_CHANGED = "system_config_changed"
    SECURITY_VIOLATION = "security_violation"
    DATA_BREACH_DETECTED = "data_breach_detected"


class AuditSeverity(str, enum.Enum):
    """Audit severity level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceStatus(str, enum.Enum):
    """Compliance status enumeration"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    REMEDIATION_REQUIRED = "remediation_required"


# AuditLog model is defined in audit_log.py to avoid conflicts


class ComplianceCheck(Base):
    """Compliance check model"""
    __tablename__ = "compliance_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Check details
    check_name = Column(String(255), nullable=False)
    check_type = Column(String(100), nullable=False)  # hipaa, security, data_protection, etc.
    description = Column(Text, nullable=True)
    
    # Check status
    status = Column(SQLEnum(ComplianceStatus), default=ComplianceStatus.PENDING_REVIEW)
    severity = Column(SQLEnum(AuditSeverity), default=AuditSeverity.MEDIUM)
    
    # Check results
    passed = Column(Boolean, nullable=False)
    details = Column(JSON, nullable=True)  # Check-specific results
    recommendations = Column(Text, nullable=True)
    
    # Timestamps
    checked_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DataAccessLog(Base):
    """Data access log model for PHI access tracking"""
    __tablename__ = "data_access_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Access details
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Data accessed
    data_type = Column(String(100), nullable=False)  # intake_report, appointment, payment, etc.
    data_id = Column(String(100), nullable=False)
    access_type = Column(String(50), nullable=False)  # view, edit, export, delete
    
    # Access context
    reason = Column(String(255), nullable=True)  # Business reason for access
    session_id = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Access details
    fields_accessed = Column(JSON, nullable=True)  # Specific fields accessed
    access_duration = Column(Integer, nullable=True)  # Seconds spent accessing data
    
    # Timestamps
    accessed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="data_access_logs")
    patient = relationship("User", foreign_keys=[patient_id])


class SecurityIncident(Base):
    """Security incident model"""
    __tablename__ = "security_incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Incident details
    incident_type = Column(String(100), nullable=False)  # unauthorized_access, data_breach, etc.
    severity = Column(SQLEnum(AuditSeverity), nullable=False)
    status = Column(String(50), default="open")  # open, investigating, resolved, closed
    
    # Incident description
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    affected_users = Column(JSON, nullable=True)  # List of affected user IDs
    affected_data = Column(JSON, nullable=True)  # Description of affected data
    
    # Investigation details
    discovered_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    investigation_notes = Column(Text, nullable=True)
    
    # Resolution
    resolution = Column(Text, nullable=True)
    remediation_actions = Column(JSON, nullable=True)
    
    # Timestamps
    discovered_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    discoverer = relationship("User", foreign_keys=[discovered_by])
    assignee = relationship("User", foreign_keys=[assigned_to])


class PrivacyConsent(Base):
    """Privacy consent model for consent management"""
    __tablename__ = "privacy_consents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Consent details
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    consent_type = Column(String(100), nullable=False)  # hipaa, marketing, research, etc.
    consent_version = Column(String(50), nullable=False)  # Version of consent form
    
    # Consent status
    given = Column(Boolean, nullable=False)
    given_at = Column(DateTime, nullable=True)
    withdrawn_at = Column(DateTime, nullable=True)
    
    # Consent details
    consent_text = Column(Text, nullable=False)  # Full consent text
    consent_method = Column(String(50), nullable=False)  # digital_signature, verbal, written
    
    # Witness and verification
    witnessed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], back_populates="privacy_consents")
    witness = relationship("User", foreign_keys=[witnessed_by])


class ComplianceReport(Base):
    """Compliance report model"""
    __tablename__ = "compliance_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Report details
    report_type = Column(String(100), nullable=False)  # hipaa_audit, security_assessment, etc.
    report_name = Column(String(255), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Report status
    status = Column(String(50), default="draft")  # draft, generated, approved, submitted
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Report content
    summary = Column(Text, nullable=True)
    findings = Column(JSON, nullable=True)
    recommendations = Column(Text, nullable=True)
    attachments = Column(JSON, nullable=True)  # File attachments
    
    # Timestamps
    generated_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    generator = relationship("User", foreign_keys=[generated_by])
    approver = relationship("User", foreign_keys=[approved_by])


class DataRetentionPolicy(Base):
    """Data retention policy model"""
    __tablename__ = "data_retention_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Policy details
    data_type = Column(String(100), nullable=False)  # patient_data, audit_logs, etc.
    retention_period_days = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    
    # Policy status
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User")


class DataRetentionLog(Base):
    """Data retention log model for tracking data deletion"""
    __tablename__ = "data_retention_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Retention details
    policy_id = Column(Integer, ForeignKey("data_retention_policies.id"), nullable=False)
    data_type = Column(String(100), nullable=False)
    data_id = Column(String(100), nullable=False)
    
    # Deletion details
    deletion_reason = Column(String(255), nullable=False)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    deletion_method = Column(String(100), nullable=False)  # automated, manual
    
    # Timestamps
    deleted_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    policy = relationship("DataRetentionPolicy")
    deleter = relationship("User")
