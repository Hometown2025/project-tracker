#!/usr/bin/env python3
"""
Focused Test for Auto-Populate Subtasks Functionality
"""

import requests
import json
from datetime import datetime, date, timedelta
import sys
import os

# Get backend URL from frontend .env
BACKEND_URL = "https://house-budget-app.preview.emergentagent.com/api"

class SubtasksOnlyTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.passed_tests = 0
        self.failed_tests = 0
        self.admin_token = None
        self.super_admin_token = None
        self.demo_token = None
        
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

    def authenticate_users(self):
        """Authenticate all required users"""
        self.log("\n=== Authenticating Users ===")
        
        # Admin login
        admin_login = {
            "username": "admin",
            "password": "admin",
            "store_id": "STORE_001"
        }
        
        admin_response = self.test_request("POST", "/auth/login", admin_login, 200, "Admin Login")
        if admin_response:
            self.admin_token = admin_response.get('session_token')
            self.log("✅ Admin authenticated successfully")
        
        # Super Admin login
        super_admin_login = {
            "username": "superadmin",
            "password": "superadmin123",
            "store_id": "GLOBAL"
        }
        
        super_admin_response = self.test_request("POST", "/auth/login", super_admin_login, 200, "Super Admin Login")
        if super_admin_response:
            self.super_admin_token = super_admin_response.get('session_token')
            self.log("✅ Super Admin authenticated successfully")
        
        # Demo user login
        demo_login = {
            "username": "demo",
            "password": "demo",
            "store_id": "STORE_001"
        }
        
        demo_response = self.test_request("POST", "/auth/login", demo_login, 200, "Demo User Login")
        if demo_response:
            self.demo_token = demo_response.get('session_token')
            self.log("✅ Demo user authenticated successfully")

    def test_auto_populate_subtasks_functionality(self):
        """Test Auto-Populate Subtasks Based on Room Labels Backend"""
        self.log("\n=== Testing Auto-Populate Subtasks Functionality ===")
        
        if not self.admin_token:
            self.log("❌ No admin token available for auto-populate subtasks testing", "ERROR")
            return
        
        # Create a test project for room creation
        test_project = {
            "name": "House Building Project - Subtasks Test",
            "description": "Project for testing auto-populate subtasks functionality",
            "color": "#FF6B35"
        }
        
        created_project = self.test_request("POST", "/projects", test_project, 200, "Create Project for Subtasks Testing", auth_token=self.admin_token)
        
        if not created_project:
            self.log("❌ Failed to create test project for subtasks testing", "ERROR")
            return
        
        project_id = created_project['id']
        
        # 1. Test Room Types Endpoint
        self.log("\n--- 1. Testing Room Types Endpoint ---")
        room_types = self.test_request("GET", "/room-types", test_name="Get Available Room Types")
        
        if room_types:
            expected_room_types = ["kitchen", "bathroom", "bedroom", "living room", "garage", "laundry room"]
            found_room_types = list(room_types.keys())
            
            for expected_type in expected_room_types:
                if expected_type in found_room_types:
                    room_info = room_types[expected_type]
                    self.log(f"✅ Room type '{expected_type}': {room_info['subtask_count']} subtasks")
                    
                    # Verify expected subtask counts
                    expected_counts = {
                        "kitchen": 7, "bathroom": 7, "bedroom": 5, 
                        "living room": 5, "garage": 5, "laundry room": 5
                    }
                    
                    if room_info['subtask_count'] == expected_counts[expected_type]:
                        self.log(f"✅ Correct subtask count for {expected_type}")
                    else:
                        self.log(f"❌ Incorrect subtask count for {expected_type}: expected {expected_counts[expected_type]}, got {room_info['subtask_count']}", "ERROR")
                        self.failed_tests += 1
                else:
                    self.log(f"❌ Missing room type: {expected_type}", "ERROR")
                    self.failed_tests += 1
        
        # 2. Test Room Type Detection with Exact Matches
        self.log("\n--- 2. Testing Room Type Detection - Exact Matches ---")
        exact_match_rooms = [
            {"title": "Kitchen", "expected_type": "kitchen", "expected_count": 7},
            {"title": "Bathroom", "expected_type": "bathroom", "expected_count": 7},
            {"title": "Bedroom", "expected_type": "bedroom", "expected_count": 5},
            {"title": "Living Room", "expected_type": "living room", "expected_count": 5},
            {"title": "Garage", "expected_type": "garage", "expected_count": 5},
            {"title": "Laundry Room", "expected_type": "laundry room", "expected_count": 5}
        ]
        
        created_rooms = []
        
        for room_data in exact_match_rooms:
            # Create room (task)
            room_task = {
                "project_id": project_id,
                "title": room_data["title"],
                "description": f"Test room for {room_data['title']} subtask generation",
                "priority": "medium"
            }
            
            created_room = self.test_request("POST", "/tasks", room_task, 200, f"Create Room - {room_data['title']}", auth_token=self.admin_token)
            
            if created_room:
                created_rooms.append({**created_room, **room_data})
                
                # Generate subtasks for this room
                subtask_response = self.test_request("POST", f"/tasks/{created_room['id']}/generate-subtasks", {}, 200, 
                                                   f"Generate Subtasks for {room_data['title']}", auth_token=self.admin_token)
                
                if subtask_response:
                    if subtask_response.get('room_type') == room_data['expected_type']:
                        self.log(f"✅ Correct room type detected: {room_data['expected_type']}")
                    else:
                        self.log(f"❌ Incorrect room type detected: expected {room_data['expected_type']}, got {subtask_response.get('room_type')}", "ERROR")
                        self.failed_tests += 1
                    
                    if subtask_response.get('total_created') == room_data['expected_count']:
                        self.log(f"✅ Correct number of subtasks created: {room_data['expected_count']}")
                    else:
                        self.log(f"❌ Incorrect number of subtasks: expected {room_data['expected_count']}, got {subtask_response.get('total_created')}", "ERROR")
                        self.failed_tests += 1
                    
                    # Verify subtasks were actually created in database
                    room_subtasks = self.test_request("GET", f"/tasks?parent_task_id={created_room['id']}", auth_token=self.admin_token,
                                                    test_name=f"Verify {room_data['title']} Subtasks in Database")
                    
                    if room_subtasks and len(room_subtasks) == room_data['expected_count']:
                        self.log(f"✅ {len(room_subtasks)} subtasks verified in database for {room_data['title']}")
                        
                        # Verify subtask structure
                        for subtask in room_subtasks:
                            required_fields = ['id', 'title', 'description', 'estimated_budget', 'actual_cost', 'order_date', 'delivery_date']
                            for field in required_fields:
                                if field in subtask:
                                    self.log(f"✅ Subtask has {field} field")
                                else:
                                    self.log(f"❌ Subtask missing {field} field", "ERROR")
                                    self.failed_tests += 1
                    else:
                        self.log(f"❌ Subtask count mismatch in database for {room_data['title']}", "ERROR")
                        self.failed_tests += 1
        
        # 3. Test Room Type Detection with Variations
        self.log("\n--- 3. Testing Room Type Detection - Variations ---")
        variation_rooms = [
            {"title": "Master Bathroom", "expected_type": "bathroom", "expected_count": 7},
            {"title": "Guest Bedroom", "expected_type": "bedroom", "expected_count": 5},
            {"title": "Main Kitchen", "expected_type": "kitchen", "expected_count": 7},
            {"title": "Family Living Room", "expected_type": "living room", "expected_count": 5}
        ]
        
        for room_data in variation_rooms:
            room_task = {
                "project_id": project_id,
                "title": room_data["title"],
                "description": f"Test room variation for {room_data['title']}",
                "priority": "medium"
            }
            
            created_room = self.test_request("POST", "/tasks", room_task, 200, f"Create Room Variation - {room_data['title']}", auth_token=self.admin_token)
            
            if created_room:
                subtask_response = self.test_request("POST", f"/tasks/{created_room['id']}/generate-subtasks", {}, 200, 
                                                   f"Generate Subtasks for {room_data['title']} Variation", auth_token=self.admin_token)
                
                if subtask_response and subtask_response.get('room_type') == room_data['expected_type']:
                    self.log(f"✅ Room variation detected correctly: {room_data['title']} → {room_data['expected_type']}")
                else:
                    self.log(f"❌ Room variation detection failed for {room_data['title']}", "ERROR")
                    self.failed_tests += 1
        
        # 4. Test Partial Matches
        self.log("\n--- 4. Testing Room Type Detection - Partial Matches ---")
        partial_match_rooms = [
            {"title": "Bath", "expected_type": "bathroom"},
            {"title": "Cook Area", "expected_type": "kitchen"},
            {"title": "Car Storage", "expected_type": "garage"}
        ]
        
        for room_data in partial_match_rooms:
            room_task = {
                "project_id": project_id,
                "title": room_data["title"],
                "description": f"Test partial match for {room_data['title']}",
                "priority": "medium"
            }
            
            created_room = self.test_request("POST", "/tasks", room_task, 200, f"Create Partial Match Room - {room_data['title']}", auth_token=self.admin_token)
            
            if created_room:
                subtask_response = self.test_request("POST", f"/tasks/{created_room['id']}/generate-subtasks", {}, 200, 
                                                   f"Generate Subtasks for {room_data['title']} Partial Match", auth_token=self.admin_token)
                
                if subtask_response and subtask_response.get('room_type') == room_data['expected_type']:
                    self.log(f"✅ Partial match detected correctly: {room_data['title']} → {room_data['expected_type']}")
                else:
                    self.log(f"❌ Partial match detection failed for {room_data['title']}", "ERROR")
                    self.failed_tests += 1
        
        # 5. Test Unrecognized Room Types
        self.log("\n--- 5. Testing Unrecognized Room Types ---")
        unrecognized_rooms = ["Office", "Basement", "Attic", "Random Room"]
        
        for room_title in unrecognized_rooms:
            room_task = {
                "project_id": project_id,
                "title": room_title,
                "description": f"Test unrecognized room type: {room_title}",
                "priority": "medium"
            }
            
            created_room = self.test_request("POST", "/tasks", room_task, 200, f"Create Unrecognized Room - {room_title}", auth_token=self.admin_token)
            
            if created_room:
                # Should return 400 error for unrecognized room type
                self.test_request("POST", f"/tasks/{created_room['id']}/generate-subtasks", {}, 400, 
                                f"Generate Subtasks for Unrecognized Room - {room_title}", auth_token=self.admin_token)
        
        # 6. Test Duplicate Prevention
        self.log("\n--- 6. Testing Duplicate Prevention ---")
        if created_rooms:
            first_room = created_rooms[0]
            # Try to generate subtasks again for a room that already has subtasks
            duplicate_response = self.test_request("POST", f"/tasks/{first_room['id']}/generate-subtasks", {}, 200, 
                                                 f"Attempt Duplicate Subtask Generation for {first_room['title']}", auth_token=self.admin_token)
            
            if duplicate_response and 'already has' in duplicate_response.get('message', ''):
                self.log("✅ Duplicate prevention working - proper error message returned")
            else:
                self.log("❌ Duplicate prevention failed", "ERROR")
                self.failed_tests += 1
        
        # 7. Test Access Control
        self.log("\n--- 7. Testing Access Control ---")
        
        # Test that regular customer cannot generate subtasks
        if self.demo_token and created_rooms:
            test_room = created_rooms[0]
            self.test_request("POST", f"/tasks/{test_room['id']}/generate-subtasks", {}, 403, 
                            "Demo User Generate Subtasks (Should Fail)", auth_token=self.demo_token)
        
        # Test that admin can generate subtasks
        if created_rooms:
            # Create a new room for admin test
            admin_room_task = {
                "project_id": project_id,
                "title": "Admin Test Kitchen",
                "description": "Kitchen for admin access control test",
                "priority": "medium"
            }
            
            admin_room = self.test_request("POST", "/tasks", admin_room_task, 200, "Create Room for Admin Access Test", auth_token=self.admin_token)
            
            if admin_room:
                admin_subtasks = self.test_request("POST", f"/tasks/{admin_room['id']}/generate-subtasks", {}, 200, 
                                                 "Admin Generate Subtasks", auth_token=self.admin_token)
                
                if admin_subtasks:
                    self.log("✅ Admin can generate subtasks")
        
        # Test that super admin can generate subtasks
        if self.super_admin_token:
            super_admin_room_task = {
                "project_id": project_id,
                "title": "Super Admin Test Bathroom",
                "description": "Bathroom for super admin access control test",
                "priority": "medium"
            }
            
            super_admin_room = self.test_request("POST", "/tasks", super_admin_room_task, 200, "Create Room for Super Admin Access Test", auth_token=self.super_admin_token)
            
            if super_admin_room:
                super_admin_subtasks = self.test_request("POST", f"/tasks/{super_admin_room['id']}/generate-subtasks", {}, 200, 
                                                        "Super Admin Generate Subtasks", auth_token=self.super_admin_token)
                
                if super_admin_subtasks:
                    self.log("✅ Super Admin can generate subtasks")
        
        # 8. Test Budget and Date Fields
        self.log("\n--- 8. Testing Budget and Date Fields in Generated Subtasks ---")
        if created_rooms:
            test_room = created_rooms[0]
            # Get subtasks for the first room
            subtasks = self.test_request("GET", f"/tasks?parent_task_id={test_room['id']}", auth_token=self.admin_token,
                                       test_name="Get Subtasks for Budget/Date Field Testing")
            
            if subtasks:
                for subtask in subtasks:
                    # Verify budget fields exist (should be nullable)
                    if 'estimated_budget' in subtask:
                        self.log(f"✅ Subtask '{subtask['title']}' has estimated_budget field: {subtask['estimated_budget']}")
                    else:
                        self.log(f"❌ Subtask '{subtask['title']}' missing estimated_budget field", "ERROR")
                        self.failed_tests += 1
                    
                    if 'actual_cost' in subtask:
                        self.log(f"✅ Subtask '{subtask['title']}' has actual_cost field: {subtask['actual_cost']}")
                    else:
                        self.log(f"❌ Subtask '{subtask['title']}' missing actual_cost field", "ERROR")
                        self.failed_tests += 1
                    
                    # Verify date fields exist (should be nullable)
                    if 'order_date' in subtask:
                        self.log(f"✅ Subtask '{subtask['title']}' has order_date field: {subtask['order_date']}")
                    else:
                        self.log(f"❌ Subtask '{subtask['title']}' missing order_date field", "ERROR")
                        self.failed_tests += 1
                    
                    if 'delivery_date' in subtask:
                        self.log(f"✅ Subtask '{subtask['title']}' has delivery_date field: {subtask['delivery_date']}")
                    else:
                        self.log(f"❌ Subtask '{subtask['title']}' missing delivery_date field", "ERROR")
                        self.failed_tests += 1
                    
                    # Verify inheritance of project_id and store_id
                    if subtask.get('project_id') == project_id:
                        self.log(f"✅ Subtask inherits correct project_id")
                    else:
                        self.log(f"❌ Subtask has incorrect project_id: expected {project_id}, got {subtask.get('project_id')}", "ERROR")
                        self.failed_tests += 1
                    
                    if subtask.get('store_id') == 'STORE_001':
                        self.log(f"✅ Subtask inherits correct store_id")
                    else:
                        self.log(f"❌ Subtask has incorrect store_id: expected STORE_001, got {subtask.get('store_id')}", "ERROR")
                        self.failed_tests += 1
        
        # 9. Test Integration - Project → Room → Generate Subtasks → Verify Hierarchy
        self.log("\n--- 9. Testing Integration and Hierarchy ---")
        
        # Create a complete integration test
        integration_project = {
            "name": "Integration Test House",
            "description": "Complete integration test for subtask generation",
            "color": "#4CAF50"
        }
        
        integration_proj = self.test_request("POST", "/projects", integration_project, 200, "Create Integration Test Project", auth_token=self.admin_token)
        
        if integration_proj:
            integration_room = {
                "project_id": integration_proj['id'],
                "title": "Integration Kitchen",
                "description": "Kitchen for complete integration test",
                "priority": "high"
            }
            
            integration_room_created = self.test_request("POST", "/tasks", integration_room, 200, "Create Integration Room", auth_token=self.admin_token)
            
            if integration_room_created:
                # Generate subtasks
                integration_subtasks = self.test_request("POST", f"/tasks/{integration_room_created['id']}/generate-subtasks", {}, 200, 
                                                       "Generate Integration Subtasks", auth_token=self.admin_token)
                
                if integration_subtasks:
                    # Verify parent task subtask count was updated
                    updated_room = self.test_request("GET", f"/tasks/{integration_room_created['id']}", auth_token=self.admin_token,
                                                   test_name="Verify Parent Room Subtask Count Updated")
                    
                    if updated_room and updated_room.get('subtask_count') == 7:
                        self.log("✅ Parent room subtask count updated correctly")
                    else:
                        self.log(f"❌ Parent room subtask count not updated: expected 7, got {updated_room.get('subtask_count') if updated_room else 'None'}", "ERROR")
                        self.failed_tests += 1
                    
                    # Verify subtasks can be edited normally
                    subtasks = self.test_request("GET", f"/tasks?parent_task_id={integration_room_created['id']}", auth_token=self.admin_token,
                                               test_name="Get Integration Subtasks for Editing Test")
                    
                    if subtasks and len(subtasks) > 0:
                        first_subtask = subtasks[0]
                        
                        # Test editing a generated subtask
                        subtask_update = {
                            "title": "Updated Electrical Work",
                            "description": "Updated description for electrical work",
                            "estimated_budget": 5000.00,
                            "actual_cost": 4500.75,
                            "order_date": "2024-12-20",
                            "delivery_date": "2024-12-25"
                        }
                        
                        updated_subtask = self.test_request("PUT", f"/tasks/{first_subtask['id']}", subtask_update, 200, 
                                                          "Update Generated Subtask", auth_token=self.admin_token)
                        
                        if updated_subtask:
                            if updated_subtask.get('title') == subtask_update['title']:
                                self.log("✅ Generated subtask can be edited normally")
                            else:
                                self.log("❌ Generated subtask editing failed", "ERROR")
                                self.failed_tests += 1
        
        self.log("\n=== Auto-Populate Subtasks Testing Complete ===")

    def run_test(self):
        """Run the focused subtasks test"""
        self.log("🚀 Starting Auto-Populate Subtasks Testing")
        self.log(f"Backend URL: {self.base_url}")
        
        try:
            # Authenticate users
            self.authenticate_users()
            
            # Test auto-populate subtasks functionality
            self.test_auto_populate_subtasks_functionality()
            
        except Exception as e:
            self.log(f"❌ Test failed with exception: {str(e)}", "ERROR")
            self.failed_tests += 1
        
        # Print final results
        self.log("\n" + "="*50)
        self.log("🏁 AUTO-POPULATE SUBTASKS TESTING COMPLETE")
        self.log(f"✅ Passed: {self.passed_tests}")
        self.log(f"❌ Failed: {self.failed_tests}")
        self.log(f"📊 Success Rate: {(self.passed_tests/(self.passed_tests + self.failed_tests)*100):.1f}%" if (self.passed_tests + self.failed_tests) > 0 else "No tests run")
        self.log("="*50)
        
        return self.failed_tests == 0

if __name__ == "__main__":
    tester = SubtasksOnlyTester()
    success = tester.run_test()
    sys.exit(0 if success else 1)