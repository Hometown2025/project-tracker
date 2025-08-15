#!/usr/bin/env python3
"""
Setup multi-store users for testing
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
import hashlib
import secrets
import uuid
from datetime import datetime

ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

def hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + pwd_hash.hex()

async def setup_multistore_users():
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    print("Setting up multi-store users...")
    
    # Update existing admin user to have STORE_001
    admin_user = await db.users.find_one({"username": "admin"})
    if admin_user:
        await db.users.update_one(
            {"username": "admin"},
            {"$set": {"store_id": "STORE_001"}}
        )
        print("✅ Updated admin user with STORE_001")
    
    # Update existing demo user to have STORE_001
    demo_user = await db.users.find_one({"username": "demo"})
    if demo_user:
        await db.users.update_one(
            {"username": "demo"},
            {"$set": {"store_id": "STORE_001"}}
        )
        print("✅ Updated demo user with STORE_001")
    
    # Create manager user for STORE_002
    manager_exists = await db.users.find_one({"username": "manager", "store_id": "STORE_002"})
    if not manager_exists:
        manager_user = {
            "id": str(uuid.uuid4()),
            "username": "manager",
            "email": "manager@store002.com",
            "role": "user",
            "store_id": "STORE_002",
            "assigned_projects": [],
            "created_date": datetime.utcnow(),
            "last_login": None,
            "is_active": True
        }
        
        manager_password = hash_password("manager123")
        
        await db.users.insert_one(manager_user)
        await db.user_passwords.insert_one({
            "user_id": manager_user["id"],
            "password_hash": manager_password
        })
        print("✅ Created manager user for STORE_002")
    
    # Create supervisor user for STORE_003
    supervisor_exists = await db.users.find_one({"username": "supervisor", "store_id": "STORE_003"})
    if not supervisor_exists:
        supervisor_user = {
            "id": str(uuid.uuid4()),
            "username": "supervisor",
            "email": "supervisor@store003.com",
            "role": "user",
            "store_id": "STORE_003",
            "assigned_projects": [],
            "created_date": datetime.utcnow(),
            "last_login": None,
            "is_active": True
        }
        
        supervisor_password = hash_password("super123")
        
        await db.users.insert_one(supervisor_user)
        await db.user_passwords.insert_one({
            "user_id": supervisor_user["id"],
            "password_hash": supervisor_password
        })
        print("✅ Created supervisor user for STORE_003")
    
    # Update all existing projects to have store_id
    projects = await db.projects.find({}).to_list(1000)
    for project in projects:
        if not project.get("store_id"):
            await db.projects.update_one(
                {"id": project["id"]},
                {"$set": {"store_id": "STORE_001"}}  # Assign to STORE_001 by default
            )
    print(f"✅ Updated {len(projects)} projects with store_id")
    
    # Update all existing tasks to have store_id
    tasks = await db.tasks.find({}).to_list(1000)
    for task in tasks:
        if not task.get("store_id"):
            await db.tasks.update_one(
                {"id": task["id"]},
                {"$set": {"store_id": "STORE_001"}}  # Assign to STORE_001 by default
            )
    print(f"✅ Updated {len(tasks)} tasks with store_id")
    
    # Update all existing ideas to have store_id
    ideas = await db.ideas.find({}).to_list(1000)
    for idea in ideas:
        if not idea.get("store_id"):
            await db.ideas.update_one(
                {"id": idea["id"]},
                {"$set": {"store_id": "STORE_001"}}  # Assign to STORE_001 by default
            )
    print(f"✅ Updated {len(ideas)} ideas with store_id")
    
    print("\nMulti-store setup complete!")
    client.close()

if __name__ == "__main__":
    asyncio.run(setup_multistore_users())