"""
Test authentication endpoints
"""
import pytest
from fastapi.testclient import TestClient


def test_register_patient(client: TestClient, test_user_data):
    """Test patient registration"""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_provider(client: TestClient, test_provider_data):
    """Test provider registration"""
    response = client.post("/api/v1/auth/register", json=test_provider_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_invalid_invite_code(client: TestClient, test_provider_data):
    """Test provider registration with invalid invite code"""
    test_provider_data["invite_code"] = "invalid-code"
    response = client.post("/api/v1/auth/register", json=test_provider_data)
    assert response.status_code == 400
    assert "Invalid invite code" in response.json()["detail"]


def test_login(client: TestClient, test_user_data):
    """Test user login"""
    # First register
    client.post("/api/v1/auth/register", json=test_user_data)
    
    # Then login
    login_data = {
        "username": test_user_data["email"],
        "password": test_user_data["password"]
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials"""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_get_current_user(client: TestClient, test_user_data):
    """Test getting current user info"""
    # Register and get token
    response = client.post("/api/v1/auth/register", json=test_user_data)
    token = response.json()["access_token"]
    
    # Get current user
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["role"] == test_user_data["role"]


def test_get_current_user_no_token(client: TestClient):
    """Test getting current user without token"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_current_user_invalid_token(client: TestClient):
    """Test getting current user with invalid token"""
    headers = {"Authorization": "Bearer invalid-token"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
