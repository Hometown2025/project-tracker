#!/usr/bin/env python3
"""
Focused Backend API Testing for Ideas Board and Calendar functionality
Tests authentication, Ideas CRUD operations, and Calendar project-based filtering
"""

import requests
import json
from datetime import datetime, date, timedelta
import sys
import os

# Get backend URL from frontend .env
BACKEND_URL = "https://housebuild.preview.emergentagent.com/api"

class IdeasCalendarTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_data = {
            'projects': [],
            'tasks': [],
            'ideas': [],
            'users': []
        }
        self.passed_tests = 0
        self.failed_tests = 0
        self.admin_token = None
        self.demo_token = None
        self.admin_user = None
        self.demo_user = None
        
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

    def test_authentication(self):
        """Test authentication with admin/admin and demo/demo credentials"""
        self.log("\n=== Testing Authentication ===")
        
        # Test admin login
        admin_login = {
            "username": "admin",
            "password": "admin"
        }
        
        admin_response = self.test_request("POST", "/auth/login", admin_login, 200, "Admin Login (admin/admin)")
        
        if admin_response:
            self.admin_token = admin_response.get('session_token')
            self.admin_user = admin_response.get('user')
            
            if self.admin_user and self.admin_user.get('role') == 'admin':
                self.log("✅ Admin user authenticated successfully with admin role")
            else:
                self.log("❌ Admin user role verification failed", "ERROR")
                self.failed_tests += 1
        
        # Test demo login
        demo_login = {
            "username": "demo",
            "password": "demo"
        }
        
        demo_response = self.test_request("POST", "/auth/login", demo_login, 200, "Demo Login (demo/demo)")
        
        if demo_response:
            self.demo_token = demo_response.get('session_token')
            self.demo_user = demo_response.get('user')
            
            if self.demo_user and self.demo_user.get('role') == 'user':
                self.log("✅ Demo user authenticated successfully with user role")
                
                # Check assigned projects
                assigned_projects = self.demo_user.get('assigned_projects', [])
                self.log(f"✅ Demo user has {len(assigned_projects)} assigned projects")
            else:
                self.log("❌ Demo user role verification failed", "ERROR")
                self.failed_tests += 1

    def test_ideas_api_endpoints(self):
        """Test Ideas API endpoints: GET, POST, PUT, DELETE"""
        self.log("\n=== Testing Ideas API Endpoints ===")
        
        if not self.admin_token:
            self.log("❌ No admin token available for Ideas API testing", "ERROR")
            return
        
        # First, create a test project for ideas
        test_project = {
            "name": "Ideas Test Project",
            "description": "Project for testing Ideas API",
            "color": "#FF6B6B"
        }
        
        created_project = self.test_request("POST", "/projects", test_project, 200, 
                                          "Create Project for Ideas Testing", auth_token=self.admin_token)
        
        if not created_project:
            self.log("❌ Failed to create project for Ideas testing", "ERROR")
            return
        
        project_id = created_project['id']
        self.test_data['projects'].append(created_project)
        
        # Test 1: GET /api/ideas - retrieve all ideas (should be empty initially)
        all_ideas = self.test_request("GET", "/ideas", test_name="GET /api/ideas - Retrieve All Ideas")
        
        if all_ideas is not None:
            self.log(f"✅ GET /api/ideas successful - Retrieved {len(all_ideas)} ideas")
        
        # Test 2: POST /api/ideas - create a new idea
        new_idea_data = {
            "project_id": project_id,
            "title": "Modern Kitchen Design",
            "description": "Contemporary kitchen layout with island and modern appliances",
            "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
            "pinterest_url": "https://pinterest.com/pin/modern-kitchen-design",
            "tags": ["kitchen", "modern", "contemporary", "island"]
        }
        
        created_idea = self.test_request("POST", "/ideas", new_idea_data, 200, 
                                       "POST /api/ideas - Create New Idea")
        
        if created_idea:
            idea_id = created_idea['id']
            self.test_data['ideas'].append(created_idea)
            self.log(f"✅ POST /api/ideas successful - Created idea: {created_idea['title']}")
            
            # Verify idea data
            if created_idea.get('project_id') == project_id:
                self.log("✅ Idea project_id correctly set")
            if created_idea.get('title') == new_idea_data['title']:
                self.log("✅ Idea title correctly set")
            if created_idea.get('tags') == new_idea_data['tags']:
                self.log("✅ Idea tags correctly set")
        else:
            self.log("❌ Failed to create idea", "ERROR")
            return
        
        # Test 3: GET /api/ideas/{idea_id} - retrieve specific idea
        single_idea = self.test_request("GET", f"/ideas/{idea_id}", test_name="GET /api/ideas/{idea_id} - Retrieve Single Idea")
        
        if single_idea:
            self.log(f"✅ GET /api/ideas/{idea_id} successful - Retrieved idea: {single_idea['title']}")
            
            # Verify data integrity
            if single_idea.get('image_data') == new_idea_data['image_data']:
                self.log("✅ Image data preserved correctly")
            if single_idea.get('pinterest_url') == new_idea_data['pinterest_url']:
                self.log("✅ Pinterest URL preserved correctly")
        
        # Test 4: PUT /api/ideas/{idea_id} - update existing idea (CRITICAL for EditIdeaModal)
        updated_idea_data = {
            "project_id": project_id,
            "title": "Updated Modern Kitchen Design",
            "description": "Updated contemporary kitchen layout with additional features",
            "pinterest_url": "https://pinterest.com/pin/updated-modern-kitchen-design",
            "tags": ["kitchen", "modern", "contemporary", "island", "updated"]
        }
        
        updated_idea = self.test_request("PUT", f"/ideas/{idea_id}", updated_idea_data, 200, 
                                       "PUT /api/ideas/{idea_id} - Update Existing Idea (CRITICAL)")
        
        if updated_idea:
            self.log(f"✅ PUT /api/ideas/{idea_id} successful - Updated idea: {updated_idea['title']}")
            
            # Verify updates
            if updated_idea.get('title') == updated_idea_data['title']:
                self.log("✅ Idea title updated correctly")
            if updated_idea.get('description') == updated_idea_data['description']:
                self.log("✅ Idea description updated correctly")
            if updated_idea.get('tags') == updated_idea_data['tags']:
                self.log("✅ Idea tags updated correctly")
            if updated_idea.get('pinterest_url') == updated_idea_data['pinterest_url']:
                self.log("✅ Pinterest URL updated correctly")
        else:
            self.log("❌ CRITICAL: PUT /api/ideas/{idea_id} failed - EditIdeaModal will not work", "ERROR")
        
        # Test 5: Create another idea for testing filtering
        second_idea_data = {
            "project_id": project_id,
            "title": "Bathroom Renovation Ideas",
            "description": "Modern bathroom design with walk-in shower",
            "tags": ["bathroom", "renovation", "modern"]
        }
        
        second_idea = self.test_request("POST", "/ideas", second_idea_data, 200, 
                                      "POST /api/ideas - Create Second Idea")
        
        if second_idea:
            self.test_data['ideas'].append(second_idea)
        
        # Test 6: GET /api/ideas with project filtering
        project_ideas = self.test_request("GET", f"/ideas?project_id={project_id}", 
                                        test_name="GET /api/ideas?project_id - Filter by Project")
        
        if project_ideas:
            self.log(f"✅ Project filtering successful - Retrieved {len(project_ideas)} ideas for project")
            
            # Verify all ideas belong to the project
            for idea in project_ideas:
                if idea.get('project_id') != project_id:
                    self.log("❌ Project filtering not working correctly", "ERROR")
                    self.failed_tests += 1
                    break
            else:
                self.log("✅ All filtered ideas belong to correct project")
        
        # Test 7: DELETE /api/ideas/{idea_id} - delete an idea
        if second_idea:
            deleted_idea = self.test_request("DELETE", f"/ideas/{second_idea['id']}", 
                                           test_name="DELETE /api/ideas/{idea_id} - Delete Idea")
            
            if deleted_idea:
                self.log("✅ DELETE /api/ideas/{idea_id} successful")
                
                # Verify idea is deleted
                deleted_check = self.test_request("GET", f"/ideas/{second_idea['id']}", 
                                                expected_status=404, 
                                                test_name="Verify Idea Deletion")
                if deleted_check is None:  # 404 expected
                    self.log("✅ Idea successfully deleted from database")

    def test_calendar_api_with_project_filtering(self):
        """Test Calendar API with project-based filtering for different user roles"""
        self.log("\n=== Testing Calendar API with Project-Based Filtering ===")
        
        if not self.admin_token or not self.demo_token:
            self.log("❌ Missing admin or demo tokens for Calendar API testing", "ERROR")
            return
        
        # First, create test data: projects and tasks with different dates
        
        # Create Project 1 (assign to demo user)
        project1_data = {
            "name": "Demo User Project",
            "description": "Project assigned to demo user",
            "color": "#4CAF50"
        }
        
        project1 = self.test_request("POST", "/projects", project1_data, 200, 
                                   "Create Project 1 for Calendar Testing", auth_token=self.admin_token)
        
        if not project1:
            self.log("❌ Failed to create project 1 for calendar testing", "ERROR")
            return
        
        self.test_data['projects'].append(project1)
        
        # Create Project 2 (NOT assigned to demo user)
        project2_data = {
            "name": "Admin Only Project",
            "description": "Project not assigned to demo user",
            "color": "#FF9800"
        }
        
        project2 = self.test_request("POST", "/projects", project2_data, 200, 
                                   "Create Project 2 for Calendar Testing", auth_token=self.admin_token)
        
        if not project2:
            self.log("❌ Failed to create project 2 for calendar testing", "ERROR")
            return
        
        self.test_data['projects'].append(project2)
        
        # Assign demo user to Project 1 only
        assignment_data = {
            "user_id": self.demo_user['id'],
            "project_ids": [project1['id']]
        }
        
        assignment_result = self.test_request("PUT", f"/admin/users/{self.demo_user['id']}/assign-projects", 
                                            assignment_data, 200, "Assign Demo User to Project 1", 
                                            auth_token=self.admin_token)
        
        if not assignment_result:
            self.log("❌ Failed to assign demo user to project", "ERROR")
            return
        
        # Create tasks in both projects with various dates
        today = date.today()
        
        # Tasks for Project 1 (demo user should see these)
        project1_tasks = [
            {
                "project_id": project1['id'],
                "title": "Project 1 Task 1",
                "description": "Task in demo user's project",
                "priority": "high",
                "due_date": (today + timedelta(days=5)).isoformat(),
                "order_date": (today + timedelta(days=2)).isoformat(),
                "delivery_date": (today + timedelta(days=7)).isoformat()
            },
            {
                "project_id": project1['id'],
                "title": "Project 1 Task 2",
                "description": "Another task in demo user's project",
                "priority": "medium",
                "due_date": (today + timedelta(days=10)).isoformat()
            }
        ]
        
        # Tasks for Project 2 (demo user should NOT see these)
        project2_tasks = [
            {
                "project_id": project2['id'],
                "title": "Project 2 Task 1",
                "description": "Task in admin-only project",
                "priority": "high",
                "due_date": (today + timedelta(days=3)).isoformat(),
                "delivery_date": (today + timedelta(days=6)).isoformat()
            }
        ]
        
        # Create all tasks
        for task_data in project1_tasks + project2_tasks:
            created_task = self.test_request("POST", "/tasks", task_data, 200, 
                                           f"Create Task: {task_data['title']}", 
                                           auth_token=self.admin_token)
            if created_task:
                self.test_data['tasks'].append(created_task)
        
        # Test 1: Admin user calendar access (should see all events)
        admin_calendar = self.test_request("GET", "/calendar", auth_token=self.admin_token, 
                                         test_name="GET /api/calendar - Admin User (All Projects)")
        
        if admin_calendar:
            self.log(f"✅ Admin calendar access successful - Retrieved {len(admin_calendar)} events")
            
            # Count events from each project
            project1_events = [event for event in admin_calendar if event.get('project_id') == project1['id']]
            project2_events = [event for event in admin_calendar if event.get('project_id') == project2['id']]
            
            self.log(f"✅ Admin sees {len(project1_events)} events from Project 1")
            self.log(f"✅ Admin sees {len(project2_events)} events from Project 2")
            
            if len(project1_events) > 0 and len(project2_events) > 0:
                self.log("✅ Admin user sees events from all projects")
            else:
                self.log("❌ Admin user not seeing events from all projects", "ERROR")
                self.failed_tests += 1
        
        # Test 2: Demo user calendar access (should see only Project 1 events)
        demo_calendar = self.test_request("GET", "/calendar", auth_token=self.demo_token, 
                                        test_name="GET /api/calendar - Demo User (Assigned Projects Only)")
        
        if demo_calendar:
            self.log(f"✅ Demo user calendar access successful - Retrieved {len(demo_calendar)} events")
            
            # Verify project-based filtering
            project1_events_demo = [event for event in demo_calendar if event.get('project_id') == project1['id']]
            project2_events_demo = [event for event in demo_calendar if event.get('project_id') == project2['id']]
            
            self.log(f"✅ Demo user sees {len(project1_events_demo)} events from assigned Project 1")
            self.log(f"✅ Demo user sees {len(project2_events_demo)} events from unassigned Project 2")
            
            # CRITICAL TEST: Demo user should only see events from assigned projects
            if len(project1_events_demo) > 0 and len(project2_events_demo) == 0:
                self.log("✅ CRITICAL: Project-based filtering working correctly - Demo user only sees assigned project events")
            elif len(project2_events_demo) > 0:
                self.log("❌ CRITICAL: Project-based filtering FAILED - Demo user sees unassigned project events", "ERROR")
                self.failed_tests += 1
            else:
                self.log("⚠️ No events found for demo user - check task creation", "WARNING")
            
            # Verify calendar event structure
            if demo_calendar:
                sample_event = demo_calendar[0]
                required_fields = ['id', 'task_id', 'title', 'date', 'priority', 'status', 'project_id', 'event_type']
                
                for field in required_fields:
                    if field in sample_event:
                        self.log(f"✅ Calendar event has required field: {field}")
                    else:
                        self.log(f"❌ Calendar event missing required field: {field}", "ERROR")
                        self.failed_tests += 1
        
        # Test 3: Verify different event types are created for tasks with multiple dates
        if admin_calendar:
            # Find events for tasks with multiple dates
            multi_date_events = {}
            for event in admin_calendar:
                task_id = event.get('task_id')
                if task_id:
                    if task_id not in multi_date_events:
                        multi_date_events[task_id] = []
                    multi_date_events[task_id].append(event)
            
            # Check for tasks with multiple events
            for task_id, events in multi_date_events.items():
                if len(events) > 1:
                    event_types = [event.get('event_type') for event in events]
                    self.log(f"✅ Task {task_id} has {len(events)} calendar events with types: {event_types}")
                    
                    # Verify different event types
                    expected_types = ['due_date', 'order_date', 'delivery_date']
                    found_types = [et for et in event_types if et in expected_types]
                    if found_types:
                        self.log(f"✅ Multiple date types working: {found_types}")
                    break
        
        # Test 4: Test calendar access without authentication (should fail)
        self.test_request("GET", "/calendar", expected_status=403, 
                         test_name="GET /api/calendar - No Authentication (Should Fail)")

    def test_project_access_verification(self):
        """Test that regular users only see calendar events from their assigned projects"""
        self.log("\n=== Testing Project Access Verification ===")
        
        if not self.admin_token or not self.demo_token:
            self.log("❌ Missing tokens for project access verification", "ERROR")
            return
        
        # Get demo user's assigned projects
        demo_user_info = self.test_request("GET", "/auth/me", auth_token=self.demo_token, 
                                         test_name="Get Demo User Info")
        
        if demo_user_info:
            assigned_projects = demo_user_info.get('assigned_projects', [])
            self.log(f"✅ Demo user has {len(assigned_projects)} assigned projects")
            
            # Get demo user's calendar
            demo_calendar = self.test_request("GET", "/calendar", auth_token=self.demo_token, 
                                            test_name="Get Demo User Calendar for Access Verification")
            
            if demo_calendar:
                # Verify all calendar events belong to assigned projects
                unauthorized_events = []
                for event in demo_calendar:
                    event_project_id = event.get('project_id')
                    if event_project_id and event_project_id not in assigned_projects:
                        unauthorized_events.append(event)
                
                if len(unauthorized_events) == 0:
                    self.log("✅ CRITICAL: All calendar events belong to user's assigned projects")
                else:
                    self.log(f"❌ CRITICAL: Found {len(unauthorized_events)} unauthorized events in user's calendar", "ERROR")
                    for event in unauthorized_events:
                        self.log(f"❌ Unauthorized event: {event.get('title')} from project {event.get('project_id')}", "ERROR")
                    self.failed_tests += 1
            
            # Test project access through projects endpoint
            demo_projects = self.test_request("GET", "/projects", auth_token=self.demo_token, 
                                            test_name="Get Demo User Projects")
            
            if demo_projects:
                demo_project_ids = [p['id'] for p in demo_projects]
                
                # Verify demo user only sees assigned projects
                unauthorized_projects = [pid for pid in demo_project_ids if pid not in assigned_projects]
                
                if len(unauthorized_projects) == 0:
                    self.log("✅ Demo user only sees assigned projects")
                else:
                    self.log(f"❌ Demo user sees {len(unauthorized_projects)} unauthorized projects", "ERROR")
                    self.failed_tests += 1

    def cleanup_test_data(self):
        """Clean up test data"""
        self.log("\n=== Cleaning Up Test Data ===")
        
        if not self.admin_token:
            self.log("❌ No admin token available for cleanup", "ERROR")
            return
        
        # Delete test tasks
        for task in self.test_data['tasks']:
            self.test_request("DELETE", f"/tasks/{task['id']}", auth_token=self.admin_token, 
                            test_name=f"Delete Task {task['title']}")
        
        # Delete test ideas
        for idea in self.test_data['ideas']:
            self.test_request("DELETE", f"/ideas/{idea['id']}", 
                            test_name=f"Delete Idea {idea['title']}")
        
        # Delete test projects
        for project in self.test_data['projects']:
            self.test_request("DELETE", f"/projects/{project['id']}", auth_token=self.admin_token, 
                            test_name=f"Delete Project {project['name']}")

    def run_focused_tests(self):
        """Run focused tests for Ideas Board and Calendar functionality"""
        self.log("🚀 Starting Focused Backend Testing for Ideas Board and Calendar")
        self.log(f"Backend URL: {self.base_url}")
        
        try:
            # Test authentication first
            self.test_authentication()
            
            if not self.admin_token or not self.demo_token:
                self.log("❌ Authentication failed - cannot proceed with API tests", "ERROR")
                return False
            
            # Test Ideas API endpoints
            self.test_ideas_api_endpoints()
            
            # Test Calendar API with project-based filtering
            self.test_calendar_api_with_project_filtering()
            
            # Test project access verification
            self.test_project_access_verification()
            
            # Clean up test data
            self.cleanup_test_data()
            
        except Exception as e:
            self.log(f"❌ Critical error during testing: {str(e)}", "ERROR")
            self.failed_tests += 1
        
        # Final results
        self.log("\n" + "="*60)
        self.log("🏁 FOCUSED TESTING COMPLETE")
        self.log(f"✅ Passed: {self.passed_tests}")
        self.log(f"❌ Failed: {self.failed_tests}")
        self.log(f"📊 Success Rate: {(self.passed_tests/(self.passed_tests + self.failed_tests)*100):.1f}%" if (self.passed_tests + self.failed_tests) > 0 else "No tests run")
        self.log("="*60)
        
        return self.failed_tests == 0

if __name__ == "__main__":
    tester = IdeasCalendarTester()
    success = tester.run_focused_tests()
    sys.exit(0 if success else 1)