"""
WebSocket Service for Real-time Notifications
Handles WebSocket connections, authentication, and message broadcasting
"""

import json
import asyncio
from typing import Dict, List, Optional, Set
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.security import verify_jwt_token
from app.models.user import User


class WebSocketManager:
    """Manages WebSocket connections and message broadcasting"""
    
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[int, WebSocket] = {}
        # Store connections by role for targeted messaging
        self.connections_by_role: Dict[str, Set[int]] = {
            "provider": set(),
            "admin": set(),
            "patient": set()
        }
        # Store connection metadata
        self.connection_metadata: Dict[int, Dict] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int, role: str, db: Session):
        """Accept WebSocket connection and authenticate user"""
        await websocket.accept()
        
        # Verify user exists and is active
        user = db.query(User).filter(User.id == user_id).first()
        if not user or user.is_active is False:
            await websocket.close(code=4001, reason="User not found or inactive")
            return False
        
        # Store connection
        self.active_connections[user_id] = websocket
        self.connections_by_role[role].add(user_id)
        self.connection_metadata[user_id] = {
            "role": role,
            "connected_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "message": "WebSocket connection established",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "role": role
        }, user_id)
        
        print(f"WebSocket connected: User {user_id} ({role})")
        return True
    
    def disconnect(self, user_id: int):
        """Remove WebSocket connection"""
        if user_id in self.active_connections:
            # Remove from role-based connections
            metadata = self.connection_metadata.get(user_id, {})
            role = metadata.get("role")
            if role and user_id in self.connections_by_role[role]:
                self.connections_by_role[role].remove(user_id)
            
            # Remove connection
            del self.active_connections[user_id]
            if user_id in self.connection_metadata:
                del self.connection_metadata[user_id]
            
            print(f"WebSocket disconnected: User {user_id}")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to specific user"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
                # Update last activity
                if user_id in self.connection_metadata:
                    self.connection_metadata[user_id]["last_activity"] = datetime.utcnow()
            except Exception as e:
                print(f"Error sending message to user {user_id}: {e}")
                self.disconnect(user_id)
    
    async def send_to_role(self, message: dict, role: str):
        """Send message to all users with specific role"""
        if role in self.connections_by_role:
            for user_id in list(self.connections_by_role[role]):
                await self.send_personal_message(message, user_id)
    
    async def send_to_providers(self, message: dict):
        """Send message to all providers"""
        await self.send_to_role(message, "provider")
    
    async def send_to_admins(self, message: dict):
        """Send message to all admins"""
        await self.send_to_role(message, "admin")
    
    async def broadcast_notification(self, notification: dict):
        """Broadcast notification based on type and target"""
        notification_type = notification.get("type")
        target_role = notification.get("target_role")
        
        if target_role:
            await self.send_to_role(notification, target_role)
        elif notification_type == "high_risk_alert":
            # High-risk alerts go to all providers and admins
            await self.send_to_providers(notification)
            await self.send_to_admins(notification)
        elif notification_type == "system_alert":
            # System alerts go to all admins
            await self.send_to_admins(notification)
        else:
            # Default: send to providers
            await self.send_to_providers(notification)
    
    def get_connection_stats(self) -> dict:
        """Get WebSocket connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "connections_by_role": {
                role: len(user_ids) for role, user_ids in self.connections_by_role.items()
            },
            "connection_metadata": self.connection_metadata
        }
    
    async def ping_all_connections(self):
        """Send ping to all connections to check health"""
        ping_message = {
            "type": "ping",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(ping_message, user_id)


class WebSocketService:
    """High-level WebSocket service for business logic"""
    
    def __init__(self):
        self.manager = WebSocketManager()
    
    async def handle_connection(self, websocket: WebSocket, token: str, db: Session):
        """Handle incoming WebSocket connection"""
        try:
            # Verify JWT token
            payload = verify_jwt_token(token)
            if not payload:
                await websocket.close(code=4001, reason="Invalid token")
                return
            
            user_id = payload.get("sub")
            role = payload.get("role")
            
            if not user_id or not role:
                await websocket.close(code=4001, reason="Invalid token payload")
                return
            
            # Connect user
            connected = await self.manager.connect(websocket, user_id, role, db)
            if not connected:
                return
            
            # Keep connection alive and handle messages
            await self._handle_messages(websocket, user_id, db)
            
        except WebSocketDisconnect:
            self.manager.disconnect(user_id)
        except Exception as e:
            print(f"WebSocket connection error: {e}")
            self.manager.disconnect(user_id)
    
    async def _handle_messages(self, websocket: WebSocket, user_id: int, db: Session):
        """Handle incoming WebSocket messages"""
        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Update last activity
                if user_id in self.manager.connection_metadata:
                    self.manager.connection_metadata[user_id]["last_activity"] = datetime.utcnow()
                
                # Handle different message types
                message_type = message.get("type")
                
                if message_type == "pong":
                    # Respond to ping
                    continue
                elif message_type == "subscribe":
                    # Handle subscription requests (future feature)
                    await self._handle_subscription(user_id, message)
                elif message_type == "mark_notification_read":
                    # Handle notification read status
                    await self._handle_notification_read(user_id, message, db)
                else:
                    # Echo unknown message types
                    await self.manager.send_personal_message({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                        "timestamp": datetime.utcnow().isoformat()
                    }, user_id)
                
        except WebSocketDisconnect:
            self.manager.disconnect(user_id)
        except Exception as e:
            print(f"Error handling WebSocket messages for user {user_id}: {e}")
            self.manager.disconnect(user_id)
    
    async def _handle_subscription(self, user_id: int, message: dict):
        """Handle subscription requests"""
        # Future: Handle user subscriptions to specific notification types
        pass
    
    async def _handle_notification_read(self, user_id: int, message: dict, db: Session):
        """Handle notification read status updates"""
        notification_id = message.get("notification_id")
        if notification_id:
            # Update notification as read in database
            # This would integrate with the notification service
            pass
    
    async def send_high_risk_alert(self, patient_name: str, report_id: int, risk_details: dict):
        """Send high-risk patient alert to providers and admins"""
        alert_message = {
            "type": "high_risk_alert",
            "priority": "critical",
            "title": "High-Risk Patient Alert",
            "message": f"Patient {patient_name} requires immediate review",
            "data": {
                "patient_name": patient_name,
                "report_id": report_id,
                "risk_level": risk_details.get("risk_level"),
                "urgency": risk_details.get("urgency"),
                "screener_name": risk_details.get("screener_name"),
                "score": risk_details.get("score"),
                "details": risk_details.get("details")
            },
            "timestamp": datetime.utcnow().isoformat(),
            "target_role": None  # Broadcast to providers and admins
        }
        
        await self.manager.broadcast_notification(alert_message)
    
    async def send_provider_assignment(self, provider_id: int, patient_name: str, report_id: int):
        """Send new assignment notification to specific provider"""
        assignment_message = {
            "type": "provider_assignment",
            "priority": "medium",
            "title": "New Patient Assignment",
            "message": f"New patient report assigned: {patient_name}",
            "data": {
                "patient_name": patient_name,
                "report_id": report_id,
                "assignment_time": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat(),
            "target_role": "provider"
        }
        
        await self.manager.send_personal_message(assignment_message, provider_id)
    
    async def send_system_notification(self, title: str, message: str, target_role: str = "admin"):
        """Send system-wide notification"""
        system_message = {
            "type": "system_notification",
            "priority": "low",
            "title": title,
            "message": message,
            "data": {},
            "timestamp": datetime.utcnow().isoformat(),
            "target_role": target_role
        }
        
        await self.manager.send_to_role(system_message, target_role)
    
    def get_connection_stats(self) -> dict:
        """Get WebSocket connection statistics"""
        return self.manager.get_connection_stats()


# Global WebSocket service instance
websocket_service = WebSocketService()
