"""
Intake Session Model
Stores conversation state and data collection during intake
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class IntakeSession(Base):
    """Intake session tracking conversation and data collection"""
    __tablename__ = "intake_sessions"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Patient (nullable for anonymous sessions)
    patient_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Session Token (for anonymous access)
    session_token = Column(String(100), unique=True, index=True, nullable=False)
    
    # Conversation State
    current_phase = Column(String(50), nullable=True)  # greeting, chief_complaint, screening, etc.
    conversation_history = Column(JSON, nullable=True)  # Array of messages
    
    # Extracted Data
    extracted_data = Column(JSON, nullable=True)  # Structured data from conversation
    screener_scores = Column(JSON, nullable=True)  # Screener results
    risk_flags = Column(JSON, nullable=True)  # Risk assessment flags
    
    # Status
    status = Column(String(20), default="active")  # active, completed, abandoned, paused
    
    # Pause/Resume functionality
    paused_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # When paused session expires (24 hours)
    resume_token = Column(String(100), nullable=True, unique=True)  # Secure token for resuming
    completed_screeners = Column(JSON, nullable=True)  # Track which screeners are fully completed
    current_screener = Column(String(50), nullable=True)  # Current screener being worked on
    screener_progress = Column(JSON, nullable=True)  # Progress within current screener
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    patient = relationship("User", back_populates="intake_sessions")
    report = relationship("IntakeReport", back_populates="session", uselist=False)
    feedback = relationship("FeedbackSubmission", back_populates="session", uselist=False)
    
    def __repr__(self):
        return f"<IntakeSession {self.session_token} - {self.status}>"

