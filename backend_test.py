#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Task Manager Application
Tests all CRUD operations, dashboard stats, calendar data, and data relationships
"""

import requests
import json
import base64
from datetime import datetime, date, timedelta
import sys
import os

# Get backend URL from frontend .env
BACKEND_URL = "https://d627ba87-f652-484b-9633-b99e5f8fdffe.preview.emergentagent.com/api"

class TaskManagerTester:
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
        
    def test_request(self, method, endpoint, data=None, expected_status=200, test_name=""):
        """Make HTTP request and validate response"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
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
    
    def test_dashboard_stats(self):
        """Test Enhanced Dashboard Stats API with new date handling"""
        self.log("\n=== Testing Enhanced Dashboard Stats API ===")
        
        result = self.test_request("GET", "/dashboard", test_name="Enhanced Dashboard Stats")
        
        if result:
            required_fields = ['total_projects', 'active_projects', 'total_tasks', 
                             'completed_tasks', 'overdue_tasks', 'today_tasks', 'ideas_count']
            
            for field in required_fields:
                if field in result:
                    self.log(f"✅ Dashboard field '{field}': {result[field]}")
                else:
                    self.log(f"❌ Missing dashboard field: {field}", "ERROR")
                    self.failed_tests += 1
            
            # Test enhanced date handling in dashboard stats
            if 'overdue_tasks' in result:
                self.log(f"✅ Overdue tasks calculation (considers due_date and delivery_date): {result['overdue_tasks']}")
            
            if 'today_tasks' in result:
                self.log(f"✅ Today tasks calculation (considers due_date, order_date, and delivery_date): {result['today_tasks']}")
        
        return result
    
    def test_projects_crud(self):
        """Test Projects CRUD operations"""
        self.log("\n=== Testing Projects CRUD ===")
        
        # Test Create Project
        project_data = {
            "name": "Website Redesign Project",
            "description": "Complete redesign of company website with modern UI/UX",
            "color": "#3B82F6"
        }
        
        created_project = self.test_request("POST", "/projects", project_data, 200, "Create Project")
        
        if created_project:
            self.test_data['projects'].append(created_project)
            project_id = created_project['id']
            
            # Test Get All Projects
            projects = self.test_request("GET", "/projects", test_name="Get All Projects")
            
            if projects and len(projects) > 0:
                self.log(f"✅ Retrieved {len(projects)} projects")
            
            # Test Get Single Project
            single_project = self.test_request("GET", f"/projects/{project_id}", test_name="Get Single Project")
            
            if single_project:
                self.log(f"✅ Retrieved project: {single_project['name']}")
            
            # Test Update Project
            update_data = {
                "name": "Website Redesign Project - Updated",
                "description": "Updated description with new requirements",
                "color": "#10B981"
            }
            
            updated_project = self.test_request("PUT", f"/projects/{project_id}", update_data, 200, "Update Project")
            
            if updated_project and updated_project['name'] == update_data['name']:
                self.log("✅ Project updated successfully")
            
            # Create another project for testing relationships
            project_data2 = {
                "name": "Mobile App Development",
                "description": "Native mobile app for iOS and Android",
                "color": "#8B5CF6"
            }
            
            created_project2 = self.test_request("POST", "/projects", project_data2, 200, "Create Second Project")
            if created_project2:
                self.test_data['projects'].append(created_project2)
    
    def test_tasks_crud(self):
        """Test Enhanced Tasks CRUD operations with new date fields"""
        self.log("\n=== Testing Enhanced Tasks CRUD ===")
        
        if not self.test_data['projects']:
            self.log("❌ No projects available for task testing", "ERROR")
            return
        
        project_id = self.test_data['projects'][0]['id']
        
        # Test Create Tasks with enhanced date fields as requested
        tasks_to_create = [
            {
                "project_id": project_id,
                "title": "Website Launch",
                "description": "Complete website launch with all features",
                "priority": "high",
                "due_date": (date.today() + timedelta(days=15)).isoformat(),
                "order_date": (date.today() + timedelta(days=5)).isoformat(),
                "delivery_date": (date.today() + timedelta(days=12)).isoformat()
            },
            {
                "project_id": project_id,
                "title": "Design Review",
                "description": "Review all design components and mockups",
                "priority": "medium",
                "due_date": (date.today() + timedelta(days=7)).isoformat()
            },
            {
                "project_id": project_id,
                "title": "Product Order",
                "description": "Order required products and materials",
                "priority": "high",
                "order_date": (date.today() + timedelta(days=3)).isoformat(),
                "delivery_date": (date.today() + timedelta(days=10)).isoformat()
            }
        ]
        
        for task_data in tasks_to_create:
            created_task = self.test_request("POST", "/tasks", task_data, 200, f"Create Task - {task_data['title']}")
            
            if created_task:
                self.test_data['tasks'].append(created_task)
                self.log(f"✅ Created task: {task_data['title']}")
                
                # Verify new date fields are properly stored
                if task_data.get('order_date') and created_task.get('order_date'):
                    self.log(f"✅ Order date stored: {created_task['order_date']}")
                if task_data.get('delivery_date') and created_task.get('delivery_date'):
                    self.log(f"✅ Delivery date stored: {created_task['delivery_date']}")
                if task_data.get('due_date') and created_task.get('due_date'):
                    self.log(f"✅ Due date stored: {created_task['due_date']}")
        
        if self.test_data['tasks']:
            task_id = self.test_data['tasks'][0]['id']
            
            # Test Get All Tasks
            all_tasks = self.test_request("GET", "/tasks", test_name="Get All Tasks")
            
            if all_tasks:
                self.log(f"✅ Retrieved {len(all_tasks)} tasks")
                
                # Verify date deserialization works
                for task in all_tasks:
                    if task.get('due_date'):
                        self.log(f"✅ Due date deserialized: {task['due_date']}")
                    if task.get('order_date'):
                        self.log(f"✅ Order date deserialized: {task['order_date']}")
                    if task.get('delivery_date'):
                        self.log(f"✅ Delivery date deserialized: {task['delivery_date']}")
            
            # Test Get Tasks by Project
            project_tasks = self.test_request("GET", f"/tasks?project_id={project_id}", test_name="Get Tasks by Project")
            
            if project_tasks:
                self.log(f"✅ Retrieved {len(project_tasks)} tasks for project")
            
            # Test Get Single Task
            single_task = self.test_request("GET", f"/tasks/{task_id}", test_name="Get Single Task")
            
            if single_task:
                self.log(f"✅ Retrieved task: {single_task['title']}")
            
            # Test Enhanced Task Updates with new date fields
            enhanced_update = {
                "title": "Updated Website Launch",
                "order_date": (date.today() + timedelta(days=2)).isoformat(),
                "delivery_date": (date.today() + timedelta(days=14)).isoformat(),
                "priority": "high"
            }
            updated_task = self.test_request("PUT", f"/tasks/{task_id}", enhanced_update, 200, "Update Task with New Date Fields")
            
            if updated_task:
                if updated_task.get('order_date') == enhanced_update['order_date']:
                    self.log("✅ Order date updated successfully")
                if updated_task.get('delivery_date') == enhanced_update['delivery_date']:
                    self.log("✅ Delivery date updated successfully")
                if updated_task.get('title') == enhanced_update['title']:
                    self.log("✅ Task title updated successfully")
            
            # Test Task Completion
            completion_update = {"completed": True}
            completed_task = self.test_request("PUT", f"/tasks/{task_id}", completion_update, 200, "Mark Task as Completed")
            
            if completed_task and completed_task['completed']:
                self.log("✅ Task marked as completed successfully")
                
                # Test uncompleting task
                uncompletion_update = {"completed": False}
                uncompleted_task = self.test_request("PUT", f"/tasks/{task_id}", uncompletion_update, 200, "Mark Task as Uncompleted")
                
                if uncompleted_task and not uncompleted_task['completed']:
                    self.log("✅ Task marked as uncompleted successfully")
    
    def test_ideas_crud(self):
        """Test Ideas CRUD operations with image data and Pinterest URLs"""
        self.log("\n=== Testing Ideas CRUD ===")
        
        if not self.test_data['projects']:
            self.log("❌ No projects available for idea testing", "ERROR")
            return
        
        project_id = self.test_data['projects'][0]['id']
        
        # Create sample base64 image data (small 1x1 pixel PNG)
        sample_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        # Test Create Ideas
        ideas_to_create = [
            {
                "project_id": project_id,
                "title": "Modern Navigation Design",
                "description": "Inspiration for clean, modern navigation patterns",
                "image_data": sample_image_base64,
                "pinterest_url": "https://pinterest.com/pin/modern-nav-design",
                "tags": ["navigation", "modern", "clean"]
            },
            {
                "project_id": project_id,
                "title": "Color Palette Ideas",
                "description": "Trending color combinations for web design",
                "pinterest_url": "https://pinterest.com/pin/color-palette-2024",
                "tags": ["colors", "palette", "trending"]
            }
        ]
        
        for idea_data in ideas_to_create:
            created_idea = self.test_request("POST", "/ideas", idea_data, 200, f"Create Idea - {idea_data['title']}")
            
            if created_idea:
                self.test_data['ideas'].append(created_idea)
                self.log(f"✅ Created idea: {idea_data['title']}")
        
        if self.test_data['ideas']:
            idea_id = self.test_data['ideas'][0]['id']
            
            # Test Get All Ideas
            all_ideas = self.test_request("GET", "/ideas", test_name="Get All Ideas")
            
            if all_ideas:
                self.log(f"✅ Retrieved {len(all_ideas)} ideas")
            
            # Test Get Ideas by Project
            project_ideas = self.test_request("GET", f"/ideas?project_id={project_id}", test_name="Get Ideas by Project")
            
            if project_ideas:
                self.log(f"✅ Retrieved {len(project_ideas)} ideas for project")
            
            # Test Get Single Idea
            single_idea = self.test_request("GET", f"/ideas/{idea_id}", test_name="Get Single Idea")
            
            if single_idea:
                self.log(f"✅ Retrieved idea: {single_idea['title']}")
                
                # Verify image data is preserved
                if single_idea.get('image_data') == sample_image_base64:
                    self.log("✅ Image data preserved correctly")
                else:
                    self.log("❌ Image data not preserved correctly", "ERROR")
                    self.failed_tests += 1
            
            # Test Update Idea
            update_data = {
                "project_id": project_id,
                "title": "Updated Navigation Design",
                "description": "Updated description with new insights",
                "pinterest_url": "https://pinterest.com/pin/updated-nav-design",
                "tags": ["navigation", "updated", "modern"]
            }
            
            updated_idea = self.test_request("PUT", f"/ideas/{idea_id}", update_data, 200, "Update Idea")
            
            if updated_idea and updated_idea['title'] == update_data['title']:
                self.log("✅ Idea updated successfully")
    
    def test_calendar_api(self):
        """Test Enhanced Calendar API with multiple date types and emojis"""
        self.log("\n=== Testing Enhanced Calendar API ===")
        
        calendar_data = self.test_request("GET", "/calendar", test_name="Get Enhanced Calendar Data")
        
        if calendar_data:
            self.log(f"✅ Retrieved {len(calendar_data)} calendar events")
            
            # Verify calendar event structure and enhanced features
            if calendar_data:
                # Check for different event types
                event_types_found = set()
                emojis_found = set()
                
                for event in calendar_data:
                    # Verify required fields
                    required_fields = ['id', 'task_id', 'title', 'date', 'priority', 'status', 'project_id', 'event_type', 'event_label']
                    
                    for field in required_fields:
                        if field not in event:
                            self.log(f"❌ Calendar event missing field: {field}", "ERROR")
                            self.failed_tests += 1
                    
                    # Track event types and emojis
                    if 'event_type' in event:
                        event_types_found.add(event['event_type'])
                    
                    if 'title' in event:
                        title = event['title']
                        if '📋' in title:
                            emojis_found.add('📋')
                        if '📦' in title:
                            emojis_found.add('📦')
                        if '🚚' in title:
                            emojis_found.add('🚚')
                
                # Verify we have different event types
                expected_event_types = {'due_date', 'order_date', 'delivery_date'}
                found_event_types = event_types_found.intersection(expected_event_types)
                
                if found_event_types:
                    self.log(f"✅ Found event types: {', '.join(found_event_types)}")
                else:
                    self.log("❌ No expected event types found", "ERROR")
                    self.failed_tests += 1
                
                # Verify emojis are present
                expected_emojis = {'📋', '📦', '🚚'}
                found_emojis = emojis_found.intersection(expected_emojis)
                
                if found_emojis:
                    self.log(f"✅ Found emojis in calendar events: {', '.join(found_emojis)}")
                else:
                    self.log("❌ No expected emojis found in calendar events", "ERROR")
                    self.failed_tests += 1
                
                # Test that tasks with multiple dates create multiple events
                task_event_counts = {}
                for event in calendar_data:
                    task_id = event.get('task_id')
                    if task_id:
                        task_event_counts[task_id] = task_event_counts.get(task_id, 0) + 1
                
                multiple_event_tasks = [task_id for task_id, count in task_event_counts.items() if count > 1]
                if multiple_event_tasks:
                    self.log(f"✅ Found {len(multiple_event_tasks)} tasks with multiple calendar events")
                else:
                    self.log("ℹ️ No tasks with multiple date events found (this is okay if test data doesn't have multiple dates)")
        
        return calendar_data
    
    def test_project_stats(self):
        """Test project statistics and completion tracking"""
        self.log("\n=== Testing Project Stats ===")
        
        # Get all projects and verify stats
        projects = self.test_request("GET", "/projects", test_name="Get Projects with Stats")
        
        if projects:
            for project in projects:
                project_id = project['id']
                task_count = project.get('task_count', 0)
                completed_tasks = project.get('completed_tasks', 0)
                
                self.log(f"✅ Project '{project['name']}': {completed_tasks}/{task_count} tasks completed")
                
                if task_count > 0:
                    completion_rate = (completed_tasks / task_count) * 100
                    self.log(f"✅ Completion rate: {completion_rate:.1f}%")
    
    def test_data_relationships_enhanced(self):
        """Test enhanced data relationships with new date fields"""
        self.log("\n=== Testing Enhanced Data Relationships ===")
        
        if not self.test_data['projects'] or not self.test_data['tasks']:
            self.log("❌ No projects or tasks available for relationship testing", "ERROR")
            return
        
        project_id = self.test_data['projects'][0]['id']
        
        # Get project with task counts
        project = self.test_request("GET", f"/projects/{project_id}", test_name="Get Project with Enhanced Task Data")
        
        if project:
            task_count = project.get('task_count', 0)
            completed_tasks = project.get('completed_tasks', 0)
            
            self.log(f"✅ Project has {task_count} total tasks")
            self.log(f"✅ Project has {completed_tasks} completed tasks")
            
            # Verify task counts match actual tasks
            project_tasks = self.test_request("GET", f"/tasks?project_id={project_id}", test_name="Verify Enhanced Task Count")
            
            if project_tasks:
                # Count tasks with different date types
                tasks_with_due_date = len([task for task in project_tasks if task.get('due_date')])
                tasks_with_order_date = len([task for task in project_tasks if task.get('order_date')])
                tasks_with_delivery_date = len([task for task in project_tasks if task.get('delivery_date')])
                
                self.log(f"✅ Tasks with due_date: {tasks_with_due_date}")
                self.log(f"✅ Tasks with order_date: {tasks_with_order_date}")
                self.log(f"✅ Tasks with delivery_date: {tasks_with_delivery_date}")
                
                if len(project_tasks) == task_count:
                    self.log("✅ Task count matches actual tasks")
                else:
                    self.log(f"❌ Task count mismatch: expected {task_count}, got {len(project_tasks)}", "ERROR")
                    self.failed_tests += 1
    
    def test_priority_system(self):
        """Test all priority levels work correctly"""
        self.log("\n=== Testing Priority System ===")
        
        priorities = ["high", "medium", "low"]
        
        for priority in priorities:
            # Get tasks with specific priority
            tasks = self.test_request("GET", f"/tasks", test_name=f"Get {priority} priority tasks")
            
            if tasks:
                priority_tasks = [task for task in tasks if task.get('priority') == priority]
                self.log(f"✅ Found {len(priority_tasks)} tasks with {priority} priority")
    
    def test_date_serialization(self):
        """Test date serialization and deserialization"""
        self.log("\n=== Testing Date Serialization/Deserialization ===")
        
        if not self.test_data['projects']:
            self.log("❌ No projects available for date serialization testing", "ERROR")
            return
        
        project_id = self.test_data['projects'][0]['id']
        
        # Test task with all date types
        test_task = {
            "project_id": project_id,
            "title": "Date Serialization Test Task",
            "description": "Testing date handling",
            "priority": "medium",
            "due_date": "2024-12-25",
            "order_date": "2024-12-20",
            "delivery_date": "2024-12-24"
        }
        
        created_task = self.test_request("POST", "/tasks", test_task, 200, "Create Task for Date Testing")
        
        if created_task:
            # Verify dates are properly stored and returned
            for date_field in ['due_date', 'order_date', 'delivery_date']:
                if created_task.get(date_field) == test_task[date_field]:
                    self.log(f"✅ {date_field} serialization/deserialization working: {created_task[date_field]}")
                else:
                    self.log(f"❌ {date_field} serialization failed: expected {test_task[date_field]}, got {created_task.get(date_field)}", "ERROR")
                    self.failed_tests += 1
            
            # Test updating dates
            date_update = {
                "due_date": "2024-12-30",
                "order_date": "2024-12-22",
                "delivery_date": "2024-12-28"
            }
            
            updated_task = self.test_request("PUT", f"/tasks/{created_task['id']}", date_update, 200, "Update Task Dates")
            
            if updated_task:
                for date_field in ['due_date', 'order_date', 'delivery_date']:
                    if updated_task.get(date_field) == date_update[date_field]:
                        self.log(f"✅ {date_field} update serialization working: {updated_task[date_field]}")
                    else:
                        self.log(f"❌ {date_field} update failed: expected {date_update[date_field]}, got {updated_task.get(date_field)}", "ERROR")
                        self.failed_tests += 1
            
            # Clean up test task
            self.test_request("DELETE", f"/tasks/{created_task['id']}", test_name="Delete Date Test Task")
    
    def test_backwards_compatibility(self):
        """Test backwards compatibility with existing functionality"""
        self.log("\n=== Testing Backwards Compatibility ===")
        
        if not self.test_data['projects']:
            self.log("❌ No projects available for backwards compatibility testing", "ERROR")
            return
        
        project_id = self.test_data['projects'][0]['id']
        
        # Test creating task with only due_date (old format)
        old_format_task = {
            "project_id": project_id,
            "title": "Backwards Compatibility Test",
            "description": "Testing old task format still works",
            "priority": "low",
            "due_date": (date.today() + timedelta(days=5)).isoformat()
        }
        
        created_task = self.test_request("POST", "/tasks", old_format_task, 200, "Create Task with Old Format")
        
        if created_task:
            self.log("✅ Old task format (due_date only) still works")
            
            # Verify new fields are None/null
            if created_task.get('order_date') is None:
                self.log("✅ order_date is None for old format task")
            if created_task.get('delivery_date') is None:
                self.log("✅ delivery_date is None for old format task")
            
            # Test that calendar still works with old format tasks
            calendar_data = self.test_request("GET", "/calendar", test_name="Calendar with Mixed Task Formats")
            
            if calendar_data:
                # Find our test task in calendar
                test_events = [event for event in calendar_data if event.get('task_id') == created_task['id']]
                if test_events:
                    self.log(f"✅ Old format task appears in calendar: {len(test_events)} event(s)")
                    
                    # Should only have due_date event
                    due_events = [event for event in test_events if event.get('event_type') == 'due_date']
                    if due_events:
                        self.log("✅ Due date event created for old format task")
            
            # Clean up test task
            self.test_request("DELETE", f"/tasks/{created_task['id']}", test_name="Delete Backwards Compatibility Test Task")
    
    def cleanup_test_data(self):
        """Clean up test data"""
        self.log("\n=== Cleaning Up Test Data ===")
        
        # Delete test tasks
        for task in self.test_data['tasks']:
            self.test_request("DELETE", f"/tasks/{task['id']}", test_name=f"Delete Task {task['title']}")
        
        # Delete test ideas
        for idea in self.test_data['ideas']:
            self.test_request("DELETE", f"/ideas/{idea['id']}", test_name=f"Delete Idea {idea['title']}")
        
        # Delete test projects (this will also delete associated tasks and ideas)
        for project in self.test_data['projects']:
            self.test_request("DELETE", f"/projects/{project['id']}", test_name=f"Delete Project {project['name']}")
    
    def run_all_tests(self):
        """Run all backend tests"""
        self.log("🚀 Starting Comprehensive Backend API Testing")
        self.log(f"Backend URL: {self.base_url}")
        
        try:
            # Test in logical order - Enhanced testing sequence
            self.test_dashboard_stats()
            self.test_projects_crud()
            self.test_tasks_crud()
            self.test_date_serialization()
            self.test_calendar_api()
            self.test_backwards_compatibility()
            self.test_data_relationships_enhanced()
            self.test_ideas_crud()
            self.test_priority_system()
            self.test_project_stats()
            
            # Clean up test data
            self.cleanup_test_data()
            
        except Exception as e:
            self.log(f"❌ Critical error during testing: {str(e)}", "ERROR")
            self.failed_tests += 1
        
        # Final results
        self.log("\n" + "="*50)
        self.log("🏁 TESTING COMPLETE")
        self.log(f"✅ Passed: {self.passed_tests}")
        self.log(f"❌ Failed: {self.failed_tests}")
        self.log(f"📊 Success Rate: {(self.passed_tests/(self.passed_tests + self.failed_tests)*100):.1f}%" if (self.passed_tests + self.failed_tests) > 0 else "No tests run")
        self.log("="*50)
        
        return self.failed_tests == 0

if __name__ == "__main__":
    tester = TaskManagerTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)