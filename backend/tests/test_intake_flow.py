"""
Test intake conversation flow end-to-end
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)


@pytest.fixture
def patient_token():
    """Create a patient token for testing"""
    return create_access_token(data={"sub": "test@example.com", "role": "patient"})


@pytest.fixture
def provider_token():
    """Create a provider token for testing"""
    return create_access_token(data={"sub": "provider@example.com", "role": "provider"})


def test_intake_session_start(patient_token):
    """Test starting an intake session"""
    
    headers = {"Authorization": f"Bearer {patient_token}"}
    
    response = client.post("/api/v1/intake/start", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "session_id" in data
    assert "greeting" in data
    assert data["phase"] == "greeting"
    
    return data["session_id"]


def test_intake_conversation_flow(patient_token):
    """Test complete intake conversation flow"""
    
    headers = {"Authorization": f"Bearer {patient_token}"}
    
    # Start session
    response = client.post("/api/v1/intake/start", headers=headers)
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    
    # Test consent phase
    consent_data = {
        "session_id": session_id,
        "message": "I consent to the assessment",
        "consent_given": True
    }
    
    response = client.post("/api/v1/intake/chat", json=consent_data, headers=headers)
    assert response.status_code == 200
    
    # Test conversation phase
    conversation_data = {
        "session_id": session_id,
        "message": "I've been feeling depressed lately"
    }
    
    response = client.post("/api/v1/intake/chat", json=conversation_data, headers=headers)
    assert response.status_code == 200
    
    # Test screener phase
    screener_data = {
        "session_id": session_id,
        "message": "Yes",
        "screener_id": "phq9",
        "question_id": "phq9_1"
    }
    
    response = client.post("/api/v1/intake/chat", json=screener_data, headers=headers)
    assert response.status_code == 200
    
    # Test completion
    completion_data = {
        "session_id": session_id,
        "message": ":finish"
    }
    
    response = client.post("/api/v1/intake/chat", json=completion_data, headers=headers)
    assert response.status_code == 200


def test_intake_pause_resume(patient_token):
    """Test pause and resume functionality"""
    
    headers = {"Authorization": f"Bearer {patient_token}"}
    
    # Start session
    response = client.post("/api/v1/intake/start", headers=headers)
    session_id = response.json()["session_id"]
    
    # Pause session
    response = client.post(f"/api/v1/intake/{session_id}/pause", headers=headers)
    assert response.status_code == 200
    
    # Resume session
    response = client.post(f"/api/v1/intake/{session_id}/resume", headers=headers)
    assert response.status_code == 200


def test_intake_safety_escalation(patient_token):
    """Test safety escalation for high-risk responses"""
    
    headers = {"Authorization": f"Bearer {patient_token}"}
    
    # Start session
    response = client.post("/api/v1/intake/start", headers=headers)
    session_id = response.json()["session_id"]
    
    # Provide high-risk response
    high_risk_data = {
        "session_id": session_id,
        "message": "I want to kill myself"
    }
    
    response = client.post("/api/v1/intake/chat", json=high_risk_data, headers=headers)
    assert response.status_code == 200
    
    # Check if escalation was triggered
    data = response.json()
    assert "escalation" in data or "safety" in data


def test_intake_rate_limiting(patient_token):
    """Test rate limiting on chat endpoint"""
    
    headers = {"Authorization": f"Bearer {patient_token}"}
    
    # Start session
    response = client.post("/api/v1/intake/start", headers=headers)
    session_id = response.json()["session_id"]
    
    # Make multiple rapid requests
    for _ in range(12):  # Exceed rate limit
        response = client.post("/api/v1/intake/chat", 
                             json={"session_id": session_id, "message": "test"}, 
                             headers=headers)
        
        if response.status_code == 429:
            break
    
    # Should eventually hit rate limit
    assert response.status_code == 429


def test_intake_invalid_session(patient_token):
    """Test handling of invalid session IDs"""
    
    headers = {"Authorization": f"Bearer {patient_token}"}
    
    # Try to chat with invalid session
    invalid_data = {
        "session_id": "invalid-session-id",
        "message": "test"
    }
    
    response = client.post("/api/v1/intake/chat", json=invalid_data, headers=headers)
    assert response.status_code == 404


def test_intake_unauthorized_access():
    """Test unauthorized access to intake endpoints"""
    
    # Try to access without token
    response = client.post("/api/v1/intake/start")
    assert response.status_code == 401
    
    # Try to access with invalid token
    headers = {"Authorization": "Bearer invalid-token"}
    response = client.post("/api/v1/intake/start", headers=headers)
    assert response.status_code == 401
