"""
Integration Test Suite for Full PsychNow System
Tests all new features: WebSocket, notifications, assignments, provider workflows
"""

import asyncio
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Any

# Test Configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_EMAIL = "integration_test@psychnow.com"
TEST_PASSWORD = "testpassword123"
ADMIN_EMAIL = "admin@psychnow.com"
ADMIN_PASSWORD = "admin123"

class IntegrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.provider_token = None
        self.patient_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def authenticate_admin(self) -> bool:
        """Test admin authentication"""
        try:
            response = self.session.post(f"{BASE_URL}/api/v1/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                self.log_test("Admin Authentication", True, f"Token received: {self.admin_token[:20]}...")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Authentication", False, str(e))
            return False
    
    def test_websocket_stats(self) -> bool:
        """Test WebSocket statistics endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/api/v1/ws/stats")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("WebSocket Stats", True, f"Connections: {data.get('data', {}).get('total_connections', 0)}")
                return True
            else:
                self.log_test("WebSocket Stats", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("WebSocket Stats", False, str(e))
            return False
    
    def test_system_stats(self) -> bool:
        """Test admin system statistics"""
        try:
            response = self.session.get(f"{BASE_URL}/api/v1/admin/system-stats")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("System Stats", True, f"Reports: {data.get('total_reports', 0)}")
                return True
            else:
                self.log_test("System Stats", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("System Stats", False, str(e))
            return False
    
    def test_assignment_stats(self) -> bool:
        """Test assignment statistics"""
        try:
            response = self.session.get(f"{BASE_URL}/api/v1/admin/assignment-stats")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Assignment Stats", True, f"Assignment Rate: {data.get('assignment_rate', 0)}%")
                return True
            else:
                self.log_test("Assignment Stats", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Assignment Stats", False, str(e))
            return False
    
    def test_unassigned_reports(self) -> bool:
        """Test unassigned reports endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/api/v1/admin/unassigned-reports")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Unassigned Reports", True, f"Count: {len(data)}")
                return True
            else:
                self.log_test("Unassigned Reports", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Unassigned Reports", False, str(e))
            return False
    
    def test_notification_endpoints(self) -> bool:
        """Test notification endpoints"""
        try:
            # Test admin notifications
            response = self.session.get(f"{BASE_URL}/api/v1/admin/notifications")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Admin Notifications", True, f"Count: {len(data)}")
            else:
                self.log_test("Admin Notifications", False, f"Status: {response.status_code}")
                return False
                
            return True
        except Exception as e:
            self.log_test("Notification Endpoints", False, str(e))
            return False
    
    def test_provider_endpoints(self) -> bool:
        """Test provider endpoints (requires provider token)"""
        # First create a test provider
        try:
            # Create provider user
            provider_data = {
                "email": "test_provider@psychnow.com",
                "password": "provider123",
                "first_name": "Test",
                "last_name": "Provider",
                "role": "provider"
            }
            
            response = self.session.post(f"{BASE_URL}/api/v1/auth/register", json=provider_data)
            
            if response.status_code == 201:
                # Login as provider
                login_response = self.session.post(f"{BASE_URL}/api/v1/auth/login", json={
                    "email": provider_data["email"],
                    "password": provider_data["password"]
                })
                
                if login_response.status_code == 200:
                    provider_token = login_response.json()["access_token"]
                    provider_session = requests.Session()
                    provider_session.headers.update({"Authorization": f"Bearer {provider_token}"})
                    
                    # Test provider dashboard stats
                    stats_response = provider_session.get(f"{BASE_URL}/api/v1/provider/dashboard-stats")
                    if stats_response.status_code == 200:
                        self.log_test("Provider Dashboard Stats", True, "Endpoint accessible")
                    else:
                        self.log_test("Provider Dashboard Stats", False, f"Status: {stats_response.status_code}")
                        return False
                    
                    # Test provider notifications
                    notif_response = provider_session.get(f"{BASE_URL}/api/v1/provider/notifications")
                    if notif_response.status_code == 200:
                        self.log_test("Provider Notifications", True, "Endpoint accessible")
                    else:
                        self.log_test("Provider Notifications", False, f"Status: {notif_response.status_code}")
                        return False
                    
                    # Test provider workload
                    workload_response = provider_session.get(f"{BASE_URL}/api/v1/provider/workload")
                    if workload_response.status_code == 200:
                        self.log_test("Provider Workload", True, "Endpoint accessible")
                    else:
                        self.log_test("Provider Workload", False, f"Status: {workload_response.status_code}")
                        return False
                    
                    return True
                else:
                    self.log_test("Provider Login", False, f"Status: {login_response.status_code}")
                    return False
            else:
                self.log_test("Provider Registration", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Provider Endpoints", False, str(e))
            return False
    
    def test_pending_providers(self) -> bool:
        """Test pending providers endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/api/v1/admin/providers/pending")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Pending Providers", True, f"Count: {data.get('count', 0)}")
                return True
            else:
                self.log_test("Pending Providers", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Pending Providers", False, str(e))
            return False
    
    def test_session_cleanup(self) -> bool:
        """Test session cleanup endpoint"""
        try:
            response = self.session.post(f"{BASE_URL}/api/v1/intake/cleanup")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Session Cleanup", True, f"Cleaned: {data.get('expired_sessions_cleaned', 0)}")
                return True
            else:
                self.log_test("Session Cleanup", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Session Cleanup", False, str(e))
            return False
    
    def test_session_stats(self) -> bool:
        """Test session statistics endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/api/v1/intake/stats")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Session Stats", True, "Statistics retrieved")
                return True
            else:
                self.log_test("Session Stats", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Session Stats", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run complete integration test suite"""
        print("🚀 Starting PsychNow Integration Tests")
        print("=" * 50)
        
        # Authentication
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return
        
        # Core System Tests
        self.test_websocket_stats()
        self.test_system_stats()
        self.test_assignment_stats()
        self.test_unassigned_reports()
        self.test_notification_endpoints()
        self.test_provider_endpoints()
        self.test_pending_providers()
        self.test_session_cleanup()
        self.test_session_stats()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n🎯 INTEGRATION TEST COMPLETE")
        
        return passed_tests == total_tests

def main():
    """Main test runner"""
    tester = IntegrationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! System is ready for deployment.")
        exit(0)
    else:
        print("\n⚠️  SOME TESTS FAILED! Please review and fix issues.")
        exit(1)

if __name__ == "__main__":
    main()
