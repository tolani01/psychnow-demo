"""
Provider Review Model
Provider's review and notes on intake reports
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class ProviderReview(Base):
    """Provider's clinical review of an intake report"""
    __tablename__ = "provider_reviews"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Keys
    report_id = Column(String(36), ForeignKey("intake_reports.id"), nullable=False)
    provider_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Review Status
    status = Column(String(20), default="pending")  # pending, in_review, completed
    
    # Clinical Notes
    clinical_notes = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    
    # Timestamps
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    report = relationship("IntakeReport", back_populates="reviews")
    provider = relationship("User", back_populates="provider_reviews")
    
    def __repr__(self):
        return f"<ProviderReview {self.id} - {self.status}>"

