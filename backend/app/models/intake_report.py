"""
Intake Report Model
Stores the final generated clinical report
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class IntakeReport(Base):
    """Final intake report generated from session"""
    __tablename__ = "intake_reports"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Keys
    session_id = Column(String(36), ForeignKey("intake_sessions.id"), nullable=False)
    patient_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Report Data
    report_data = Column(JSON, nullable=False)  # Complete structured report
    clinician_report_data = Column(JSON, nullable=True)  # Clinician-focused report
    
    # Classifications
    severity_level = Column(String(20), nullable=True)  # mild, moderate, severe
    risk_level = Column(String(20), nullable=True)  # low, moderate, high
    urgency = Column(String(20), nullable=True)  # routine, urgent, emergent
    
    # PDF Storage (dual reports)
    pdf_path = Column(String(500), nullable=True)  # Legacy/patient PDF
    patient_pdf_path = Column(String(500), nullable=True)  # Patient-facing PDF
    clinician_pdf_path = Column(String(500), nullable=True)  # Clinician PDF
    
    # Feedback tracking
    feedback_submitted = Column(Boolean, default=False)
    
    # Sharing
    shared_with_provider_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("IntakeSession", back_populates="report")
    patient = relationship("User", back_populates="intake_reports", foreign_keys=[patient_id])
    reviews = relationship("ProviderReview", back_populates="report")
    appointments = relationship("Appointment", back_populates="intake_report")
    telemedicine_sessions = relationship("TelemedicineSession", back_populates="report")
    
    def __repr__(self):
        return f"<IntakeReport {self.id} - {self.severity_level}/{self.risk_level}>"

