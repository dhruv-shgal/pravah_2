#!/usr/bin/env python3
"""
Startup script for updated PRAVAH services
- Signup: email, password, username, user_id, 5 face images
- Login: email/user_id, password (no face verification)
"""

import subprocess
import sys
import time
import os
import requests
from pathlib import Path

def check_fastapi_backend():
    """Check if FastAPI backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ FastAPI backend is running")
            return True
    except requests.exceptions.ConnectionError:
        print("❌ FastAPI backend not found on port 8000")
    except Exception as e:
        print(f"❌ Error checking backend: {e}")
    
    return False

def start_fastapi():
    """Start FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    try:
        process = subprocess.Popen([
            sys.executable, 'fastapi2.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it time to start
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ FastAPI backend started on port 8000")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ FastAPI failed to start:")
            print(f"   stdout: {stdout.decode()}")
            print(f"   stderr: {stderr.decode()}")
            return None
    except Exception as e:
        print(f"❌ Error starting FastAPI: {e}")
        return None

def start_flask():
    """Start Flask frontend"""
    print("🌐 Starting Flask frontend...")
    try:
        os.chdir('flask_app')
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Services stopped by user")
    except Exception as e:
        print(f"❌ Error starting Flask: {e}")

def run_api_test():
    """Run API tests"""
    print("🧪 Running API tests...")
    try:
        subprocess.run([sys.executable, 'test_new_api.py'], check=True)
    except Exception as e:
        print(f"❌ Error running tests: {e}")

def main():
    """Main function"""
    print("🌱 PRAVAH Updated Services")
    print("=" * 40)
    print("📝 New Features:")
    print("   • Signup: email + password + username + user_id + 5 face images")
    print("   • Login: email/user_id + password (no face verification)")
    print("   • Face registration for future features")
    print()
    
    print("Choose an option:")
    print("1. Start both services (FastAPI + Flask)")
    print("2. Start FastAPI only")
    print("3. Start Flask only (requires FastAPI running)")
    print("4. Run API tests")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == '1':
        # Start both services
        fastapi_process = start_fastapi()
        if fastapi_process:
            try:
                start_flask()
            finally:
                print("\n🧹 Cleaning up...")
                if fastapi_process.poll() is None:
                    fastapi_process.terminate()
                    fastapi_process.wait()
                    print("✅ FastAPI stopped")
        else:
            print("❌ Cannot start Flask without FastAPI")
    
    elif choice == '2':
        # Start FastAPI only
        fastapi_process = start_fastapi()
        if fastapi_process:
            try:
                print("📍 FastAPI running on http://localhost:8000")
                print("📖 API docs at http://localhost:8000/docs")
                print("🔄 Press Ctrl+C to stop")
                
                # Keep running until interrupted
                while fastapi_process.poll() is None:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping FastAPI...")
                fastapi_process.terminate()
                fastapi_process.wait()
                print("✅ FastAPI stopped")
    
    elif choice == '3':
        # Start Flask only
        if check_fastapi_backend():
            start_flask()
        else:
            print("❌ FastAPI backend not running. Please start it first.")
    
    elif choice == '4':
        # Run tests
        if check_fastapi_backend():
            run_api_test()
        else:
            print("❌ FastAPI backend not running. Please start it first.")
    
    elif choice == '5':
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()