"""
WebRTC Service for Telemedicine
Handles video/audio consultation setup, signaling, and session management
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.user import User
from app.models.intake_report import IntakeReport
from app.models.telemedicine_session import TelemedicineSession
from app.services.websocket_service import websocket_service


class WebRTCService:
    """Service for managing WebRTC telemedicine sessions"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.session_rooms: Dict[str, List[str]] = {}
        self.stun_servers = [
            "stun:stun.l.google.com:19302",
            "stun:stun1.l.google.com:19302"
        ]
        self.turn_servers = [
            # Add TURN server configuration for production
            # "turn:your-turn-server.com:3478?transport=udp"
        ]
    
    async def create_consultation_session(
        self,
        provider_id: int,
        patient_id: int,
        report_id: Optional[int] = None,
        session_type: str = "consultation",
        duration_minutes: int = 60,
        db: Session = None
    ) -> Dict[str, Any]:
        """Create a new telemedicine consultation session"""
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Create session record in database
        telemedicine_session = TelemedicineSession(
            session_id=session_id,
            provider_id=provider_id,
            patient_id=patient_id,
            report_id=report_id,
            session_type=session_type,
            status="scheduled",
            scheduled_start=datetime.utcnow() + timedelta(minutes=5),  # 5 minutes from now
            scheduled_duration=duration_minutes,
            created_at=datetime.utcnow()
        )
        
        if db:
            db.add(telemedicine_session)
            db.commit()
            db.refresh(telemedicine_session)
        
        # Store session in memory
        self.active_sessions[session_id] = {
            "session_id": session_id,
            "provider_id": provider_id,
            "patient_id": patient_id,
            "report_id": report_id,
            "session_type": session_type,
            "status": "scheduled",
            "created_at": datetime.utcnow(),
            "participants": [],
            "ice_candidates": [],
            "sdp_offers": {},
            "sdp_answers": {},
            "recording_enabled": False,
            "recording_data": None
        }
        
        # Send notifications to both participants
        await self._send_session_notifications(session_id, "session_created")
        
        return {
            "session_id": session_id,
            "provider_id": provider_id,
            "patient_id": patient_id,
            "report_id": report_id,
            "session_type": session_type,
            "status": "scheduled",
            "scheduled_start": telemedicine_session.scheduled_start.isoformat(),
            "duration_minutes": duration_minutes,
            "webrtc_config": {
                "stun_servers": self.stun_servers,
                "turn_servers": self.turn_servers,
                "session_id": session_id
            }
        }
    
    async def join_session(
        self,
        session_id: str,
        user_id: int,
        user_role: str,
        db: Session = None
    ) -> Dict[str, Any]:
        """Join an existing telemedicine session"""
        
        if session_id not in self.active_sessions:
            raise ValueError("Session not found")
        
        session = self.active_sessions[session_id]
        
        # Verify user has permission to join
        if user_role == "provider" and user_id != session["provider_id"]:
            raise ValueError("Provider not authorized for this session")
        if user_role == "patient" and user_id != session["patient_id"]:
            raise ValueError("Patient not authorized for this session")
        
        # Add participant to session
        participant = {
            "user_id": user_id,
            "role": user_role,
            "joined_at": datetime.utcnow(),
            "status": "connected"
        }
        
        if user_id not in [p["user_id"] for p in session["participants"]]:
            session["participants"].append(participant)
        
        # Update session status if needed
        if session["status"] == "scheduled":
            session["status"] = "active"
            session["started_at"] = datetime.utcnow()
        
        # Send join notification to other participants
        await self._send_session_notifications(session_id, "participant_joined", {
            "user_id": user_id,
            "role": user_role
        })
        
        return {
            "session_id": session_id,
            "user_id": user_id,
            "role": user_role,
            "status": "joined",
            "webrtc_config": {
                "stun_servers": self.stun_servers,
                "turn_servers": self.turn_servers,
                "session_id": session_id
            },
            "participants": session["participants"]
        }
    
    async def handle_ice_candidate(
        self,
        session_id: str,
        user_id: int,
        candidate: Dict[str, Any]
    ):
        """Handle ICE candidate exchange"""
        
        if session_id not in self.active_sessions:
            raise ValueError("Session not found")
        
        session = self.active_sessions[session_id]
        
        # Store ICE candidate
        candidate_data = {
            "user_id": user_id,
            "candidate": candidate,
            "timestamp": datetime.utcnow()
        }
        session["ice_candidates"].append(candidate_data)
        
        # Forward to other participants
        await self._broadcast_to_session(session_id, {
            "type": "ice_candidate",
            "from_user_id": user_id,
            "candidate": candidate,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_user=user_id)
    
    async def handle_sdp_offer(
        self,
        session_id: str,
        user_id: int,
        sdp_offer: str
    ):
        """Handle SDP offer exchange"""
        
        if session_id not in self.active_sessions:
            raise ValueError("Session not found")
        
        session = self.active_sessions[session_id]
        
        # Store SDP offer
        session["sdp_offers"][user_id] = {
            "sdp": sdp_offer,
            "timestamp": datetime.utcnow()
        }
        
        # Forward to other participants
        await self._broadcast_to_session(session_id, {
            "type": "sdp_offer",
            "from_user_id": user_id,
            "sdp": sdp_offer,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_user=user_id)
    
    async def handle_sdp_answer(
        self,
        session_id: str,
        user_id: int,
        sdp_answer: str
    ):
        """Handle SDP answer exchange"""
        
        if session_id not in self.active_sessions:
            raise ValueError("Session not found")
        
        session = self.active_sessions[session_id]
        
        # Store SDP answer
        session["sdp_answers"][user_id] = {
            "sdp": sdp_answer,
            "timestamp": datetime.utcnow()
        }
        
        # Forward to offer sender
        for offerer_id, offer_data in session["sdp_offers"].items():
            if offerer_id != user_id:
                await websocket_service.manager.send_personal_message({
                    "type": "sdp_answer",
                    "from_user_id": user_id,
                    "sdp": sdp_answer,
                    "session_id": session_id,
                    "timestamp": datetime.utcnow().isoformat()
                }, offerer_id)
    
    async def end_session(
        self,
        session_id: str,
        user_id: int,
        reason: str = "completed",
        db: Session = None
    ):
        """End a telemedicine session"""
        
        if session_id not in self.active_sessions:
            raise ValueError("Session not found")
        
        session = self.active_sessions[session_id]
        
        # Update session status
        session["status"] = "ended"
        session["ended_at"] = datetime.utcnow()
        session["end_reason"] = reason
        
        # Calculate session duration
        if "started_at" in session:
            duration = (datetime.utcnow() - session["started_at"]).total_seconds()
            session["duration_seconds"] = duration
        
        # Update database record
        if db:
            db_session = db.query(TelemedicineSession).filter(
                TelemedicineSession.session_id == session_id
            ).first()
            
            if db_session:
                db_session.status = "ended"
                db_session.ended_at = datetime.utcnow()
                db_session.end_reason = reason
                if "duration_seconds" in session:
                    db_session.duration_seconds = session["duration_seconds"]
                db.commit()
        
        # Notify all participants
        await self._broadcast_to_session(session_id, {
            "type": "session_ended",
            "reason": reason,
            "ended_by": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Clean up session data after a delay
        asyncio.create_task(self._cleanup_session(session_id, delay=300))  # 5 minutes
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a telemedicine session"""
        
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        return {
            "session_id": session_id,
            "provider_id": session["provider_id"],
            "patient_id": session["patient_id"],
            "report_id": session.get("report_id"),
            "session_type": session["session_type"],
            "status": session["status"],
            "participants": session["participants"],
            "created_at": session["created_at"].isoformat(),
            "started_at": session.get("started_at").isoformat() if session.get("started_at") else None,
            "ended_at": session.get("ended_at").isoformat() if session.get("ended_at") else None,
            "duration_seconds": session.get("duration_seconds")
        }
    
    async def get_user_sessions(
        self,
        user_id: int,
        status: Optional[str] = None,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Get telemedicine sessions for a user"""
        
        sessions = []
        
        # Get from active sessions
        for session_id, session_data in self.active_sessions.items():
            if (session_data["provider_id"] == user_id or 
                session_data["patient_id"] == user_id):
                
                if status is None or session_data["status"] == status:
                    sessions.append({
                        "session_id": session_id,
                        "provider_id": session_data["provider_id"],
                        "patient_id": session_data["patient_id"],
                        "report_id": session_data.get("report_id"),
                        "session_type": session_data["session_type"],
                        "status": session_data["status"],
                        "created_at": session_data["created_at"].isoformat(),
                        "started_at": session_data.get("started_at").isoformat() if session_data.get("started_at") else None,
                        "ended_at": session_data.get("ended_at").isoformat() if session_data.get("ended_at") else None
                    })
        
        # Get from database for completed sessions
        if db:
            query = db.query(TelemedicineSession).filter(
                (TelemedicineSession.provider_id == user_id) |
                (TelemedicineSession.patient_id == user_id)
            )
            
            if status:
                query = query.filter(TelemedicineSession.status == status)
            
            db_sessions = query.order_by(TelemedicineSession.created_at.desc()).limit(50).all()
            
            for db_session in db_sessions:
                # Skip if already in active sessions
                if db_session.session_id not in self.active_sessions:
                    sessions.append({
                        "session_id": db_session.session_id,
                        "provider_id": db_session.provider_id,
                        "patient_id": db_session.patient_id,
                        "report_id": db_session.report_id,
                        "session_type": db_session.session_type,
                        "status": db_session.status,
                        "created_at": db_session.created_at.isoformat(),
                        "started_at": db_session.started_at.isoformat() if db_session.started_at else None,
                        "ended_at": db_session.ended_at.isoformat() if db_session.ended_at else None,
                        "duration_seconds": db_session.duration_seconds
                    })
        
        return sessions
    
    async def _send_session_notifications(
        self,
        session_id: str,
        notification_type: str,
        data: Optional[Dict] = None
    ):
        """Send notifications about session events"""
        
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        
        # Send to provider
        await websocket_service.manager.send_personal_message({
            "type": "telemedicine_notification",
            "session_id": session_id,
            "notification_type": notification_type,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }, session["provider_id"])
        
        # Send to patient
        await websocket_service.manager.send_personal_message({
            "type": "telemedicine_notification",
            "session_id": session_id,
            "notification_type": notification_type,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }, session["patient_id"])
    
    async def _broadcast_to_session(
        self,
        session_id: str,
        message: Dict[str, Any],
        exclude_user: Optional[int] = None
    ):
        """Broadcast message to all session participants"""
        
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        
        for participant in session["participants"]:
            if participant["user_id"] != exclude_user:
                await websocket_service.manager.send_personal_message({
                    **message,
                    "session_id": session_id
                }, participant["user_id"])
    
    async def _cleanup_session(self, session_id: str, delay: int = 300):
        """Clean up session data after delay"""
        
        await asyncio.sleep(delay)
        
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            
            # Only cleanup if session has ended
            if session.get("status") == "ended":
                del self.active_sessions[session_id]
                print(f"Cleaned up session: {session_id}")


# Global WebRTC service instance
webrtc_service = WebRTCService()
