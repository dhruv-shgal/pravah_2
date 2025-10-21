#!/usr/bin/env python3
"""
Startup script for PRAVAH Flask app with OpenCV face capture
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def install_opencv_dependencies():
    """Install OpenCV and related dependencies"""
    print("📦 Installing OpenCV dependencies...")
    
    packages = [
        'opencv-python==4.8.1.78',
        'Pillow==10.0.1', 
        'numpy==1.24.3'
    ]
    
    try:
        for package in packages:
            print(f"   Installing {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                          check=True, capture_output=True)
        
        print("✅ OpenCV dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def test_opencv():
    """Test OpenCV installation"""
    print("🧪 Testing OpenCV installation...")
    
    try:
        import cv2
        import numpy as np
        from PIL import Image
        
        print(f"   OpenCV version: {cv2.__version__}")
        print(f"   NumPy version: {np.__version__}")
        print("✅ OpenCV test successful")
        return True
    except ImportError as e:
        print(f"❌ OpenCV test failed: {e}")
        return False

def check_camera():
    """Check if camera is available"""
    print("📷 Checking camera availability...")
    
    try:
        import cv2
        
        # Try to open camera
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                print("✅ Camera is available and working")
                return True
            else:
                print("⚠️  Camera opened but failed to capture frame")
                return False
        else:
            print("❌ Camera not available or in use")
            return False
    except Exception as e:
        print(f"❌ Camera check error: {e}")
        return False

def start_flask_with_opencv():
    """Start Flask app with OpenCV support"""
    print("🚀 Starting Flask app with OpenCV...")
    
    try:
        os.chdir('flask_app')
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Flask app stopped by user")
    except Exception as e:
        print(f"❌ Error starting Flask: {e}")

def run_opencv_tests():
    """Run OpenCV integration tests"""
    print("🧪 Running OpenCV integration tests...")
    
    try:
        os.chdir('flask_app')
        subprocess.run([sys.executable, 'test_opencv_capture.py'], check=True)
    except Exception as e:
        print(f"❌ Error running tests: {e}")

def main():
    """Main function"""
    print("🌱 PRAVAH Flask App with OpenCV")
    print("=" * 40)
    print("📸 Face capture using OpenCV backend")
    print()
    
    # Install dependencies
    if not install_opencv_dependencies():
        return
    
    # Test OpenCV
    if not test_opencv():
        return
    
    # Check camera
    camera_available = check_camera()
    if not camera_available:
        print("⚠️  Camera not available - face capture may not work")
        choice = input("Continue anyway? (y/N): ").lower()
        if choice != 'y':
            return
    
    print("\nChoose an option:")
    print("1. Start Flask app with OpenCV")
    print("2. Run OpenCV integration tests")
    print("3. Install dependencies only")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        print("\n📍 Flask app will run on: http://localhost:5000")
        print("📸 OpenCV face capture enabled")
        print("🔄 Press Ctrl+C to stop")
        print()
        start_flask_with_opencv()
    
    elif choice == '2':
        run_opencv_tests()
    
    elif choice == '3':
        print("✅ Dependencies installed successfully")
    
    elif choice == '4':
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()