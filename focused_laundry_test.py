#!/usr/bin/env python3
"""
Focused Test for Laundry Room Subtask Generation - Verify Specific Content
"""

import requests
import json

# Get backend URL from frontend .env
BACKEND_URL = "https://buildbuddy-2.preview.emergentagent.com/api"

def authenticate_admin():
    """Authenticate as admin user"""
    admin_login = {
        "username": "admin",
        "password": "admin",
        "store_id": "STORE_001"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=admin_login)
    if response.status_code == 200:
        return response.json().get('session_token')
    return None

def create_test_project(token):
    """Create a test project"""
    project_data = {
        "name": "Laundry Room Test Project",
        "description": "Test project for laundry room subtask verification",
        "color": "#4CAF50"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BACKEND_URL}/projects", json=project_data, headers=headers)
    if response.status_code == 200:
        return response.json()['id']
    return None

def create_laundry_room_task(token, project_id, title):
    """Create a laundry room task"""
    task_data = {
        "project_id": project_id,
        "title": title,
        "description": f"Test laundry room task: {title}",
        "priority": "medium"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BACKEND_URL}/tasks", json=task_data, headers=headers)
    if response.status_code == 200:
        return response.json()['id']
    return None

def generate_subtasks(token, task_id):
    """Generate subtasks for a task"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BACKEND_URL}/tasks/{task_id}/generate-subtasks", headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def get_subtasks_for_task(token, parent_task_id):
    """Get subtasks for a specific parent task"""
    headers = {"Authorization": f"Bearer {token}"}
    # Use the correct query parameter
    response = requests.get(f"{BACKEND_URL}/tasks", params={"parent_task_id": parent_task_id}, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def main():
    print("🧪 FOCUSED LAUNDRY ROOM SUBTASK CONTENT VERIFICATION")
    print("=" * 60)
    
    # Authenticate
    token = authenticate_admin()
    if not token:
        print("❌ Authentication failed")
        return
    print("✅ Admin authenticated")
    
    # Create test project
    project_id = create_test_project(token)
    if not project_id:
        print("❌ Project creation failed")
        return
    print(f"✅ Test project created: {project_id}")
    
    # Create laundry room task
    task_id = create_laundry_room_task(token, project_id, "Laundry Room Renovation")
    if not task_id:
        print("❌ Task creation failed")
        return
    print(f"✅ Laundry room task created: {task_id}")
    
    # Generate subtasks
    generation_result = generate_subtasks(token, task_id)
    if not generation_result:
        print("❌ Subtask generation failed")
        return
    
    print(f"✅ Subtask generation response: {generation_result}")
    
    # Get the actual subtasks
    subtasks = get_subtasks_for_task(token, task_id)
    if not subtasks:
        print("❌ Failed to retrieve subtasks")
        return
    
    print(f"\n📊 SUBTASK VERIFICATION RESULTS")
    print(f"Total subtasks generated: {len(subtasks)}")
    
    if len(subtasks) == 9:
        print("✅ CORRECT: Generated 9 subtasks for laundry room")
    else:
        print(f"❌ INCORRECT: Expected 9 subtasks, got {len(subtasks)}")
    
    # Extract and verify subtask content
    subtask_data = {}
    print(f"\n📋 GENERATED SUBTASKS:")
    for i, subtask in enumerate(subtasks, 1):
        title = subtask['title']
        description = subtask['description']
        subtask_data[title] = description
        print(f"{i:2d}. {title}: {description}")
    
    # Verify the 4 NEW subtasks
    new_subtasks = {
        "Wall Coverings": "Install wall coverings, paint, or tile backsplash",
        "Cabinets": "Install laundry room cabinets and storage solutions",
        "Cabinet Hardware": "Install cabinet handles, knobs, and drawer slides",
        "Lighting": "Install overhead lighting and task lighting fixtures"
    }
    
    print(f"\n🆕 VERIFYING 4 NEW SUBTASKS:")
    new_found = 0
    for title, expected_desc in new_subtasks.items():
        if title in subtask_data:
            actual_desc = subtask_data[title]
            if actual_desc == expected_desc:
                print(f"✅ {title}: {actual_desc}")
                new_found += 1
            else:
                print(f"❌ {title}: Description mismatch")
                print(f"   Expected: {expected_desc}")
                print(f"   Actual: {actual_desc}")
        else:
            print(f"❌ {title}: MISSING")
    
    # Verify the 5 EXISTING subtasks
    existing_subtasks = {
        "Plumbing": "Install washer/dryer connections and utility sink",
        "Electrical Work": "Install electrical outlets and lighting",
        "Flooring": "Install laundry room flooring",
        "Appliances": "Install washer, dryer, and connections",
        "Ventilation": "Install proper ventilation for dryer"
    }
    
    print(f"\n🔄 VERIFYING 5 EXISTING SUBTASKS PRESERVED:")
    existing_found = 0
    for title, expected_desc in existing_subtasks.items():
        if title in subtask_data:
            actual_desc = subtask_data[title]
            if actual_desc == expected_desc:
                print(f"✅ {title}: {actual_desc}")
                existing_found += 1
            else:
                print(f"❌ {title}: Description changed")
                print(f"   Expected: {expected_desc}")
                print(f"   Actual: {actual_desc}")
        else:
            print(f"❌ {title}: MISSING")
    
    # Final summary
    print(f"\n📈 FINAL VERIFICATION SUMMARY:")
    print(f"✅ Total subtasks: {len(subtasks)}/9 {'✓' if len(subtasks) == 9 else '✗'}")
    print(f"✅ New subtasks: {new_found}/4 {'✓' if new_found == 4 else '✗'}")
    print(f"✅ Existing subtasks: {existing_found}/5 {'✓' if existing_found == 5 else '✗'}")
    
    all_correct = (len(subtasks) == 9 and new_found == 4 and existing_found == 5)
    print(f"\n🎯 OVERALL RESULT: {'✅ ALL REQUIREMENTS MET' if all_correct else '❌ SOME REQUIREMENTS FAILED'}")
    
    return all_correct

if __name__ == "__main__":
    main()