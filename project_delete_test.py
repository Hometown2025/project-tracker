#!/usr/bin/env python3
"""
Focused Project Delete Functionality Testing
Tests the specific project deletion functionality that the user reported as not working
"""

import requests
import json
from datetime import datetime, date, timedelta
import sys
import os

# Get backend URL from frontend .env
BACKEND_URL = "https://cbeb4b42-6dc1-47fd-acaa-07a377732d5e.preview.emergentagent.com/api"

class ProjectDeleteTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.passed_tests = 0
        self.failed_tests = 0
        self.admin_token = None
        self.superadmin_token = None
        self.customer_token = None
        
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
                    return {"status": "passed", "data": response.json()}
                except:
                    return {"status": "passed", "data": response.text}
            else:
                self.failed_tests += 1
                self.log(f"❌ FAILED: {test_name} - Expected {expected_status}, got {response.status_code}", "ERROR")
                self.log(f"Response: {response.text}", "ERROR")
                return {"status": "failed", "actual_status": response.status_code}
                
        except Exception as e:
            self.failed_tests += 1
            self.log(f"❌ FAILED: {test_name} - Exception: {str(e)}", "ERROR")
            return {"status": "error", "error": str(e)}

    def authenticate_users(self):
        """Authenticate all required users for testing"""
        self.log("\n=== Authenticating Test Users ===")
        
        # Admin authentication (admin/admin/STORE_001)
        admin_login = {
            "username": "admin",
            "password": "admin",
            "store_id": "STORE_001"
        }
        
        admin_response = self.test_request("POST", "/auth/login", admin_login, 200, "Admin Authentication")
        if admin_response and admin_response["status"] == "passed":
            self.admin_token = admin_response["data"].get('session_token')
            self.log("✅ Admin authenticated successfully")
        
        # Super Admin authentication (superadmin/superadmin123/GLOBAL)
        superadmin_login = {
            "username": "superadmin",
            "password": "superadmin123",
            "store_id": "GLOBAL"
        }
        
        superadmin_response = self.test_request("POST", "/auth/login", superadmin_login, 200, "Super Admin Authentication")
        if superadmin_response and superadmin_response["status"] == "passed":
            self.superadmin_token = superadmin_response["data"].get('session_token')
            self.log("✅ Super Admin authenticated successfully")
        
        # Customer authentication (demo/demo/STORE_001)
        customer_login = {
            "username": "demo",
            "password": "demo",
            "store_id": "STORE_001"
        }
        
        customer_response = self.test_request("POST", "/auth/login", customer_login, 200, "Customer Authentication")
        if customer_response and customer_response["status"] == "passed":
            self.customer_token = customer_response["data"].get('session_token')
            self.log("✅ Customer authenticated successfully")

    def test_project_deletion_functionality(self):
        """Test comprehensive project deletion functionality"""
        self.log("\n=== Testing Project Deletion Functionality ===")
        
        if not self.admin_token:
            self.log("❌ Admin token not available", "ERROR")
            return
        
        # 1. Create test project with associated tasks and ideas
        self.log("\n--- 1. Creating Test Project with Associated Data ---")
        
        test_project = {
            "name": "House Renovation Delete Test",
            "description": "Test project for deletion functionality with associated tasks and ideas",
            "color": "#FF5722",
            "estimated_budget": 50000.00
        }
        
        created_project = self.test_request("POST", "/projects", test_project, 200, 
                                          "Create Test Project", auth_token=self.admin_token)
        
        if not created_project:
            self.log("❌ Failed to create test project", "ERROR")
            return
        
        project_id = created_project['id']
        self.log(f"✅ Created test project: {project_id}")
        
        # Create associated tasks (rooms)
        test_tasks = [
            {
                "project_id": project_id,
                "title": "Kitchen Renovation",
                "description": "Complete kitchen renovation with new cabinets and appliances",
                "priority": "high",
                "estimated_budget": 15000.00,
                "actual_cost": 12500.75
            },
            {
                "project_id": project_id,
                "title": "Bathroom Remodel",
                "description": "Master bathroom remodel with new fixtures",
                "priority": "medium",
                "estimated_budget": 8000.25,
                "actual_cost": 8500.00
            }
        ]
        
        created_tasks = []
        for task_data in test_tasks:
            created_task = self.test_request("POST", "/tasks", task_data, 200, 
                                           f"Create Task - {task_data['title']}", auth_token=self.admin_token)
            if created_task:
                created_tasks.append(created_task)
                self.log(f"✅ Created task: {created_task['id']}")
        
        # Create associated ideas
        test_ideas = [
            {
                "project_id": project_id,
                "title": "Modern Kitchen Design Ideas",
                "description": "Collection of modern kitchen design inspirations",
                "tags": ["kitchen", "modern", "design"]
            },
            {
                "project_id": project_id,
                "title": "Bathroom Tile Patterns",
                "description": "Various tile pattern ideas for bathroom renovation",
                "tags": ["bathroom", "tiles", "patterns"]
            }
        ]
        
        created_ideas = []
        for idea_data in test_ideas:
            created_idea = self.test_request("POST", "/ideas", idea_data, 200, 
                                           f"Create Idea - {idea_data['title']}", auth_token=self.admin_token)
            if created_idea:
                created_ideas.append(created_idea)
                self.log(f"✅ Created idea: {created_idea['id']}")
        
        # 2. Verify project exists and has associated data
        self.log("\n--- 2. Verifying Project and Associated Data Exist ---")
        
        # Verify project exists
        project_check = self.test_request("GET", f"/projects/{project_id}", auth_token=self.admin_token,
                                        test_name="Verify Project Exists Before Deletion")
        if project_check:
            self.log(f"✅ Project exists: {project_check['name']}")
        
        # Verify tasks exist
        tasks_check = self.test_request("GET", f"/tasks?project_id={project_id}", auth_token=self.admin_token,
                                      test_name="Verify Tasks Exist Before Deletion")
        if tasks_check:
            self.log(f"✅ Found {len(tasks_check)} tasks associated with project")
        
        # Verify ideas exist
        ideas_check = self.test_request("GET", f"/ideas?project_id={project_id}", auth_token=self.admin_token,
                                      test_name="Verify Ideas Exist Before Deletion")
        if ideas_check:
            self.log(f"✅ Found {len(ideas_check)} ideas associated with project")
        
        # 3. Test project deletion with admin credentials
        self.log("\n--- 3. Testing Project Deletion with Admin Credentials ---")
        
        delete_response = self.test_request("DELETE", f"/projects/{project_id}", expected_status=200,
                                          auth_token=self.admin_token, test_name="Delete Project (Admin)")
        
        if delete_response:
            self.log("✅ Project deletion successful")
            
            # 4. Verify cascade deletion - project should be gone
            self.log("\n--- 4. Verifying Cascade Deletion ---")
            
            # Verify project is deleted
            self.test_request("GET", f"/projects/{project_id}", expected_status=404,
                            auth_token=self.admin_token, test_name="Verify Project Deleted")
            
            # Verify associated tasks are deleted by checking individual task IDs
            tasks_deleted_successfully = True
            for task in created_tasks:
                # Make direct request to check if task exists
                url = f"{self.base_url}/tasks/{task['id']}"
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = self.session.get(url, headers=headers)
                
                self.log(f"Checking if task {task['id']} was deleted - Status: {response.status_code}")
                
                if response.status_code == 404:
                    self.log(f"✅ Task {task['id']} successfully deleted")
                    self.passed_tests += 1
                else:
                    self.log(f"❌ Task {task['id']} still exists (status: {response.status_code})", "ERROR")
                    tasks_deleted_successfully = False
                    self.failed_tests += 1
            
            if tasks_deleted_successfully:
                self.log("✅ All associated tasks deleted successfully")
            
            # Verify associated ideas are deleted by checking individual idea IDs
            ideas_deleted_successfully = True
            for idea in created_ideas:
                # Make direct request to check if idea exists
                url = f"{self.base_url}/ideas/{idea['id']}"
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = self.session.get(url, headers=headers)
                
                self.log(f"Checking if idea {idea['id']} was deleted - Status: {response.status_code}")
                
                if response.status_code == 404:
                    self.log(f"✅ Idea {idea['id']} successfully deleted")
                    self.passed_tests += 1
                else:
                    self.log(f"❌ Idea {idea['id']} still exists (status: {response.status_code})", "ERROR")
                    ideas_deleted_successfully = False
                    self.failed_tests += 1
            
            if ideas_deleted_successfully:
                self.log("✅ All associated ideas deleted successfully")

    def test_authentication_and_authorization(self):
        """Test authentication and authorization for project deletion"""
        self.log("\n=== Testing Authentication and Authorization ===")
        
        # Create test project for authorization testing
        test_project = {
            "name": "Authorization Test Project",
            "description": "Project for testing authorization",
            "color": "#2196F3"
        }
        
        created_project = self.test_request("POST", "/projects", test_project, 200,
                                          "Create Project for Authorization Test", auth_token=self.admin_token)
        
        if not created_project:
            self.log("❌ Failed to create project for authorization test", "ERROR")
            return
        
        project_id = created_project['id']
        
        # Test customer cannot delete projects (should get 403)
        if self.customer_token:
            self.log("\n--- Testing Customer Access (Should Fail) ---")
            self.test_request("DELETE", f"/projects/{project_id}", expected_status=403,
                            auth_token=self.customer_token, test_name="Customer Delete Project (Should Fail)")
        
        # Test deletion without authentication (should get 401/403)
        self.log("\n--- Testing No Authentication (Should Fail) ---")
        self.test_request("DELETE", f"/projects/{project_id}", expected_status=403,
                        test_name="Delete Project Without Auth (Should Fail)")
        
        # Test super admin can delete projects
        if self.superadmin_token:
            self.log("\n--- Testing Super Admin Access ---")
            delete_response = self.test_request("DELETE", f"/projects/{project_id}", expected_status=200,
                                              auth_token=self.superadmin_token, test_name="Super Admin Delete Project")
            if delete_response:
                self.log("✅ Super admin can delete projects")

    def test_store_isolation(self):
        """Test store isolation for project deletion"""
        self.log("\n=== Testing Store Isolation ===")
        
        if not self.admin_token:
            self.log("❌ Admin token not available for store isolation test", "ERROR")
            return
        
        # Create project in STORE_001
        store1_project = {
            "name": "Store 1 Isolation Test Project",
            "description": "Project for testing store isolation",
            "color": "#4CAF50"
        }
        
        created_project = self.test_request("POST", "/projects", store1_project, 200,
                                          "Create Store 1 Project", auth_token=self.admin_token)
        
        if not created_project:
            self.log("❌ Failed to create store 1 project", "ERROR")
            return
        
        project_id = created_project['id']
        
        # Try to authenticate as store 2 manager
        store2_login = {
            "username": "manager",
            "password": "manager123",
            "store_id": "STORE_002"
        }
        
        store2_response = self.test_request("POST", "/auth/login", store2_login, 200, "Store 2 Manager Login")
        
        if store2_response:
            store2_token = store2_response.get('session_token')
            
            # Store 2 manager should not be able to delete Store 1 project
            self.log("\n--- Testing Cross-Store Access (Should Fail) ---")
            self.test_request("DELETE", f"/projects/{project_id}", expected_status=404,
                            auth_token=store2_token, test_name="Store 2 Manager Delete Store 1 Project (Should Fail)")
        
        # Clean up - delete the project with store 1 admin
        self.test_request("DELETE", f"/projects/{project_id}", expected_status=200,
                        auth_token=self.admin_token, test_name="Cleanup Store 1 Project")

    def test_error_handling(self):
        """Test error handling for project deletion"""
        self.log("\n=== Testing Error Handling ===")
        
        if not self.admin_token:
            self.log("❌ Admin token not available for error handling test", "ERROR")
            return
        
        # Test deletion of non-existent project (should get 404)
        fake_project_id = "non-existent-project-id-12345"
        self.test_request("DELETE", f"/projects/{fake_project_id}", expected_status=404,
                        auth_token=self.admin_token, test_name="Delete Non-Existent Project (Should Get 404)")

    def run_all_tests(self):
        """Run all project deletion tests"""
        self.log("🚀 Starting Project Delete Functionality Testing")
        self.log("=" * 60)
        
        # Authenticate users
        self.authenticate_users()
        
        # Run all test scenarios
        self.test_authentication_and_authorization()
        self.test_project_deletion_functionality()
        self.test_store_isolation()
        self.test_error_handling()
        
        # Print summary
        self.log("\n" + "=" * 60)
        self.log("📊 PROJECT DELETE TESTING SUMMARY")
        self.log("=" * 60)
        self.log(f"✅ Passed Tests: {self.passed_tests}")
        self.log(f"❌ Failed Tests: {self.failed_tests}")
        total_tests = self.passed_tests + self.failed_tests
        if total_tests > 0:
            success_rate = (self.passed_tests / total_tests) * 100
            self.log(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.failed_tests == 0:
            self.log("🎉 ALL PROJECT DELETE TESTS PASSED!")
        else:
            self.log(f"⚠️  {self.failed_tests} tests failed - review issues above")
        
        return self.failed_tests == 0

if __name__ == "__main__":
    tester = ProjectDeleteTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)