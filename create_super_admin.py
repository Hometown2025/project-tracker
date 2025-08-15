#!/usr/bin/env python3
"""
Create super admin user that can manage all stores
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
DATABASE_NAME = os.environ.get('DB_NAME', 'test_database')

def hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + pwd_hash.hex()

async def create_super_admin():
    """Create super admin user that can manage all stores"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DATABASE_NAME]
    
    print("Creating Super Admin user...")
    
    # Super admin details
    super_admin_data = {
        "username": "superadmin",
        "password": "superadmin123",
        "email": "superadmin@lumberyard.com",
        "role": "super_admin",
        "store_id": "GLOBAL"  # Special store ID for super admin
    }
    
    # Check if super admin already exists
    existing_super_admin = await db.users.find_one({
        "username": super_admin_data["username"],
        "role": "super_admin"
    })
    
    if existing_super_admin:
        print("⏭️  Super Admin already exists")
        print(f"Username: {super_admin_data['username']}")
        print(f"Store ID: GLOBAL")
        return
    
    # Create super admin user
    user = {
        "id": str(uuid.uuid4()),
        "username": super_admin_data["username"],
        "email": super_admin_data["email"],
        "role": super_admin_data["role"],
        "store_id": super_admin_data["store_id"],
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
        "password_hash": hash_password(super_admin_data["password"])
    }
    await db.user_passwords.insert_one(password_record)
    
    print("✅ Super Admin created successfully!")
    print("=" * 50)
    print("🔑 SUPER ADMIN LOGIN CREDENTIALS:")
    print(f"Store ID: {super_admin_data['store_id']}")
    print(f"Username: {super_admin_data['username']}")
    print(f"Password: {super_admin_data['password']}")
    print("=" * 50)
    print("\n🌟 SUPER ADMIN CAPABILITIES:")
    print("• Can view all stores and their data")
    print("• Can create admins for any store")
    print("• Can create regular users for any store")
    print("• Can manage users across all lumber yards")
    print("• Can assign projects to users in any store")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_super_admin())