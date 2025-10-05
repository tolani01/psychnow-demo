"""
Notification Model
Alerts and notifications for users (especially high-risk alerts for admins)
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class Notification(Base):
    """Notification/alert for users"""
    __tablename__ = "notifications"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Recipient
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Notification Content
    type = Column(String(50), nullable=False)  # high_risk_alert, appointment_reminder, message_received
    priority = Column(String(20), nullable=False, default="medium")  # low, medium, high, urgent
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Linked Resource (optional)
    resource_type = Column(String(50), nullable=True)  # intake_session, report, encounter
    resource_id = Column(String(36), nullable=True)
    
    # Status
    read_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True)  # Auto-hide after this time
    
    # Relationships
    user = relationship("User", backref="notifications")
    
    def __repr__(self):
        return f"<Notification {self.type} - {self.priority} - {self.user_id}>"

