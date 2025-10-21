#!/usr/bin/env python3
"""
Test script for the updated API with email/password login and 5 face images signup
"""

import requests
import io
from PIL import Image
import numpy as np

def create_test_image(color='red'):
    """Create a simple test image"""
    img_array = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes

def test_new_signup():
    """Test the new signup endpoint with 5 face images"""
    print("🧪 Testing New Signup API...")
    
    # Create 5 test images
    face_images = []
    for i in range(5):
        face_images.append(('face_images', (f'face_{i+1}.jpg', create_test_image(), 'image/jpeg')))
    
    data = {
        'email': 'test@example.com',
        'password': 'testpassword123',
        'username': 'testuser',
        'user_id': 'test_user_123'
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/signup",
            files=face_images,
            data=data,
            timeout=30
        )
        
        print(f"   Signup status: {response.status_code}")
        print(f"   Signup response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success')}")
            print(f"   Message: {result.get('message')}")
            print(f"   User ID: {result.get('user_id')}")
            return result.get('user_id')
        
    except Exception as e:
        print(f"❌ Signup error: {e}")
    
    return None

def test_new_login(user_id=None):
    """Test the new login endpoint with email/password"""
    print("\n🧪 Testing New Login API...")
    
    # Test with email
    data = {
        'identifier': 'test@example.com',
        'password': 'testpassword123'
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/login",
            data=data,
            timeout=30
        )
        
        print(f"   Login status: {response.status_code}")
        print(f"   Login response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success')}")
            print(f"   Message: {result.get('message')}")
            print(f"   User Data: {result.get('user_data')}")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
    
    # Test with user_id if provided
    if user_id:
        print("\n🧪 Testing Login with User ID...")
        data = {
            'identifier': user_id,
            'password': 'testpassword123'
        }
        
        try:
            response = requests.post(
                "http://localhost:8000/api/login",
                data=data,
                timeout=30
            )
            
            print(f"   Login with User ID status: {response.status_code}")
            print(f"   Login with User ID response: {response.text}")
            
        except Exception as e:
            print(f"❌ Login with User ID error: {e}")

def test_flask_integration():
    """Test Flask integration"""
    print("\n🧪 Testing Flask Integration...")
    
    try:
        # Test Flask health
        response = requests.get("http://localhost:5000/health")
        print(f"   Flask health status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Flask health response: {response.json()}")
        
        # Test Flask backend connectivity
        response = requests.get("http://localhost:5000/test-backend")
        print(f"   Flask backend test status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Flask backend test response: {response.json()}")
        
    except Exception as e:
        print(f"❌ Flask integration error: {e}")

if __name__ == "__main__":
    print("🔍 Testing Updated PRAVAH API")
    print("=" * 40)
    
    # Test FastAPI endpoints
    user_id = test_new_signup()
    test_new_login(user_id)
    
    # Test Flask integration
    test_flask_integration()
    
    print("\n✅ Testing complete!")
    print("\nAPI Changes Summary:")
    print("📝 Signup now requires: email, password, username, user_id, 5 face images")
    print("🔐 Login now requires: identifier (email/user_id), password")
    print("❌ Face verification removed from login")
    print("✅ Face registration still used for signup (5 images for better accuracy)")