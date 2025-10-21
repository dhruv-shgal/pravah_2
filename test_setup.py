#!/usr/bin/env python3
"""
Test setup script for PRAVAH Flask + FastAPI integration
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    required_packages = ['flask', 'requests', 'fastapi', 'uvicorn', 'pillow']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package}")
    
    if missing_packages:
        print(f"\n📥 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, check=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    
    return True

def start_simple_backend():
    """Start the simple FastAPI backend for testing"""
    print("\n🚀 Starting Simple FastAPI Backend...")
    try:
        process = subprocess.Popen([
            sys.executable, 'simple_fastapi.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it time to start
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Simple FastAPI backend started on port 8000")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Failed to start backend:")
            print(f"   stdout: {stdout.decode()}")
            print(f"   stderr: {stderr.decode()}")
            return None
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_flask_frontend():
    """Start the Flask frontend"""
    print("\n🌐 Starting Flask Frontend...")
    try:
        os.chdir('flask_app')
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Services stopped by user")
    except Exception as e:
        print(f"❌ Error starting Flask: {e}")

def run_tests():
    """Run diagnostic tests"""
    print("\n🧪 Running Diagnostic Tests...")
    
    try:
        os.chdir('flask_app')
        
        print("1. Testing FastAPI backend...")
        subprocess.run([sys.executable, 'debug_fastapi.py'], check=True)
        
        print("\n2. Testing signup functionality...")
        subprocess.run([sys.executable, 'test_signup.py'], check=True)
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")

def main():
    """Main function"""
    print("🌱 PRAVAH Test Setup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    print("\nChoose an option:")
    print("1. Start Simple Backend + Flask (Recommended for testing)")
    print("2. Start Full Backend + Flask (Requires AI models)")
    print("3. Run Diagnostic Tests Only")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        # Start simple backend
        backend_process = start_simple_backend()
        if backend_process:
            try:
                start_flask_frontend()
            finally:
                print("\n🧹 Cleaning up...")
                if backend_process.poll() is None:
                    backend_process.terminate()
                    backend_process.wait()
                    print("✅ Backend stopped")
    
    elif choice == '2':
        print("\n⚠️  Starting full backend requires:")
        print("   - YOLO model files (plantation_yolov11.pt, etc.)")
        print("   - InsightFace installation")
        print("   - GPU support (optional)")
        
        confirm = input("\nContinue? (y/N): ").lower()
        if confirm == 'y':
            print("Please start the full backend manually:")
            print("   python fastapi2.py")
            print("\nThen start Flask:")
            print("   cd flask_app && python app.py")
    
    elif choice == '3':
        run_tests()
    
    elif choice == '4':
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()