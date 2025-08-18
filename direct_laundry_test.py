#!/usr/bin/env python3
"""
Direct Verification of Laundry Room Subtask Generation Response
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
        "name": "Final Laundry Room Test",
        "description": "Final test for laundry room subtask verification",
        "color": "#4CAF50"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BACKEND_URL}/projects", json=project_data, headers=headers)
    if response.status_code == 200:
        return response.json()['id']
    return None

def create_laundry_room_task(token, project_id):
    """Create a laundry room task"""
    task_data = {
        "project_id": project_id,
        "title": "Final Laundry Room Test",
        "description": "Final test for laundry room subtask generation",
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

def main():
    print("🔍 DIRECT LAUNDRY ROOM SUBTASK GENERATION VERIFICATION")
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
    task_id = create_laundry_room_task(token, project_id)
    if not task_id:
        print("❌ Task creation failed")
        return
    print(f"✅ Laundry room task created: {task_id}")
    
    # Generate subtasks and analyze the response directly
    generation_result = generate_subtasks(token, task_id)
    if not generation_result:
        print("❌ Subtask generation failed")
        return
    
    print(f"\n📊 GENERATION RESPONSE ANALYSIS:")
    print(f"Room type detected: {generation_result.get('room_type', 'unknown')}")
    print(f"Total created: {generation_result.get('total_created', 0)}")
    print(f"Message: {generation_result.get('message', 'No message')}")
    
    # Analyze the created_subtasks array directly from the response
    created_subtasks = generation_result.get('created_subtasks', [])
    print(f"\n📋 SUBTASKS CREATED (from response): {len(created_subtasks)}")
    
    if len(created_subtasks) == 9:
        print("✅ CORRECT: Generated 9 subtasks for laundry room")
    else:
        print(f"❌ INCORRECT: Expected 9 subtasks, got {len(created_subtasks)}")
    
    # Extract subtask data from the response
    subtask_data = {}
    for i, subtask in enumerate(created_subtasks, 1):
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
    
    # Test different laundry room title variations
    print(f"\n🔍 TESTING LAUNDRY ROOM DETECTION VARIATIONS:")
    
    test_titles = [
        "Utility Room Upgrade",
        "Laundry Area Remodel"
    ]
    
    for title in test_titles:
        # Create task
        task_data = {
            "project_id": project_id,
            "title": title,
            "description": f"Test task: {title}",
            "priority": "medium"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BACKEND_URL}/tasks", json=task_data, headers=headers)
        
        if response.status_code == 200:
            test_task_id = response.json()['id']
            
            # Generate subtasks
            test_result = generate_subtasks(token, test_task_id)
            if test_result:
                room_type = test_result.get('room_type', 'unknown')
                count = test_result.get('total_created', 0)
                print(f"✅ '{title}' → {room_type} ({count} subtasks)")
                
                if room_type == 'laundry room' and count == 9:
                    print(f"   ✅ Correctly detected and generated 9 subtasks")
                else:
                    print(f"   ❌ Expected laundry room with 9 subtasks")
            else:
                print(f"❌ '{title}' → Failed to generate subtasks")
        else:
            print(f"❌ Failed to create task: {title}")
    
    # Final summary
    print(f"\n📈 FINAL VERIFICATION SUMMARY:")
    print(f"✅ Total subtasks: {len(created_subtasks)}/9 {'✓' if len(created_subtasks) == 9 else '✗'}")
    print(f"✅ New subtasks: {new_found}/4 {'✓' if new_found == 4 else '✗'}")
    print(f"✅ Existing subtasks: {existing_found}/5 {'✓' if existing_found == 5 else '✗'}")
    
    all_correct = (len(created_subtasks) == 9 and new_found == 4 and existing_found == 5)
    print(f"\n🎯 OVERALL RESULT: {'✅ ALL REQUIREMENTS MET' if all_correct else '❌ SOME REQUIREMENTS FAILED'}")
    
    return all_correct

if __name__ == "__main__":
    main()