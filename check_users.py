#!/usr/bin/env python3
"""
Check existing users in the database
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

async def check_users():
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    print("Checking existing users...")
    users = await db.users.find({}).to_list(1000)
    
    print(f"Found {len(users)} users:")
    for user in users:
        print(f"- Username: {user.get('username')}, Role: {user.get('role')}, Store ID: {user.get('store_id', 'NOT SET')}")
    
    # Check if we need to create test users
    required_users = [
        {"username": "admin", "store_id": "STORE_001", "role": "admin"},
        {"username": "manager", "store_id": "STORE_002", "role": "user"},
        {"username": "supervisor", "store_id": "STORE_003", "role": "user"}
    ]
    
    print("\nRequired users for multi-store testing:")
    for req_user in required_users:
        existing = await db.users.find_one({"username": req_user["username"], "store_id": req_user["store_id"]})
        if existing:
            print(f"✅ {req_user['username']} with {req_user['store_id']} exists")
        else:
            print(f"❌ {req_user['username']} with {req_user['store_id']} missing")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_users())