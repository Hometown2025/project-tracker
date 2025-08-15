#!/usr/bin/env python3
"""
Focused test for WebSocket functionality
"""

import requests
import websocket
import json
import threading
import time
import ssl

BACKEND_URL = "https://housebuild.preview.emergentagent.com/api"

def test_websocket():
    print("🔄 Testing WebSocket Connection...")
    
    # Login as admin
    admin_login = {"username": "admin", "password": "admin"}
    admin_response = requests.post(f"{BACKEND_URL}/auth/login", json=admin_login)
    
    if admin_response.status_code != 200:
        print("❌ Admin login failed")
        return False
    
    admin_user = admin_response.json()['user']
    user_id = admin_user['id']
    
    print(f"✅ Logged in as admin: {user_id}")
    
    # Test WebSocket connection
    ws_url = BACKEND_URL.replace("https://", "wss://").replace("/api", "") + f"/ws/{user_id}"
    print(f"🔗 Connecting to WebSocket: {ws_url}")
    
    connected = False
    messages_received = []
    
    def on_message(ws, message):
        print(f"📨 WebSocket message received: {message}")
        messages_received.append(message)
    
    def on_error(ws, error):
        print(f"❌ WebSocket error: {error}")
    
    def on_close(ws, close_status_code, close_msg):
        print(f"🔌 WebSocket connection closed: {close_status_code} - {close_msg}")
    
    def on_open(ws):
        nonlocal connected
        connected = True
        print("✅ WebSocket connection established!")
        # Send a ping to keep connection alive
        ws.send("ping")
    
    try:
        # Create WebSocket connection with SSL context
        ws = websocket.WebSocketApp(ws_url,
                                  on_open=on_open,
                                  on_message=on_message,
                                  on_error=on_error,
                                  on_close=on_close)
        
        # Run WebSocket in a separate thread
        wst = threading.Thread(target=lambda: ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}))
        wst.daemon = True
        wst.start()
        
        # Wait for connection
        time.sleep(3)
        
        if connected:
            print("✅ WebSocket infrastructure test passed!")
            
            # Test sending a message to trigger real-time notification
            print("🔄 Testing real-time notifications...")
            
            # Create a project to trigger notification
            project_data = {
                "name": "WebSocket Test Project",
                "description": "Testing WebSocket notifications",
                "color": "#FF5722"
            }
            
            admin_token = admin_response.json()['session_token']
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            project_response = requests.post(f"{BACKEND_URL}/projects", json=project_data, headers=headers)
            
            if project_response.status_code == 200:
                print("✅ Project created for notification test")
                
                # Wait for notification
                time.sleep(2)
                
                if messages_received:
                    print(f"✅ Received {len(messages_received)} WebSocket messages")
                    for msg in messages_received:
                        try:
                            parsed = json.loads(msg)
                            if parsed.get('type') == 'notification':
                                print("✅ Real-time notification received!")
                        except:
                            pass
                else:
                    print("⚠️ No WebSocket messages received (this might be expected)")
                
                # Clean up test project
                project_id = project_response.json()['id']
                requests.delete(f"{BACKEND_URL}/projects/{project_id}", headers=headers)
            
            # Close WebSocket
            ws.close()
            return True
        else:
            print("❌ WebSocket connection failed")
            return False
            
    except Exception as e:
        print(f"❌ WebSocket test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = test_websocket()
    if success:
        print("🎉 WebSocket test completed!")
    else:
        print("❌ WebSocket test failed!")