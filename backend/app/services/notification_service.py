"""
Notification Service for High-Risk Alerts and Provider Assignments
Handles notification creation, delivery, and management
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.notification import Notification
from app.models.intake_report import IntakeReport
from app.models.user import User
from app.services.websocket_service import websocket_service


class NotificationService:
    """Service for managing notifications and alerts"""
    
    def __init__(self):
        self.websocket_service = websocket_service
    
    async def create_high_risk_alert(
        self, 
        report_id: int, 
        patient_name: str, 
        risk_details: Dict[str, Any], 
        db: Session
    ) -> Notification:
        """Create and send high-risk patient alert"""
        
        # Create notification record
        notification = Notification(
            type="high_risk_alert",
            title="High-Risk Patient Alert",
            message=f"Patient {patient_name} requires immediate review",
            priority="critical",
            data={
                "report_id": report_id,
                "patient_name": patient_name,
                "risk_level": risk_details.get("risk_level"),
                "urgency": risk_details.get("urgency"),
                "screener_name": risk_details.get("screener_name"),
                "score": risk_details.get("score"),
                "details": risk_details.get("details")
            },
            target_role="provider",  # Also sent to admins via WebSocket
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        # Send real-time WebSocket notification
        await self.websocket_service.send_high_risk_alert(
            patient_name, report_id, risk_details
        )
        
        # Create additional notification for admins
        admin_notification = Notification(
            type="high_risk_alert",
            title="High-Risk Patient Alert",
            message=f"Patient {patient_name} requires immediate review",
            priority="critical",
            data=notification.data,
            target_role="admin",
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        db.add(admin_notification)
        db.commit()
        
        print(f"High-risk alert created for patient {patient_name} (Report ID: {report_id})")
        return notification
    
    async def create_provider_assignment(
        self, 
        provider_id: int, 
        patient_name: str, 
        report_id: int, 
        db: Session
    ) -> Notification:
        """Create and send provider assignment notification"""
        
        # Get provider details
        provider = db.query(User).filter(User.id == provider_id).first()
        if not provider:
            raise ValueError(f"Provider with ID {provider_id} not found")
        
        # Create notification record
        notification = Notification(
            type="provider_assignment",
            title="New Patient Assignment",
            message=f"New patient report assigned: {patient_name}",
            priority="medium",
            data={
                "report_id": report_id,
                "patient_name": patient_name,
                "provider_id": provider_id,
                "provider_name": provider.name,
                "assignment_time": datetime.utcnow().isoformat()
            },
            target_user_id=provider_id,
            target_role="provider",
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        # Send real-time WebSocket notification
        await self.websocket_service.send_provider_assignment(
            provider_id, patient_name, report_id
        )
        
        print(f"Provider assignment notification sent to {provider.name} for patient {patient_name}")
        return notification
    
    async def create_system_notification(
        self, 
        title: str, 
        message: str, 
        target_role: str = "admin",
        priority: str = "low",
        data: Optional[Dict] = None,
        db: Optional[Session] = None
    ) -> Optional[Notification]:
        """Create system-wide notification"""
        
        notification = Notification(
            type="system_notification",
            title=title,
            message=message,
            priority=priority,
            data=data or {},
            target_role=target_role,
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        if db:
            db.add(notification)
            db.commit()
            db.refresh(notification)
        
        # Send real-time WebSocket notification
        await self.websocket_service.send_system_notification(
            title, message, target_role
        )
        
        print(f"System notification sent: {title}")
        return notification
    
    def get_user_notifications(
        self, 
        user_id: int, 
        limit: int = 50, 
        unread_only: bool = False,
        db: Session = None
    ) -> List[Notification]:
        """Get notifications for a specific user"""
        
        query = db.query(Notification).filter(
            or_(
                Notification.target_user_id == user_id,
                and_(
                    Notification.target_user_id.is_(None),
                    Notification.target_role == db.query(User).filter(User.id == user_id).first().role
                )
            )
        )
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        return query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    def get_unread_count(self, user_id: int, db: Session) -> int:
        """Get count of unread notifications for user"""
        return db.query(Notification).filter(
            or_(
                Notification.target_user_id == user_id,
                and_(
                    Notification.target_user_id.is_(None),
                    Notification.target_role == db.query(User).filter(User.id == user_id).first().role
                )
            ),
            Notification.is_read == False
        ).count()
    
    def mark_notification_read(self, notification_id: int, user_id: int, db: Session) -> bool:
        """Mark notification as read"""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            or_(
                Notification.target_user_id == user_id,
                and_(
                    Notification.target_user_id.is_(None),
                    Notification.target_role == db.query(User).filter(User.id == user_id).first().role
                )
            )
        ).first()
        
        if notification:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            db.commit()
            return True
        
        return False
    
    def mark_all_notifications_read(self, user_id: int, db: Session) -> int:
        """Mark all notifications as read for user"""
        updated_count = db.query(Notification).filter(
            or_(
                Notification.target_user_id == user_id,
                and_(
                    Notification.target_user_id.is_(None),
                    Notification.target_role == db.query(User).filter(User.id == user_id).first().role
                )
            ),
            Notification.is_read == False
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })
        
        db.commit()
        return updated_count
    
    def cleanup_old_notifications(self, days_old: int = 30, db: Session = None) -> int:
        """Clean up old read notifications"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        deleted_count = db.query(Notification).filter(
            Notification.is_read == True,
            Notification.read_at < cutoff_date
        ).delete()
        
        db.commit()
        return deleted_count
    
    def get_notification_stats(self, db: Session) -> Dict[str, Any]:
        """Get notification statistics for admin dashboard"""
        total_notifications = db.query(Notification).count()
        unread_notifications = db.query(Notification).filter(Notification.is_read == False).count()
        
        # Notifications by type
        high_risk_alerts = db.query(Notification).filter(
            Notification.type == "high_risk_alert"
        ).count()
        
        provider_assignments = db.query(Notification).filter(
            Notification.type == "provider_assignment"
        ).count()
        
        system_notifications = db.query(Notification).filter(
            Notification.type == "system_notification"
        ).count()
        
        # Recent high-risk alerts (last 24 hours)
        recent_high_risk = db.query(Notification).filter(
            Notification.type == "high_risk_alert",
            Notification.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        return {
            "total_notifications": total_notifications,
            "unread_notifications": unread_notifications,
            "notifications_by_type": {
                "high_risk_alerts": high_risk_alerts,
                "provider_assignments": provider_assignments,
                "system_notifications": system_notifications
            },
            "recent_high_risk_alerts": recent_high_risk
        }
    
    async def send_bulk_notification(
        self, 
        title: str, 
        message: str, 
        target_user_ids: List[int], 
        notification_type: str = "system_notification",
        priority: str = "medium",
        db: Session = None
    ) -> List[Notification]:
        """Send notification to multiple users"""
        
        notifications = []
        
        for user_id in target_user_ids:
            notification = Notification(
                type=notification_type,
                title=title,
                message=message,
                priority=priority,
                data={"bulk_notification": True},
                target_user_id=user_id,
                is_read=False,
                created_at=datetime.utcnow()
            )
            
            if db:
                db.add(notification)
            
            notifications.append(notification)
        
        if db:
            db.commit()
        
        # Send WebSocket notifications to online users
        for user_id in target_user_ids:
            await self.websocket_service.manager.send_personal_message({
                "type": notification_type,
                "priority": priority,
                "title": title,
                "message": message,
                "data": {"bulk_notification": True},
                "timestamp": datetime.utcnow().isoformat()
            }, user_id)
        
        print(f"Bulk notification sent to {len(target_user_ids)} users: {title}")
        return notifications


# Global notification service instance
notification_service = NotificationService()
