"""
Telemedicine Session Model
Stores telemedicine consultation session data
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class TelemedicineSession(Base):
    """Telemedicine consultation session"""
    
    __tablename__ = "telemedicine_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Session participants
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Related intake report (if applicable)
    report_id = Column(Integer, ForeignKey("intake_reports.id"), nullable=True)
    
    # Session details
    session_type = Column(String(50), nullable=False, default="consultation")  # consultation, follow_up, emergency
    status = Column(String(20), nullable=False, default="scheduled")  # scheduled, active, ended, cancelled
    
    # Timing
    scheduled_start = Column(DateTime, nullable=False)
    scheduled_duration = Column(Integer, nullable=False, default=60)  # minutes
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Session metadata
    end_reason = Column(String(100), nullable=True)  # completed, cancelled, technical_issue, etc.
    recording_enabled = Column(Boolean, default=False)
    recording_url = Column(String(500), nullable=True)
    
    # Technical details
    webrtc_config = Column(JSON, nullable=True)  # STUN/TURN server configuration
    connection_quality = Column(JSON, nullable=True)  # Quality metrics during session
    technical_issues = Column(JSON, nullable=True)  # Logged technical problems
    
    # Clinical notes
    provider_notes = Column(Text, nullable=True)
    patient_notes = Column(Text, nullable=True)
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    
    # Relationships
    provider = relationship("User", foreign_keys=[provider_id], back_populates="provider_sessions")
    patient = relationship("User", foreign_keys=[patient_id], back_populates="patient_sessions")
    report = relationship("IntakeReport", back_populates="telemedicine_sessions")
