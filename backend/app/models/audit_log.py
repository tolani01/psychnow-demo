"""
Audit Log Model
Immutable audit trail for compliance and security
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class AuditLog(Base):
    """Audit log for tracking all significant actions"""
    __tablename__ = "audit_logs"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Event Details
    event_type = Column(String(100), nullable=False, index=True)  # login, access_phi, risk_detected, etc.
    action = Column(String(50), nullable=False)  # create, read, update, delete
    
    # Actor
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Resource
    resource_type = Column(String(50), nullable=True)  # intake_session, report, prescription
    resource_id = Column(String(36), nullable=True)
    
    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Additional Data
    event_metadata = Column(JSON, nullable=True)  # Event-specific details (renamed from 'metadata' - reserved word)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_audit_event_time', 'event_type', 'timestamp'),
        Index('idx_audit_user_time', 'user_id', 'timestamp'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
    )
    
    def __repr__(self):
        return f"<AuditLog {self.event_type} - {self.timestamp}>"

