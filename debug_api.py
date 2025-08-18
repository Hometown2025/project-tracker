#!/usr/bin/env python3
"""
Debug test to see what the API is actually returning
"""

import requests
import json

# Get backend URL from frontend .env
BACKEND_URL = "https://buildbuddy-2.preview.emergentagent.com/api"

def debug_api_response():
    # Authenticate
    admin_login = {
        "username": "admin",
        "password": "admin",
        "store_id": "STORE_001"
    }
    
    session = requests.Session()
    
    # Login
    login_response = session.post(f"{BACKEND_URL}/auth/login", json=admin_login)
    print(f"Login Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        admin_token = login_response.json().get('session_token')
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create test project
        project_data = {
            "name": "Debug Test Project",
            "description": "Debug testing",
            "color": "#FF0000"
        }
        
        project_response = session.post(f"{BACKEND_URL}/projects", json=project_data, headers=headers)
        print(f"Project Creation Status: {project_response.status_code}")
        
        if project_response.status_code == 200:
            project_id = project_response.json()['id']
            
            # Create pantry room
            room_data = {
                "project_id": project_id,
                "title": "Pantry Renovation",
                "description": "Test pantry room",
                "priority": "medium",
                "subtask_level": 0
            }
            
            room_response = session.post(f"{BACKEND_URL}/tasks", json=room_data, headers=headers)
            print(f"Room Creation Status: {room_response.status_code}")
            
            if room_response.status_code == 200:
                room_id = room_response.json()['id']
                print(f"Room ID: {room_id}")
                
                # Generate subtasks
                subtask_response = session.post(f"{BACKEND_URL}/tasks/{room_id}/generate-subtasks", headers=headers)
                print(f"Subtask Generation Status: {subtask_response.status_code}")
                print(f"Subtask Response: {subtask_response.text}")
                
                # Check if subtasks were actually created by querying them
                subtasks_query = session.get(f"{BACKEND_URL}/tasks/{room_id}/subtasks", headers=headers)
                print(f"Subtasks Query Status: {subtasks_query.status_code}")
                print(f"Subtasks Query Response: {subtasks_query.text}")

if __name__ == "__main__":
    debug_api_response()