#!/usr/bin/env python3
"""
Focused test for bathroom subtask generation feature
"""

import requests
import json
from datetime import datetime, date, timedelta
import sys
import os

# Get backend URL from frontend .env
BACKEND_URL = "https://buildbuddy-2.preview.emergentagent.com/api"

class BathroomSubtaskTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.passed_tests = 0
        self.failed_tests = 0
        self.admin_token = None
        
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
        """Authenticate as admin user"""
        admin_login = {
            "username": "admin",
            "password": "admin",
            "store_id": "STORE_001"
        }
        
        admin_response = self.test_request("POST", "/auth/login", admin_login, 200, "Admin Authentication")
        
        if admin_response:
            self.admin_token = admin_response.get('session_token')
            self.log("✅ Admin authentication successful")
            return True
        else:
            self.log("❌ Admin authentication failed", "ERROR")
            return False

    def test_bathroom_subtask_generation(self):
        """Test Updated Bathroom Subtask Generation Feature"""
        self.log("\n=== Testing Updated Bathroom Subtask Generation Feature ===")
        
        if not self.admin_token:
            self.log("❌ No admin token available for bathroom subtask testing", "ERROR")
            return
        
        # Create a test project for bathroom tasks
        bathroom_project = {
            "name": "Bathroom Renovation Project",
            "description": "Testing bathroom subtask generation",
            "color": "#4CAF50"
        }
        
        created_project = self.test_request("POST", "/projects", bathroom_project, 200, 
                                          "Create Bathroom Project", auth_token=self.admin_token)
        
        if not created_project:
            self.log("❌ Failed to create test project for bathroom testing", "ERROR")
            return
        
        project_id = created_project['id']
        self.log(f"✅ Created test project: {project_id}")
        
        # Test scenarios with different bathroom titles
        bathroom_test_scenarios = [
            {
                "title": "Guest Bathroom Renovation",
                "description": "Complete renovation of guest bathroom",
                "expected_room_type": "bathroom"
            },
            {
                "title": "Master Bath Remodel", 
                "description": "Remodel master bathroom with modern fixtures",
                "expected_room_type": "bathroom"
            },
            {
                "title": "Powder Room Update",
                "description": "Update powder room with new vanity and fixtures",
                "expected_room_type": "bathroom"
            }
        ]
        
        # Expected bathroom subtasks (11 total as per requirement)
        expected_bathroom_subtasks = [
            {"title": "Plumbing", "description": "Install toilet, sink, shower/tub plumbing"},
            {"title": "Electrical Work", "description": "Install electrical outlets and ventilation fan"},
            {"title": "Tile Work", "description": "Install wall and floor tiles"},
            {"title": "Fixtures", "description": "Install toilet, sink, shower/tub fixtures"},
            {"title": "Cabinets", "description": "Install bathroom cabinets and mirror"},  # Changed from "Vanity"
            {"title": "Lighting", "description": "Install bathroom lighting fixtures and switches"},  # NEW
            {"title": "Cabinet Hardware", "description": "Install cabinet handles, knobs, and drawer slides"},  # NEW
            {"title": "Shower/Tub", "description": "Install shower doors, tub surrounds, and accessories"},  # NEW
            {"title": "Countertop", "description": "Install bathroom countertops and vanity tops"},  # NEW
            {"title": "Flooring", "description": "Install bathroom flooring"},
            {"title": "Painting", "description": "Paint walls and trim"}
        ]
        
        for scenario in bathroom_test_scenarios:
            self.log(f"\n--- Testing Scenario: {scenario['title']} ---")
            
            # Create bathroom task/room
            bathroom_task = {
                "project_id": project_id,
                "title": scenario['title'],
                "description": scenario['description'],
                "priority": "high"
            }
            
            created_task = self.test_request("POST", "/tasks", bathroom_task, 200, 
                                           f"Create Bathroom Task - {scenario['title']}", 
                                           auth_token=self.admin_token)
            
            if not created_task:
                self.log(f"❌ Failed to create bathroom task: {scenario['title']}", "ERROR")
                continue
            
            task_id = created_task['id']
            self.log(f"✅ Created bathroom task: {task_id}")
            
            # Test bathroom room detection and subtask generation
            subtask_response = self.test_request("POST", f"/tasks/{task_id}/generate-subtasks", 
                                               None, 200, 
                                               f"Generate Subtasks for {scenario['title']}", 
                                               auth_token=self.admin_token)
            
            if subtask_response:
                # Verify room type detection
                detected_room_type = subtask_response.get('room_type')
                if detected_room_type == scenario['expected_room_type']:
                    self.log(f"✅ Room type correctly detected as: {detected_room_type}")
                else:
                    self.log(f"❌ Room type detection failed: expected {scenario['expected_room_type']}, got {detected_room_type}", "ERROR")
                    self.failed_tests += 1
                
                # Verify subtask count (should be 11 for bathroom)
                message = subtask_response.get('message', '')
                if 'generated 11 standard subtasks' in message:
                    self.log(f"✅ Correct number of subtasks created: 11")
                else:
                    self.log(f"❌ Incorrect subtask count in message: {message}", "ERROR")
                    self.failed_tests += 1
                
                # Get the actual created subtasks to verify content
                created_subtasks_list = self.test_request("GET", f"/tasks?parent_task_id={task_id}", 
                                                        auth_token=self.admin_token,
                                                        test_name=f"Get Generated Subtasks for {scenario['title']}")
                
                if created_subtasks_list:
                    self.log(f"✅ Retrieved {len(created_subtasks_list)} generated subtasks")
                    
                    # Verify all expected subtasks are present
                    created_titles = [subtask['title'] for subtask in created_subtasks_list]
                    expected_titles = [subtask['title'] for subtask in expected_bathroom_subtasks]
                    
                    # Check for "Vanity" -> "Cabinets" change
                    if "Vanity" in created_titles:
                        self.log("❌ Found old 'Vanity' subtask - should be changed to 'Cabinets'", "ERROR")
                        self.failed_tests += 1
                    elif "Cabinets" in created_titles:
                        self.log("✅ Confirmed 'Vanity' has been changed to 'Cabinets'")
                    
                    # Check for new subtasks
                    new_subtasks = ["Lighting", "Cabinet Hardware", "Shower/Tub", "Countertop"]
                    for new_subtask in new_subtasks:
                        if new_subtask in created_titles:
                            self.log(f"✅ New subtask '{new_subtask}' found")
                        else:
                            self.log(f"❌ New subtask '{new_subtask}' missing", "ERROR")
                            self.failed_tests += 1
                    
                    # Check for existing subtasks
                    existing_subtasks = ["Plumbing", "Electrical Work", "Tile Work", "Fixtures", "Flooring", "Painting"]
                    for existing_subtask in existing_subtasks:
                        if existing_subtask in created_titles:
                            self.log(f"✅ Existing subtask '{existing_subtask}' preserved")
                        else:
                            self.log(f"❌ Existing subtask '{existing_subtask}' missing", "ERROR")
                            self.failed_tests += 1
                    
                    # Verify subtask descriptions
                    for created_subtask in created_subtasks_list:
                        created_title = created_subtask['title']
                        created_description = created_subtask['description']
                        
                        # Find expected subtask with matching title
                        expected_subtask = next((s for s in expected_bathroom_subtasks if s['title'] == created_title), None)
                        
                        if expected_subtask:
                            if created_description == expected_subtask['description']:
                                self.log(f"✅ Subtask '{created_title}' has correct description")
                            else:
                                self.log(f"❌ Subtask '{created_title}' has incorrect description", "ERROR")
                                self.log(f"   Expected: {expected_subtask['description']}", "ERROR")
                                self.log(f"   Got: {created_description}", "ERROR")
                                self.failed_tests += 1
                        else:
                            self.log(f"❌ Unexpected subtask found: {created_title}", "ERROR")
                            self.failed_tests += 1
                    
                    # Verify all subtasks have required fields
                    for subtask in created_subtasks_list:
                        required_fields = ['id', 'title', 'description', 'estimated_budget', 'actual_cost', 
                                         'order_date', 'delivery_date', 'store_id', 'project_id', 'parent_task_id']
                        
                        missing_fields = []
                        for field in required_fields:
                            if field not in subtask:
                                missing_fields.append(field)
                        
                        if not missing_fields:
                            self.log(f"✅ Subtask '{subtask['title']}' has all required fields")
                        else:
                            self.log(f"❌ Subtask '{subtask['title']}' missing fields: {missing_fields}", "ERROR")
                            self.failed_tests += 1
                
                # Test duplicate prevention
                duplicate_response = self.test_request("POST", f"/tasks/{task_id}/generate-subtasks", 
                                                     None, 200, 
                                                     f"Test Duplicate Prevention for {scenario['title']}", 
                                                     auth_token=self.admin_token)
                
                if duplicate_response:
                    message = duplicate_response.get('message', '')
                    if 'already has' in message and 'subtasks' in message:
                        self.log("✅ Duplicate subtask generation properly prevented")
                    else:
                        self.log(f"❌ Duplicate prevention message unexpected: {message}", "ERROR")
                        self.failed_tests += 1
        
        # Test room type detection variations
        self.log("\n--- Testing Room Type Detection Variations ---")
        
        detection_test_cases = [
            {"title": "bathroom", "should_detect": True},
            {"title": "Bathroom", "should_detect": True},
            {"title": "BATHROOM", "should_detect": True},
            {"title": "bath", "should_detect": True},
            {"title": "Bath", "should_detect": True},
            {"title": "powder", "should_detect": True},
            {"title": "Powder", "should_detect": True},
            {"title": "Master Bathroom Suite", "should_detect": True},
            {"title": "Guest Bath Area", "should_detect": True},
            {"title": "Half Bath", "should_detect": True},
            {"title": "Powder Room Renovation", "should_detect": True},
            {"title": "Kitchen", "should_detect": False},
            {"title": "Living Room", "should_detect": False},
            {"title": "Office", "should_detect": False}
        ]
        
        for test_case in detection_test_cases:
            test_task = {
                "project_id": project_id,
                "title": test_case['title'],
                "description": f"Testing detection for {test_case['title']}",
                "priority": "medium"
            }
            
            created_task = self.test_request("POST", "/tasks", test_task, 200, 
                                           f"Create Detection Test Task - {test_case['title']}", 
                                           auth_token=self.admin_token)
            
            if created_task:
                task_id = created_task['id']
                
                if test_case['should_detect']:
                    # Should successfully generate bathroom subtasks
                    subtask_response = self.test_request("POST", f"/tasks/{task_id}/generate-subtasks", 
                                                       None, 200, 
                                                       f"Generate Subtasks for Detection Test - {test_case['title']}", 
                                                       auth_token=self.admin_token)
                    
                    if subtask_response and subtask_response.get('room_type') == 'bathroom':
                        self.log(f"✅ '{test_case['title']}' correctly detected as bathroom")
                    else:
                        self.log(f"❌ '{test_case['title']}' failed bathroom detection", "ERROR")
                        self.failed_tests += 1
                else:
                    # Should fail to detect as bathroom
                    subtask_response = self.test_request("POST", f"/tasks/{task_id}/generate-subtasks", 
                                                       None, 400, 
                                                       f"Generate Subtasks for Non-Bathroom - {test_case['title']}", 
                                                       auth_token=self.admin_token)
                    
                    if subtask_response:
                        self.log(f"✅ '{test_case['title']}' correctly rejected as non-bathroom")
                    else:
                        self.log(f"❌ '{test_case['title']}' incorrectly detected as bathroom", "ERROR")
                        self.failed_tests += 1
        
        self.log("\n=== Bathroom Subtask Generation Testing Complete ===")

    def run_test(self):
        """Run the bathroom subtask generation test"""
        self.log("🚀 Starting Bathroom Subtask Generation Testing")
        self.log(f"Backend URL: {self.base_url}")
        
        try:
            # Authenticate first
            if not self.authenticate():
                return False
            
            # Run the bathroom test
            self.test_bathroom_subtask_generation()
            
        except Exception as e:
            self.log(f"❌ Test failed with exception: {str(e)}", "ERROR")
            self.failed_tests += 1
        
        # Print final results
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.log(f"\n{'='*50}")
        self.log(f"🏁 BATHROOM SUBTASK TEST RESULTS")
        self.log(f"{'='*50}")
        self.log(f"✅ Passed: {self.passed_tests}")
        self.log(f"❌ Failed: {self.failed_tests}")
        self.log(f"📊 Success Rate: {success_rate:.1f}%")
        self.log(f"{'='*50}")
        
        return success_rate > 80

if __name__ == "__main__":
    tester = BathroomSubtaskTester()
    success = tester.run_test()
    sys.exit(0 if success else 1)