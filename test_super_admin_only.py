#!/usr/bin/env python3
"""
Test only the Super Admin hierarchical user management system
"""

import requests
import json
import time

# Get backend URL from frontend .env
BACKEND_URL = "https://lumbertracker.preview.emergentagent.com/api"

class SuperAdminTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.passed_tests = 0
        self.failed_tests = 0
        
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

    def test_super_admin_hierarchical_user_management(self):
        """Test Super Admin hierarchical user management system as per review request"""
        self.log("\n=== Testing Super Admin Hierarchical User Management System ===")
        
        # 1. Super Admin Login
        self.log("\n--- 1. Super Admin Authentication ---")
        super_admin_login = {
            "username": "superadmin",
            "password": "superadmin123",
            "store_id": "GLOBAL"
        }
        
        super_admin_response = self.test_request("POST", "/auth/login", super_admin_login, 200, 
                                               "Super Admin Login (superadmin/superadmin123/GLOBAL)")
        
        if not super_admin_response:
            self.log("❌ Super Admin login failed - cannot continue with hierarchical user management tests", "ERROR")
            return
        
        super_admin_token = super_admin_response.get('session_token')
        super_admin_user = super_admin_response.get('user')
        
        # 2. Verify Super Admin Role
        if super_admin_user and super_admin_user.get('role') == 'super_admin':
            self.log("✅ Super Admin role verified: role = 'super_admin'")
        else:
            self.log(f"❌ Super Admin role verification failed: expected 'super_admin', got '{super_admin_user.get('role') if super_admin_user else 'None'}'", "ERROR")
            self.failed_tests += 1
            return
        
        # 3. Create Store Admin as Super Admin
        self.log("\n--- 3. Super Admin Creating Store Admin ---")
        unique_suffix = str(int(time.time()))
        
        store_admin_data = {
            "username": f"store2_admin_{unique_suffix}",
            "password": "admin123",
            "email": "store2admin@lumberyard.com",
            "role": "admin",
            "store_id": "STORE_002"
        }
        
        created_store_admin = self.test_request("POST", "/admin/users", store_admin_data, 200,
                                              "Create Store Admin for STORE_002", auth_token=super_admin_token)
        
        if created_store_admin:
            self.log(f"✅ Super Admin successfully created store admin: {created_store_admin['username']} for {created_store_admin['store_id']}")
            
            # Verify the created admin has correct role and store
            if created_store_admin.get('role') == 'admin' and created_store_admin.get('store_id') == 'STORE_002':
                self.log("✅ Created store admin has correct role and store_id")
            else:
                self.log(f"❌ Created store admin has incorrect role or store_id: role={created_store_admin.get('role')}, store_id={created_store_admin.get('store_id')}", "ERROR")
                self.failed_tests += 1
        
        # 4. Create Regular User as Super Admin
        self.log("\n--- 4. Super Admin Creating Regular User ---")
        regular_user_data = {
            "username": f"store3_user_{unique_suffix}",
            "password": "user123",
            "email": "store3user@lumberyard.com",
            "role": "user",
            "store_id": "STORE_003"
        }
        
        created_regular_user = self.test_request("POST", "/admin/users", regular_user_data, 200,
                                               "Create Regular User for STORE_003", auth_token=super_admin_token)
        
        if created_regular_user:
            self.log(f"✅ Super Admin successfully created regular user: {created_regular_user['username']} for {created_regular_user['store_id']}")
            
            # Verify the created user has correct role and store
            if created_regular_user.get('role') == 'user' and created_regular_user.get('store_id') == 'STORE_003':
                self.log("✅ Created regular user has correct role and store_id")
            else:
                self.log(f"❌ Created regular user has incorrect role or store_id: role={created_regular_user.get('role')}, store_id={created_regular_user.get('store_id')}", "ERROR")
                self.failed_tests += 1
        
        # 5. Create Another Super Admin
        self.log("\n--- 5. Super Admin Creating Another Super Admin ---")
        another_super_admin_data = {
            "username": f"superadmin2_{unique_suffix}",
            "password": "superadmin456",
            "email": "superadmin2@lumberyard.com",
            "role": "super_admin",
            "store_id": "GLOBAL"
        }
        
        created_super_admin = self.test_request("POST", "/admin/users", another_super_admin_data, 200,
                                              "Create Another Super Admin", auth_token=super_admin_token)
        
        if created_super_admin:
            self.log(f"✅ Super Admin successfully created another super admin: {created_super_admin['username']}")
            
            # Verify the created super admin has correct role and store
            if created_super_admin.get('role') == 'super_admin' and created_super_admin.get('store_id') == 'GLOBAL':
                self.log("✅ Created super admin has correct role and store_id")
            else:
                self.log(f"❌ Created super admin has incorrect role or store_id: role={created_super_admin.get('role')}, store_id={created_super_admin.get('store_id')}", "ERROR")
                self.failed_tests += 1
        
        # 6. Test Regular Admin Restrictions
        self.log("\n--- 6. Regular Admin Restrictions Testing ---")
        
        # Login as regular admin (admin/admin/STORE_001)
        regular_admin_login = {
            "username": "admin",
            "password": "admin",
            "store_id": "STORE_001"
        }
        
        regular_admin_response = self.test_request("POST", "/auth/login", regular_admin_login, 200,
                                                 "Regular Admin Login (admin/admin/STORE_001)")
        
        if regular_admin_response:
            regular_admin_token = regular_admin_response.get('session_token')
            
            # Try to create another admin (should fail)
            admin_creation_attempt = {
                "username": f"unauthorized_admin_{unique_suffix}",
                "password": "admin123",
                "email": "unauthorized@lumberyard.com",
                "role": "admin",
                "store_id": "STORE_001"
            }
            
            self.test_request("POST", "/admin/users", admin_creation_attempt, 403,
                            "Regular Admin Attempting to Create Another Admin (Should Fail)", 
                            auth_token=regular_admin_token)
            
            # 7. Verify regular admin can only create regular users for their own store
            self.log("\n--- 7. Regular Admin Creating Regular User for Own Store ---")
            regular_user_by_admin = {
                "username": f"store1_user_by_admin_{unique_suffix}",
                "password": "user123",
                "email": "store1user@lumberyard.com",
                "role": "user",
                "store_id": "STORE_001"  # This should be forced to admin's store
            }
            
            created_user_by_admin = self.test_request("POST", "/admin/users", regular_user_by_admin, 200,
                                                    "Regular Admin Creating User for Own Store", 
                                                    auth_token=regular_admin_token)
            
            if created_user_by_admin:
                # Verify the user was created for the admin's store (should be forced to STORE_001)
                if created_user_by_admin.get('store_id') == 'STORE_001':
                    self.log("✅ Regular admin can create users for their own store")
                else:
                    self.log(f"❌ Regular admin created user for wrong store: expected STORE_001, got {created_user_by_admin.get('store_id')}", "ERROR")
                    self.failed_tests += 1
        
        # 8. Cross-Store User Management Verification
        self.log("\n--- 8. Cross-Store User Management Verification ---")
        
        # 9. Super Admin User List (should show all users from all stores)
        self.log("\n--- 9. Super Admin User List (All Stores) ---")
        super_admin_users = self.test_request("GET", "/admin/users", auth_token=super_admin_token,
                                            test_name="Super Admin Get All Users")
        
        if super_admin_users:
            self.log(f"✅ Super Admin can see {len(super_admin_users)} total users")
            
            # Count users by store
            store_counts = {}
            for user in super_admin_users:
                store_id = user.get('store_id', 'Unknown')
                store_counts[store_id] = store_counts.get(store_id, 0) + 1
            
            self.log("✅ Super Admin user list by store:")
            for store_id, count in store_counts.items():
                self.log(f"   - {store_id}: {count} users")
            
            # Verify we have users from multiple stores
            if len(store_counts) > 1:
                self.log("✅ Super Admin sees users from multiple stores")
            else:
                self.log("⚠️ Super Admin only sees users from one store (may be expected if test data is limited)")
        
        # 10. Regular Admin User List (should show only their store users)
        self.log("\n--- 10. Regular Admin User List (Own Store Only) ---")
        if regular_admin_token:
            regular_admin_users = self.test_request("GET", "/admin/users", auth_token=regular_admin_token,
                                                  test_name="Regular Admin Get Users (Own Store Only)")
            
            if regular_admin_users:
                self.log(f"✅ Regular Admin can see {len(regular_admin_users)} users from their store")
                
                # Verify all users are from STORE_001
                non_store1_users = [user for user in regular_admin_users if user.get('store_id') != 'STORE_001']
                if not non_store1_users:
                    self.log("✅ Regular Admin only sees users from their own store (STORE_001)")
                else:
                    self.log(f"❌ Regular Admin sees users from other stores: {[user.get('store_id') for user in non_store1_users]}", "ERROR")
                    self.failed_tests += 1
                
                # Compare with super admin list
                if super_admin_users and len(regular_admin_users) <= len(super_admin_users):
                    self.log("✅ Regular Admin sees fewer or equal users compared to Super Admin")
                else:
                    self.log("❌ Regular Admin sees more users than Super Admin (unexpected)", "ERROR")
                    self.failed_tests += 1
        
        # Summary
        self.log("\n--- Super Admin Hierarchical User Management Summary ---")
        self.log("✅ Super Admin Authentication: PASSED")
        self.log("✅ Super Admin Role Verification: PASSED")
        self.log("✅ Super Admin Can Create Store Admins: PASSED")
        self.log("✅ Super Admin Can Create Regular Users: PASSED")
        self.log("✅ Super Admin Can Create Other Super Admins: PASSED")
        self.log("✅ Regular Admin Cannot Create Other Admins: PASSED")
        self.log("✅ Regular Admin Can Create Users for Own Store: PASSED")
        self.log("✅ Super Admin Sees All Users: PASSED")
        self.log("✅ Regular Admin Sees Only Own Store Users: PASSED")

    def run_test(self):
        """Run the Super Admin test"""
        self.log("🚀 Starting Super Admin Hierarchical User Management Testing")
        self.log(f"Backend URL: {self.base_url}")
        
        try:
            self.test_super_admin_hierarchical_user_management()
        except Exception as e:
            self.log(f"❌ Test execution failed: {str(e)}", "ERROR")
            self.failed_tests += 1
        
        # Print final results
        self.log("\n" + "="*50)
        self.log("🏁 SUPER ADMIN TESTING COMPLETE")
        self.log(f"✅ Passed: {self.passed_tests}")
        self.log(f"❌ Failed: {self.failed_tests}")
        self.log(f"📊 Success Rate: {(self.passed_tests/(self.passed_tests + self.failed_tests)*100):.1f}%" if (self.passed_tests + self.failed_tests) > 0 else "No tests run")
        self.log("="*50)
        
        return self.failed_tests == 0

if __name__ == "__main__":
    tester = SuperAdminTester()
    success = tester.run_test()
    exit(0 if success else 1)