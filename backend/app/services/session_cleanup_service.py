"""
Session Cleanup Service
Handles cleanup of expired paused sessions and maintenance tasks
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.intake_session import IntakeSession
from app.services.conversation_service import conversation_service
import logging

logger = logging.getLogger(__name__)


class SessionCleanupService:
    """Service for cleaning up expired sessions and maintenance tasks"""
    
    def __init__(self):
        self.cleanup_interval_hours = 1  # Run cleanup every hour
    
    def cleanup_expired_sessions(self, db: Session):
        """
        Clean up expired paused sessions
        Marks them as abandoned and removes from memory
        """
        try:
            # Find expired paused sessions
            expired_sessions = db.query(IntakeSession).filter(
                IntakeSession.status == "paused",
                IntakeSession.expires_at < datetime.utcnow()
            ).all()
            
            cleaned_count = 0
            for session in expired_sessions:
                # Mark as abandoned
                session.status = "abandoned"
                
                # Remove from conversation service memory
                if session.session_token in conversation_service.sessions:
                    del conversation_service.sessions[session.session_token]
                
                cleaned_count += 1
            
            if cleaned_count > 0:
                db.commit()
                logger.info(f"Cleaned up {cleaned_count} expired paused sessions")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            db.rollback()
            return 0
    
    def cleanup_abandoned_sessions(self, db: Session, hours_threshold: int = 48):
        """
        Clean up abandoned sessions older than threshold
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_threshold)
            
            abandoned_sessions = db.query(IntakeSession).filter(
                IntakeSession.status == "abandoned",
                IntakeSession.updated_at < cutoff_time
            ).all()
            
            cleaned_count = 0
            for session in abandoned_sessions:
                # Remove from conversation service memory if still there
                if session.session_token in conversation_service.sessions:
                    del conversation_service.sessions[session.session_token]
                
                cleaned_count += 1
            
            if cleaned_count > 0:
                # Note: We don't delete from database, just clean memory
                # Database records should be kept for audit purposes
                logger.info(f"Cleaned up {cleaned_count} abandoned sessions from memory")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up abandoned sessions: {e}")
            return 0
    
    def get_expiring_sessions(self, db: Session, hours_ahead: int = 2):
        """
        Get sessions that will expire within the specified hours
        Used for sending reminder emails
        """
        try:
            cutoff_time = datetime.utcnow() + timedelta(hours=hours_ahead)
            
            expiring_sessions = db.query(IntakeSession).filter(
                IntakeSession.status == "paused",
                IntakeSession.expires_at <= cutoff_time,
                IntakeSession.expires_at > datetime.utcnow()
            ).all()
            
            return expiring_sessions
            
        except Exception as e:
            logger.error(f"Error getting expiring sessions: {e}")
            return []
    
    def get_session_stats(self, db: Session):
        """
        Get statistics about session states
        """
        try:
            stats = {
                "active": db.query(IntakeSession).filter(
                    IntakeSession.status == "active"
                ).count(),
                "paused": db.query(IntakeSession).filter(
                    IntakeSession.status == "paused"
                ).count(),
                "completed": db.query(IntakeSession).filter(
                    IntakeSession.status == "completed"
                ).count(),
                "abandoned": db.query(IntakeSession).filter(
                    IntakeSession.status == "abandoned"
                ).count(),
                "total": db.query(IntakeSession).count()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting session stats: {e}")
            return {}


# Global cleanup service instance
session_cleanup_service = SessionCleanupService()
