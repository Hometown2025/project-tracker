#!/usr/bin/env python3
"""
Focused Test for Updated Room Subtask Configurations (Kitchen, Bedroom, Living Room)
"""

import requests
import json
from datetime import datetime

# Get backend URL from frontend .env
BACKEND_URL = "https://buildbuddy-2.preview.emergentagent.com/api"

class UpdatedRoomSubtaskTester:
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
        self.log("\n=== Authentication ===")
        
        # Test Store 1 Login: admin/admin with STORE_001
        store1_login = {
            "username": "admin",
            "password": "admin",
            "store_id": "STORE_001"
        }
        
        response = self.test_request("POST", "/auth/login", store1_login, 200, 
                                   "Store 1 Admin Login (admin/admin/STORE_001)")
        
        if response:
            self.admin_token = response.get('session_token')
            self.log(f"✅ Admin authentication successful")
            return True
        else:
            self.log("❌ Admin authentication failed", "ERROR")
            return False

    def test_updated_room_subtask_configurations(self):
        """Test Updated Kitchen, Bedroom, and Living Room Subtask Configurations"""
        self.log("\n=== Testing Updated Room Subtask Configurations (Kitchen, Bedroom, Living Room) ===")
        
        if not self.admin_token:
            self.log("❌ No admin token available for room subtask testing", "ERROR")
            return
        
        # Create a test project for room tasks
        room_project = {
            "name": "Updated Room Subtask Testing Project",
            "description": "Testing updated subtask configurations for Kitchen, Bedroom, and Living Room",
            "color": "#FF9800"
        }
        
        created_project = self.test_request("POST", "/projects", room_project, 200, 
                                          "Create Room Testing Project", auth_token=self.admin_token)
        
        if not created_project:
            self.log("❌ Failed to create test project for room testing", "ERROR")
            return
        
        project_id = created_project['id']
        self.log(f"✅ Created test project: {project_id}")
        
        # Define expected subtasks for each room type
        expected_room_subtasks = {
            "kitchen": {
                "count": 9,
                "subtasks": [
                    {"title": "Wall Coverings", "description": "Install wall coverings, paint, or wallpaper"},
                    {"title": "Flooring", "description": "Install kitchen flooring"},
                    {"title": "Lighting", "description": "Install kitchen lighting and electrical fixtures"},
                    {"title": "Cabinets", "description": "Install kitchen cabinets and storage solutions"},
                    {"title": "Cabinet Hardware", "description": "Install cabinet handles, knobs, and drawer slides"},
                    {"title": "Sink", "description": "Install kitchen sink and disposal"},
                    {"title": "Faucet", "description": "Install kitchen faucet and water connections"},
                    {"title": "Countertop", "description": "Install kitchen countertops"},
                    {"title": "Backsplash", "description": "Install kitchen backsplash and tile work"}
                ]
            },
            "bedroom": {
                "count": 3,
                "subtasks": [
                    {"title": "Wall Coverings", "description": "Install wall coverings, paint, or wallpaper"},
                    {"title": "Flooring", "description": "Install bedroom flooring"},
                    {"title": "Lighting", "description": "Install bedroom lighting and electrical fixtures"}
                ]
            },
            "living room": {
                "count": 4,
                "subtasks": [
                    {"title": "Wall Coverings", "description": "Install wall coverings, paint, or wallpaper"},
                    {"title": "Flooring", "description": "Install living room flooring"},
                    {"title": "Lighting", "description": "Install living room lighting and electrical fixtures"},
                    {"title": "Fire Place", "description": "Install or renovate fireplace and surround"}
                ]
            }
        }
        
        # Test scenarios for each room type with various title variations
        room_test_scenarios = {
            "kitchen": [
                {"title": "Kitchen Remodel", "description": "Complete kitchen renovation"},
                {"title": "Main Kitchen", "description": "Main kitchen upgrade"},
                {"title": "Galley Kitchen", "description": "Galley kitchen renovation"}
            ],
            "bedroom": [
                {"title": "Master Bedroom", "description": "Master bedroom renovation"},
                {"title": "Guest Bedroom", "description": "Guest bedroom update"},
                {"title": "Kids Bedroom", "description": "Children's bedroom makeover"}
            ],
            "living room": [
                {"title": "Living Room Renovation", "description": "Living room complete renovation"},
                {"title": "Family Room", "description": "Family room update"},
                {"title": "Great Room", "description": "Great room renovation"}
            ]
        }
        
        # Test each room type
        for room_type, scenarios in room_test_scenarios.items():
            self.log(f"\n--- Testing {room_type.upper()} Room Type ---")
            expected_config = expected_room_subtasks[room_type]
            
            for scenario in scenarios:
                self.log(f"\n--- Testing Scenario: {scenario['title']} ---")
                
                # Create room task
                room_task = {
                    "project_id": project_id,
                    "title": scenario['title'],
                    "description": scenario['description'],
                    "priority": "high"
                }
                
                created_task = self.test_request("POST", "/tasks", room_task, 200, 
                                               f"Create {room_type.title()} Task - {scenario['title']}", 
                                               auth_token=self.admin_token)
                
                if not created_task:
                    self.log(f"❌ Failed to create {room_type} task: {scenario['title']}", "ERROR")
                    continue
                
                task_id = created_task['id']
                self.log(f"✅ Created {room_type} task: {task_id}")
                
                # Test room detection and subtask generation
                subtask_response = self.test_request("POST", f"/tasks/{task_id}/generate-subtasks", 
                                                   None, 200, 
                                                   f"Generate Subtasks for {scenario['title']}", 
                                                   auth_token=self.admin_token)
                
                if subtask_response:
                    # Verify room type detection
                    detected_room_type = subtask_response.get('room_type')
                    if detected_room_type == room_type:
                        self.log(f"✅ Room type correctly detected as: {detected_room_type}")
                        self.passed_tests += 1
                    else:
                        self.log(f"❌ Room type detection failed: expected {room_type}, got {detected_room_type}", "ERROR")
                        self.failed_tests += 1
                    
                    # Verify subtask count
                    message = subtask_response.get('message', '')
                    expected_count = expected_config['count']
                    if f'generated {expected_count} standard subtasks' in message:
                        self.log(f"✅ Correct number of subtasks created: {expected_count}")
                        self.passed_tests += 1
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
                        expected_titles = [subtask['title'] for subtask in expected_config['subtasks']]
                        
                        # Check each expected subtask
                        for expected_subtask in expected_config['subtasks']:
                            if expected_subtask['title'] in created_titles:
                                self.log(f"✅ Found expected subtask: '{expected_subtask['title']}'")
                                self.passed_tests += 1
                                
                                # Find the created subtask and verify description
                                created_subtask = next((s for s in created_subtasks_list if s['title'] == expected_subtask['title']), None)
                                if created_subtask and created_subtask['description'] == expected_subtask['description']:
                                    self.log(f"✅ Correct description for '{expected_subtask['title']}'")
                                    self.passed_tests += 1
                                else:
                                    self.log(f"❌ Incorrect description for '{expected_subtask['title']}'", "ERROR")
                                    self.failed_tests += 1
                            else:
                                self.log(f"❌ Missing expected subtask: '{expected_subtask['title']}'", "ERROR")
                                self.failed_tests += 1
                        
                        # Verify no old subtasks are present (for kitchen specifically)
                        if room_type == "kitchen":
                            old_kitchen_subtasks = ["Electrical Work", "Painting", "Windows", "Appliances"]
                            for old_subtask in old_kitchen_subtasks:
                                if old_subtask in created_titles:
                                    self.log(f"❌ Found old subtask '{old_subtask}' - should be removed", "ERROR")
                                    self.failed_tests += 1
                                else:
                                    self.log(f"✅ Confirmed old subtask '{old_subtask}' is no longer generated")
                                    self.passed_tests += 1
                        
                        # Verify subtask structure and required fields
                        for subtask in created_subtasks_list:
                            required_fields = ['id', 'title', 'description', 'estimated_budget', 'actual_cost', 
                                             'order_date', 'delivery_date', 'store_id', 'project_id', 'parent_task_id']
                            
                            missing_fields = [field for field in required_fields if field not in subtask]
                            if missing_fields:
                                self.log(f"❌ Subtask '{subtask['title']}' missing fields: {missing_fields}", "ERROR")
                                self.failed_tests += 1
                            else:
                                self.log(f"✅ Subtask '{subtask['title']}' has all required fields")
                                self.passed_tests += 1
                        
                        # Verify no duplicate subtasks
                        if len(created_titles) == len(set(created_titles)):
                            self.log("✅ No duplicate subtasks found")
                            self.passed_tests += 1
                        else:
                            self.log("❌ Duplicate subtasks detected", "ERROR")
                            self.failed_tests += 1
                    
                    else:
                        self.log(f"❌ Failed to retrieve generated subtasks for {scenario['title']}", "ERROR")
                        self.failed_tests += 1
                
                else:
                    self.log(f"❌ Failed to generate subtasks for {scenario['title']}", "ERROR")
                    self.failed_tests += 1
        
        self.log(f"\n✅ Updated Room Subtask Configuration Testing Complete")

    def run_test(self):
        """Run the focused test"""
        self.log("🚀 Starting Updated Room Subtask Configuration Testing")
        self.log(f"Backend URL: {self.base_url}")
        
        # Authenticate first
        if not self.authenticate():
            self.log("❌ Cannot proceed without authentication", "ERROR")
            return
        
        # Run the test
        self.test_updated_room_subtask_configurations()
        
        # Print final results
        self.log("\n" + "="*50)
        self.log("🏁 TESTING COMPLETE")
        self.log(f"✅ Passed: {self.passed_tests}")
        self.log(f"❌ Failed: {self.failed_tests}")
        total_tests = self.passed_tests + self.failed_tests
        if total_tests > 0:
            success_rate = (self.passed_tests / total_tests) * 100
            self.log(f"📊 Success Rate: {success_rate:.1f}%")
        self.log("="*50)

if __name__ == "__main__":
    tester = UpdatedRoomSubtaskTester()
    tester.run_test()