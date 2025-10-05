"""
Escalation Service
Handles high-risk patient alerts and notifications
"""
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.models.user import User, UserRole


class EscalationService:
    """Service for handling high-risk escalations"""
    
    async def handle_high_risk_detection(
        self,
        session_data: Dict[str, Any],
        risk_details: Dict[str, Any],
        db: Session
    ):
        """
        Handle detection of high-risk patient
        
        Args:
            session_data: Intake session data
            risk_details: Details of risk assessment (from C-SSRS or similar)
            db: Database session
        """
        # Create audit log
        audit = AuditLog(
            event_type="high_risk_detected",
            action="create",
            user_id=session_data.get("patient_id"),
            resource_type="intake_session",
            resource_id=session_data.get("session_token"),
            event_metadata={
                "risk_level": risk_details.get("risk_level"),
                "screener": risk_details.get("screener_name"),
                "score": risk_details.get("score"),
                "flagged_at": datetime.utcnow().isoformat()
            },
            timestamp=datetime.utcnow()
        )
        db.add(audit)
        
        # Get all admin users
        admins = db.query(User).filter(User.role == UserRole.ADMIN, User.is_active == True).all()
        
        # Create notification for each admin
        for admin in admins:
            notification = Notification(
                user_id=admin.id,
                type="high_risk_alert",
                priority="urgent",
                title="⚠️ HIGH RISK PATIENT DETECTED",
                message=f"""
A patient intake has been flagged as high risk.

Risk Level: {risk_details.get('risk_level', 'Unknown')}
Screener: {risk_details.get('screener_name', 'Unknown')}
Details: {risk_details.get('details', 'No additional details')}

Session ID: {session_data.get('session_token')}
Flagged At: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

ACTION REQUIRED: Review immediately and follow safety protocol.
                """.strip(),
                resource_type="intake_session",
                resource_id=session_data.get("session_token"),
                created_at=datetime.utcnow()
            )
            db.add(notification)
        
        db.commit()
        
        # TODO: Send email/SMS to admin (for pilot)
        # await self.send_sms_alert(admin.phone, message)
        # await self.send_email_alert(admin.email, message)
        
        return {
            "escalated": True,
            "notified_admins": len(admins),
            "audit_logged": True
        }
    
    async def send_email_alert(self, email: str, message: str):
        """
        Send email alert for high-risk patient
        Placeholder for future email integration
        """
        # TODO: Integrate with email service (Postmark, SendGrid, etc.)
        print(f"📧 EMAIL ALERT to {email}: {message}")
        pass
    
    async def send_sms_alert(self, phone: str, message: str):
        """
        Send SMS alert for high-risk patient
        Placeholder for future SMS integration (Twilio)
        """
        # TODO: Integrate with Twilio
        print(f"📱 SMS ALERT to {phone}: {message}")
        pass


# Global escalation service instance
escalation_service = EscalationService()

