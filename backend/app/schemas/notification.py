"""
Notification Schemas
Models for notifications and alerts
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationResponse(BaseModel):
    """Notification response"""
    id: str
    type: str
    priority: str
    title: str
    message: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    read_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationUpdate(BaseModel):
    """Update notification status"""
    read: bool = False
    acknowledged: bool = False

