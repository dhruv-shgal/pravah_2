#!/usr/bin/env python3
"""
Debug script to check FastAPI status and fix common issues
"""

import requests
import json

def check_fastapi_status():
    """Check FastAPI backend status"""
    print("🔍 Checking FastAPI Backend Status")
    print("=" * 40)
    
    try:
        # Test root endpoint
        print("1. Testing root endpoint...")
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Message: {data.get('message', 'No message')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
        else:
            print(f"   Error: {response.text}")
        
        # Test health endpoint
        print("\n2. Testing health endpoint...")
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   GPU Available: {data.get('gpu_available', False)}")
            print(f"   Models Loaded: {data.get('models_loaded', False)}")
        else:
            print(f"   Error: {response.text}")
        
        # Test if we can access the docs
        print("\n3. Testing docs endpoint...")
        response = requests.get("http://localhost:8000/docs", timeout=5)
        print(f"   Docs Status: {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ FastAPI backend is not running on port 8000")
        print("\nTo start FastAPI backend:")
        print("   python fastapi2.py")
        return False
    except Exception as e:
        print(f"❌ Error checking FastAPI: {e}")
        return False

def test_simple_signup():
    """Test a simple signup request"""
    print("\n🧪 Testing Simple Signup Request")
    print("=" * 40)
    
    try:
        # Create minimal test data
        data = {
            'username': 'test_user',
            'email': 'test@example.com'
        }
        
        # Create a simple 1x1 pixel image
        import io
        from PIL import Image
        
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {
            'face_image': ('test.jpg', img_bytes, 'image/jpeg')
        }
        
        print("Sending signup request...")
        response = requests.post(
            "http://localhost:8000/api/signup",
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
        elif response.status_code == 422:
            print("❌ Validation Error - Check request format")
        elif response.status_code == 500:
            print("❌ Internal Server Error - Check FastAPI logs")
        
    except Exception as e:
        print(f"❌ Error testing signup: {e}")

if __name__ == "__main__":
    if check_fastapi_status():
        test_simple_signup()
    
    print("\n📋 Troubleshooting Tips:")
    print("1. Check FastAPI console for error messages")
    print("2. Ensure model files are in the correct location")
    print("3. Check if InsightFace and other dependencies are installed")
    print("4. Try restarting FastAPI backend")
    print("5. Check the FastAPI logs for initialization errors")