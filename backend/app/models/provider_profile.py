"""
Provider Profile Model
Extended information for provider users
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class ProviderProfile(Base):
    """Provider profile with professional information"""
    __tablename__ = "provider_profiles"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Key to User
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Professional Info
    npi = Column(String(20), nullable=True)
    license_number = Column(String(50), nullable=True)
    license_state = Column(String(2), nullable=True)
    specialty = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Approval Status
    invite_code = Column(String(50), nullable=True)
    approval_status = Column(String(20), default="pending")  # pending, approved, rejected
    approved_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="provider_profile", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<ProviderProfile {self.user_id} - {self.approval_status}>"

