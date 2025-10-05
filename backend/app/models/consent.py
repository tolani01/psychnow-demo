"""
Consent Model
Tracks user consent for HIPAA, telehealth, financial agreements
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class Consent(Base):
    """User consent records for compliance"""
    __tablename__ = "consents"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Key
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Consent Details
    consent_type = Column(String(50), nullable=False)  # hipaa, telehealth, financial
    version = Column(String(10), nullable=False)  # e.g., "1.0", "2.1"
    content_hash = Column(String(64), nullable=True)  # SHA-256 of consent text
    
    # Acceptance Details
    accepted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Revocation
    revoked_at = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("User", backref="consents")
    
    def __repr__(self):
        return f"<Consent {self.consent_type} - {self.user_id}>"

