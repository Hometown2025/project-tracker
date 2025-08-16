#!/usr/bin/env python3
"""
Create test users for different lumber yard stores
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import hashlib
import secrets
import uuid

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DATABASE_NAME = 'taskflow_db'

def hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + pwd_hash.hex()

async def create_test_stores():
    """Create test users for different lumber yard stores"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DATABASE_NAME]
    
    print("Creating test users for different lumber yard stores...")
    
    # Test stores and their users
    stores_data = [
        {
            "store_id": "STORE_001",
            "store_name": "Downtown Lumberyard",
            "users": [
                {"username": "admin", "password": "admin", "role": "admin", "email": "admin@downtown.lumber"},
                {"username": "demo", "password": "demo", "role": "customer", "email": "demo@downtown.lumber"},
                {"username": "john", "password": "john123", "role": "customer", "email": "john@downtown.lumber"},
            ]
        },
        {
            "store_id": "STORE_002", 
            "store_name": "Northside Lumber Co",
            "users": [
                {"username": "manager", "password": "manager123", "role": "admin", "email": "manager@northside.lumber"},
                {"username": "sarah", "password": "sarah123", "role": "user", "email": "sarah@northside.lumber"},
                {"username": "mike", "password": "mike123", "role": "user", "email": "mike@northside.lumber"},
            ]
        },
        {
            "store_id": "STORE_003",
            "store_name": "Westend Building Supply", 
            "users": [
                {"username": "supervisor", "password": "super123", "role": "admin", "email": "supervisor@westend.lumber"},
                {"username": "emma", "password": "emma123", "role": "user", "email": "emma@westend.lumber"},
            ]
        }
    ]
    
    for store in stores_data:
        print(f"\n--- Creating users for {store['store_name']} (ID: {store['store_id']}) ---")
        
        for user_data in store["users"]:
            # Check if user already exists
            existing_user = await db.users.find_one({
                "username": user_data["username"],
                "store_id": store["store_id"]
            })
            
            if existing_user:
                print(f"  ⏭️  User {user_data['username']} already exists for {store['store_id']}")
                continue
            
            # Create user
            user = {
                "id": str(uuid.uuid4()),
                "username": user_data["username"],
                "email": user_data["email"],
                "role": user_data["role"],
                "store_id": store["store_id"],
                "assigned_projects": [],
                "created_date": datetime.utcnow(),
                "last_login": None,
                "is_active": True
            }
            
            # Insert user
            await db.users.insert_one(user)
            
            # Create password record
            password_record = {
                "user_id": user["id"],
                "password_hash": hash_password(user_data["password"])
            }
            await db.user_passwords.insert_one(password_record)
            
            print(f"  ✅ Created {user_data['role']} user: {user_data['username']} (password: {user_data['password']})")
    
    print("\n🎉 Test stores and users created successfully!")
    print("\n📋 Login credentials:")
    print("=" * 50)
    
    for store in stores_data:
        print(f"\n{store['store_name']} (Store ID: {store['store_id']}):")
        for user_data in store["users"]:
            role_badge = "👑 ADMIN" if user_data["role"] == "admin" else "👤 USER"
            print(f"  {role_badge} {user_data['username']} / {user_data['password']}")
    
    print("\n💡 To test multi-tenancy:")
    print("1. Login with admin/admin from STORE_001")
    print("2. Create some projects and ideas")
    print("3. Login with manager/manager123 from STORE_002") 
    print("4. Verify you don't see STORE_001's data")
    print("5. Create different projects for STORE_002")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_test_stores())