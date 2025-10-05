"""
Telemedicine API Endpoints
WebRTC consultation and session management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.db.session import get_db
from app.models.user import User
from app.models.telemedicine_session import TelemedicineSession
from app.core.deps import get_current_user, get_current_provider
from app.services.webrtc_service import webrtc_service
from app.services.websocket_service import websocket_service

router = APIRouter()


# Pydantic models
class CreateSessionRequest(BaseModel):
    patient_id: int
    report_id: Optional[int] = None
    session_type: str = "consultation"
    duration_minutes: int = 60
    scheduled_start: Optional[datetime] = None


class JoinSessionRequest(BaseModel):
    session_id: str


class ICECandidateRequest(BaseModel):
    session_id: str
    candidate: Dict[str, Any]


class SDPOfferRequest(BaseModel):
    session_id: str
    sdp_offer: str


class SDPAnswerRequest(BaseModel):
    session_id: str
    sdp_answer: str


class EndSessionRequest(BaseModel):
    session_id: str
    reason: str = "completed"


@router.post("/sessions/create")
async def create_consultation_session(
    request: CreateSessionRequest,
    current_user: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Create a new telemedicine consultation session
    """
    try:
        # Verify patient exists
        patient = db.query(User).filter(
            User.id == request.patient_id,
            User.role == "patient",
            User.is_active == True
        ).first()
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found or inactive"
            )
        
        # Create session
        session_data = await webrtc_service.create_consultation_session(
            provider_id=current_user.id,
            patient_id=request.patient_id,
            report_id=request.report_id,
            session_type=request.session_type,
            duration_minutes=request.duration_minutes,
            db=db
        )
        
        return {
            "success": True,
            "message": "Telemedicine session created successfully",
            "data": session_data
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@router.post("/sessions/join")
async def join_session(
    request: JoinSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Join an existing telemedicine session
    """
    try:
        # Determine user role
        user_role = "provider" if current_user.role == "provider" else "patient"
        
        session_data = await webrtc_service.join_session(
            session_id=request.session_id,
            user_id=current_user.id,
            user_role=user_role,
            db=db
        )
        
        return {
            "success": True,
            "message": "Successfully joined session",
            "data": session_data
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to join session: {str(e)}"
        )


@router.post("/sessions/ice-candidate")
async def handle_ice_candidate(
    request: ICECandidateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Handle ICE candidate exchange for WebRTC connection
    """
    try:
        await webrtc_service.handle_ice_candidate(
            session_id=request.session_id,
            user_id=current_user.id,
            candidate=request.candidate
        )
        
        return {
            "success": True,
            "message": "ICE candidate processed"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process ICE candidate: {str(e)}"
        )


@router.post("/sessions/sdp-offer")
async def handle_sdp_offer(
    request: SDPOfferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Handle SDP offer for WebRTC connection
    """
    try:
        await webrtc_service.handle_sdp_offer(
            session_id=request.session_id,
            user_id=current_user.id,
            sdp_offer=request.sdp_offer
        )
        
        return {
            "success": True,
            "message": "SDP offer processed"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process SDP offer: {str(e)}"
        )


@router.post("/sessions/sdp-answer")
async def handle_sdp_answer(
    request: SDPAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Handle SDP answer for WebRTC connection
    """
    try:
        await webrtc_service.handle_sdp_answer(
            session_id=request.session_id,
            user_id=current_user.id,
            sdp_answer=request.sdp_answer
        )
        
        return {
            "success": True,
            "message": "SDP answer processed"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process SDP answer: {str(e)}"
        )


@router.post("/sessions/end")
async def end_session(
    request: EndSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    End a telemedicine session
    """
    try:
        await webrtc_service.end_session(
            session_id=request.session_id,
            user_id=current_user.id,
            reason=request.reason,
            db=db
        )
        
        return {
            "success": True,
            "message": "Session ended successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end session: {str(e)}"
        )


@router.get("/sessions/{session_id}")
async def get_session_info(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get information about a telemedicine session
    """
    try:
        session_info = await webrtc_service.get_session_info(session_id)
        
        if not session_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Verify user has access to this session
        if (current_user.id != session_info["provider_id"] and 
            current_user.id != session_info["patient_id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this session"
            )
        
        return {
            "success": True,
            "data": session_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session info: {str(e)}"
        )


@router.get("/sessions")
async def get_user_sessions(
    status: Optional[str] = Query(None, description="Filter by session status"),
    limit: int = Query(50, description="Maximum number of sessions"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get telemedicine sessions for the current user
    """
    try:
        sessions = await webrtc_service.get_user_sessions(
            user_id=current_user.id,
            status=status,
            db=db
        )
        
        # Limit results
        sessions = sessions[:limit]
        
        return {
            "success": True,
            "data": sessions,
            "count": len(sessions)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sessions: {str(e)}"
        )


@router.websocket("/sessions/{session_id}/signaling")
async def websocket_signaling(
    websocket: WebSocket,
    session_id: str,
    token: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for WebRTC signaling
    """
    try:
        # Verify session exists
        session_info = await webrtc_service.get_session_info(session_id)
        if not session_info:
            await websocket.close(code=4004, reason="Session not found")
            return
        
        # Verify token and get user
        from app.core.security import verify_jwt_token
        payload = verify_jwt_token(token)
        if not payload:
            await websocket.close(code=4001, reason="Invalid token")
            return
        
        user_id = payload.get("sub")
        user_role = payload.get("role")
        
        # Verify user has access to session
        if (user_id != session_info["provider_id"] and 
            user_id != session_info["patient_id"]):
            await websocket.close(code=4003, reason="Access denied")
            return
        
        await websocket.accept()
        
        # Handle WebSocket messages for signaling
        try:
            while True:
                data = await websocket.receive_json()
                message_type = data.get("type")
                
                if message_type == "ice_candidate":
                    await webrtc_service.handle_ice_candidate(
                        session_id, user_id, data.get("candidate", {})
                    )
                elif message_type == "sdp_offer":
                    await webrtc_service.handle_sdp_offer(
                        session_id, user_id, data.get("sdp", "")
                    )
                elif message_type == "sdp_answer":
                    await webrtc_service.handle_sdp_answer(
                        session_id, user_id, data.get("sdp", "")
                    )
                elif message_type == "ping":
                    await websocket.send_json({"type": "pong"})
                
        except WebSocketDisconnect:
            print(f"WebSocket disconnected for session {session_id}, user {user_id}")
        except Exception as e:
            print(f"WebSocket error in session {session_id}: {e}")
            await websocket.close(code=4000, reason="Internal error")
            
    except Exception as e:
        print(f"WebSocket connection error: {e}")
        await websocket.close(code=4000, reason="Connection error")


@router.get("/config/webrtc")
async def get_webrtc_config(
    current_user: User = Depends(get_current_user)
):
    """
    Get WebRTC configuration (STUN/TURN servers)
    """
    return {
        "success": True,
        "data": {
            "stun_servers": webrtc_service.stun_servers,
            "turn_servers": webrtc_service.turn_servers,
            "ice_servers": {
                "stun": webrtc_service.stun_servers,
                "turn": webrtc_service.turn_servers
            }
        }
    }
