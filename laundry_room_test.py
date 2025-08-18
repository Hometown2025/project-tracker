#!/usr/bin/env python3
"""
Comprehensive Testing for Updated Laundry Room Subtask Generation Feature
Tests the specific requirements from the review request:
- Verify 9 total subtasks (was 5, now 9 with 4 additions)
- Verify 4 new subtasks: Wall Coverings, Cabinets, Cabinet Hardware, Lighting
- Verify 5 existing subtasks preserved: Plumbing, Electrical Work, Flooring, Appliances, Ventilation
- Test laundry room detection with various titles
- Test specific scenarios: Laundry Room Renovation, Utility Room Upgrade, Laundry Area Remodel
"""

import requests
import json
from datetime import datetime
import sys

# Get backend URL from frontend .env
BACKEND_URL = "https://buildbuddy-2.preview.emergentagent.com/api"

class LaundryRoomSubtaskTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.passed_tests = 0
        self.failed_tests = 0
        self.admin_token = None
        self.test_project_id = None
        
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

    def authenticate_admin(self):
        """Authenticate as admin user"""
        self.log("\n=== Authenticating as Admin ===")
        
        admin_login = {
            "username": "admin",
            "password": "admin",
            "store_id": "STORE_001"
        }
        
        response = self.test_request("POST", "/auth/login", admin_login, 200, "Admin Authentication")
        
        if response:
            self.admin_token = response.get('session_token')
            self.log("✅ Admin authentication successful")
            return True
        else:
            self.log("❌ Admin authentication failed", "ERROR")
            return False

    def create_test_project(self):
        """Create a test project for laundry room tasks"""
        self.log("\n=== Creating Test Project ===")
        
        project_data = {
            "name": "Laundry Room Renovation Test Project",
            "description": "Test project for laundry room subtask generation",
            "color": "#4CAF50"
        }
        
        response = self.test_request("POST", "/projects", project_data, 200, 
                                   "Create Test Project", auth_token=self.admin_token)
        
        if response:
            self.test_project_id = response['id']
            self.log(f"✅ Test project created: {self.test_project_id}")
            return True
        else:
            self.log("❌ Failed to create test project", "ERROR")
            return False

    def create_laundry_room_task(self, title):
        """Create a laundry room task with given title"""
        task_data = {
            "project_id": self.test_project_id,
            "title": title,
            "description": f"Test laundry room task: {title}",
            "priority": "medium"
        }
        
        response = self.test_request("POST", "/tasks", task_data, 200, 
                                   f"Create Laundry Room Task: {title}", auth_token=self.admin_token)
        
        if response:
            return response['id']
        else:
            return None

    def test_laundry_room_subtask_generation(self, task_title, task_id):
        """Test subtask generation for a laundry room task"""
        self.log(f"\n=== Testing Subtask Generation for: {task_title} ===")
        
        # Generate subtasks
        response = self.test_request("POST", f"/tasks/{task_id}/generate-subtasks", {}, 200,
                                   f"Generate Subtasks for {task_title}", auth_token=self.admin_token)
        
        if not response:
            return False
        
        # Verify response contains expected information
        if 'created_subtasks' in response:
            created_count = len(response['created_subtasks'])
            room_type = response.get('room_type', 'unknown')
            
            self.log(f"✅ Room type detected: {room_type}")
            self.log(f"✅ Created {created_count} subtasks")
            
            # Verify correct count (should be 9 for laundry room)
            if created_count == 9:
                self.log("✅ CORRECT: Generated 9 subtasks for laundry room (was 5, now 9)")
            else:
                self.log(f"❌ INCORRECT: Expected 9 subtasks, got {created_count}", "ERROR")
                self.failed_tests += 1
                return False
        
        # Get the actual subtasks to verify content
        subtasks_response = self.test_request("GET", f"/tasks?parent_task_id={task_id}", {}, 200,
                                            f"Get Generated Subtasks for {task_title}", auth_token=self.admin_token)
        
        if not subtasks_response:
            return False
        
        # Verify subtask count matches
        if len(subtasks_response) != 9:
            self.log(f"❌ INCORRECT: Expected 9 subtasks in database, got {len(subtasks_response)}", "ERROR")
            self.failed_tests += 1
            return False
        
        # Extract subtask titles and descriptions
        subtask_data = {}
        for subtask in subtasks_response:
            title = subtask['title']
            description = subtask['description']
            subtask_data[title] = description
            self.log(f"  - {title}: {description}")
        
        # Verify the 4 NEW subtasks are present
        new_subtasks = {
            "Wall Coverings": "Install wall coverings, paint, or tile backsplash",
            "Cabinets": "Install laundry room cabinets and storage solutions",
            "Cabinet Hardware": "Install cabinet handles, knobs, and drawer slides",
            "Lighting": "Install overhead lighting and task lighting fixtures"
        }
        
        self.log("\n--- Verifying 4 NEW Subtasks ---")
        for title, expected_desc in new_subtasks.items():
            if title in subtask_data:
                actual_desc = subtask_data[title]
                if actual_desc == expected_desc:
                    self.log(f"✅ NEW SUBTASK VERIFIED: {title} - {actual_desc}")
                else:
                    self.log(f"❌ NEW SUBTASK DESCRIPTION MISMATCH: {title}", "ERROR")
                    self.log(f"   Expected: {expected_desc}", "ERROR")
                    self.log(f"   Actual: {actual_desc}", "ERROR")
                    self.failed_tests += 1
            else:
                self.log(f"❌ NEW SUBTASK MISSING: {title}", "ERROR")
                self.failed_tests += 1
        
        # Verify the 5 EXISTING subtasks are preserved
        existing_subtasks = {
            "Plumbing": "Install washer/dryer connections and utility sink",
            "Electrical Work": "Install electrical outlets and lighting",
            "Flooring": "Install laundry room flooring",
            "Appliances": "Install washer, dryer, and connections",
            "Ventilation": "Install proper ventilation for dryer"
        }
        
        self.log("\n--- Verifying 5 EXISTING Subtasks Preserved ---")
        for title, expected_desc in existing_subtasks.items():
            if title in subtask_data:
                actual_desc = subtask_data[title]
                if actual_desc == expected_desc:
                    self.log(f"✅ EXISTING SUBTASK PRESERVED: {title} - {actual_desc}")
                else:
                    self.log(f"❌ EXISTING SUBTASK DESCRIPTION CHANGED: {title}", "ERROR")
                    self.log(f"   Expected: {expected_desc}", "ERROR")
                    self.log(f"   Actual: {actual_desc}", "ERROR")
                    self.failed_tests += 1
            else:
                self.log(f"❌ EXISTING SUBTASK MISSING: {title}", "ERROR")
                self.failed_tests += 1
        
        # Verify all subtasks have required fields
        self.log("\n--- Verifying Subtask Structure ---")
        required_fields = ['id', 'title', 'description', 'estimated_budget', 'actual_cost', 
                          'order_date', 'delivery_date', 'store_id', 'project_id', 'parent_task_id']
        
        for subtask in subtasks_response:
            for field in required_fields:
                if field not in subtask:
                    self.log(f"❌ SUBTASK MISSING FIELD: {subtask['title']} missing {field}", "ERROR")
                    self.failed_tests += 1
        
        self.log("✅ All subtask structure verification completed")
        return True

    def test_laundry_room_detection(self):
        """Test laundry room detection with various title variations"""
        self.log("\n=== Testing Laundry Room Detection Variations ===")
        
        test_cases = [
            "Laundry Room Renovation",
            "Utility Room Upgrade", 
            "Laundry Area Remodel",
            "laundry room",
            "LAUNDRY ROOM",
            "Laundry",
            "Main Laundry Room",
            "Basement Laundry Area",
            "Upstairs Utility Room",
            "Wash Room"
        ]
        
        for title in test_cases:
            self.log(f"\n--- Testing Detection: {title} ---")
            
            # Create task
            task_id = self.create_laundry_room_task(title)
            if not task_id:
                continue
            
            # Test subtask generation
            success = self.test_laundry_room_subtask_generation(title, task_id)
            
            if success:
                self.log(f"✅ DETECTION SUCCESS: '{title}' correctly detected as laundry room")
            else:
                self.log(f"❌ DETECTION FAILED: '{title}' not properly handled", "ERROR")

    def test_duplicate_prevention(self):
        """Test that duplicate subtask generation is prevented"""
        self.log("\n=== Testing Duplicate Prevention ===")
        
        # Create a laundry room task
        task_id = self.create_laundry_room_task("Duplicate Test Laundry Room")
        if not task_id:
            return
        
        # Generate subtasks first time
        response1 = self.test_request("POST", f"/tasks/{task_id}/generate-subtasks", {}, 200,
                                    "First Subtask Generation", auth_token=self.admin_token)
        
        if response1:
            self.log("✅ First subtask generation successful")
            
            # Try to generate subtasks again (should be prevented)
            response2 = self.test_request("POST", f"/tasks/{task_id}/generate-subtasks", {}, 200,
                                        "Second Subtask Generation (Should Be Prevented)", auth_token=self.admin_token)
            
            if response2 and 'message' in response2:
                if 'already has' in response2['message']:
                    self.log("✅ Duplicate prevention working correctly")
                else:
                    self.log(f"❌ Unexpected response for duplicate generation: {response2['message']}", "ERROR")
                    self.failed_tests += 1
            else:
                self.log("❌ Duplicate prevention not working", "ERROR")
                self.failed_tests += 1

    def test_non_laundry_room_tasks(self):
        """Test that non-laundry room tasks don't generate laundry subtasks"""
        self.log("\n=== Testing Non-Laundry Room Tasks ===")
        
        non_laundry_tasks = [
            "Kitchen Renovation",
            "Bathroom Remodel", 
            "Living Room Update",
            "Office Space",
            "Random Room"
        ]
        
        for title in non_laundry_tasks:
            task_id = self.create_laundry_room_task(title)  # Using same function but different title
            if not task_id:
                continue
            
            response = self.test_request("POST", f"/tasks/{task_id}/generate-subtasks", {}, 200,
                                       f"Generate Subtasks for {title}", auth_token=self.admin_token)
            
            if response:
                if 'room_type' in response:
                    room_type = response['room_type']
                    if room_type != 'laundry room':
                        self.log(f"✅ {title} correctly detected as {room_type} (not laundry room)")
                    else:
                        self.log(f"❌ {title} incorrectly detected as laundry room", "ERROR")
                        self.failed_tests += 1
                elif 'error' in response or 'Could not detect' in str(response):
                    self.log(f"✅ {title} correctly rejected (unrecognized room type)")
                else:
                    self.log(f"⚠️ Unexpected response for {title}: {response}")

    def run_all_tests(self):
        """Run all laundry room subtask generation tests"""
        self.log("🧪 STARTING COMPREHENSIVE LAUNDRY ROOM SUBTASK GENERATION TESTING")
        self.log("=" * 80)
        
        # Authenticate
        if not self.authenticate_admin():
            return False
        
        # Create test project
        if not self.create_test_project():
            return False
        
        # Run all test suites
        self.test_laundry_room_detection()
        self.test_duplicate_prevention()
        self.test_non_laundry_room_tasks()
        
        # Print final results
        self.log("\n" + "=" * 80)
        self.log("🏁 LAUNDRY ROOM SUBTASK GENERATION TESTING COMPLETE")
        self.log(f"✅ PASSED: {self.passed_tests}")
        self.log(f"❌ FAILED: {self.failed_tests}")
        
        total_tests = self.passed_tests + self.failed_tests
        if total_tests > 0:
            success_rate = (self.passed_tests / total_tests) * 100
            self.log(f"📊 SUCCESS RATE: {success_rate:.1f}% ({self.passed_tests}/{total_tests})")
        
        return self.failed_tests == 0

if __name__ == "__main__":
    tester = LaundryRoomSubtaskTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)