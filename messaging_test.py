#!/usr/bin/env python3
"""
Focused test for messaging system functionality
"""

import requests
import json
import time

BACKEND_URL = "https://pastel-tasks.preview.emergentagent.com/api"

def test_messaging_system():
    print("🔄 Testing Messaging System...")
    
    # Login as admin
    admin_login = {"username": "admin", "password": "admin"}
    admin_response = requests.post(f"{BACKEND_URL}/auth/login", json=admin_login)
    
    if admin_response.status_code != 200:
        print("❌ Admin login failed")
        return False
    
    admin_token = admin_response.json()['session_token']
    admin_user = admin_response.json()['user']
    
    # Login as demo
    demo_login = {"username": "demo", "password": "demo"}
    demo_response = requests.post(f"{BACKEND_URL}/auth/login", json=demo_login)
    
    if demo_response.status_code != 200:
        print("❌ Demo login failed")
        return False
    
    demo_token = demo_response.json()['session_token']
    demo_user = demo_response.json()['user']
    
    print(f"✅ Logged in as admin: {admin_user['id']}")
    print(f"✅ Logged in as demo: {demo_user['id']}")
    
    # Test 1: Send message from demo to admin
    message_data = {
        "content": "Test message from demo user to admin",
        "recipient_type": "admin"
    }
    
    headers = {"Authorization": f"Bearer {demo_token}"}
    message_response = requests.post(f"{BACKEND_URL}/messages", json=message_data, headers=headers)
    
    if message_response.status_code != 200:
        print(f"❌ Message sending failed: {message_response.status_code} - {message_response.text}")
        return False
    
    message = message_response.json()
    conversation_id = message['conversation_id']
    print(f"✅ Message sent successfully, conversation ID: {conversation_id}")
    
    # Test 2: Get conversations for demo user
    demo_headers = {"Authorization": f"Bearer {demo_token}"}
    conversations_response = requests.get(f"{BACKEND_URL}/conversations", headers=demo_headers)
    
    if conversations_response.status_code != 200:
        print(f"❌ Get conversations failed: {conversations_response.status_code} - {conversations_response.text}")
        return False
    
    conversations = conversations_response.json()
    print(f"✅ Retrieved {len(conversations)} conversations for demo user")
    
    # Test 3: Get messages in conversation
    messages_response = requests.get(f"{BACKEND_URL}/conversations/{conversation_id}/messages", headers=demo_headers)
    
    if messages_response.status_code != 200:
        print(f"❌ Get messages failed: {messages_response.status_code} - {messages_response.text}")
        return False
    
    messages = messages_response.json()
    print(f"✅ Retrieved {len(messages)} messages from conversation")
    
    # Test 4: Admin gets conversations
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    admin_conversations_response = requests.get(f"{BACKEND_URL}/conversations", headers=admin_headers)
    
    if admin_conversations_response.status_code != 200:
        print(f"❌ Admin get conversations failed: {admin_conversations_response.status_code} - {admin_conversations_response.text}")
        return False
    
    admin_conversations = admin_conversations_response.json()
    print(f"✅ Retrieved {len(admin_conversations)} conversations for admin user")
    
    # Test 5: Mark conversation as read
    mark_read_response = requests.post(f"{BACKEND_URL}/conversations/{conversation_id}/mark-read", headers=demo_headers)
    
    if mark_read_response.status_code != 200:
        print(f"❌ Mark as read failed: {mark_read_response.status_code} - {mark_read_response.text}")
        return False
    
    print("✅ Conversation marked as read successfully")
    
    return True

if __name__ == "__main__":
    success = test_messaging_system()
    if success:
        print("🎉 All messaging tests passed!")
    else:
        print("❌ Some messaging tests failed!")