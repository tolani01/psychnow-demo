"""
Test intake endpoints
"""
import pytest
from fastapi.testclient import TestClient


def test_start_intake_session(client: TestClient, test_user_data):
    """Test starting an intake session"""
    # Register user and get token
    response = client.post("/api/v1/auth/register", json=test_user_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Start intake session
    response = client.post("/api/v1/intake/start", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["status"] == "active"


def test_start_intake_session_unauthorized(client: TestClient):
    """Test starting intake session without authentication"""
    response = client.post("/api/v1/intake/start")
    assert response.status_code == 401


def test_chat_intake_session(client: TestClient, test_user_data):
    """Test chatting in intake session"""
    # Register user and get token
    response = client.post("/api/v1/auth/register", json=test_user_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Start intake session
    response = client.post("/api/v1/intake/start", headers=headers)
    session_id = response.json()["session_id"]
    
    # Send chat message
    chat_data = {
        "session_id": session_id,
        "message": "Hello, I'm feeling anxious"
    }
    response = client.post("/api/v1/intake/chat", json=chat_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "phase" in data


def test_chat_invalid_session(client: TestClient, test_user_data):
    """Test chatting with invalid session ID"""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    chat_data = {
        "session_id": 99999,  # Invalid session ID
        "message": "Hello"
    }
    response = client.post("/api/v1/intake/chat", json=chat_data, headers=headers)
    assert response.status_code == 404


def test_get_intake_session(client: TestClient, test_user_data):
    """Test getting intake session details"""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Start intake session
    response = client.post("/api/v1/intake/start", headers=headers)
    session_id = response.json()["session_id"]
    
    # Get session details
    response = client.get(f"/api/v1/intake/session/{session_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id
    assert data["status"] == "active"


def test_pause_intake_session(client: TestClient, test_user_data):
    """Test pausing an intake session"""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Start intake session
    response = client.post("/api/v1/intake/start", headers=headers)
    session_id = response.json()["session_id"]
    
    # Pause session
    response = client.post(f"/api/v1/intake/session/{session_id}/pause", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "paused"
    assert "pause_expires_at" in data


def test_resume_intake_session(client: TestClient, test_user_data):
    """Test resuming a paused intake session"""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Start intake session
    response = client.post("/api/v1/intake/start", headers=headers)
    session_id = response.json()["session_id"]
    
    # Pause session
    client.post(f"/api/v1/intake/session/{session_id}/pause", headers=headers)
    
    # Resume session
    response = client.post(f"/api/v1/intake/session/{session_id}/resume", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
