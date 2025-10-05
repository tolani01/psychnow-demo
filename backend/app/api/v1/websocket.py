"""
WebSocket API endpoints for real-time notifications
"""

from fastapi import APIRouter, WebSocket, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.services.websocket_service import websocket_service

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for real-time notifications
    
    Query Parameters:
    - token: JWT authentication token
    
    Message Types:
    - pong: Response to ping
    - subscribe: Subscribe to notification types
    - mark_notification_read: Mark notification as read
    
    Notification Types:
    - high_risk_alert: Critical patient alerts
    - provider_assignment: New patient assignments
    - system_notification: System-wide notifications
    """
    await websocket_service.handle_connection(websocket, token, db)


@router.get("/ws/stats")
async def get_websocket_stats(db: Session = Depends(get_db)):
    """Get WebSocket connection statistics"""
    stats = websocket_service.get_connection_stats()
    return {
        "success": True,
        "data": stats,
        "message": "WebSocket statistics retrieved successfully"
    }
