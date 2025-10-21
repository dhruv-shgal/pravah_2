#!/usr/bin/env python3
"""
Test script to debug FastAPI signup endpoint
"""

import requests
import io
from PIL import Image
import numpy as np

# Create a simple test image
def create_test_image():
    """Create a simple test image"""
    # Create a 640x480 RGB image
    img_array = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes

def test_fastapi_direct():
    """Test FastAPI signup endpoint directly"""
    print("🧪 Testing FastAPI signup endpoint directly...")
    
    # Create test data
    test_image = create_test_image()
    
    files = {
        'face_image': ('test_face.jpg', test_image, 'image/jpeg')
    }
    
    data = {
        'username': 'test_user',
        'email': 'test@example.com'
    }
    
    try:
        # Test root endpoint first
        print("1. Testing root endpoint...")
        root_response = requests.get("http://localhost:8000/")
        print(f"   Root status: {root_response.status_code}")
        if root_response.status_code == 200:
            print(f"   Root response: {root_response.json()}")
        
        # Test health endpoint
        print("2. Testing health endpoint...")
        health_response = requests.get("http://localhost:8000/health")
        print(f"   Health status: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"   Health response: {health_response.json()}")
        
        # Test signup endpoint
        print("3. Testing signup endpoint...")
        signup_response = requests.post(
            "http://localhost:8000/api/signup",
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"   Signup status: {signup_response.status_code}")
        print(f"   Signup response: {signup_response.text}")
        
        if signup_response.status_code == 200:
            result = signup_response.json()
            print(f"   Success: {result.get('success')}")
            print(f"   Message: {result.get('message')}")
            print(f"   User ID: {result.get('user_id')}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: FastAPI backend not running on port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_flask_signup():
    """Test Flask signup endpoint"""
    print("\n🧪 Testing Flask signup endpoint...")
    
    # Create test data
    test_image = create_test_image()
    
    files = {
        'face_image': ('test_face.jpg', test_image, 'image/jpeg')
    }
    
    data = {
        'username': 'test_user',
        'email': 'test@example.com',
        'userId': 'test_user_123'
    }
    
    try:
        # Test Flask backend health
        print("1. Testing Flask backend health...")
        health_response = requests.get("http://localhost:5000/health")
        print(f"   Flask health status: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"   Flask health response: {health_response.json()}")
        
        # Test Flask test-backend endpoint
        print("2. Testing Flask backend connectivity...")
        test_response = requests.get("http://localhost:5000/test-backend")
        print(f"   Backend test status: {test_response.status_code}")
        if test_response.status_code == 200:
            print(f"   Backend test response: {test_response.json()}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Flask backend not running on port 5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔍 PRAVAH Backend Testing")
    print("=" * 40)
    
    test_fastapi_direct()
    test_flask_signup()
    
    print("\n✅ Testing complete!")
    print("\nIf you see errors:")
    print("1. Make sure FastAPI is running: python fastapi2.py")
    print("2. Make sure Flask is running: python flask_app/app.py")
    print("3. Check that all model files are present")
    print("4. Check the console output for detailed error messages")