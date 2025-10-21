#!/usr/bin/env python3
"""
PRAVAH Flask Frontend Launcher
Connects to FastAPI backend for AI-powered conservation verification
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

def install_requirements():
    """Install Flask requirements"""
    print("📦 Installing Flask requirements...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['static/uploads', 'static/css', 'static/js']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    print("✅ Directories created")

def main():
    """Main function"""
    print("🌱 PRAVAH Flask Frontend")
    print("=" * 40)
    print("AI Meets Conservation - Frontend Connector")
    print()
    
    # Create directories
    create_directories()
    
    # Install requirements
    if not install_requirements():
        return
    
    # Check FastAPI backend
    print("\n🔍 Checking FastAPI backend...")
    if not check_fastapi_backend():
        print("\n⚠️  FastAPI backend is not running!")
        print("Please start the FastAPI backend first:")
        print("   python fastapi2.py")
        print("\nOr run both services together:")
        print("   python ../start_services.py")
        
        choice = input("\nContinue anyway? (y/N): ").lower()
        if choice != 'y':
            return
    
    # Start Flask app
    print("\n🚀 Starting Flask frontend...")
    print("📍 Flask will run on: http://localhost:5000")
    print("📍 FastAPI backend on: http://localhost:8000")
    print("\n🔄 Press Ctrl+C to stop")
    print()
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Flask frontend stopped")
    except Exception as e:
        print(f"\n❌ Error starting Flask: {e}")

if __name__ == "__main__":
    main()