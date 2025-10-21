#!/usr/bin/env python3
"""
Startup script for Eco-Connect services
This script helps start both FastAPI backend and Flask frontend
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_requirements():
    """Check if required files exist"""
    required_files = [
        'fastapi2.py',
        'app.py',
        'plantation_yolov11.pt',
        'waste_collection_yolov11.pt', 
        'animal_feeding_yolov11.pt'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found")
    return True

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Flask requirements...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Flask requirements installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    
    return True

def start_fastapi():
    """Start FastAPI backend"""
    print("🚀 Starting FastAPI backend on port 8000...")
    try:
        # Start FastAPI in background
        process = subprocess.Popen([
            sys.executable, 'fastapi2.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it time to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ FastAPI backend started successfully")
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
    print("🌐 Starting Flask frontend on port 5000...")
    try:
        # Start Flask
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Services stopped by user")
    except Exception as e:
        print(f"❌ Error starting Flask: {e}")

def main():
    """Main startup function"""
    print("🌱 Eco-Connect Service Startup")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please ensure all required files are present")
        return
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Failed to install requirements")
        return
    
    # Start FastAPI backend
    fastapi_process = start_fastapi()
    if not fastapi_process:
        print("\n❌ Cannot start Flask without FastAPI backend")
        return
    
    try:
        # Start Flask frontend
        print("\n🌐 Starting Flask frontend...")
        print("📍 Access the app at: http://localhost:5000")
        print("📍 FastAPI docs at: http://localhost:8000/docs")
        print("\n🔄 Press Ctrl+C to stop all services")
        
        start_flask()
        
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        if fastapi_process and fastapi_process.poll() is None:
            fastapi_process.terminate()
            fastapi_process.wait()
            print("✅ FastAPI backend stopped")

if __name__ == "__main__":
    main()