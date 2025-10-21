#!/usr/bin/env python3
"""
Debug script to test session handling in Flask app
"""

import requests
import json
import base64

def test_session_flow():
    """Test the complete session flow"""
    print("🔍 Testing Session Flow")
    print("=" * 30)
    
    base_url = "http://localhost:5000"
    
    # Use a session to maintain cookies
    session = requests.Session()
    
    try:
        # 1. Check initial session
        print("1. Checking initial session...")
        response = session.get(f"{base_url}/debug_session")
        if response.status_code == 200:
            data = response.json()
            print(f"   Initial face images count: {data['face_images_count']}")
            print(f"   Session keys: {data['all_session_keys']}")
        
        # 2. Save some test images
        print("\n2. Saving test images...")
        mock_image_data = "data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        
        for i in range(5):
            response = session.post(f"{base_url}/save_face_image", 
                                  json={
                                      'image_data': mock_image_data,
                                      'image_index': i
                                  })
            if response.status_code == 200:
                result = response.json()
                print(f"   Image {i+1}: {result['message']} (Count: {result.get('images_count', 'N/A')})")
            else:
                print(f"   Image {i+1}: Failed - {response.status_code}")
        
        # 3. Check session after saving
        print("\n3. Checking session after saving...")
        response = session.get(f"{base_url}/debug_session")
        if response.status_code == 200:
            data = response.json()
            print(f"   Face images count: {data['face_images_count']}")
            print(f"   Face images keys: {data['face_images_keys']}")
        
        # 4. Check image count endpoint
        print("\n4. Checking image count endpoint...")
        response = session.get(f"{base_url}/get_face_images_count")
        if response.status_code == 200:
            data = response.json()
            print(f"   Count from endpoint: {data['count']}")
            print(f"   Keys from endpoint: {data.get('keys', [])}")
        
        # 5. Test signup form submission (without actually submitting)
        print("\n5. Testing signup page access...")
        response = session.get(f"{base_url}/signup")
        if response.status_code == 200:
            print("   Signup page accessible")
        else:
            print(f"   Signup page error: {response.status_code}")
        
        print("\n✅ Session flow test complete!")
        
    except Exception as e:
        print(f"❌ Test error: {e}")

def test_direct_signup():
    """Test direct signup with mock data"""
    print("\n🧪 Testing Direct Signup")
    print("=" * 30)
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    try:
        # First save 5 images
        print("Saving 5 test images...")
        mock_image_data = "data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        
        for i in range(5):
            session.post(f"{base_url}/save_face_image", 
                        json={
                            'image_data': mock_image_data,
                            'image_index': i
                        })
        
        # Check count
        response = session.get(f"{base_url}/get_face_images_count")
        if response.status_code == 200:
            data = response.json()
            print(f"Images saved: {data['count']}/5")
        
        # Try signup
        print("Attempting signup...")
        signup_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'username': 'testuser',
            'userId': 'test_user_123'
        }
        
        response = session.post(f"{base_url}/signup", data=signup_data)
        print(f"Signup response status: {response.status_code}")
        
        if response.status_code == 200:
            if 'Please capture all 5 face images' in response.text:
                print("❌ Still getting face images error")
            elif 'Account created successfully' in response.text:
                print("✅ Signup successful!")
            else:
                print("? Unknown signup response")
        
    except Exception as e:
        print(f"❌ Signup test error: {e}")

if __name__ == "__main__":
    print("🔍 Flask Session Debug Tool")
    print("=" * 40)
    print("Make sure Flask app is running on port 5000")
    print()
    
    test_session_flow()
    test_direct_signup()
    
    print("\n📋 Debug Steps:")
    print("1. Visit http://localhost:5000/debug for interactive testing")
    print("2. Check Flask console for DEBUG messages")
    print("3. Try the signup flow manually")
    print("4. Check if session cookies are being set properly")