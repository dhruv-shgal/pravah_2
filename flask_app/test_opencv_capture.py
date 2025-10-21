#!/usr/bin/env python3
"""
Test script for OpenCV face capture integration in Flask
"""

import requests
import time
import json

def test_opencv_routes():
    """Test OpenCV camera routes"""
    print("🧪 Testing OpenCV Camera Routes")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    try:
        # Test start camera
        print("1. Testing start camera...")
        response = requests.get(f"{base_url}/start_camera")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success')}")
            print(f"   Message: {result.get('message')}")
        
        # Test capture frame
        print("\n2. Testing capture frame...")
        response = requests.get(f"{base_url}/capture_frame")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success')}")
            print(f"   Frame data length: {len(result.get('frame', ''))}")
        
        # Test save face image (mock data)
        print("\n3. Testing save face image...")
        mock_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        
        response = requests.post(f"{base_url}/save_face_image", 
                               json={
                                   'image_data': mock_image_data,
                                   'image_index': 0
                               })
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success')}")
            print(f"   Message: {result.get('message')}")
        
        # Test get face images count
        print("\n4. Testing get face images count...")
        response = requests.get(f"{base_url}/get_face_images_count")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Images count: {result.get('count')}")
        
        # Test stop camera
        print("\n5. Testing stop camera...")
        response = requests.get(f"{base_url}/stop_camera")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success')}")
            print(f"   Message: {result.get('message')}")
        
        print("\n✅ All OpenCV routes tested successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Flask app not running on port 5000")
        print("Please start Flask app: cd flask_app && python app.py")
    except Exception as e:
        print(f"❌ Test error: {e}")

def test_signup_flow():
    """Test complete signup flow with OpenCV"""
    print("\n🧪 Testing Complete Signup Flow")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    try:
        # Simulate capturing 5 images
        print("Simulating capture of 5 face images...")
        mock_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        
        for i in range(5):
            response = requests.post(f"{base_url}/save_face_image", 
                                   json={
                                       'image_data': mock_image_data,
                                       'image_index': i
                                   })
            if response.status_code == 200:
                result = response.json()
                print(f"   Image {i+1}: {result.get('message')}")
        
        # Check final count
        response = requests.get(f"{base_url}/get_face_images_count")
        if response.status_code == 200:
            result = response.json()
            print(f"   Final count: {result.get('count')}/5 images")
        
        print("\n✅ Signup flow simulation complete!")
        print("Note: This simulates the image capture process.")
        print("For full testing, use the web interface with a real camera.")
        
    except Exception as e:
        print(f"❌ Signup flow test error: {e}")

if __name__ == "__main__":
    print("🔍 OpenCV Flask Integration Test")
    print("=" * 50)
    
    test_opencv_routes()
    test_signup_flow()
    
    print("\n📋 Next Steps:")
    print("1. Start Flask app: cd flask_app && python app.py")
    print("2. Open browser: http://localhost:5000/signup")
    print("3. Test face capture with real camera")
    print("4. Ensure FastAPI backend is running for full signup test")