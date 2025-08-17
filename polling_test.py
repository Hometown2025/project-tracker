#!/usr/bin/env python3
"""
Focused Testing for Polling-Based Real-time System
Tests the updated polling-based notification and message system
"""

import requests
import json
from datetime import datetime, date, timedelta
import sys
import os

# Get backend URL from frontend .env
BACKEND_URL = "https://house-budget-app.preview.emergentagent.com/api"

class PollingSystemTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_data = {
            'projects': [],
            'tasks': [],
            'conversations': []
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
    
    def setup_authentication(self):
        """Setup admin and demo user authentication"""
        self.log("\n=== Setting up Authentication ===")
        
        # Login as admin
        admin_login = {"username": "admin", "password": "admin"}
        admin_response = self.test_request("POST", "/auth/login", admin_login, 200, "Admin Login")
        
        if admin_response:
            self.admin_token = admin_response.get('session_token')
            self.admin_user = admin_response.get('user')
            self.log("✅ Admin authentication successful")
        else:
            self.log("❌ Admin authentication failed", "ERROR")
            return False
        
        # Login as demo
        demo_login = {"username": "demo", "password": "demo"}
        demo_response = self.test_request("POST", "/auth/login", demo_login, 200, "Demo Login")
        
        if demo_response:
            self.demo_token = demo_response.get('session_token')
            self.demo_user = demo_response.get('user')
            self.log("✅ Demo authentication successful")
        else:
            self.log("❌ Demo authentication failed", "ERROR")
            return False
        
        return True
    
    def test_polling_endpoints(self):
        """Test polling endpoints"""
        self.log("\n=== Testing Polling Endpoints ===")
        
        # Test 1: GET /api/notifications/poll
        notifications = self.test_request("GET", "/notifications/poll", auth_token=self.demo_token, 
                                        test_name="GET /api/notifications/poll")
        
        if notifications is not None:
            self.log(f"✅ Notifications polling endpoint working: {len(notifications)} notifications")
            
            # Verify response structure
            if isinstance(notifications, list):
                self.log("✅ Notifications response is a list")
                if notifications:
                    notification = notifications[0]
                    required_fields = ['id', 'type', 'title', 'message', 'user_id', 'created_at', 'is_read']
                    for field in required_fields:
                        if field in notification:
                            self.log(f"✅ Notification has field '{field}': {notification[field]}")
                        else:
                            self.log(f"❌ Missing notification field: {field}", "ERROR")
                            self.failed_tests += 1
            else:
                self.log("❌ Notifications response is not a list", "ERROR")
                self.failed_tests += 1
        
        # Test 2: POST /api/notifications/mark-read
        mark_read = self.test_request("POST", "/notifications/mark-read", auth_token=self.demo_token, 
                                    test_name="POST /api/notifications/mark-read")
        
        if mark_read:
            self.log("✅ Mark notifications as read endpoint working")
        
        # Test 3: GET /api/messages/poll
        messages_poll = self.test_request("GET", "/messages/poll", auth_token=self.demo_token, 
                                        test_name="GET /api/messages/poll")
        
        if messages_poll is not None:
            if 'unread_count' in messages_poll:
                unread_count = messages_poll['unread_count']
                self.log(f"✅ Messages polling endpoint working: {unread_count} unread messages")
            else:
                self.log("❌ Messages poll response missing 'unread_count' field", "ERROR")
                self.failed_tests += 1
    
    def test_notification_system_with_database(self):
        """Test notification system with database storage"""
        self.log("\n=== Testing Notification System with Database Storage ===")
        
        # Create a project to trigger notifications
        project_data = {
            "name": "Database Notification Test Project",
            "description": "Testing database-stored notifications",
            "color": "#FF5722"
        }
        
        # Assign demo user to receive notifications
        assignment_data = {
            "user_id": self.demo_user['id'],
            "project_ids": []
        }
        
        # Get existing projects first
        existing_projects = self.test_request("GET", "/projects", auth_token=self.admin_token, 
                                            test_name="Get Existing Projects")
        
        if existing_projects:
            project_ids = [p['id'] for p in existing_projects]
            assignment_data['project_ids'] = project_ids
            
            self.test_request("PUT", f"/admin/users/{self.demo_user['id']}/assign-projects", 
                            assignment_data, 200, "Assign Demo User to Existing Projects", 
                            auth_token=self.admin_token)
        
        # Create new project
        created_project = self.test_request("POST", "/projects", project_data, 200, 
                                          "Create Project for Database Notification Test", 
                                          auth_token=self.admin_token)
        
        if created_project:
            self.test_data['projects'].append(created_project)
            project_id = created_project['id']
            
            # Assign demo user to new project
            assignment_data['project_ids'].append(project_id)
            self.test_request("PUT", f"/admin/users/{self.demo_user['id']}/assign-projects", 
                            assignment_data, 200, "Assign Demo User to New Project", 
                            auth_token=self.admin_token)
            
            # Poll for project creation notification
            notifications = self.test_request("GET", "/notifications/poll", auth_token=self.demo_token, 
                                            test_name="Poll for Project Creation Notification")
            
            if notifications:
                project_notifications = [n for n in notifications if n.get('type') == 'project_created']
                if project_notifications:
                    self.log("✅ Project creation notification stored in database and retrieved via polling")
                    
                    # Verify notification is for correct user
                    notification = project_notifications[0]
                    if notification.get('user_id') == self.demo_user['id']:
                        self.log("✅ Notification created for correct user (demo)")
                    else:
                        self.log(f"❌ Notification user_id mismatch: expected {self.demo_user['id']}, got {notification.get('user_id')}", "ERROR")
                        self.failed_tests += 1
                else:
                    self.log("❌ Project creation notification not found in database", "ERROR")
                    self.failed_tests += 1
            
            # Update project to trigger update notification
            update_data = {
                "name": "Updated Database Notification Test Project",
                "description": "Updated for testing",
                "color": "#4CAF50"
            }
            
            updated_project = self.test_request("PUT", f"/projects/{project_id}", update_data, 200, 
                                              "Update Project for Database Notification Test", 
                                              auth_token=self.admin_token)
            
            if updated_project:
                # Poll for project update notification
                update_notifications = self.test_request("GET", "/notifications/poll", auth_token=self.demo_token, 
                                                        test_name="Poll for Project Update Notification")
                
                if update_notifications:
                    project_update_notifications = [n for n in update_notifications if n.get('type') == 'project_updated']
                    if project_update_notifications:
                        self.log("✅ Project update notification stored in database and retrieved via polling")
                    else:
                        self.log("❌ Project update notification not found in database", "ERROR")
                        self.failed_tests += 1
            
            # Create task to trigger task notifications
            task_data = {
                "project_id": project_id,
                "title": "Database Notification Test Task",
                "description": "Testing task notifications in database",
                "priority": "high"
            }
            
            created_task = self.test_request("POST", "/tasks", task_data, 200, 
                                           "Create Task for Database Notification Test", 
                                           auth_token=self.admin_token)
            
            if created_task:
                self.test_data['tasks'].append(created_task)
                task_id = created_task['id']
                
                # Poll for task creation notification
                task_notifications = self.test_request("GET", "/notifications/poll", auth_token=self.demo_token, 
                                                      test_name="Poll for Task Creation Notification")
                
                if task_notifications:
                    task_created_notifications = [n for n in task_notifications if n.get('type') == 'task_created']
                    if task_created_notifications:
                        self.log("✅ Task creation notification stored in database and retrieved via polling")
                    else:
                        self.log("❌ Task creation notification not found in database", "ERROR")
                        self.failed_tests += 1
                
                # Complete task to trigger completion notification
                completion_update = {"completed": True}
                completed_task = self.test_request("PUT", f"/tasks/{task_id}", completion_update, 200, 
                                                 "Complete Task for Database Notification Test", 
                                                 auth_token=self.admin_token)
                
                if completed_task:
                    # Poll for task completion notification
                    completion_notifications = self.test_request("GET", "/notifications/poll", auth_token=self.demo_token, 
                                                               test_name="Poll for Task Completion Notification")
                    
                    if completion_notifications:
                        task_completed_notifications = [n for n in completion_notifications if n.get('type') == 'task_completed']
                        if task_completed_notifications:
                            self.log("✅ Task completion notification stored in database and retrieved via polling")
                        else:
                            self.log("❌ Task completion notification not found in database", "ERROR")
                            self.failed_tests += 1
    
    def test_message_system_integration(self):
        """Test message system integration with polling"""
        self.log("\n=== Testing Message System Integration ===")
        
        # Test message sending and notification creation
        message_data = {
            "content": "Testing message system integration with polling notifications",
            "recipient_type": "admin"
        }
        
        sent_message = self.test_request("POST", "/messages", message_data, 200, 
                                       "Send Message for Integration Test", auth_token=self.demo_token)
        
        if sent_message:
            conversation_id = sent_message['conversation_id']
            self.test_data['conversations'].append({'id': conversation_id})
            self.log(f"✅ Message sent successfully, conversation ID: {conversation_id}")
            
            # Test that message notification was created
            admin_notifications = self.test_request("GET", "/notifications/poll", auth_token=self.admin_token, 
                                                   test_name="Poll for Message Notifications (Admin)")
            
            if admin_notifications:
                message_notifications = [n for n in admin_notifications if n.get('type') == 'message_received']
                if message_notifications:
                    self.log("✅ Message notification created and stored in database")
                    
                    # Verify notification content
                    notification = message_notifications[0]
                    if notification.get('title') == 'New Message':
                        self.log("✅ Message notification has correct title")
                    else:
                        self.log(f"❌ Message notification has incorrect title: {notification.get('title')}", "ERROR")
                        self.failed_tests += 1
                else:
                    self.log("❌ Message notification not created in database", "ERROR")
                    self.failed_tests += 1
            
            # Test conversations still work
            conversations = self.test_request("GET", "/conversations", auth_token=self.demo_token, 
                                            test_name="Get Conversations")
            
            if conversations:
                found_conversation = False
                for conv in conversations:
                    if conv['id'] == conversation_id:
                        found_conversation = True
                        self.log("✅ Conversation found in user's conversation list")
                        break
                
                if not found_conversation:
                    self.log("❌ Conversation not found in user's list", "ERROR")
                    self.failed_tests += 1
            
            # Test messages in conversation
            messages = self.test_request("GET", f"/conversations/{conversation_id}/messages", 
                                       auth_token=self.demo_token, 
                                       test_name="Get Messages in Conversation")
            
            if messages:
                if len(messages) > 0:
                    self.log(f"✅ Retrieved {len(messages)} messages from conversation")
                    
                    # Verify our message is there
                    found_message = False
                    for msg in messages:
                        if msg['content'] == message_data['content']:
                            found_message = True
                            self.log(f"✅ Message found: sender={msg['sender_name']}, role={msg['sender_role']}")
                            break
                    
                    if not found_message:
                        self.log("❌ Sent message not found in conversation", "ERROR")
                        self.failed_tests += 1
                else:
                    self.log("❌ No messages found in conversation", "ERROR")
                    self.failed_tests += 1
            
            # Test unread message polling
            demo_unread = self.test_request("GET", "/messages/poll", auth_token=self.demo_token, 
                                          test_name="Poll Unread Messages (Demo)")
            
            if demo_unread is not None:
                unread_count = demo_unread.get('unread_count', 0)
                self.log(f"✅ Demo user unread message count: {unread_count}")
            
            # Admin replies
            admin_reply = {
                "content": "Admin reply for integration testing",
                "recipient_type": "user",
                "recipient_id": self.demo_user['id']
            }
            
            admin_message = self.test_request("POST", "/messages", admin_reply, 200, 
                                            "Admin Reply for Integration Test", auth_token=self.admin_token)
            
            if admin_message:
                # Test demo user unread count increased
                demo_unread_after = self.test_request("GET", "/messages/poll", auth_token=self.demo_token, 
                                                    test_name="Poll Unread Messages After Admin Reply")
                
                if demo_unread_after is not None:
                    unread_count_after = demo_unread_after.get('unread_count', 0)
                    if unread_count_after > unread_count:
                        self.log(f"✅ Unread message count increased after admin reply: {unread_count_after}")
                    else:
                        self.log(f"❌ Unread message count did not increase: {unread_count_after}", "ERROR")
                        self.failed_tests += 1
    
    def test_database_operations(self):
        """Test database operations for notifications and messages"""
        self.log("\n=== Testing Database Operations ===")
        
        # Test notification database fields
        notifications = self.test_request("GET", "/notifications/poll", auth_token=self.demo_token, 
                                        test_name="Get Notifications for Database Field Test")
        
        if notifications:
            for notification in notifications:
                # Verify is_read field exists and is boolean
                if 'is_read' in notification:
                    is_read = notification['is_read']
                    if isinstance(is_read, bool):
                        self.log(f"✅ Notification is_read field is boolean: {is_read}")
                    else:
                        self.log(f"❌ Notification is_read field is not boolean: {type(is_read)}", "ERROR")
                        self.failed_tests += 1
                else:
                    self.log("❌ Notification missing is_read field", "ERROR")
                    self.failed_tests += 1
                
                # Verify other required fields
                required_fields = ['id', 'type', 'title', 'message', 'user_id', 'created_at']
                for field in required_fields:
                    if field not in notification:
                        self.log(f"❌ Notification missing required field: {field}", "ERROR")
                        self.failed_tests += 1
        
        # Test marking notifications as read updates is_read field
        mark_read_response = self.test_request("POST", "/notifications/mark-read", auth_token=self.demo_token, 
                                             test_name="Mark Notifications Read for Database Test")
        
        if mark_read_response:
            # Verify notifications are now marked as read (should return empty list)
            read_notifications = self.test_request("GET", "/notifications/poll", auth_token=self.demo_token, 
                                                  test_name="Verify Notifications Marked as Read")
            
            if read_notifications is not None:
                if len(read_notifications) == 0:
                    self.log("✅ is_read field updated correctly - no unread notifications returned")
                else:
                    self.log(f"❌ is_read field not updated correctly - {len(read_notifications)} notifications still unread", "ERROR")
                    self.failed_tests += 1
        
        # Test conversation and message data integrity
        if self.test_data['conversations']:
            conversation_id = self.test_data['conversations'][0]['id']
            
            # Get conversation details
            conversations = self.test_request("GET", "/conversations", auth_token=self.demo_token, 
                                            test_name="Get Conversations for Data Integrity Test")
            
            if conversations:
                found_conv = None
                for conv in conversations:
                    if conv['id'] == conversation_id:
                        found_conv = conv
                        break
                
                if found_conv:
                    # Verify conversation data integrity
                    required_conv_fields = ['id', 'participants', 'title', 'created_by', 'created_at', 'last_message_at']
                    for field in required_conv_fields:
                        if field in found_conv:
                            self.log(f"✅ Conversation has field '{field}': {found_conv[field]}")
                        else:
                            self.log(f"❌ Conversation missing field: {field}", "ERROR")
                            self.failed_tests += 1
                    
                    # Verify unread_count field
                    if 'unread_count_for_user' in found_conv:
                        unread_count = found_conv['unread_count_for_user']
                        if isinstance(unread_count, int):
                            self.log(f"✅ Conversation unread_count_for_user is integer: {unread_count}")
                        else:
                            self.log(f"❌ Conversation unread_count_for_user is not integer: {type(unread_count)}", "ERROR")
                            self.failed_tests += 1
    
    def test_authentication_integration(self):
        """Test authentication integration with polling endpoints"""
        self.log("\n=== Testing Authentication Integration ===")
        
        # Test polling endpoints work with authentication
        auth_tests = [
            ("GET", "/notifications/poll", "Notifications Poll with Auth"),
            ("POST", "/notifications/mark-read", "Mark Notifications Read with Auth"),
            ("GET", "/messages/poll", "Messages Poll with Auth")
        ]
        
        for method, endpoint, test_name in auth_tests:
            # Test with valid token
            result = self.test_request(method, endpoint, auth_token=self.demo_token, test_name=f"{test_name} (Valid Token)")
            if result is not None:
                self.log(f"✅ {test_name} works with valid authentication")
            
            # Test without token (should fail)
            result = self.test_request(method, endpoint, expected_status=403, test_name=f"{test_name} (No Token)")
            if result is None:  # Expected to fail
                self.log(f"✅ {test_name} properly rejects requests without authentication")
                self.passed_tests += 1  # Adjust since we expect this to "fail"
        
        # Test role-based access control
        # Admin should be able to see notifications for all projects
        admin_notifications = self.test_request("GET", "/notifications/poll", auth_token=self.admin_token, 
                                               test_name="Admin Notifications Poll")
        
        if admin_notifications is not None:
            self.log(f"✅ Admin can poll notifications: {len(admin_notifications)} notifications")
        
        # Demo user should only see notifications for assigned projects
        demo_notifications = self.test_request("GET", "/notifications/poll", auth_token=self.demo_token, 
                                             test_name="Demo User Notifications Poll")
        
        if demo_notifications is not None:
            self.log(f"✅ Demo user can poll notifications: {len(demo_notifications)} notifications")
    
    def run_polling_tests(self):
        """Run all polling-based system tests"""
        self.log("🚀 Starting Polling-Based Real-time System Testing")
        self.log(f"Backend URL: {self.base_url}")
        
        try:
            # Setup authentication
            if not self.setup_authentication():
                self.log("❌ Authentication setup failed, cannot continue", "ERROR")
                return
            
            # Run polling tests
            self.test_polling_endpoints()
            self.test_notification_system_with_database()
            self.test_message_system_integration()
            self.test_database_operations()
            self.test_authentication_integration()
            
        except Exception as e:
            self.log(f"❌ Critical error during testing: {str(e)}", "ERROR")
            self.failed_tests += 1
        
        # Final results
        self.log("\n" + "="*50)
        self.log("🏁 POLLING SYSTEM TESTING COMPLETE")
        self.log(f"✅ Passed: {self.passed_tests}")
        self.log(f"❌ Failed: {self.failed_tests}")
        self.log(f"📊 Success Rate: {(self.passed_tests / (self.passed_tests + self.failed_tests) * 100):.1f}%")
        
        if self.failed_tests == 0:
            self.log("🎉 ALL POLLING SYSTEM TESTS PASSED!", "SUCCESS")
            return True
        else:
            self.log(f"⚠️  {self.failed_tests} tests failed", "ERROR")
            return False

if __name__ == "__main__":
    tester = PollingSystemTester()
    success = tester.run_polling_tests()
    sys.exit(0 if success else 1)