#!/usr/bin/env python3
"""
Focused test for the three new room type subtask generation features: PANTRY, CLOSET, DINING ROOM
"""

import requests
import json
from datetime import datetime

# Get backend URL from frontend .env
BACKEND_URL = "https://buildbuddy-2.preview.emergentagent.com/api"

class FocusedRoomTester:
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

    def authenticate(self):
        """Authenticate as admin user"""
        self.log("\n=== Authentication ===")
        
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

    def setup_test_project(self):
        """Create a test project for room testing"""
        self.log("\n=== Setting Up Test Project ===")
        
        project_data = {
            "name": "New Room Types Test Project",
            "description": "Testing PANTRY, CLOSET, and DINING ROOM subtask generation",
            "color": "#FF6B6B"
        }
        
        created_project = self.test_request("POST", "/projects", project_data, 200, 
                                          "Create Test Project", auth_token=self.admin_token)
        
        if created_project:
            self.test_project_id = created_project['id']
            self.log(f"✅ Test project created: {self.test_project_id}")
            return True
        else:
            self.log("❌ Failed to create test project", "ERROR")
            return False

    def test_new_room_type_subtask_generation(self):
        """Test the three new room type subtask generation features: PANTRY, CLOSET, DINING ROOM"""
        self.log("\n=== Testing New Room Type Subtask Generation Features ===")
        
        # Test data for the three new room types
        room_test_scenarios = {
            "pantry": {
                "variations": [
                    "Pantry Renovation",
                    "Food Storage Pantry", 
                    "Kitchen Pantry"
                ],
                "expected_subtasks": [
                    {"title": "Wall Coverings", "description": "Install wall coverings, paint, or wallpaper"},
                    {"title": "Flooring", "description": "Install pantry flooring"},
                    {"title": "Cabinets", "description": "Install pantry cabinets and shelving systems"},
                    {"title": "Cabinet Hardware", "description": "Install cabinet handles, knobs, and drawer slides"}
                ],
                "expected_count": 4
            },
            "closet": {
                "variations": [
                    "Master Closet",
                    "Walk-in Closet",
                    "Bedroom Wardrobe"
                ],
                "expected_subtasks": [
                    {"title": "Shelving", "description": "Install closet shelving and organization systems"}
                ],
                "expected_count": 1
            },
            "dining room": {
                "variations": [
                    "Dining Room Remodel",
                    "Formal Dining Area",
                    "Dining Room Renovation"
                ],
                "expected_subtasks": [
                    {"title": "Wall Coverings", "description": "Install wall coverings, paint, or wallpaper"},
                    {"title": "Flooring", "description": "Install dining room flooring"},
                    {"title": "Lighting", "description": "Install dining room lighting fixtures and chandeliers"}
                ],
                "expected_count": 3
            }
        }
        
        # Test each room type with multiple variations
        for room_type, test_data in room_test_scenarios.items():
            self.log(f"\n--- Testing {room_type.upper()} Room Type ---")
            
            for i, room_title in enumerate(test_data["variations"]):
                self.log(f"\n--- Testing {room_type.upper()} Variation {i+1}: '{room_title}' ---")
                
                # Create a room task
                room_task_data = {
                    "project_id": self.test_project_id,
                    "title": room_title,
                    "description": f"Test room for {room_type} subtask generation",
                    "priority": "medium",
                    "subtask_level": 0
                }
                
                created_room = self.test_request("POST", "/tasks", room_task_data, 200, 
                                               f"Create {room_type} Room - {room_title}", auth_token=self.admin_token)
                
                if created_room:
                    room_id = created_room['id']
                    self.log(f"✅ Created {room_type} room: {room_title} (ID: {room_id})")
                    
                    # Generate subtasks for this room
                    subtasks_response = self.test_request("POST", f"/tasks/{room_id}/generate-subtasks", 
                                                        None, 200, f"Generate {room_type} Subtasks", 
                                                        auth_token=self.admin_token)
                    
                    if subtasks_response:
                        self.log(f"✅ Subtask generation successful for {room_type}")
                        
                        # Verify the correct number of subtasks were created
                        generated_subtasks = subtasks_response.get('created_subtasks', [])
                        expected_count = test_data["expected_count"]
                        
                        if len(generated_subtasks) == expected_count:
                            self.log(f"✅ Correct subtask count: {len(generated_subtasks)} subtasks generated for {room_type}")
                        else:
                            self.log(f"❌ Incorrect subtask count for {room_type}: expected {expected_count}, got {len(generated_subtasks)}", "ERROR")
                            self.failed_tests += 1
                            continue
                        
                        # Verify each expected subtask is present with correct title and description
                        expected_subtasks = test_data["expected_subtasks"]
                        
                        for expected_subtask in expected_subtasks:
                            found_subtask = None
                            for generated_subtask in generated_subtasks:
                                if generated_subtask.get('title') == expected_subtask['title']:
                                    found_subtask = generated_subtask
                                    break
                            
                            if found_subtask:
                                # Verify title matches
                                if found_subtask['title'] == expected_subtask['title']:
                                    self.log(f"✅ {room_type} subtask title correct: '{found_subtask['title']}'")
                                else:
                                    self.log(f"❌ {room_type} subtask title incorrect: expected '{expected_subtask['title']}', got '{found_subtask['title']}'", "ERROR")
                                    self.failed_tests += 1
                                
                                # Verify description matches
                                if found_subtask['description'] == expected_subtask['description']:
                                    self.log(f"✅ {room_type} subtask description correct: '{found_subtask['description']}'")
                                else:
                                    self.log(f"❌ {room_type} subtask description incorrect: expected '{expected_subtask['description']}', got '{found_subtask['description']}'", "ERROR")
                                    self.failed_tests += 1
                                
                                # Verify required fields are present
                                required_fields = ['id', 'title', 'description', 'estimated_budget', 'actual_cost', 
                                                 'order_date', 'delivery_date', 'store_id', 'project_id', 'parent_task_id']
                                
                                for field in required_fields:
                                    if field in found_subtask:
                                        self.log(f"✅ {room_type} subtask has required field: {field}")
                                    else:
                                        self.log(f"❌ {room_type} subtask missing required field: {field}", "ERROR")
                                        self.failed_tests += 1
                                
                                # Verify parent_task_id is correct
                                if found_subtask.get('parent_task_id') == room_id:
                                    self.log(f"✅ {room_type} subtask has correct parent_task_id")
                                else:
                                    self.log(f"❌ {room_type} subtask has incorrect parent_task_id: expected {room_id}, got {found_subtask.get('parent_task_id')}", "ERROR")
                                    self.failed_tests += 1
                                
                            else:
                                self.log(f"❌ {room_type} expected subtask not found: '{expected_subtask['title']}'", "ERROR")
                                self.failed_tests += 1
                        
                        # Test duplicate prevention
                        duplicate_response = self.test_request("POST", f"/tasks/{room_id}/generate-subtasks", 
                                                             None, 200, f"Test {room_type} Duplicate Prevention", 
                                                             auth_token=self.admin_token)
                        
                        if duplicate_response and 'already has' in duplicate_response.get('message', ''):
                            self.log(f"✅ {room_type} duplicate prevention working correctly")
                        else:
                            self.log(f"❌ {room_type} duplicate prevention not working", "ERROR")
                            self.failed_tests += 1
                    
                    else:
                        self.log(f"❌ Failed to generate subtasks for {room_type} room: {room_title}", "ERROR")
                        self.failed_tests += 1
                
                else:
                    self.log(f"❌ Failed to create {room_type} room: {room_title}", "ERROR")
                    self.failed_tests += 1
        
        # Test room detection with edge cases
        self.log("\n--- Testing Room Detection Edge Cases ---")
        
        edge_case_tests = [
            {"title": "PANTRY STORAGE", "expected_type": "pantry"},
            {"title": "master bedroom closet", "expected_type": "closet"},
            {"title": "Formal Dining", "expected_type": "dining room"},
            {"title": "Office Space", "expected_type": None},  # Should fail
            {"title": "Random Room", "expected_type": None}   # Should fail
        ]
        
        for edge_case in edge_case_tests:
            room_task_data = {
                "project_id": self.test_project_id,
                "title": edge_case["title"],
                "description": f"Edge case test for room detection",
                "priority": "low",
                "subtask_level": 0
            }
            
            created_room = self.test_request("POST", "/tasks", room_task_data, 200, 
                                           f"Create Edge Case Room - {edge_case['title']}", auth_token=self.admin_token)
            
            if created_room:
                room_id = created_room['id']
                
                if edge_case["expected_type"]:
                    # Should succeed
                    subtasks_response = self.test_request("POST", f"/tasks/{room_id}/generate-subtasks", 
                                                        None, 200, f"Generate Subtasks for {edge_case['title']}", 
                                                        auth_token=self.admin_token)
                    
                    if subtasks_response:
                        self.log(f"✅ Room detection working for edge case: '{edge_case['title']}' detected as {edge_case['expected_type']}")
                    else:
                        self.log(f"❌ Room detection failed for edge case: '{edge_case['title']}'", "ERROR")
                        self.failed_tests += 1
                else:
                    # Should fail with 400 error
                    subtasks_response = self.test_request("POST", f"/tasks/{room_id}/generate-subtasks", 
                                                        None, 400, f"Generate Subtasks for Unrecognized Room - {edge_case['title']}", 
                                                        auth_token=self.admin_token)
                    
                    if subtasks_response is None:  # 400 error expected
                        self.log(f"✅ Unrecognized room type properly rejected: '{edge_case['title']}'")
                    else:
                        self.log(f"❌ Unrecognized room type should have been rejected: '{edge_case['title']}'", "ERROR")
                        self.failed_tests += 1
        
        self.log(f"\n=== New Room Type Subtask Generation Testing Complete ===")

    def run_focused_test(self):
        """Run focused test for new room types"""
        self.log("🚀 Starting Focused New Room Type Subtask Generation Testing")
        self.log(f"Backend URL: {self.base_url}")
        
        try:
            # Authenticate
            if not self.authenticate():
                return False
            
            # Setup test project
            if not self.setup_test_project():
                return False
            
            # Test new room type subtask generation
            self.test_new_room_type_subtask_generation()
            
        except Exception as e:
            self.log(f"❌ Test execution failed: {str(e)}", "ERROR")
            self.failed_tests += 1
        
        # Print final results
        self.log("\n" + "="*50)
        self.log("🏁 FOCUSED TESTING COMPLETE")
        self.log(f"✅ Passed: {self.passed_tests}")
        self.log(f"❌ Failed: {self.failed_tests}")
        self.log(f"📊 Success Rate: {(self.passed_tests/(self.passed_tests + self.failed_tests)*100):.1f}%" if (self.passed_tests + self.failed_tests) > 0 else "No tests run")
        self.log("="*50)
        
        return self.failed_tests == 0

if __name__ == "__main__":
    tester = FocusedRoomTester()
    success = tester.run_focused_test()
    exit(0 if success else 1)