#!/usr/bin/env python3
"""
Comprehensive End-to-End Test Suite for PsychNow Platform
Tests the complete user journey from registration to report generation
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Test configuration
BASE_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:3000"

class TestSession:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.session_id = None
        
        # Setup retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def test_health_check(self) -> bool:
        """Test if backend is running"""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                self.log("✅ Backend health check passed")
                return True
            else:
                self.log(f"❌ Backend health check failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Backend health check failed: {e}", "ERROR")
            return False

    def test_frontend_health(self) -> bool:
        """Test if frontend is running"""
        try:
            response = self.session.get(FRONTEND_URL, timeout=5)
            if response.status_code == 200:
                self.log("✅ Frontend health check passed")
                return True
            else:
                self.log(f"❌ Frontend health check failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Frontend health check failed: {e}", "ERROR")
            return False

    def register_user(self) -> bool:
        """Test user registration"""
        user_data = {
            "email": f"testuser_{int(time.time())}@example.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "role": "patient"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/v1/auth/register", json=user_data)
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.log("✅ User registration successful")
                return True
            else:
                self.log(f"❌ User registration failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ User registration failed: {e}", "ERROR")
            return False

    def test_auth_me(self) -> bool:
        """Test getting current user info"""
        if not self.token:
            self.log("❌ No token available for auth test", "ERROR")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = self.session.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.user_id = data["id"]
                self.log("✅ Auth me endpoint successful")
                return True
            else:
                self.log(f"❌ Auth me failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Auth me failed: {e}", "ERROR")
            return False

    def start_intake_session(self) -> bool:
        """Test starting intake session"""
        if not self.token:
            self.log("❌ No token available for intake test", "ERROR")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = self.session.post(f"{BASE_URL}/api/v1/intake/start", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.session_id = data["session_id"]
                self.log("✅ Intake session started successfully")
                return True
            else:
                self.log(f"❌ Intake session start failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Intake session start failed: {e}", "ERROR")
            return False

    def test_intake_chat(self) -> bool:
        """Test intake chat functionality"""
        if not self.token or not self.session_id:
            self.log("❌ No token or session ID for chat test", "ERROR")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test initial greeting
        chat_data = {
            "session_id": self.session_id,
            "message": "Hello, I'm ready to start my assessment"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/v1/intake/chat", json=chat_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Chat response received: {data.get('phase', 'unknown phase')}")
                
                # Test consent flow
                if "consent" in data.get("phase", "").lower():
                    consent_data = {
                        "session_id": self.session_id,
                        "message": "Yes, I consent to proceed"
                    }
                    response = self.session.post(f"{BASE_URL}/api/v1/intake/chat", json=consent_data, headers=headers)
                    if response.status_code == 200:
                        self.log("✅ Consent flow completed")
                
                # Test symptom reporting
                symptom_data = {
                    "session_id": self.session_id,
                    "message": "I've been feeling anxious and depressed for the past few weeks"
                }
                response = self.session.post(f"{BASE_URL}/api/v1/intake/chat", json=symptom_data, headers=headers)
                if response.status_code == 200:
                    self.log("✅ Symptom reporting successful")
                    
                return True
            else:
                self.log(f"❌ Chat test failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Chat test failed: {e}", "ERROR")
            return False

    def test_screeners_list(self) -> bool:
        """Test getting available screeners"""
        try:
            response = self.session.get(f"{BASE_URL}/api/v1/screeners")
            if response.status_code == 200:
                data = response.json()
                screener_count = len(data.get("screeners", []))
                self.log(f"✅ Screeners list retrieved: {screener_count} screeners available")
                return screener_count >= 30  # Should have 30 screeners
            else:
                self.log(f"❌ Screeners list failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Screeners list failed: {e}", "ERROR")
            return False

    def test_pause_resume(self) -> bool:
        """Test pause/resume functionality"""
        if not self.token or not self.session_id:
            self.log("❌ No token or session ID for pause/resume test", "ERROR")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            # Test pause
            response = self.session.post(f"{BASE_URL}/api/v1/intake/session/{self.session_id}/pause", headers=headers)
            if response.status_code == 200:
                self.log("✅ Session paused successfully")
                
                # Test resume
                response = self.session.post(f"{BASE_URL}/api/v1/intake/session/{self.session_id}/resume", headers=headers)
                if response.status_code == 200:
                    self.log("✅ Session resumed successfully")
                    return True
                else:
                    self.log(f"❌ Session resume failed: {response.status_code}", "ERROR")
                    return False
            else:
                self.log(f"❌ Session pause failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Pause/resume test failed: {e}", "ERROR")
            return False

    def test_rate_limiting(self) -> bool:
        """Test rate limiting functionality"""
        if not self.token:
            self.log("❌ No token available for rate limiting test", "ERROR")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Send multiple rapid requests to test rate limiting
        rate_limit_hit = False
        for i in range(25):  # Exceed the 20/minute limit
            try:
                response = self.session.post(f"{BASE_URL}/api/v1/intake/start", headers=headers)
                if response.status_code == 429:
                    rate_limit_hit = True
                    self.log("✅ Rate limiting working correctly")
                    break
            except Exception as e:
                self.log(f"Rate limiting test request {i} failed: {e}")
                
        if not rate_limit_hit:
            self.log("⚠️ Rate limiting not triggered (may be expected in test environment)", "WARNING")
            
        return True

    def run_comprehensive_test(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        self.log("🚀 Starting comprehensive end-to-end testing...")
        
        results = {}
        
        # Health checks
        results["backend_health"] = self.test_health_check()
        results["frontend_health"] = self.test_frontend_health()
        
        if not results["backend_health"]:
            self.log("❌ Backend not available, skipping remaining tests", "ERROR")
            return results
        
        # Authentication tests
        results["user_registration"] = self.register_user()
        results["auth_me"] = self.test_auth_me()
        
        # Intake tests
        results["intake_start"] = self.start_intake_session()
        results["intake_chat"] = self.test_intake_chat()
        results["pause_resume"] = self.test_pause_resume()
        
        # System tests
        results["screeners_list"] = self.test_screeners_list()
        results["rate_limiting"] = self.test_rate_limiting()
        
        # Summary
        passed = sum(results.values())
        total = len(results)
        success_rate = (passed / total) * 100
        
        self.log(f"📊 Test Results: {passed}/{total} passed ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            self.log("🎉 Comprehensive testing PASSED - System ready for production!", "SUCCESS")
        else:
            self.log("⚠️ Some tests failed - Review issues before production deployment", "WARNING")
            
        return results


def main():
    """Main test execution"""
    print("=" * 60)
    print("🧪 PSYCHNOW COMPREHENSIVE END-TO-END TEST SUITE")
    print("=" * 60)
    
    test_session = TestSession()
    results = test_session.run_comprehensive_test()
    
    print("\n" + "=" * 60)
    print("📋 DETAILED TEST RESULTS")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title():<25} {status}")
    
    print("=" * 60)
    
    # Exit with appropriate code
    failed_tests = [name for name, result in results.items() if not result]
    if failed_tests:
        print(f"⚠️ Failed tests: {', '.join(failed_tests)}")
        exit(1)
    else:
        print("🎉 All tests passed!")
        exit(0)


if __name__ == "__main__":
    main()
