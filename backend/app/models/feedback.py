"""
Feedback Submission Model
Stores clinician feedback from demo testing
"""
from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class FeedbackSubmission(Base):
    """Clinician feedback on demo assessment"""
    __tablename__ = "feedback_submissions"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Key
    session_id = Column(String(36), ForeignKey("intake_sessions.id"), nullable=False)
    
    # Ratings (1-5 scale)
    conversation_rating = Column(Integer, nullable=False)
    patient_report_rating = Column(Integer, nullable=False)
    clinician_report_rating = Column(Integer, nullable=False)
    
    # Practice adoption intent
    would_use = Column(String(50), nullable=False)  # yes_definitely, yes_probably, maybe, probably_not, no
    
    # Open-ended feedback
    strength = Column(Text, nullable=True)
    concern = Column(Text, nullable=True)
    missing_patient = Column(Text, nullable=True)
    missing_clinician = Column(Text, nullable=True)
    additional_comments = Column(Text, nullable=True)
    
    # Optional tester info
    tester_email = Column(String(255), nullable=True)
    tester_name = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("IntakeSession", back_populates="feedback")
    
    def __repr__(self):
        return f"<FeedbackSubmission {self.id} - Session {self.session_id}>"
    
    def to_dict(self):
        """Convert to dictionary for email"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "ratings": {
                "conversation": self.conversation_rating,
                "patient_report": self.patient_report_rating,
                "clinician_report": self.clinician_report_rating,
            },
            "would_use": self.would_use,
            "feedback": {
                "strength": self.strength,
                "concern": self.concern,
                "missing_patient": self.missing_patient,
                "missing_clinician": self.missing_clinician,
                "additional_comments": self.additional_comments,
            },
            "tester": {
                "email": self.tester_email,
                "name": self.tester_name,
            },
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
        }

