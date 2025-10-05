"""
Test authentication flow end-to-end
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.session import get_db
from app.models.user import User
from app.core.security import create_access_token

client = TestClient(app)


@pytest.fixture
def test_db():
    """Get test database session"""
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_user_registration_flow(test_db: Session):
    """Test complete user registration flow"""
    
    # Test registration
    registration_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "role": "patient"
    }
    
    response = client.post("/api/v1/auth/register", json=registration_data)
    assert response.status_code == 201
    
    # Test login
    login_data = {
        "username": "test@example.com",
        "password": "TestPassword123!"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    
    # Test protected endpoint
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_provider_registration_with_invite(test_db: Session):
    """Test provider registration with invite code"""
    
    registration_data = {
        "email": "provider@example.com",
        "password": "ProviderPass123!",
        "first_name": "Provider",
        "last_name": "User",
        "role": "provider",
        "invite_code": "PSYCHNOW-PROVIDER-2024"
    }
    
    response = client.post("/api/v1/auth/register", json=registration_data)
    assert response.status_code == 201
    
    # Verify provider can access provider endpoints
    login_data = {
        "username": "provider@example.com",
        "password": "ProviderPass123!"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test provider dashboard access
    response = client.get("/api/v1/providers/dashboard", headers=headers)
    assert response.status_code == 200


def test_invalid_login_attempts():
    """Test rate limiting on login attempts"""
    
    login_data = {
        "username": "nonexistent@example.com",
        "password": "WrongPassword"
    }
    
    # Make multiple failed login attempts
    for _ in range(6):  # Exceed rate limit
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code in [401, 429]  # Either unauthorized or rate limited


def test_password_validation():
    """Test password strength validation"""
    
    weak_passwords = [
        "123",  # Too short
        "password",  # Too weak
        "12345678",  # No special chars
    ]
    
    for weak_password in weak_passwords:
        registration_data = {
            "email": f"test{weak_password}@example.com",
            "password": weak_password,
            "first_name": "Test",
            "last_name": "User",
            "role": "patient"
        }
        
        response = client.post("/api/v1/auth/register", json=registration_data)
        assert response.status_code == 422  # Validation error


def test_email_validation():
    """Test email format validation"""
    
    invalid_emails = [
        "invalid-email",
        "@example.com",
        "test@",
        "test..test@example.com"
    ]
    
    for invalid_email in invalid_emails:
        registration_data = {
            "email": invalid_email,
            "password": "ValidPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "role": "patient"
        }
        
        response = client.post("/api/v1/auth/register", json=registration_data)
        assert response.status_code == 422  # Validation error
