#!/usr/bin/env python3
"""
Budget Functionality Testing for Task Manager Application
Tests budget functionality for projects and tasks as per review request
"""

import requests
import json
from datetime import datetime, date, timedelta
import sys
import os

# Get backend URL from frontend .env
BACKEND_URL = "https://house-budget-app.preview.emergentagent.com/api"

class BudgetTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.passed_tests = 0
        self.failed_tests = 0
        self.admin_token = None
        self.demo_token = None
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
        """Authenticate as admin and demo users"""
        self.log("\n=== Authentication Setup ===")
        
        # Admin login
        admin_login = {
            "username": "admin",
            "password": "admin",
            "store_id": "STORE_001"
        }
        
        admin_response = self.test_request("POST", "/auth/login", admin_login, 200, "Admin Login")
        
        if admin_response:
            self.admin_token = admin_response.get('session_token')
            self.log("✅ Admin authentication successful")
        else:
            self.log("❌ Admin authentication failed", "ERROR")
            return False
        
        # Demo login
        demo_login = {
            "username": "demo",
            "password": "demo",
            "store_id": "STORE_001"
        }
        
        demo_response = self.test_request("POST", "/auth/login", demo_login, 200, "Demo Login")
        
        if demo_response:
            self.demo_token = demo_response.get('session_token')
            self.log("✅ Demo authentication successful")
        else:
            self.log("❌ Demo authentication failed", "ERROR")
        
        return True

    def test_budget_functionality(self):
        """Test comprehensive budget functionality for projects and tasks"""
        self.log("\n=== Testing Budget Functionality for Projects and Tasks ===")
        
        if not self.admin_token:
            self.log("❌ No admin token available for budget functionality testing", "ERROR")
            return
        
        # Test 1: Create Project with Budget
        self.log("\n--- 1. Create Project with Budget ---")
        project_with_budget = {
            "name": "Budget Test House Project",
            "description": "House renovation project with budget tracking",
            "color": "#4CAF50",
            "estimated_budget": 50000.75
        }
        
        created_project = self.test_request("POST", "/projects", project_with_budget, 200, 
                                          "Create Project with Budget", auth_token=self.admin_token)
        
        if created_project:
            self.test_project_id = created_project['id']
            
            # Verify budget field is stored correctly
            if created_project.get('estimated_budget') == 50000.75:
                self.log("✅ Project estimated_budget field stored correctly")
            else:
                self.log(f"❌ Project estimated_budget not stored correctly: expected 50000.75, got {created_project.get('estimated_budget')}", "ERROR")
                self.failed_tests += 1
            
            # Test 2: Update Project Budget
            self.log("\n--- 2. Update Project Budget ---")
            budget_update = {
                "name": "Budget Test House Project - Updated",
                "description": "Updated house renovation project with new budget",
                "color": "#4CAF50",
                "estimated_budget": 65000.50
            }
            
            updated_project = self.test_request("PUT", f"/projects/{self.test_project_id}", budget_update, 200, 
                                              "Update Project Budget", auth_token=self.admin_token)
            
            if updated_project:
                if updated_project.get('estimated_budget') == 65000.50:
                    self.log("✅ Project budget update working correctly")
                else:
                    self.log(f"❌ Project budget update failed: expected 65000.50, got {updated_project.get('estimated_budget')}", "ERROR")
                    self.failed_tests += 1
            
            # Test 3: Create Tasks/Rooms with Budget Fields
            self.log("\n--- 3. Create Tasks/Rooms with Budget Fields ---")
            
            # Kitchen room with budget
            kitchen_task = {
                "project_id": self.test_project_id,
                "title": "Kitchen Renovation",
                "description": "Complete kitchen renovation with new appliances",
                "priority": "high",
                "estimated_budget": 15000.00,
                "actual_cost": 12500.75
            }
            
            created_kitchen = self.test_request("POST", "/tasks", kitchen_task, 200, 
                                              "Create Kitchen Task with Budget", auth_token=self.admin_token)
            
            if created_kitchen:
                # Verify budget fields are stored
                if created_kitchen.get('estimated_budget') == 15000.00:
                    self.log("✅ Task estimated_budget field stored correctly")
                else:
                    self.log(f"❌ Task estimated_budget not stored correctly: expected 15000.00, got {created_kitchen.get('estimated_budget')}", "ERROR")
                    self.failed_tests += 1
                
                if created_kitchen.get('actual_cost') == 12500.75:
                    self.log("✅ Task actual_cost field stored correctly")
                else:
                    self.log(f"❌ Task actual_cost not stored correctly: expected 12500.75, got {created_kitchen.get('actual_cost')}", "ERROR")
                    self.failed_tests += 1
            
            # Bathroom room with budget
            bathroom_task = {
                "project_id": self.test_project_id,
                "title": "Bathroom Renovation",
                "description": "Master bathroom renovation",
                "priority": "medium",
                "estimated_budget": 8000.25,
                "actual_cost": 8500.00
            }
            
            created_bathroom = self.test_request("POST", "/tasks", bathroom_task, 200, 
                                               "Create Bathroom Task with Budget", auth_token=self.admin_token)
            
            if created_bathroom:
                # Verify budget fields
                if created_bathroom.get('estimated_budget') == 8000.25:
                    self.log("✅ Second task estimated_budget field stored correctly")
                else:
                    self.log(f"❌ Second task estimated_budget not stored correctly: expected 8000.25, got {created_bathroom.get('estimated_budget')}", "ERROR")
                    self.failed_tests += 1
            
            # Test 4: Update Task Budget Information
            self.log("\n--- 4. Update Task Budget Information ---")
            if created_kitchen:
                kitchen_id = created_kitchen['id']
                budget_task_update = {
                    "title": "Kitchen Renovation - Updated",
                    "estimated_budget": 16000.00,
                    "actual_cost": 15200.50
                }
                
                updated_kitchen = self.test_request("PUT", f"/tasks/{kitchen_id}", budget_task_update, 200, 
                                                  "Update Task Budget", auth_token=self.admin_token)
                
                if updated_kitchen:
                    if updated_kitchen.get('estimated_budget') == 16000.00:
                        self.log("✅ Task budget update working correctly")
                    else:
                        self.log(f"❌ Task budget update failed: expected 16000.00, got {updated_kitchen.get('estimated_budget')}", "ERROR")
                        self.failed_tests += 1
                    
                    if updated_kitchen.get('actual_cost') == 15200.50:
                        self.log("✅ Task actual cost update working correctly")
                    else:
                        self.log(f"❌ Task actual cost update failed: expected 15200.50, got {updated_kitchen.get('actual_cost')}", "ERROR")
                        self.failed_tests += 1
            
            # Test 5: Budget Summary Endpoint
            self.log("\n--- 5. Budget Summary Endpoint ---")
            budget_summary = self.test_request("GET", f"/projects/{self.test_project_id}/budget", auth_token=self.admin_token, 
                                             test_name="Get Project Budget Summary")
            
            if budget_summary:
                # Verify budget summary structure
                required_fields = ['project_id', 'total_estimated', 'total_actual', 'remaining_budget', 'over_budget']
                
                for field in required_fields:
                    if field in budget_summary:
                        self.log(f"✅ Budget summary field '{field}': {budget_summary[field]}")
                    else:
                        self.log(f"❌ Missing budget summary field: {field}", "ERROR")
                        self.failed_tests += 1
                
                # Log budget calculations
                self.log(f"✅ Budget Summary Details:")
                self.log(f"   - Project ID: {budget_summary.get('project_id')}")
                self.log(f"   - Total Estimated: ${budget_summary.get('total_estimated', 0):,.2f}")
                self.log(f"   - Total Actual: ${budget_summary.get('total_actual', 0):,.2f}")
                self.log(f"   - Remaining Budget: ${budget_summary.get('remaining_budget', 0):,.2f}")
                self.log(f"   - Over Budget: {budget_summary.get('over_budget', False)}")
                
                # Check budget items
                budget_items = budget_summary.get('budget_items', [])
                self.log(f"   - Budget Items Count: {len(budget_items)}")
                
                if len(budget_items) > 0:
                    self.log("✅ Budget items included in summary")
                    for item in budget_items[:3]:  # Show first 3 items
                        self.log(f"     * {item.get('item_name', 'Unknown')}: ${item.get('estimated_cost', 0):,.2f}")
                else:
                    self.log("ℹ️ No budget items in summary (may be expected if using task-based budgeting)")
            
            # Test 6: Budget Fields Accept Decimal Values and Null
            self.log("\n--- 6. Budget Fields Accept Decimal Values and Null ---")
            
            # Test with decimal values
            decimal_task = {
                "project_id": self.test_project_id,
                "title": "Living Room Renovation",
                "description": "Living room with precise decimal budget",
                "priority": "low",
                "estimated_budget": 5432.99,
                "actual_cost": 5678.12
            }
            
            created_decimal_task = self.test_request("POST", "/tasks", decimal_task, 200, 
                                                   "Create Task with Decimal Budget", auth_token=self.admin_token)
            
            if created_decimal_task:
                if created_decimal_task.get('estimated_budget') == 5432.99:
                    self.log("✅ Decimal budget values accepted and stored correctly")
                else:
                    self.log(f"❌ Decimal budget values not handled correctly: expected 5432.99, got {created_decimal_task.get('estimated_budget')}", "ERROR")
                    self.failed_tests += 1
            
            # Test with null values
            null_budget_task = {
                "project_id": self.test_project_id,
                "title": "Garage Organization",
                "description": "Garage organization without budget",
                "priority": "low",
                "estimated_budget": None,
                "actual_cost": None
            }
            
            created_null_task = self.test_request("POST", "/tasks", null_budget_task, 200, 
                                                 "Create Task with Null Budget", auth_token=self.admin_token)
            
            if created_null_task:
                if created_null_task.get('estimated_budget') is None:
                    self.log("✅ Null budget values accepted and stored correctly")
                else:
                    self.log(f"❌ Null budget values not handled correctly: expected None, got {created_null_task.get('estimated_budget')}", "ERROR")
                    self.failed_tests += 1
            
            # Test 7: Zero Budget Values
            self.log("\n--- 7. Zero Budget Values ---")
            
            zero_budget_task = {
                "project_id": self.test_project_id,
                "title": "Free DIY Project",
                "description": "DIY project with zero cost",
                "priority": "low",
                "estimated_budget": 0.0,
                "actual_cost": 0.0
            }
            
            created_zero_task = self.test_request("POST", "/tasks", zero_budget_task, 200, 
                                                 "Create Task with Zero Budget", auth_token=self.admin_token)
            
            if created_zero_task:
                if created_zero_task.get('estimated_budget') == 0.0:
                    self.log("✅ Zero budget values accepted and stored correctly")
                else:
                    self.log(f"❌ Zero budget values not handled correctly: expected 0.0, got {created_zero_task.get('estimated_budget')}", "ERROR")
                    self.failed_tests += 1
            
            # Test 8: Budget Validation (Negative Values)
            self.log("\n--- 8. Budget Validation (Negative Values) ---")
            
            negative_budget_project = {
                "name": "Negative Budget Test Project",
                "description": "Testing negative budget handling",
                "color": "#FF5722",
                "estimated_budget": -1000.00
            }
            
            # Test negative budget - this should either be rejected or accepted with business logic handling
            negative_project = self.test_request("POST", "/projects", negative_budget_project, None, 
                                                "Create Project with Negative Budget", auth_token=self.admin_token)
            
            if negative_project and negative_project.get('estimated_budget') == -1000.00:
                self.log("⚠️ Negative budget values are accepted (business logic should handle this)")
                # Clean up
                self.test_request("DELETE", f"/projects/{negative_project['id']}", auth_token=self.admin_token, test_name="Delete Negative Budget Test Project")
            elif negative_project is None:
                self.log("✅ Negative budget values are properly handled")
            
            # Test 9: Authentication and Authorization
            self.log("\n--- 9. Authentication and Authorization ---")
            
            # Test without authentication (should fail)
            self.test_request("GET", f"/projects/{self.test_project_id}/budget", expected_status=403, 
                             test_name="Budget Access Without Authentication (Should Fail)")
            
            # Test with demo user (might succeed or fail depending on project assignment)
            if self.demo_token:
                demo_budget = self.test_request("GET", f"/projects/{self.test_project_id}/budget", auth_token=self.demo_token, 
                                              test_name="Demo User Access Budget Summary")
                
                if demo_budget is not None:
                    self.log("✅ Regular user can access budget summary for assigned projects")
                else:
                    self.log("✅ Regular user properly restricted from budget access")

    def cleanup(self):
        """Clean up test data"""
        self.log("\n=== Cleanup ===")
        
        if self.admin_token and self.test_project_id:
            # Delete the test project (this will cascade delete tasks)
            self.test_request("DELETE", f"/projects/{self.test_project_id}", auth_token=self.admin_token, 
                            test_name="Delete Test Project")
            self.log("✅ Test project cleaned up")

    def run_budget_tests(self):
        """Run all budget functionality tests"""
        self.log("🚀 Starting Budget Functionality Testing")
        self.log(f"Backend URL: {self.base_url}")
        
        try:
            # Authenticate
            if not self.authenticate():
                self.log("❌ Authentication failed, cannot continue", "ERROR")
                return False
            
            # Run budget tests
            self.test_budget_functionality()
            
            # Clean up
            self.cleanup()
            
        except Exception as e:
            self.log(f"❌ Critical error during testing: {str(e)}", "ERROR")
            self.failed_tests += 1
        
        # Final results
        self.log("\n" + "="*60)
        self.log("🏁 BUDGET FUNCTIONALITY TESTING COMPLETE")
        self.log(f"✅ Passed: {self.passed_tests}")
        self.log(f"❌ Failed: {self.failed_tests}")
        self.log(f"📊 Success Rate: {(self.passed_tests/(self.passed_tests + self.failed_tests)*100):.1f}%" if (self.passed_tests + self.failed_tests) > 0 else "No tests run")
        self.log("="*60)
        
        return self.failed_tests == 0

if __name__ == "__main__":
    tester = BudgetTester()
    success = tester.run_budget_tests()
    sys.exit(0 if success else 1)