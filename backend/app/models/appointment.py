"""
Appointment Model
Stores appointment scheduling and management data
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class AppointmentStatus(enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class AppointmentType(enum.Enum):
    INTAKE = "intake"
    FOLLOW_UP = "follow_up"
    CONSULTATION = "consultation"
    EMERGENCY = "emergency"


class Appointment(Base):
    """Appointment scheduling and management"""
    
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Appointment details
    appointment_type = Column(Enum(AppointmentType), nullable=False, default=AppointmentType.CONSULTATION)
    status = Column(Enum(AppointmentStatus), nullable=False, default=AppointmentStatus.SCHEDULED)
    
    # Participants
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Scheduling
    scheduled_start = Column(DateTime, nullable=False)
    scheduled_end = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False, default=60)
    
    # Actual timing (if different from scheduled)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    
    # Location/Virtual
    location_type = Column(String(20), nullable=False, default="virtual")  # virtual, in_person
    location_details = Column(String(500), nullable=True)  # Address or meeting link
    meeting_link = Column(String(500), nullable=True)  # For virtual appointments
    
    # Appointment content
    reason_for_visit = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    provider_notes = Column(Text, nullable=True)
    
    # Related data
    intake_report_id = Column(Integer, ForeignKey("intake_reports.id"), nullable=True)
    telemedicine_session_id = Column(String(100), nullable=True)
    
    # Reminders and notifications
    reminder_sent = Column(Boolean, default=False)
    confirmation_sent = Column(Boolean, default=False)
    reminder_schedule = Column(JSON, nullable=True)  # Custom reminder schedule
    
    # Rescheduling/Cancellation
    cancellation_reason = Column(String(200), nullable=True)
    cancelled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Recurring appointments
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50), nullable=True)  # weekly, monthly, etc.
    parent_appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], back_populates="patient_appointments")
    provider = relationship("User", foreign_keys=[provider_id], back_populates="provider_appointments")
    intake_report = relationship("IntakeReport", back_populates="appointments")
    created_by_user = relationship("User", foreign_keys=[created_by])
    cancelled_by_user = relationship("User", foreign_keys=[cancelled_by])
    parent_appointment = relationship("Appointment", remote_side=[id], back_populates="child_appointments")
    child_appointments = relationship("Appointment", back_populates="parent_appointment")
    invoice = relationship("Invoice", back_populates="appointment")
