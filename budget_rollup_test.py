#!/usr/bin/env python3
"""
Budget Rollup Functionality Testing
Tests all budget calculation, rollup, and API endpoints as per review request
"""

import requests
import json
from datetime import datetime, date, timedelta
import sys
import os

# Get backend URL from frontend .env
BACKEND_URL = "https://buildbuddy-2.preview.emergentagent.com/api"

class BudgetRollupTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.passed_tests = 0
        self.failed_tests = 0
        self.admin_token = None
        self.superadmin_token = None
        self.customer_token = None
        self.test_data = {
            'projects': [],
            'rooms': [],
            'subtasks': []
        }
        
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
        """Authenticate all required users for testing"""
        self.log("\n=== Authenticating Test Users ===")
        
        # Admin: Store ID: STORE_001, username: admin, password: admin
        admin_login = {
            "username": "admin",
            "password": "admin",
            "store_id": "STORE_001"
        }
        
        admin_response = self.test_request("POST", "/auth/login", admin_login, 200, "Admin Authentication")
        if admin_response:
            self.admin_token = admin_response.get('session_token')
            self.log("✅ Admin authenticated successfully")
        
        # Super Admin: Store ID: GLOBAL, username: superadmin, password: superadmin123
        superadmin_login = {
            "username": "superadmin",
            "password": "superadmin123",
            "store_id": "GLOBAL"
        }
        
        superadmin_response = self.test_request("POST", "/auth/login", superadmin_login, 200, "Super Admin Authentication")
        if superadmin_response:
            self.superadmin_token = superadmin_response.get('session_token')
            self.log("✅ Super Admin authenticated successfully")
        
        # Customer: demo user for access control testing
        customer_login = {
            "username": "demo",
            "password": "demo",
            "store_id": "STORE_001"
        }
        
        customer_response = self.test_request("POST", "/auth/login", customer_login, 200, "Customer Authentication")
        if customer_response:
            self.customer_token = customer_response.get('session_token')
            self.log("✅ Customer authenticated successfully")

    def test_budget_calculation_accuracy(self):
        """Test budget calculation accuracy: subtask totals → room totals → project totals"""
        self.log("\n=== Testing Budget Calculation Accuracy ===")
        
        if not self.admin_token:
            self.log("❌ No admin token available", "ERROR")
            return
        
        # 1. Create project with estimated_budget: $50,000
        project_data = {
            "name": "Budget Test House Renovation",
            "description": "Testing budget rollup calculations",
            "color": "#4CAF50",
            "estimated_budget": 50000.00
        }
        
        project = self.test_request("POST", "/projects", project_data, 200, 
                                  "Create Project with $50,000 Budget", auth_token=self.admin_token)
        
        if not project:
            self.log("❌ Failed to create test project", "ERROR")
            return
        
        self.test_data['projects'].append(project)
        project_id = project['id']
        self.log(f"✅ Created project with estimated budget: ${project_data['estimated_budget']:,.2f}")
        
        # 2. Create room with estimated_budget: $10,000, actual_cost: $8,500
        room_data = {
            "project_id": project_id,
            "title": "Master Kitchen",
            "description": "Main kitchen renovation",
            "priority": "high",
            "subtask_level": 0,
            "estimated_budget": 10000.00,
            "actual_cost": 8500.00
        }
        
        room = self.test_request("POST", "/tasks", room_data, 200,
                               "Create Room with $10,000 Budget", auth_token=self.admin_token)
        
        if not room:
            self.log("❌ Failed to create test room", "ERROR")
            return
        
        self.test_data['rooms'].append(room)
        room_id = room['id']
        self.log(f"✅ Created room - Estimated: ${room_data['estimated_budget']:,.2f}, Actual: ${room_data['actual_cost']:,.2f}")
        
        # 3. Create subtasks with various estimated_budget and actual_cost values
        subtasks_data = [
            {
                "project_id": project_id,
                "parent_task_id": room_id,
                "title": "Kitchen Cabinets",
                "description": "Install kitchen cabinets",
                "priority": "high",
                "subtask_level": 1,
                "estimated_budget": 3500.00,
                "actual_cost": 3200.00
            },
            {
                "project_id": project_id,
                "parent_task_id": room_id,
                "title": "Kitchen Countertops",
                "description": "Install granite countertops",
                "priority": "high",
                "subtask_level": 1,
                "estimated_budget": 2500.00,
                "actual_cost": 2800.00
            },
            {
                "project_id": project_id,
                "parent_task_id": room_id,
                "title": "Kitchen Appliances",
                "description": "Install kitchen appliances",
                "priority": "medium",
                "subtask_level": 1,
                "estimated_budget": 4000.00,
                "actual_cost": 3750.00
            }
        ]
        
        subtask_estimated_total = 0
        subtask_actual_total = 0
        
        for subtask_data in subtasks_data:
            subtask = self.test_request("POST", "/tasks", subtask_data, 200,
                                      f"Create Subtask: {subtask_data['title']}", auth_token=self.admin_token)
            
            if subtask:
                self.test_data['subtasks'].append(subtask)
                subtask_estimated_total += subtask_data['estimated_budget']
                subtask_actual_total += subtask_data['actual_cost']
                self.log(f"✅ Created subtask - Estimated: ${subtask_data['estimated_budget']:,.2f}, Actual: ${subtask_data['actual_cost']:,.2f}")
        
        # 4. Verify calculations roll up correctly
        self.log("\n--- Verifying Budget Rollup Calculations ---")
        
        # Expected totals
        expected_subtask_estimated = subtask_estimated_total  # $10,000
        expected_subtask_actual = subtask_actual_total        # $9,750
        expected_room_total_estimated = room_data['estimated_budget'] + expected_subtask_estimated  # $20,000
        expected_room_total_actual = room_data['actual_cost'] + expected_subtask_actual            # $18,250
        expected_project_total_estimated = project_data['estimated_budget'] + expected_room_total_estimated  # $70,000
        expected_project_total_actual = expected_room_total_actual  # $18,250
        expected_project_variance = expected_project_total_actual - expected_project_total_estimated  # -$51,750
        
        self.log(f"Expected Subtask Totals - Estimated: ${expected_subtask_estimated:,.2f}, Actual: ${expected_subtask_actual:,.2f}")
        self.log(f"Expected Room Totals - Estimated: ${expected_room_total_estimated:,.2f}, Actual: ${expected_room_total_actual:,.2f}")
        self.log(f"Expected Project Totals - Estimated: ${expected_project_total_estimated:,.2f}, Actual: ${expected_project_total_actual:,.2f}")
        self.log(f"Expected Project Variance: ${expected_project_variance:,.2f}")
        
        return {
            'project_id': project_id,
            'room_id': room_id,
            'expected_subtask_estimated': expected_subtask_estimated,
            'expected_subtask_actual': expected_subtask_actual,
            'expected_room_total_estimated': expected_room_total_estimated,
            'expected_room_total_actual': expected_room_total_actual,
            'expected_project_total_estimated': expected_project_total_estimated,
            'expected_project_total_actual': expected_project_total_actual,
            'expected_project_variance': expected_project_variance
        }

    def test_project_budget_summary_endpoint(self, test_data):
        """Test GET /api/projects/{project_id}/budget-summary endpoint"""
        self.log("\n=== Testing Project Budget Summary Endpoint ===")
        
        if not self.admin_token or not test_data:
            self.log("❌ Missing admin token or test data", "ERROR")
            return
        
        project_id = test_data['project_id']
        
        # Test GET /api/projects/{project_id}/budget-summary
        budget_summary = self.test_request("GET", f"/projects/{project_id}/budget-summary", 
                                         auth_token=self.admin_token,
                                         test_name="Get Project Budget Summary")
        
        if not budget_summary:
            self.log("❌ Failed to get project budget summary", "ERROR")
            return
        
        # Verify response includes required fields
        required_fields = [
            'project_own_estimated_budget',
            'project_estimated_total', 
            'project_actual_total',
            'total_estimated_with_project',
            'budget_variance',
            'room_breakdown'
        ]
        
        for field in required_fields:
            if field in budget_summary:
                self.log(f"✅ Budget summary includes {field}: {budget_summary[field]}")
            else:
                self.log(f"❌ Budget summary missing field: {field}", "ERROR")
                self.failed_tests += 1
        
        # Verify calculations are correct
        if 'project_own_estimated_budget' in budget_summary:
            if budget_summary['project_own_estimated_budget'] == 50000.00:
                self.log("✅ Project own estimated budget correct: $50,000.00")
            else:
                self.log(f"❌ Project own estimated budget incorrect: expected $50,000.00, got ${budget_summary['project_own_estimated_budget']:,.2f}", "ERROR")
                self.failed_tests += 1
        
        if 'total_estimated_with_project' in budget_summary:
            expected_total = test_data['expected_project_total_estimated']
            actual_total = budget_summary['total_estimated_with_project']
            if abs(actual_total - expected_total) < 0.01:  # Allow for floating point precision
                self.log(f"✅ Total estimated with project correct: ${actual_total:,.2f}")
            else:
                self.log(f"❌ Total estimated with project incorrect: expected ${expected_total:,.2f}, got ${actual_total:,.2f}", "ERROR")
                self.failed_tests += 1
        
        if 'budget_variance' in budget_summary:
            expected_variance = test_data['expected_project_variance']
            actual_variance = budget_summary['budget_variance']
            if abs(actual_variance - expected_variance) < 0.01:
                self.log(f"✅ Budget variance correct: ${actual_variance:,.2f}")
            else:
                self.log(f"❌ Budget variance incorrect: expected ${expected_variance:,.2f}, got ${actual_variance:,.2f}", "ERROR")
                self.failed_tests += 1
        
        # Verify room_breakdown array
        if 'room_breakdown' in budget_summary:
            room_breakdown = budget_summary['room_breakdown']
            if isinstance(room_breakdown, list) and len(room_breakdown) > 0:
                self.log(f"✅ Room breakdown array contains {len(room_breakdown)} rooms")
                
                # Check first room details
                room = room_breakdown[0]
                room_required_fields = ['room_id', 'room_title', 'room_estimated_budget', 
                                      'room_actual_cost', 'subtask_estimated_total', 
                                      'subtask_actual_total', 'total_estimated', 'total_actual']
                
                for field in room_required_fields:
                    if field in room:
                        self.log(f"✅ Room breakdown includes {field}: {room[field]}")
                    else:
                        self.log(f"❌ Room breakdown missing field: {field}", "ERROR")
                        self.failed_tests += 1
            else:
                self.log("❌ Room breakdown is not a valid array or is empty", "ERROR")
                self.failed_tests += 1
        
        return budget_summary

    def test_task_budget_summary_endpoint(self, test_data):
        """Test GET /api/tasks/{task_id}/budget-summary for main rooms"""
        self.log("\n=== Testing Task/Room Budget Summary Endpoint ===")
        
        if not self.admin_token or not test_data:
            self.log("❌ Missing admin token or test data", "ERROR")
            return
        
        room_id = test_data['room_id']
        
        # Test GET /api/tasks/{task_id}/budget-summary for main room (subtask_level = 0)
        room_budget_summary = self.test_request("GET", f"/tasks/{room_id}/budget-summary",
                                               auth_token=self.admin_token,
                                               test_name="Get Room Budget Summary")
        
        if not room_budget_summary:
            self.log("❌ Failed to get room budget summary", "ERROR")
            return
        
        # Verify response includes required fields
        required_fields = [
            'task_estimated_budget',
            'task_actual_cost',
            'subtask_estimated_total',
            'subtask_actual_total',
            'total_estimated',
            'total_actual',
            'subtask_breakdown'
        ]
        
        for field in required_fields:
            if field in room_budget_summary:
                self.log(f"✅ Room budget summary includes {field}: {room_budget_summary[field]}")
            else:
                self.log(f"❌ Room budget summary missing field: {field}", "ERROR")
                self.failed_tests += 1
        
        # Verify calculations
        if 'subtask_estimated_total' in room_budget_summary:
            expected_subtask_estimated = test_data['expected_subtask_estimated']
            actual_subtask_estimated = room_budget_summary['subtask_estimated_total']
            if abs(actual_subtask_estimated - expected_subtask_estimated) < 0.01:
                self.log(f"✅ Subtask estimated total correct: ${actual_subtask_estimated:,.2f}")
            else:
                self.log(f"❌ Subtask estimated total incorrect: expected ${expected_subtask_estimated:,.2f}, got ${actual_subtask_estimated:,.2f}", "ERROR")
                self.failed_tests += 1
        
        if 'total_estimated' in room_budget_summary:
            expected_room_total_estimated = test_data['expected_room_total_estimated']
            actual_room_total_estimated = room_budget_summary['total_estimated']
            if abs(actual_room_total_estimated - expected_room_total_estimated) < 0.01:
                self.log(f"✅ Room total estimated correct: ${actual_room_total_estimated:,.2f}")
            else:
                self.log(f"❌ Room total estimated incorrect: expected ${expected_room_total_estimated:,.2f}, got ${actual_room_total_estimated:,.2f}", "ERROR")
                self.failed_tests += 1
        
        # Verify subtask_breakdown array
        if 'subtask_breakdown' in room_budget_summary:
            subtask_breakdown = room_budget_summary['subtask_breakdown']
            if isinstance(subtask_breakdown, list) and len(subtask_breakdown) > 0:
                self.log(f"✅ Subtask breakdown array contains {len(subtask_breakdown)} subtasks")
                
                # Check first subtask details
                subtask = subtask_breakdown[0]
                subtask_required_fields = ['subtask_id', 'subtask_title', 'estimated_budget', 'actual_cost']
                
                for field in subtask_required_fields:
                    if field in subtask:
                        self.log(f"✅ Subtask breakdown includes {field}: {subtask[field]}")
                    else:
                        self.log(f"❌ Subtask breakdown missing field: {field}", "ERROR")
                        self.failed_tests += 1
            else:
                self.log("❌ Subtask breakdown is not a valid array or is empty", "ERROR")
                self.failed_tests += 1
        
        return room_budget_summary

    def test_enhanced_projects_endpoint(self, test_data):
        """Test GET /api/projects endpoint with calculated budget fields"""
        self.log("\n=== Testing Enhanced Projects Endpoint ===")
        
        if not self.admin_token:
            self.log("❌ No admin token available", "ERROR")
            return
        
        # Test GET /api/projects endpoint
        projects = self.test_request("GET", "/projects", auth_token=self.admin_token,
                                   test_name="Get Projects with Calculated Budget Fields")
        
        if not projects:
            self.log("❌ Failed to get projects", "ERROR")
            return
        
        # Find our test project
        test_project = None
        for project in projects:
            if project['id'] == test_data['project_id']:
                test_project = project
                break
        
        if not test_project:
            self.log("❌ Test project not found in projects list", "ERROR")
            return
        
        # Verify each project includes calculated budget fields
        required_budget_fields = [
            'calculated_estimated_total',
            'calculated_actual_total',
            'total_estimated_with_project',
            'budget_variance'
        ]
        
        for field in required_budget_fields:
            if field in test_project:
                self.log(f"✅ Project includes {field}: {test_project[field]}")
            else:
                self.log(f"❌ Project missing calculated budget field: {field}", "ERROR")
                self.failed_tests += 1
        
        # Verify calculations are correct
        if 'total_estimated_with_project' in test_project:
            expected_total = test_data['expected_project_total_estimated']
            actual_total = test_project['total_estimated_with_project']
            if abs(actual_total - expected_total) < 0.01:
                self.log(f"✅ Project total estimated with project correct: ${actual_total:,.2f}")
            else:
                self.log(f"❌ Project total estimated incorrect: expected ${expected_total:,.2f}, got ${actual_total:,.2f}", "ERROR")
                self.failed_tests += 1
        
        if 'budget_variance' in test_project:
            expected_variance = test_data['expected_project_variance']
            actual_variance = test_project['budget_variance']
            if abs(actual_variance - expected_variance) < 0.01:
                self.log(f"✅ Project budget variance correct: ${actual_variance:,.2f}")
            else:
                self.log(f"❌ Project budget variance incorrect: expected ${expected_variance:,.2f}, got ${actual_variance:,.2f}", "ERROR")
                self.failed_tests += 1
        
        return test_project

    def test_enhanced_tasks_endpoint(self, test_data):
        """Test GET /api/tasks endpoint for rooms with calculated budget fields"""
        self.log("\n=== Testing Enhanced Tasks Endpoint ===")
        
        if not self.admin_token:
            self.log("❌ No admin token available", "ERROR")
            return
        
        # Test GET /api/tasks endpoint for rooms (subtask_level = 0)
        tasks = self.test_request("GET", "/tasks", auth_token=self.admin_token,
                                test_name="Get Tasks with Calculated Budget Fields")
        
        if not tasks:
            self.log("❌ Failed to get tasks", "ERROR")
            return
        
        # Find our test room
        test_room = None
        for task in tasks:
            if task['id'] == test_data['room_id'] and task.get('subtask_level') == 0:
                test_room = task
                break
        
        if not test_room:
            self.log("❌ Test room not found in tasks list", "ERROR")
            return
        
        # Verify room includes calculated budget fields
        required_budget_fields = [
            'subtask_estimated_total',
            'subtask_actual_total',
            'total_estimated',
            'total_actual',
            'budget_variance'
        ]
        
        for field in required_budget_fields:
            if field in test_room:
                self.log(f"✅ Room includes {field}: {test_room[field]}")
            else:
                self.log(f"❌ Room missing calculated budget field: {field}", "ERROR")
                self.failed_tests += 1
        
        # Verify calculations are correct
        if 'subtask_estimated_total' in test_room:
            expected_subtask_estimated = test_data['expected_subtask_estimated']
            actual_subtask_estimated = test_room['subtask_estimated_total']
            if abs(actual_subtask_estimated - expected_subtask_estimated) < 0.01:
                self.log(f"✅ Room subtask estimated total correct: ${actual_subtask_estimated:,.2f}")
            else:
                self.log(f"❌ Room subtask estimated total incorrect: expected ${expected_subtask_estimated:,.2f}, got ${actual_subtask_estimated:,.2f}", "ERROR")
                self.failed_tests += 1
        
        if 'total_estimated' in test_room:
            expected_room_total_estimated = test_data['expected_room_total_estimated']
            actual_room_total_estimated = test_room['total_estimated']
            if abs(actual_room_total_estimated - expected_room_total_estimated) < 0.01:
                self.log(f"✅ Room total estimated correct: ${actual_room_total_estimated:,.2f}")
            else:
                self.log(f"❌ Room total estimated incorrect: expected ${expected_room_total_estimated:,.2f}, got ${actual_room_total_estimated:,.2f}", "ERROR")
                self.failed_tests += 1
        
        return test_room

    def test_budget_hierarchy(self):
        """Test budget calculations cascade correctly through hierarchy"""
        self.log("\n=== Testing Budget Hierarchy ===")
        
        if not self.admin_token:
            self.log("❌ No admin token available", "ERROR")
            return
        
        # Create complex structure: Project → Multiple Rooms → Multiple Subtasks per room
        project_data = {
            "name": "Complex Budget Hierarchy Test",
            "description": "Testing complex budget hierarchy calculations",
            "color": "#FF9800",
            "estimated_budget": 100000.00
        }
        
        project = self.test_request("POST", "/projects", project_data, 200,
                                  "Create Complex Hierarchy Project", auth_token=self.admin_token)
        
        if not project:
            self.log("❌ Failed to create hierarchy test project", "ERROR")
            return
        
        project_id = project['id']
        
        # Create multiple rooms with different budget scenarios
        rooms_data = [
            {
                "project_id": project_id,
                "title": "Living Room",
                "description": "Living room renovation",
                "priority": "high",
                "subtask_level": 0,
                "estimated_budget": 15000.00,
                "actual_cost": 14500.00
            },
            {
                "project_id": project_id,
                "title": "Master Bedroom",
                "description": "Master bedroom renovation",
                "priority": "medium",
                "subtask_level": 0,
                "estimated_budget": None,  # Room with no budget
                "actual_cost": None
            },
            {
                "project_id": project_id,
                "title": "Guest Bathroom",
                "description": "Guest bathroom renovation",
                "priority": "low",
                "subtask_level": 0,
                "estimated_budget": 8000.00,
                "actual_cost": 8750.00
            }
        ]
        
        created_rooms = []
        for room_data in rooms_data:
            room = self.test_request("POST", "/tasks", room_data, 200,
                                   f"Create Room: {room_data['title']}", auth_token=self.admin_token)
            if room:
                created_rooms.append(room)
        
        # Create subtasks for each room with mixed scenarios
        total_expected_estimated = 0
        total_expected_actual = 0
        
        for i, room in enumerate(created_rooms):
            room_id = room['id']
            room_title = room['title']
            
            # Different subtask scenarios for each room
            if i == 0:  # Living Room - all subtasks have budgets
                subtasks_data = [
                    {
                        "project_id": project_id,
                        "parent_task_id": room_id,
                        "title": f"{room_title} Flooring",
                        "description": "Install flooring",
                        "priority": "high",
                        "subtask_level": 1,
                        "estimated_budget": 5000.00,
                        "actual_cost": 4800.00
                    },
                    {
                        "project_id": project_id,
                        "parent_task_id": room_id,
                        "title": f"{room_title} Painting",
                        "description": "Paint walls and ceiling",
                        "priority": "medium",
                        "subtask_level": 1,
                        "estimated_budget": 2000.00,
                        "actual_cost": 2100.00
                    }
                ]
            elif i == 1:  # Master Bedroom - some subtasks without costs
                subtasks_data = [
                    {
                        "project_id": project_id,
                        "parent_task_id": room_id,
                        "title": f"{room_title} Closet",
                        "description": "Install closet system",
                        "priority": "medium",
                        "subtask_level": 1,
                        "estimated_budget": 3000.00,
                        "actual_cost": None
                    },
                    {
                        "project_id": project_id,
                        "parent_task_id": room_id,
                        "title": f"{room_title} Lighting",
                        "description": "Install lighting fixtures",
                        "priority": "low",
                        "subtask_level": 1,
                        "estimated_budget": None,
                        "actual_cost": 1200.00
                    }
                ]
            else:  # Guest Bathroom - zero values
                subtasks_data = [
                    {
                        "project_id": project_id,
                        "parent_task_id": room_id,
                        "title": f"{room_title} Fixtures",
                        "description": "Install bathroom fixtures",
                        "priority": "high",
                        "subtask_level": 1,
                        "estimated_budget": 0.00,
                        "actual_cost": 0.00
                    }
                ]
            
            # Create subtasks
            for subtask_data in subtasks_data:
                subtask = self.test_request("POST", "/tasks", subtask_data, 200,
                                          f"Create Subtask: {subtask_data['title']}", auth_token=self.admin_token)
                if subtask:
                    if subtask_data.get('estimated_budget'):
                        total_expected_estimated += subtask_data['estimated_budget']
                    if subtask_data.get('actual_cost'):
                        total_expected_actual += subtask_data['actual_cost']
        
        # Add room budgets to totals
        for room_data in rooms_data:
            if room_data.get('estimated_budget'):
                total_expected_estimated += room_data['estimated_budget']
            if room_data.get('actual_cost'):
                total_expected_actual += room_data['actual_cost']
        
        self.log(f"Expected hierarchy totals - Estimated: ${total_expected_estimated:,.2f}, Actual: ${total_expected_actual:,.2f}")
        
        # Test project budget summary to verify hierarchy calculations
        budget_summary = self.test_request("GET", f"/projects/{project_id}/budget-summary",
                                         auth_token=self.admin_token,
                                         test_name="Get Complex Hierarchy Budget Summary")
        
        if budget_summary:
            project_estimated = budget_summary.get('project_estimated_total', 0)
            project_actual = budget_summary.get('project_actual_total', 0)
            
            if abs(project_estimated - total_expected_estimated) < 0.01:
                self.log(f"✅ Complex hierarchy estimated total correct: ${project_estimated:,.2f}")
            else:
                self.log(f"❌ Complex hierarchy estimated total incorrect: expected ${total_expected_estimated:,.2f}, got ${project_estimated:,.2f}", "ERROR")
                self.failed_tests += 1
            
            if abs(project_actual - total_expected_actual) < 0.01:
                self.log(f"✅ Complex hierarchy actual total correct: ${project_actual:,.2f}")
            else:
                self.log(f"❌ Complex hierarchy actual total incorrect: expected ${total_expected_actual:,.2f}, got ${project_actual:,.2f}", "ERROR")
                self.failed_tests += 1
        
        return project_id

    def test_zero_null_value_handling(self):
        """Test zero and null value handling in budget calculations"""
        self.log("\n=== Testing Zero and Null Value Handling ===")
        
        if not self.admin_token:
            self.log("❌ No admin token available", "ERROR")
            return
        
        # Create project with null budget
        project_data = {
            "name": "Null Budget Test Project",
            "description": "Testing null budget handling",
            "color": "#9C27B0",
            "estimated_budget": None
        }
        
        project = self.test_request("POST", "/projects", project_data, 200,
                                  "Create Project with Null Budget", auth_token=self.admin_token)
        
        if not project:
            self.log("❌ Failed to create null budget project", "ERROR")
            return
        
        project_id = project['id']
        
        # Create room with zero budget values
        room_data = {
            "project_id": project_id,
            "title": "Zero Budget Room",
            "description": "Room with zero budget values",
            "priority": "medium",
            "subtask_level": 0,
            "estimated_budget": 0.00,
            "actual_cost": 0.00
        }
        
        room = self.test_request("POST", "/tasks", room_data, 200,
                               "Create Room with Zero Budget", auth_token=self.admin_token)
        
        if not room:
            self.log("❌ Failed to create zero budget room", "ERROR")
            return
        
        room_id = room['id']
        
        # Create subtasks with mixed null/zero/non-null values
        subtasks_data = [
            {
                "project_id": project_id,
                "parent_task_id": room_id,
                "title": "Null Budget Subtask",
                "description": "Subtask with null budget values",
                "priority": "low",
                "subtask_level": 1,
                "estimated_budget": None,
                "actual_cost": None
            },
            {
                "project_id": project_id,
                "parent_task_id": room_id,
                "title": "Zero Budget Subtask",
                "description": "Subtask with zero budget values",
                "priority": "low",
                "subtask_level": 1,
                "estimated_budget": 0.00,
                "actual_cost": 0.00
            },
            {
                "project_id": project_id,
                "parent_task_id": room_id,
                "title": "Mixed Values Subtask",
                "description": "Subtask with mixed null and value",
                "priority": "low",
                "subtask_level": 1,
                "estimated_budget": 1000.00,
                "actual_cost": None
            }
        ]
        
        for subtask_data in subtasks_data:
            subtask = self.test_request("POST", "/tasks", subtask_data, 200,
                                      f"Create Subtask: {subtask_data['title']}", auth_token=self.admin_token)
            if subtask:
                self.log(f"✅ Created subtask with mixed null/zero values")
        
        # Test budget calculations handle null/zero values correctly
        budget_summary = self.test_request("GET", f"/projects/{project_id}/budget-summary",
                                         auth_token=self.admin_token,
                                         test_name="Get Null/Zero Budget Summary")
        
        if budget_summary:
            # Should handle null/zero values gracefully
            project_own_estimated = budget_summary.get('project_own_estimated_budget', 0)
            project_estimated_total = budget_summary.get('project_estimated_total', 0)
            project_actual_total = budget_summary.get('project_actual_total', 0)
            
            self.log(f"✅ Null/Zero handling - Project own estimated: ${project_own_estimated}")
            self.log(f"✅ Null/Zero handling - Project estimated total: ${project_estimated_total:,.2f}")
            self.log(f"✅ Null/Zero handling - Project actual total: ${project_actual_total:,.2f}")
            
            # Expected: only the $1000 estimated budget from mixed values subtask
            if abs(project_estimated_total - 1000.00) < 0.01:
                self.log("✅ Null/Zero value handling correct for estimated totals")
            else:
                self.log(f"❌ Null/Zero value handling incorrect: expected $1,000.00, got ${project_estimated_total:,.2f}", "ERROR")
                self.failed_tests += 1
            
            # Expected: $0 actual (all actual costs are null or zero)
            if abs(project_actual_total - 0.00) < 0.01:
                self.log("✅ Null/Zero value handling correct for actual totals")
            else:
                self.log(f"❌ Null/Zero value handling incorrect: expected $0.00, got ${project_actual_total:,.2f}", "ERROR")
                self.failed_tests += 1

    def test_access_control(self):
        """Test access control for budget endpoints"""
        self.log("\n=== Testing Access Control ===")
        
        if not self.admin_token or not self.superadmin_token or not self.customer_token:
            self.log("❌ Missing required tokens for access control testing", "ERROR")
            return
        
        # Use existing test project if available
        if not self.test_data['projects']:
            self.log("❌ No test projects available for access control testing", "ERROR")
            return
        
        project_id = self.test_data['projects'][0]['id']
        room_id = self.test_data['rooms'][0]['id'] if self.test_data['rooms'] else None
        
        # Test customer access to budget summaries (should be restricted based on project assignment)
        self.log("\n--- Testing Customer Access Control ---")
        
        # Customer should be able to access budget summaries for assigned projects
        customer_project_summary = self.test_request("GET", f"/projects/{project_id}/budget-summary",
                                                    auth_token=self.customer_token,
                                                    test_name="Customer Access Project Budget Summary")
        
        if customer_project_summary:
            self.log("✅ Customer can access budget summary for assigned project")
        else:
            self.log("ℹ️ Customer cannot access project budget summary (may not be assigned)")
        
        if room_id:
            customer_room_summary = self.test_request("GET", f"/tasks/{room_id}/budget-summary",
                                                     auth_token=self.customer_token,
                                                     test_name="Customer Access Room Budget Summary")
            
            if customer_room_summary:
                self.log("✅ Customer can access room budget summary for assigned project")
            else:
                self.log("ℹ️ Customer cannot access room budget summary (may not be assigned)")
        
        # Test admin access (should have access to their store projects)
        self.log("\n--- Testing Admin Access Control ---")
        
        admin_project_summary = self.test_request("GET", f"/projects/{project_id}/budget-summary",
                                                 auth_token=self.admin_token,
                                                 test_name="Admin Access Project Budget Summary")
        
        if admin_project_summary:
            self.log("✅ Admin can access project budget summary for their store")
        
        if room_id:
            admin_room_summary = self.test_request("GET", f"/tasks/{room_id}/budget-summary",
                                                  auth_token=self.admin_token,
                                                  test_name="Admin Access Room Budget Summary")
            
            if admin_room_summary:
                self.log("✅ Admin can access room budget summary for their store")
        
        # Test super admin access (should have access to all budget summaries)
        self.log("\n--- Testing Super Admin Access Control ---")
        
        superadmin_project_summary = self.test_request("GET", f"/projects/{project_id}/budget-summary",
                                                      auth_token=self.superadmin_token,
                                                      test_name="Super Admin Access Project Budget Summary")
        
        if superadmin_project_summary:
            self.log("✅ Super admin can access all project budget summaries")
        
        if room_id:
            superadmin_room_summary = self.test_request("GET", f"/tasks/{room_id}/budget-summary",
                                                       auth_token=self.superadmin_token,
                                                       test_name="Super Admin Access Room Budget Summary")
            
            if superadmin_room_summary:
                self.log("✅ Super admin can access all room budget summaries")
        
        # Test unauthorized access (no token)
        self.log("\n--- Testing Unauthorized Access ---")
        
        self.test_request("GET", f"/projects/{project_id}/budget-summary",
                         expected_status=403,
                         test_name="Unauthorized Access Project Budget Summary")
        
        if room_id:
            self.test_request("GET", f"/tasks/{room_id}/budget-summary",
                             expected_status=403,
                             test_name="Unauthorized Access Room Budget Summary")

    def test_performance(self):
        """Test performance with projects containing many rooms and subtasks"""
        self.log("\n=== Testing Performance ===")
        
        if not self.admin_token:
            self.log("❌ No admin token available", "ERROR")
            return
        
        # Create project with many rooms and subtasks
        project_data = {
            "name": "Performance Test Project",
            "description": "Testing performance with many rooms and subtasks",
            "color": "#607D8B",
            "estimated_budget": 500000.00
        }
        
        project = self.test_request("POST", "/projects", project_data, 200,
                                  "Create Performance Test Project", auth_token=self.admin_token)
        
        if not project:
            self.log("❌ Failed to create performance test project", "ERROR")
            return
        
        project_id = project['id']
        
        # Create 10 rooms
        room_ids = []
        for i in range(10):
            room_data = {
                "project_id": project_id,
                "title": f"Performance Room {i+1}",
                "description": f"Performance test room {i+1}",
                "priority": "medium",
                "subtask_level": 0,
                "estimated_budget": 10000.00,
                "actual_cost": 9500.00
            }
            
            room = self.test_request("POST", "/tasks", room_data, 200,
                                   f"Create Performance Room {i+1}", auth_token=self.admin_token)
            if room:
                room_ids.append(room['id'])
        
        # Create 5 subtasks per room (50 total subtasks)
        for room_id in room_ids:
            for j in range(5):
                subtask_data = {
                    "project_id": project_id,
                    "parent_task_id": room_id,
                    "title": f"Performance Subtask {j+1}",
                    "description": f"Performance test subtask {j+1}",
                    "priority": "low",
                    "subtask_level": 1,
                    "estimated_budget": 1000.00,
                    "actual_cost": 950.00
                }
                
                self.test_request("POST", "/tasks", subtask_data, 200,
                                f"Create Performance Subtask", auth_token=self.admin_token)
        
        # Test performance of budget calculations
        import time
        
        start_time = time.time()
        budget_summary = self.test_request("GET", f"/projects/{project_id}/budget-summary",
                                         auth_token=self.admin_token,
                                         test_name="Performance Test Project Budget Summary")
        end_time = time.time()
        
        response_time = end_time - start_time
        self.log(f"✅ Project budget summary response time: {response_time:.3f} seconds")
        
        if response_time < 5.0:  # Should respond within 5 seconds
            self.log("✅ Performance test passed - response time acceptable")
        else:
            self.log(f"❌ Performance test failed - response time too slow: {response_time:.3f}s", "ERROR")
            self.failed_tests += 1
        
        if budget_summary:
            # Verify calculations are still accurate with large dataset
            expected_room_total = 10 * 10000.00  # 10 rooms * $10,000 each
            expected_subtask_total = 50 * 1000.00  # 50 subtasks * $1,000 each
            expected_total_estimated = expected_room_total + expected_subtask_total  # $150,000
            
            project_estimated_total = budget_summary.get('project_estimated_total', 0)
            
            if abs(project_estimated_total - expected_total_estimated) < 0.01:
                self.log(f"✅ Performance test calculations accurate: ${project_estimated_total:,.2f}")
            else:
                self.log(f"❌ Performance test calculations incorrect: expected ${expected_total_estimated:,.2f}, got ${project_estimated_total:,.2f}", "ERROR")
                self.failed_tests += 1

    def run_all_tests(self):
        """Run all budget rollup functionality tests"""
        self.log("🚀 Starting Budget Rollup Functionality Testing")
        self.log("=" * 60)
        
        # Authenticate users
        self.authenticate_users()
        
        if not self.admin_token:
            self.log("❌ Cannot proceed without admin authentication", "ERROR")
            return
        
        # 1. Test budget calculation accuracy
        test_data = self.test_budget_calculation_accuracy()
        
        if test_data:
            # 2. Test project budget summary endpoint
            self.test_project_budget_summary_endpoint(test_data)
            
            # 3. Test task/room budget summary endpoint
            self.test_task_budget_summary_endpoint(test_data)
            
            # 4. Test enhanced projects endpoint
            self.test_enhanced_projects_endpoint(test_data)
            
            # 5. Test enhanced tasks endpoint
            self.test_enhanced_tasks_endpoint(test_data)
        
        # 6. Test budget hierarchy
        self.test_budget_hierarchy()
        
        # 7. Test zero and null value handling
        self.test_zero_null_value_handling()
        
        # 8. Test access control
        self.test_access_control()
        
        # 9. Test performance
        self.test_performance()
        
        # Print final results
        self.print_final_results()

    def print_final_results(self):
        """Print final test results"""
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.log("\n" + "=" * 60)
        self.log("🏁 BUDGET ROLLUP FUNCTIONALITY TESTING COMPLETE")
        self.log("=" * 60)
        self.log(f"✅ PASSED: {self.passed_tests}")
        self.log(f"❌ FAILED: {self.failed_tests}")
        self.log(f"📊 SUCCESS RATE: {success_rate:.1f}%")
        self.log("=" * 60)
        
        if self.failed_tests == 0:
            self.log("🎉 ALL BUDGET ROLLUP TESTS PASSED!", "SUCCESS")
        else:
            self.log(f"⚠️ {self.failed_tests} TESTS FAILED - REVIEW REQUIRED", "ERROR")

if __name__ == "__main__":
    tester = BudgetRollupTester()
    tester.run_all_tests()