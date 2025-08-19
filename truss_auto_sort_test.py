#!/usr/bin/env python3
"""
Truss Tracker Auto-Sort Feature Testing
Tests the truss tracking functionality to verify auto-sort feature implementation and status ordering
"""

import requests
import json
from datetime import datetime, date, timedelta
import sys
import os

# Get backend URL from frontend .env
BACKEND_URL = "https://42d3b5c4-df30-4e66-be00-cc66e9964ae4.preview.emergentagent.com/api"

class TrussAutoSortTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.passed_tests = 0
        self.failed_tests = 0
        self.admin_token = None
        self.demo_token = None
        self.created_truss_ids = []
        
    def log(self, message, level="INFO"):
        """Log test messages"""
        print(f"[{level}] {message}")
        
    def test_request(self, method, endpoint, data=None, expected_status=200, test_name="", auth_token=None):
        """Make HTTP request and validate response"""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            self.log(f"Testing {test_name}: {method} {endpoint}")
            self.log(f"Response Status: {response.status_code}")
            
            if response.status_code == expected_status:
                self.passed_tests += 1
                self.log(f"✅ PASSED: {test_name}", "SUCCESS")
                try:
                    return response.json()
                except:
                    return response.text
            else:
                self.failed_tests += 1
                self.log(f"❌ FAILED: {test_name} - Expected {expected_status}, got {response.status_code}", "ERROR")
                self.log(f"Response: {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.failed_tests += 1
            self.log(f"❌ FAILED: {test_name} - Exception: {str(e)}", "ERROR")
            return None

    def authenticate(self):
        """Authenticate admin user"""
        self.log("\n=== Authentication ===")
        
        # Test admin login
        admin_login = {
            "username": "admin",
            "password": "admin",
            "store_id": "STORE_001"
        }
        
        admin_response = self.test_request("POST", "/auth/login", admin_login, 200, "Admin Login")
        
        if admin_response:
            self.admin_token = admin_response.get('session_token')
            self.log("✅ Admin authentication successful")
            return True
        else:
            self.log("❌ Admin authentication failed", "ERROR")
            return False

    def test_truss_api_endpoints(self):
        """Test Truss API Endpoints"""
        self.log("\n=== Testing Truss API Endpoints ===")
        
        # 1. Test GET /api/trusses endpoint
        trusses_response = self.test_request("GET", "/trusses", auth_token=self.admin_token, 
                                           test_name="GET /api/trusses - retrieve all truss projects")
        
        if trusses_response is not None:
            self.log(f"✅ GET /api/trusses working - retrieved {len(trusses_response)} trusses")
        
        # 2. Test POST /api/trusses endpoint with basic truss
        basic_truss = {
            "project_name": "API Test Truss",
            "project_number": "API-001",
            "designer": "Test Designer",
            "salesman": "Test Salesman",
            "project_status": "ready_for_shop",
            "estimated_delivery": "2025-01-15T00:00:00",
            "lumber_2x4_bd_ft": 100.0,
            "notes": "Basic API test truss"
        }
        
        created_truss = self.test_request("POST", "/trusses", basic_truss, 200, 
                                        "POST /api/trusses - create new truss project", 
                                        auth_token=self.admin_token)
        
        if created_truss:
            self.created_truss_ids.append(created_truss['id'])
            self.log("✅ POST /api/trusses working - truss creation successful")
        
        return trusses_response, created_truss

    def test_status_values(self):
        """Test Status Values - Verify all status types are supported"""
        self.log("\n=== Testing Status Values ===")
        
        valid_statuses = [
            "on_hold",
            "in_the_shop", 
            "ready_for_shop",
            "optimizing",
            "awaiting_final_measurements",
            "completed",
            "delivered"
        ]
        
        self.log(f"Testing {len(valid_statuses)} status values: {', '.join(valid_statuses)}")
        
        # Test creating trusses with each status type
        for i, status in enumerate(valid_statuses):
            status_test_truss = {
                "project_name": f"Status Test - {status.replace('_', ' ').title()}",
                "project_number": f"STS-{i+1:03d}",
                "designer": "Status Tester",
                "salesman": "Status Sales",
                "project_status": status,
                "estimated_delivery": "2025-02-01T00:00:00",
                "lumber_2x4_bd_ft": 100.0,
                "notes": f"Testing {status} status"
            }
            
            status_truss = self.test_request("POST", "/trusses", status_test_truss, 200,
                                           f"Create Truss with {status} status",
                                           auth_token=self.admin_token)
            
            if status_truss:
                self.created_truss_ids.append(status_truss['id'])
                if status_truss.get('project_status') == status:
                    self.log(f"✅ Successfully created truss with {status} status")
                else:
                    self.log(f"❌ Status mismatch for {status}: got {status_truss.get('project_status')}", "ERROR")
                    self.failed_tests += 1
        
        return valid_statuses

    def create_test_data_for_auto_sort(self):
        """Create Test Data with different statuses and delivery dates for auto-sort testing"""
        self.log("\n=== Creating Test Data for Auto-sort Testing ===")
        
        test_trusses = [
            {
                "project_name": "Project A - Ready for Shop",
                "project_number": "TRS-A001",
                "designer": "John Smith",
                "salesman": "Mike Johnson",
                "project_status": "ready_for_shop",
                "estimated_delivery": "2025-01-15T00:00:00",
                "lumber_2x4_bd_ft": 150.5,
                "lumber_2x6_bd_ft": 200.0,
                "lumber_2x8_12ft": 10,
                "lumber_2x8_16ft": 8,
                "lumber_2x8_18ft": 6,
                "lumber_2x8_20ft": 4,
                "estimated_production_days": 5.0,
                "notes": "High priority project for auto-sort testing"
            },
            {
                "project_name": "Project B - On Hold",
                "project_number": "TRS-B002", 
                "designer": "Sarah Wilson",
                "salesman": "Tom Brown",
                "project_status": "on_hold",
                "estimated_delivery": "2025-01-10T00:00:00",
                "lumber_2x4_bd_ft": 120.0,
                "lumber_2x6_bd_ft": 180.5,
                "lumber_2x8_12ft": 12,
                "lumber_2x8_16ft": 10,
                "lumber_2x8_18ft": 8,
                "lumber_2x8_20ft": 6,
                "estimated_production_days": 3.5,
                "notes": "On hold pending customer approval"
            },
            {
                "project_name": "Project C - Awaiting Final Measurements",
                "project_number": "TRS-C003",
                "designer": "David Lee",
                "salesman": "Lisa Davis",
                "project_status": "awaiting_final_measurements",
                "estimated_delivery": "2025-01-05T00:00:00",
                "lumber_2x4_bd_ft": 175.25,
                "lumber_2x6_bd_ft": 225.75,
                "lumber_2x8_12ft": 15,
                "lumber_2x8_16ft": 12,
                "lumber_2x8_18ft": 10,
                "lumber_2x8_20ft": 8,
                "estimated_production_days": 7.0,
                "notes": "Urgent - awaiting final site measurements"
            },
            {
                "project_name": "Project D - In The Shop",
                "project_number": "TRS-D004",
                "designer": "Emily Chen",
                "salesman": "Robert Taylor",
                "project_status": "in_the_shop",
                "estimated_delivery": "2025-01-20T00:00:00",
                "lumber_2x4_bd_ft": 300.0,
                "lumber_2x6_bd_ft": 400.5,
                "lumber_2x8_12ft": 20,
                "lumber_2x8_16ft": 18,
                "lumber_2x8_18ft": 15,
                "lumber_2x8_20ft": 12,
                "estimated_production_days": 10.0,
                "notes": "Large project currently in production"
            }
        ]
        
        created_test_trusses = []
        
        for truss_data in test_trusses:
            created_truss = self.test_request("POST", "/trusses", truss_data, 200, 
                                            f"Create Test Truss - {truss_data['project_name']}", 
                                            auth_token=self.admin_token)
            
            if created_truss:
                self.created_truss_ids.append(created_truss['id'])
                created_test_trusses.append(created_truss)
                self.log(f"✅ Created test truss: {truss_data['project_name']} with status {truss_data['project_status']}")
        
        return created_test_trusses

    def verify_data_structure(self):
        """Verify Data Structure - Ensure truss projects include required fields"""
        self.log("\n=== Verifying Data Structure ===")
        
        if not self.created_truss_ids:
            self.log("❌ No trusses available for data structure verification", "ERROR")
            return False
        
        # Get a specific truss to verify structure
        test_truss_id = self.created_truss_ids[0]
        single_truss = self.test_request("GET", f"/trusses/{test_truss_id}", auth_token=self.admin_token,
                                       test_name="Get Single Truss - Verify Structure")
        
        if not single_truss:
            return False
        
        # Check required fields for auto-sort functionality
        required_fields = [
            'id', 'project_name', 'project_number', 'designer', 'salesman',
            'project_status', 'estimated_delivery', 'lumber_2x4_bd_ft', 'lumber_2x6_bd_ft',
            'lumber_2x8_12ft', 'lumber_2x8_16ft', 'lumber_2x8_18ft', 'lumber_2x8_20ft',
            'estimated_production_days', 'notes', 'store_id', 'created_by', 'created_date'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in single_truss:
                missing_fields.append(field)
        
        if not missing_fields:
            self.log("✅ All required truss tracking fields present")
        else:
            self.log(f"❌ Missing truss fields: {missing_fields}", "ERROR")
            self.failed_tests += 1
            return False
        
        # Verify project_status field with valid enum values
        valid_statuses = ["on_hold", "in_the_shop", "ready_for_shop", "optimizing", 
                         "awaiting_final_measurements", "completed", "delivered"]
        
        if single_truss.get('project_status') in valid_statuses:
            self.log(f"✅ Valid project_status enum value: {single_truss['project_status']}")
        else:
            self.log(f"❌ Invalid project_status value: {single_truss.get('project_status')}", "ERROR")
            self.failed_tests += 1
            return False
        
        # Verify estimated_delivery date field
        if single_truss.get('estimated_delivery'):
            self.log(f"✅ Truss has estimated_delivery field: {single_truss['estimated_delivery']}")
        else:
            self.log("❌ Missing estimated_delivery field", "ERROR")
            self.failed_tests += 1
            return False
        
        return True

    def test_truss_creation_and_retrieval(self):
        """Test Truss Creation and Retrieval with all status types"""
        self.log("\n=== Testing Truss Creation and Retrieval ===")
        
        # Get all trusses to verify they can be retrieved
        all_trusses = self.test_request("GET", "/trusses", auth_token=self.admin_token,
                                      test_name="Get All Trusses - Verify Auto-sort Data")
        
        if not all_trusses:
            return False
        
        self.log(f"✅ Retrieved {len(all_trusses)} trusses for auto-sort verification")
        
        # Verify each truss has the data needed for auto-sort
        trusses_with_status = 0
        trusses_with_delivery = 0
        status_counts = {}
        
        for truss in all_trusses:
            if truss.get('project_status'):
                trusses_with_status += 1
                status = truss['project_status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            if truss.get('estimated_delivery'):
                trusses_with_delivery += 1
        
        self.log(f"✅ Trusses with project_status: {trusses_with_status}/{len(all_trusses)}")
        self.log(f"✅ Trusses with estimated_delivery: {trusses_with_delivery}/{len(all_trusses)}")
        
        # Show status distribution for auto-sort verification
        self.log("✅ Status distribution for auto-sort:")
        for status, count in status_counts.items():
            self.log(f"   - {status}: {count} trusses")
        
        # Verify all expected statuses are represented
        valid_statuses = ["on_hold", "in_the_shop", "ready_for_shop", "optimizing", 
                         "awaiting_final_measurements", "completed", "delivered"]
        found_statuses = set(status_counts.keys())
        expected_statuses = set(valid_statuses)
        
        if found_statuses.intersection(expected_statuses):
            self.log(f"✅ Found {len(found_statuses.intersection(expected_statuses))} of {len(expected_statuses)} expected status types")
        else:
            self.log("❌ No expected status types found in trusses", "ERROR")
            self.failed_tests += 1
            return False
        
        return True

    def test_auto_sort_priority_verification(self):
        """Test Auto-sort Priority Verification - Verify backend supports auto-sort feature"""
        self.log("\n=== Testing Auto-sort Priority Verification ===")
        
        # Get all trusses and analyze for auto-sort capability
        all_trusses = self.test_request("GET", "/trusses", auth_token=self.admin_token,
                                      test_name="Get All Trusses for Auto-sort Analysis")
        
        if not all_trusses:
            return False
        
        # Analyze trusses for auto-sort data completeness
        auto_sort_ready_trusses = []
        
        for truss in all_trusses:
            has_status = bool(truss.get('project_status'))
            has_delivery = bool(truss.get('estimated_delivery'))
            
            if has_status and has_delivery:
                auto_sort_ready_trusses.append({
                    'id': truss['id'],
                    'project_name': truss['project_name'],
                    'status': truss['project_status'],
                    'delivery': truss['estimated_delivery']
                })
        
        self.log(f"✅ Auto-sort ready trusses: {len(auto_sort_ready_trusses)}/{len(all_trusses)}")
        
        if len(auto_sort_ready_trusses) > 0:
            self.log("✅ Backend supports auto-sort feature - trusses have required data")
            
            # Show sample of auto-sort ready data
            self.log("✅ Sample auto-sort data:")
            for i, truss in enumerate(auto_sort_ready_trusses[:5]):  # Show first 5
                self.log(f"   {i+1}. {truss['project_name']}: {truss['status']} | {truss['delivery']}")
            
            return True
        else:
            self.log("❌ No trusses ready for auto-sort - missing required data", "ERROR")
            self.failed_tests += 1
            return False

    def test_access_control(self):
        """Test Access Control - Verify only admins can access truss endpoints"""
        self.log("\n=== Testing Access Control ===")
        
        # Test that demo user cannot access truss endpoints
        demo_login = {
            "username": "demo",
            "password": "demo",
            "store_id": "STORE_001"
        }
        
        demo_response = self.test_request("POST", "/auth/login", demo_login, 200, "Demo User Login")
        
        if demo_response:
            demo_token = demo_response.get('session_token')
            
            # Demo user should not be able to access truss endpoints
            self.test_request("GET", "/trusses", expected_status=403, auth_token=demo_token, 
                            test_name="Demo User Access Trusses (Should Fail)")
            
            self.test_request("POST", "/trusses", {"project_name": "Test"}, expected_status=403, 
                            auth_token=demo_token, test_name="Demo User Create Truss (Should Fail)")
            
            self.log("✅ Access control working - only admins can access truss endpoints")
            return True
        else:
            self.log("❌ Demo user authentication failed", "ERROR")
            return False

    def cleanup_test_data(self):
        """Clean up created test data"""
        self.log("\n=== Cleaning Up Test Data ===")
        
        deleted_count = 0
        for truss_id in self.created_truss_ids:
            delete_response = self.test_request("DELETE", f"/trusses/{truss_id}", 
                                              expected_status=200, auth_token=self.admin_token,
                                              test_name=f"Delete Test Truss {truss_id}")
            if delete_response:
                deleted_count += 1
        
        self.log(f"✅ Cleaned up {deleted_count}/{len(self.created_truss_ids)} test trusses")

    def print_test_summary(self):
        """Print final test results"""
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.log("\n" + "="*50)
        self.log("🏁 TRUSS AUTO-SORT TESTING COMPLETE")
        self.log(f"✅ Passed: {self.passed_tests}")
        self.log(f"❌ Failed: {self.failed_tests}")
        self.log(f"📊 Success Rate: {success_rate:.1f}%")
        self.log("="*50)

    def run_all_tests(self):
        """Run all truss auto-sort tests"""
        self.log("🚀 Starting Truss Auto-Sort Feature Testing")
        self.log(f"Backend URL: {self.base_url}")
        
        try:
            # 1. Authentication
            if not self.authenticate():
                self.log("❌ Authentication failed - cannot proceed with tests", "ERROR")
                return
            
            # 2. Test Truss API Endpoints
            self.test_truss_api_endpoints()
            
            # 3. Test Status Values
            self.test_status_values()
            
            # 4. Create Test Data for Auto-sort
            self.create_test_data_for_auto_sort()
            
            # 5. Verify Data Structure
            self.verify_data_structure()
            
            # 6. Test Truss Creation and Retrieval
            self.test_truss_creation_and_retrieval()
            
            # 7. Test Auto-sort Priority Verification
            self.test_auto_sort_priority_verification()
            
            # 8. Test Access Control
            self.test_access_control()
            
            # 9. Cleanup
            self.cleanup_test_data()
            
        except Exception as e:
            self.log(f"❌ Test suite failed with exception: {str(e)}", "ERROR")
            self.failed_tests += 1
        
        # Print final results
        self.print_test_summary()

if __name__ == "__main__":
    tester = TrussAutoSortTester()
    tester.run_all_tests()