#!/usr/bin/env python3
"""
Comprehensive File Attachment System Testing
Tests all file upload, retrieval, management, and integration functionality
"""

import requests
import json
import os
import tempfile
from datetime import datetime
import sys
from pathlib import Path

# Get backend URL from frontend .env
BACKEND_URL = "https://lumbertracker.preview.emergentagent.com/api"

class FileAttachmentTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.passed_tests = 0
        self.failed_tests = 0
        self.admin_token = None
        self.demo_token = None
        self.admin_user = None
        self.demo_user = None
        self.test_project_id = None
        self.test_task_id = None
        self.uploaded_files = []
        
    def log(self, message, level="INFO"):
        """Log test messages"""
        print(f"[{level}] {message}")
        
    def test_request(self, method, endpoint, data=None, files=None, expected_status=200, test_name="", auth_token=None):
        """Make HTTP request and validate response"""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                if files:
                    response = self.session.post(url, data=data, files=files, headers=headers)
                else:
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
        admin_response = self.test_request("POST", "/auth/login", admin_login, test_name="Admin Login")
        
        if admin_response:
            self.admin_token = admin_response.get('session_token')
            self.admin_user = admin_response.get('user')
            self.log("✅ Admin authentication successful")
        else:
            self.log("❌ Admin authentication failed", "ERROR")
            return False
        
        # Login as demo user
        demo_login = {"username": "demo", "password": "demo"}
        demo_response = self.test_request("POST", "/auth/login", demo_login, test_name="Demo Login")
        
        if demo_response:
            self.demo_token = demo_response.get('session_token')
            self.demo_user = demo_response.get('user')
            self.log("✅ Demo authentication successful")
        else:
            self.log("❌ Demo authentication failed", "ERROR")
            return False
        
        return True
    
    def setup_test_data(self):
        """Create test project and task for file attachment testing"""
        self.log("\n=== Setting up Test Data ===")
        
        # Create test project
        project_data = {
            "name": "File Attachment Test Project",
            "description": "Project for testing file attachments",
            "color": "#FF6B6B"
        }
        
        project = self.test_request("POST", "/projects", project_data, auth_token=self.admin_token, test_name="Create Test Project")
        
        if project:
            self.test_project_id = project['id']
            self.log(f"✅ Test project created: {self.test_project_id}")
            
            # Assign demo user to project
            assignment_data = {
                "user_id": self.demo_user['id'],
                "project_ids": [self.test_project_id]
            }
            
            self.test_request("PUT", f"/admin/users/{self.demo_user['id']}/assign-projects", 
                            assignment_data, auth_token=self.admin_token, test_name="Assign Demo User to Project")
        else:
            self.log("❌ Failed to create test project", "ERROR")
            return False
        
        # Create test task
        task_data = {
            "project_id": self.test_project_id,
            "title": "File Attachment Test Task",
            "description": "Task for testing file attachments",
            "priority": "high"
        }
        
        task = self.test_request("POST", "/tasks", task_data, auth_token=self.admin_token, test_name="Create Test Task")
        
        if task:
            self.test_task_id = task['id']
            self.log(f"✅ Test task created: {self.test_task_id}")
        else:
            self.log("❌ Failed to create test task", "ERROR")
            return False
        
        return True
    
    def create_test_files(self):
        """Create various test files for upload testing"""
        test_files = {}
        
        # Create a small text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test text file for file attachment testing.\nIt contains multiple lines.\nEnd of file.")
            test_files['text'] = f.name
        
        # Create a small JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"test": "data", "numbers": [1, 2, 3], "nested": {"key": "value"}}, f)
            test_files['json'] = f.name
        
        # Create a small CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Name,Age,City\nJohn,25,New York\nJane,30,Los Angeles\nBob,35,Chicago")
            test_files['csv'] = f.name
        
        # Create a small image file (1x1 PNG)
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(png_data)
            test_files['image'] = f.name
        
        # Create a large file for size limit testing (simulate 60MB file)
        large_file_path = tempfile.mktemp(suffix='.txt')
        with open(large_file_path, 'w') as f:
            # Write approximately 60MB of data
            chunk = "A" * 1024  # 1KB chunk
            for _ in range(60 * 1024):  # 60MB
                f.write(chunk)
        test_files['large'] = large_file_path
        
        return test_files
    
    def test_file_upload_endpoints(self):
        """Test file upload endpoints with various scenarios"""
        self.log("\n=== Testing File Upload Endpoints ===")
        
        test_files = self.create_test_files()
        
        # Test 1: Upload file to project (admin)
        with open(test_files['text'], 'rb') as f:
            files = {'file': ('test_document.txt', f, 'text/plain')}
            data = {'project_id': self.test_project_id}
            
            response = self.test_request("POST", "/files/upload", data=data, files=files, 
                                       auth_token=self.admin_token, test_name="Upload File to Project (Admin)")
            
            if response:
                self.uploaded_files.append(response)
                self.log(f"✅ File uploaded: {response['filename']}, Size: {response['file_size']} bytes")
                
                # Verify file metadata
                if response.get('file_type') == 'document':
                    self.log("✅ File type correctly identified as document")
                else:
                    self.log(f"❌ File type incorrect: expected 'document', got '{response.get('file_type')}'", "ERROR")
                    self.failed_tests += 1
        
        # Test 2: Upload file to task (admin)
        with open(test_files['json'], 'rb') as f:
            files = {'file': ('config.json', f, 'application/json')}
            data = {'task_id': self.test_task_id}
            
            response = self.test_request("POST", "/files/upload", data=data, files=files, 
                                       auth_token=self.admin_token, test_name="Upload File to Task (Admin)")
            
            if response:
                self.uploaded_files.append(response)
                self.log(f"✅ File uploaded to task: {response['filename']}")
        
        # Test 3: Upload image file (should create thumbnail)
        with open(test_files['image'], 'rb') as f:
            files = {'file': ('test_image.png', f, 'image/png')}
            data = {'project_id': self.test_project_id}
            
            response = self.test_request("POST", "/files/upload", data=data, files=files, 
                                       auth_token=self.admin_token, test_name="Upload Image File (Admin)")
            
            if response:
                self.uploaded_files.append(response)
                self.log(f"✅ Image file uploaded: {response['filename']}")
                
                if response.get('file_type') == 'image':
                    self.log("✅ Image file type correctly identified")
                else:
                    self.log(f"❌ Image file type incorrect: expected 'image', got '{response.get('file_type')}'", "ERROR")
                    self.failed_tests += 1
        
        # Test 4: Upload file as demo user (with permissions)
        with open(test_files['csv'], 'rb') as f:
            files = {'file': ('data.csv', f, 'text/csv')}
            data = {'project_id': self.test_project_id}
            
            response = self.test_request("POST", "/files/upload", data=data, files=files, 
                                       auth_token=self.demo_token, test_name="Upload File to Project (Demo User)")
            
            if response:
                self.uploaded_files.append(response)
                self.log("✅ Demo user can upload files to assigned project")
        
        # Test 5: File size validation (50MB limit)
        with open(test_files['large'], 'rb') as f:
            files = {'file': ('large_file.txt', f, 'text/plain')}
            data = {'project_id': self.test_project_id}
            
            self.test_request("POST", "/files/upload", data=data, files=files, expected_status=400,
                            auth_token=self.admin_token, test_name="Upload Large File (Should Fail - Size Limit)")
        
        # Test 6: Invalid file type (create a file with unsupported extension)
        invalid_file_path = tempfile.mktemp(suffix='.exe')
        with open(invalid_file_path, 'w') as f:
            f.write("fake executable content")
        
        with open(invalid_file_path, 'rb') as f:
            files = {'file': ('malware.exe', f, 'application/octet-stream')}
            data = {'project_id': self.test_project_id}
            
            self.test_request("POST", "/files/upload", data=data, files=files, expected_status=400,
                            auth_token=self.admin_token, test_name="Upload Invalid File Type (Should Fail)")
        
        # Test 7: Upload without authentication
        with open(test_files['text'], 'rb') as f:
            files = {'file': ('unauthorized.txt', f, 'text/plain')}
            data = {'project_id': self.test_project_id}
            
            self.test_request("POST", "/files/upload", data=data, files=files, expected_status=403,
                            test_name="Upload File Without Authentication (Should Fail)")
        
        # Test 8: Upload to non-existent project
        with open(test_files['text'], 'rb') as f:
            files = {'file': ('test.txt', f, 'text/plain')}
            data = {'project_id': 'non-existent-project-id'}
            
            self.test_request("POST", "/files/upload", data=data, files=files, expected_status=404,
                            auth_token=self.admin_token, test_name="Upload to Non-existent Project (Should Fail)")
        
        # Test 9: Upload to non-existent task
        with open(test_files['text'], 'rb') as f:
            files = {'file': ('test.txt', f, 'text/plain')}
            data = {'task_id': 'non-existent-task-id'}
            
            self.test_request("POST", "/files/upload", data=data, files=files, expected_status=404,
                            auth_token=self.admin_token, test_name="Upload to Non-existent Task (Should Fail)")
        
        # Clean up test files
        for file_path in test_files.values():
            try:
                os.unlink(file_path)
            except:
                pass
        
        try:
            os.unlink(invalid_file_path)
        except:
            pass
    
    def test_file_retrieval_endpoints(self):
        """Test file retrieval endpoints"""
        self.log("\n=== Testing File Retrieval Endpoints ===")
        
        if not self.uploaded_files:
            self.log("❌ No uploaded files available for retrieval testing", "ERROR")
            return
        
        # Test 1: Get files for project
        project_files = self.test_request("GET", f"/files/project/{self.test_project_id}", 
                                        auth_token=self.admin_token, test_name="Get Project Files (Admin)")
        
        if project_files:
            self.log(f"✅ Retrieved {len(project_files)} files for project")
            
            # Verify file metadata structure
            for file_obj in project_files:
                required_fields = ['id', 'filename', 'original_filename', 'file_size', 'file_type', 
                                 'mime_type', 'uploaded_by', 'uploaded_at', 'project_id']
                
                for field in required_fields:
                    if field not in file_obj:
                        self.log(f"❌ Missing field '{field}' in file metadata", "ERROR")
                        self.failed_tests += 1
                    else:
                        self.log(f"✅ File metadata field '{field}': {file_obj[field]}")
        
        # Test 2: Get files for task
        task_files = self.test_request("GET", f"/files/task/{self.test_task_id}", 
                                     auth_token=self.admin_token, test_name="Get Task Files (Admin)")
        
        if task_files:
            self.log(f"✅ Retrieved {len(task_files)} files for task")
        
        # Test 3: Demo user access to project files (should work - assigned to project)
        demo_project_files = self.test_request("GET", f"/files/project/{self.test_project_id}", 
                                             auth_token=self.demo_token, test_name="Get Project Files (Demo User)")
        
        if demo_project_files is not None:
            self.log(f"✅ Demo user can access project files: {len(demo_project_files)} files")
        
        # Test 4: Demo user access to task files (should work - task in assigned project)
        demo_task_files = self.test_request("GET", f"/files/task/{self.test_task_id}", 
                                           auth_token=self.demo_token, test_name="Get Task Files (Demo User)")
        
        if demo_task_files is not None:
            self.log(f"✅ Demo user can access task files: {len(demo_task_files)} files")
        
        # Test 5: Access files without authentication
        self.test_request("GET", f"/files/project/{self.test_project_id}", expected_status=403,
                        test_name="Get Project Files Without Auth (Should Fail)")
        
        # Test 6: Access non-existent project files
        self.test_request("GET", "/files/project/non-existent-project", expected_status=404,
                        auth_token=self.admin_token, test_name="Get Non-existent Project Files (Should Fail)")
        
        # Test 7: Access non-existent task files
        self.test_request("GET", "/files/task/non-existent-task", expected_status=404,
                        auth_token=self.admin_token, test_name="Get Non-existent Task Files (Should Fail)")
    
    def test_file_download_endpoints(self):
        """Test file download and thumbnail endpoints"""
        self.log("\n=== Testing File Download Endpoints ===")
        
        if not self.uploaded_files:
            self.log("❌ No uploaded files available for download testing", "ERROR")
            return
        
        # Test 1: Download file (admin)
        file_id = self.uploaded_files[0]['file_id']
        download_response = self.test_request("GET", f"/files/download/{file_id}", 
                                            auth_token=self.admin_token, test_name="Download File (Admin)")
        
        if download_response:
            self.log("✅ File download successful (Admin)")
        
        # Test 2: Download file (demo user - should work if has access)
        demo_download = self.test_request("GET", f"/files/download/{file_id}", 
                                        auth_token=self.demo_token, test_name="Download File (Demo User)")
        
        if demo_download:
            self.log("✅ File download successful (Demo User)")
        
        # Test 3: Download without authentication
        self.test_request("GET", f"/files/download/{file_id}", expected_status=403,
                        test_name="Download File Without Auth (Should Fail)")
        
        # Test 4: Download non-existent file
        self.test_request("GET", "/files/download/non-existent-file-id", expected_status=404,
                        auth_token=self.admin_token, test_name="Download Non-existent File (Should Fail)")
        
        # Test 5: Get thumbnail for image file (if we uploaded an image)
        image_files = [f for f in self.uploaded_files if f.get('file_type') == 'image']
        
        if image_files:
            image_file_id = image_files[0]['file_id']
            thumbnail_response = self.test_request("GET", f"/files/thumbnail/{image_file_id}", 
                                                 auth_token=self.admin_token, test_name="Get Image Thumbnail (Admin)")
            
            if thumbnail_response:
                self.log("✅ Image thumbnail retrieval successful")
            
            # Test thumbnail access for demo user
            demo_thumbnail = self.test_request("GET", f"/files/thumbnail/{image_file_id}", 
                                             auth_token=self.demo_token, test_name="Get Image Thumbnail (Demo User)")
            
            if demo_thumbnail:
                self.log("✅ Image thumbnail retrieval successful (Demo User)")
        
        # Test 6: Get thumbnail for non-image file (should fail)
        non_image_files = [f for f in self.uploaded_files if f.get('file_type') != 'image']
        
        if non_image_files:
            non_image_file_id = non_image_files[0]['file_id']
            self.test_request("GET", f"/files/thumbnail/{non_image_file_id}", expected_status=404,
                            auth_token=self.admin_token, test_name="Get Thumbnail for Non-image (Should Fail)")
    
    def test_file_management_endpoints(self):
        """Test file deletion and management"""
        self.log("\n=== Testing File Management Endpoints ===")
        
        if not self.uploaded_files:
            self.log("❌ No uploaded files available for management testing", "ERROR")
            return
        
        # Test 1: Delete file as admin (should work)
        if len(self.uploaded_files) > 1:
            file_to_delete = self.uploaded_files[-1]  # Delete the last uploaded file
            file_id = file_to_delete['file_id']
            
            delete_response = self.test_request("DELETE", f"/files/{file_id}", 
                                              auth_token=self.admin_token, test_name="Delete File (Admin)")
            
            if delete_response:
                self.log("✅ File deletion successful (Admin)")
                self.uploaded_files.remove(file_to_delete)
                
                # Verify file is actually deleted
                self.test_request("GET", f"/files/download/{file_id}", expected_status=404,
                                auth_token=self.admin_token, test_name="Verify File Deleted")
        
        # Test 2: Delete file as uploader (demo user should be able to delete their own files)
        demo_uploaded_files = [f for f in self.uploaded_files if f.get('uploaded_by') == self.demo_user['id']]
        
        if demo_uploaded_files:
            file_to_delete = demo_uploaded_files[0]
            file_id = file_to_delete['file_id']
            
            delete_response = self.test_request("DELETE", f"/files/{file_id}", 
                                              auth_token=self.demo_token, test_name="Delete Own File (Demo User)")
            
            if delete_response:
                self.log("✅ Demo user can delete own files")
                self.uploaded_files.remove(file_to_delete)
        
        # Test 3: Delete file without authentication
        if self.uploaded_files:
            file_id = self.uploaded_files[0]['file_id']
            self.test_request("DELETE", f"/files/{file_id}", expected_status=403,
                            test_name="Delete File Without Auth (Should Fail)")
        
        # Test 4: Delete non-existent file
        self.test_request("DELETE", "/files/non-existent-file-id", expected_status=404,
                        auth_token=self.admin_token, test_name="Delete Non-existent File (Should Fail)")
        
        # Test 5: Demo user trying to delete admin's file (should fail)
        admin_files = [f for f in self.uploaded_files if f.get('uploaded_by') == self.admin_user['id']]
        
        if admin_files:
            admin_file_id = admin_files[0]['file_id']
            self.test_request("DELETE", f"/files/{admin_file_id}", expected_status=403,
                            auth_token=self.demo_token, test_name="Delete Admin File as Demo User (Should Fail)")
    
    def test_integration_with_projects_tasks(self):
        """Test integration with projects and tasks (file_count fields)"""
        self.log("\n=== Testing Integration with Projects/Tasks ===")
        
        # Test 1: Verify project includes file_count field
        project = self.test_request("GET", f"/projects/{self.test_project_id}", 
                                  auth_token=self.admin_token, test_name="Get Project with File Count")
        
        if project:
            if 'file_count' in project:
                file_count = project['file_count']
                self.log(f"✅ Project file_count field present: {file_count}")
                
                # Verify file count matches actual files
                project_files = self.test_request("GET", f"/files/project/{self.test_project_id}", 
                                                auth_token=self.admin_token, test_name="Verify Project File Count")
                
                if project_files and len(project_files) == file_count:
                    self.log("✅ Project file_count matches actual files")
                elif project_files:
                    self.log(f"❌ Project file_count mismatch: expected {len(project_files)}, got {file_count}", "ERROR")
                    self.failed_tests += 1
            else:
                self.log("❌ Project missing file_count field", "ERROR")
                self.failed_tests += 1
        
        # Test 2: Verify task includes file_count field
        task = self.test_request("GET", f"/tasks/{self.test_task_id}", 
                               auth_token=self.admin_token, test_name="Get Task with File Count")
        
        if task:
            if 'file_count' in task:
                file_count = task['file_count']
                self.log(f"✅ Task file_count field present: {file_count}")
                
                # Verify file count matches actual files
                task_files = self.test_request("GET", f"/files/task/{self.test_task_id}", 
                                             auth_token=self.admin_token, test_name="Verify Task File Count")
                
                if task_files and len(task_files) == file_count:
                    self.log("✅ Task file_count matches actual files")
                elif task_files:
                    self.log(f"❌ Task file_count mismatch: expected {len(task_files)}, got {file_count}", "ERROR")
                    self.failed_tests += 1
            else:
                self.log("❌ Task missing file_count field", "ERROR")
                self.failed_tests += 1
        
        # Test 3: Verify file counts in project list
        projects = self.test_request("GET", "/projects", auth_token=self.admin_token, test_name="Get All Projects with File Counts")
        
        if projects:
            test_project = next((p for p in projects if p['id'] == self.test_project_id), None)
            if test_project and 'file_count' in test_project:
                self.log(f"✅ Project list includes file_count: {test_project['file_count']}")
            else:
                self.log("❌ Project list missing file_count field", "ERROR")
                self.failed_tests += 1
        
        # Test 4: Verify file counts in task list
        tasks = self.test_request("GET", "/tasks", auth_token=self.admin_token, test_name="Get All Tasks with File Counts")
        
        if tasks:
            test_task = next((t for t in tasks if t['id'] == self.test_task_id), None)
            if test_task and 'file_count' in test_task:
                self.log(f"✅ Task list includes file_count: {test_task['file_count']}")
            else:
                self.log("❌ Task list missing file_count field", "ERROR")
                self.failed_tests += 1
        
        # Test 5: Upload another file and verify counts update
        test_file_path = tempfile.mktemp(suffix='.txt')
        with open(test_file_path, 'w') as f:
            f.write("Test file for count verification")
        
        with open(test_file_path, 'rb') as f:
            files = {'file': ('count_test.txt', f, 'text/plain')}
            data = {'project_id': self.test_project_id}
            
            upload_response = self.test_request("POST", "/files/upload", data=data, files=files, 
                                              auth_token=self.admin_token, test_name="Upload File for Count Test")
            
            if upload_response:
                self.uploaded_files.append(upload_response)
                
                # Check if project file count increased
                updated_project = self.test_request("GET", f"/projects/{self.test_project_id}", 
                                                  auth_token=self.admin_token, test_name="Verify Updated Project File Count")
                
                if updated_project and updated_project.get('file_count', 0) > project.get('file_count', 0):
                    self.log("✅ Project file_count updated after file upload")
                else:
                    self.log("❌ Project file_count not updated after file upload", "ERROR")
                    self.failed_tests += 1
        
        # Clean up
        try:
            os.unlink(test_file_path)
        except:
            pass
    
    def test_database_operations(self):
        """Test database operations for file attachments"""
        self.log("\n=== Testing Database Operations ===")
        
        if not self.uploaded_files:
            self.log("❌ No uploaded files available for database testing", "ERROR")
            return
        
        # Test 1: Verify file metadata is stored correctly
        project_files = self.test_request("GET", f"/files/project/{self.test_project_id}", 
                                        auth_token=self.admin_token, test_name="Get Files for Database Verification")
        
        if project_files:
            for file_obj in project_files:
                # Verify required database fields
                required_fields = {
                    'id': str,
                    'filename': str,
                    'original_filename': str,
                    'file_size': int,
                    'file_type': str,
                    'mime_type': str,
                    'uploaded_by': str,
                    'uploaded_at': str,
                    'project_id': str
                }
                
                for field, expected_type in required_fields.items():
                    if field in file_obj:
                        value = file_obj[field]
                        if field == 'uploaded_at':
                            # Verify datetime format
                            try:
                                datetime.fromisoformat(value.replace('Z', '+00:00'))
                                self.log(f"✅ Database field '{field}' has valid datetime format")
                            except:
                                self.log(f"❌ Database field '{field}' has invalid datetime format: {value}", "ERROR")
                                self.failed_tests += 1
                        elif field == 'file_size' and isinstance(value, int) and value > 0:
                            self.log(f"✅ Database field '{field}' has valid size: {value} bytes")
                        elif field in ['id', 'uploaded_by', 'project_id'] and isinstance(value, str) and len(value) > 0:
                            self.log(f"✅ Database field '{field}' has valid UUID format")
                        elif isinstance(value, expected_type) and value:
                            self.log(f"✅ Database field '{field}' stored correctly: {value}")
                        else:
                            self.log(f"❌ Database field '{field}' invalid: {value} (type: {type(value)})", "ERROR")
                            self.failed_tests += 1
                    else:
                        self.log(f"❌ Database missing required field: {field}", "ERROR")
                        self.failed_tests += 1
                
                # Verify file is properly linked to project
                if file_obj.get('project_id') == self.test_project_id:
                    self.log("✅ File properly linked to project")
                else:
                    self.log(f"❌ File not properly linked to project: expected {self.test_project_id}, got {file_obj.get('project_id')}", "ERROR")
                    self.failed_tests += 1
        
        # Test 2: Verify task file linking
        task_files = self.test_request("GET", f"/files/task/{self.test_task_id}", 
                                     auth_token=self.admin_token, test_name="Get Task Files for Database Verification")
        
        if task_files:
            for file_obj in task_files:
                if file_obj.get('task_id') == self.test_task_id:
                    self.log("✅ File properly linked to task")
                else:
                    self.log(f"❌ File not properly linked to task: expected {self.test_task_id}, got {file_obj.get('task_id')}", "ERROR")
                    self.failed_tests += 1
        
        # Test 3: Verify image files have is_image flag set correctly
        image_files = [f for f in project_files if f.get('file_type') == 'image']
        
        for image_file in image_files:
            if image_file.get('is_image') is True:
                self.log("✅ Image file has is_image flag set correctly")
            else:
                self.log(f"❌ Image file missing is_image flag: {image_file.get('is_image')}", "ERROR")
                self.failed_tests += 1
        
        # Test 4: Verify non-image files have is_image flag set to False
        non_image_files = [f for f in project_files if f.get('file_type') != 'image']
        
        for non_image_file in non_image_files:
            if non_image_file.get('is_image') is False:
                self.log("✅ Non-image file has is_image flag set correctly")
            else:
                self.log(f"❌ Non-image file has incorrect is_image flag: {non_image_file.get('is_image')}", "ERROR")
                self.failed_tests += 1
    
    def test_role_based_access_control(self):
        """Test role-based access control for file operations"""
        self.log("\n=== Testing Role-Based Access Control ===")
        
        # Create a project that demo user is NOT assigned to
        unassigned_project_data = {
            "name": "Unassigned Project for RBAC Test",
            "description": "Project demo user should not access",
            "color": "#FF0000"
        }
        
        unassigned_project = self.test_request("POST", "/projects", unassigned_project_data, 
                                             auth_token=self.admin_token, test_name="Create Unassigned Project")
        
        if unassigned_project:
            unassigned_project_id = unassigned_project['id']
            
            # Test 1: Demo user should not be able to upload to unassigned project
            test_file_path = tempfile.mktemp(suffix='.txt')
            with open(test_file_path, 'w') as f:
                f.write("RBAC test file")
            
            with open(test_file_path, 'rb') as f:
                files = {'file': ('rbac_test.txt', f, 'text/plain')}
                data = {'project_id': unassigned_project_id}
                
                self.test_request("POST", "/files/upload", data=data, files=files, expected_status=403,
                                auth_token=self.demo_token, test_name="Upload to Unassigned Project (Should Fail)")
            
            # Test 2: Admin uploads file to unassigned project
            with open(test_file_path, 'rb') as f:
                files = {'file': ('admin_rbac_test.txt', f, 'text/plain')}
                data = {'project_id': unassigned_project_id}
                
                admin_upload = self.test_request("POST", "/files/upload", data=data, files=files, 
                                                auth_token=self.admin_token, test_name="Admin Upload to Unassigned Project")
                
                if admin_upload:
                    # Test 3: Demo user should not be able to access files from unassigned project
                    self.test_request("GET", f"/files/project/{unassigned_project_id}", expected_status=403,
                                    auth_token=self.demo_token, test_name="Access Unassigned Project Files (Should Fail)")
                    
                    # Test 4: Demo user should not be able to download files from unassigned project
                    file_id = admin_upload['file_id']
                    self.test_request("GET", f"/files/download/{file_id}", expected_status=403,
                                    auth_token=self.demo_token, test_name="Download Unassigned Project File (Should Fail)")
                    
                    # Test 5: Admin can access and download
                    admin_files = self.test_request("GET", f"/files/project/{unassigned_project_id}", 
                                                  auth_token=self.admin_token, test_name="Admin Access Unassigned Project Files")
                    
                    if admin_files:
                        self.log("✅ Admin can access all project files")
                    
                    admin_download = self.test_request("GET", f"/files/download/{file_id}", 
                                                     auth_token=self.admin_token, test_name="Admin Download Any File")
                    
                    if admin_download:
                        self.log("✅ Admin can download any file")
            
            # Clean up
            try:
                os.unlink(test_file_path)
            except:
                pass
            
            # Delete the unassigned project
            self.test_request("DELETE", f"/projects/{unassigned_project_id}", 
                            auth_token=self.admin_token, test_name="Clean up Unassigned Project")
    
    def cleanup_test_data(self):
        """Clean up test data"""
        self.log("\n=== Cleaning up Test Data ===")
        
        # Delete remaining uploaded files
        for file_info in self.uploaded_files:
            file_id = file_info['file_id']
            self.test_request("DELETE", f"/files/{file_id}", 
                            auth_token=self.admin_token, test_name=f"Delete File {file_id}")
        
        # Delete test task
        if self.test_task_id:
            self.test_request("DELETE", f"/tasks/{self.test_task_id}", 
                            auth_token=self.admin_token, test_name="Delete Test Task")
        
        # Delete test project
        if self.test_project_id:
            self.test_request("DELETE", f"/projects/{self.test_project_id}", 
                            auth_token=self.admin_token, test_name="Delete Test Project")
    
    def run_all_tests(self):
        """Run all file attachment tests"""
        self.log("🚀 Starting Comprehensive File Attachment System Testing")
        self.log(f"Backend URL: {self.base_url}")
        
        # Setup
        if not self.setup_authentication():
            self.log("❌ Authentication setup failed, aborting tests", "ERROR")
            return
        
        if not self.setup_test_data():
            self.log("❌ Test data setup failed, aborting tests", "ERROR")
            return
        
        # Run tests
        try:
            self.test_file_upload_endpoints()
            self.test_file_retrieval_endpoints()
            self.test_file_download_endpoints()
            self.test_file_management_endpoints()
            self.test_integration_with_projects_tasks()
            self.test_database_operations()
            self.test_role_based_access_control()
        finally:
            # Always cleanup
            self.cleanup_test_data()
        
        # Summary
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.log(f"\n{'='*60}")
        self.log(f"📊 FILE ATTACHMENT SYSTEM TEST SUMMARY")
        self.log(f"{'='*60}")
        self.log(f"✅ Passed: {self.passed_tests}")
        self.log(f"❌ Failed: {self.failed_tests}")
        self.log(f"📈 Success Rate: {success_rate:.1f}%")
        self.log(f"{'='*60}")
        
        if self.failed_tests == 0:
            self.log("🎉 ALL FILE ATTACHMENT TESTS PASSED!", "SUCCESS")
            return True
        else:
            self.log(f"⚠️  {self.failed_tests} tests failed. Please review the errors above.", "ERROR")
            return False

if __name__ == "__main__":
    tester = FileAttachmentTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)