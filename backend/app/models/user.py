"""
User Model
Represents all users (patients, providers, admins)
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.db.base import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    PATIENT = "patient"
    PROVIDER = "provider"
    ADMIN = "admin"


class User(Base):
    """User model for all user types"""
    __tablename__ = "users"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # User Info
    role = Column(SQLEnum(UserRole), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    provider_profile = relationship(
        "ProviderProfile", 
        back_populates="user", 
        uselist=False,
        foreign_keys="[ProviderProfile.user_id]"
    )
    intake_sessions = relationship("IntakeSession", back_populates="patient")
    intake_reports = relationship(
        "IntakeReport", 
        back_populates="patient",
        foreign_keys="[IntakeReport.patient_id]"
    )
    provider_reviews = relationship("ProviderReview", back_populates="provider")
    
    # Patient Portal Relationships
    patient_appointments = relationship("Appointment", foreign_keys="[Appointment.patient_id]", back_populates="patient")
    provider_appointments = relationship("Appointment", foreign_keys="[Appointment.provider_id]", back_populates="provider")
    
    # Billing Relationships
    patient_invoices = relationship("Invoice", foreign_keys="[Invoice.patient_id]", back_populates="patient")
    provider_invoices = relationship("Invoice", foreign_keys="[Invoice.provider_id]", back_populates="provider")
    patient_payments = relationship("Payment", foreign_keys="[Payment.patient_id]", back_populates="patient")
    billing_settings = relationship("BillingSettings", back_populates="provider", uselist=False)
    billing_notifications = relationship("BillingNotification", back_populates="user")
    
    # Compliance Relationships
    audit_logs = relationship("AuditLog", back_populates="user")
    data_access_logs = relationship("DataAccessLog", foreign_keys="[DataAccessLog.user_id]", back_populates="user")
    privacy_consents = relationship("PrivacyConsent", foreign_keys="[PrivacyConsent.patient_id]", back_populates="patient")
    
    # Telemedicine Relationships
    provider_sessions = relationship("TelemedicineSession", foreign_keys="[TelemedicineSession.provider_id]", back_populates="provider")
    patient_sessions = relationship("TelemedicineSession", foreign_keys="[TelemedicineSession.patient_id]", back_populates="patient")
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"

