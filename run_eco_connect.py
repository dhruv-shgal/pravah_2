#!/usr/bin/env python3
"""
Complete Eco-Connect System Startup
Runs all APIs and Flask app together
"""
import subprocess
import sys
import time
import os
import threading
from pathlib import Path

def run_service(script_path, service_name, port=None):
    """Run a service in a separate thread"""
    def target():
        try:
            if port:
                print(f"🚀 Starting {service_name} on port {port}...")
            else:
                print(f"🚀 Starting {service_name}...")
            
            # Change to the script's directory if needed
            if '/' in script_path or '\\' in script_path:
                script_dir = os.path.dirname(script_path)
                script_name = os.path.basename(script_path)
                if script_dir:
                    os.chdir(script_dir)
                    subprocess.run([sys.executable, script_name])
                else:
                    subprocess.run([sys.executable, script_path])
            else:
                subprocess.run([sys.executable, script_path])
                
        except Exception as e:
            print(f"❌ Error running {service_name}: {e}")
    
    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    return thread

def main():
    print("🌱 Eco-Connect Complete System Startup")
    print("=" * 50)
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    print(f"📁 Current directory: {current_dir}")
    
    # Check if model files exist
    models = [
        (r'C:\Users\dhruv\OneDrive\Desktop\pravah\eco_connect\plantation_yolov11.pt', 'Plantation'),
        (r'C:\Users\dhruv\OneDrive\Desktop\pravah\eco_connect\waste_collection_yolov11.pt', 'Waste Collection'),
        (r'C:\Users\dhruv\OneDrive\Desktop\pravah\eco_connect\animal_feeding_yolov11.pt', 'Animal Feeding')
    ]
    
    print("\n📋 Checking model files...")
    missing_models = []
    for model_path, model_name in models:
        if os.path.exists(model_path):
            print(f"✅ {model_name}: Found")
        else:
            print(f"❌ {model_name}: NOT FOUND - {model_path}")
            missing_models.append(model_name)
    
    if missing_models:
        print(f"\n⚠️  Warning: {len(missing_models)} model(s) missing!")
        print("   The corresponding APIs may not work properly.")
    
    print("\n🚀 Starting services...")
    
    # Start all services
    threads = []
    
    # Start API services
    threads.append(run_service('plantation_api.py', 'Plantation API', 8001))
    time.sleep(2)
    
    threads.append(run_service('waste_api.py', 'Waste Collection API', 8002))
    time.sleep(2)
    
    threads.append(run_service('animal_feeding_api.py', 'Animal Feeding API', 8003))
    time.sleep(2)
    
    # Start Flask app
    threads.append(run_service('flask_eco/app.py', 'Flask Web App', 3000))
    time.sleep(3)
    
    print("\n✅ All services started!")
    print("\n📡 Service URLs:")
    print("   🌱 Plantation API:     http://localhost:8001")
    print("   🗑️  Waste Collection:   http://localhost:8002")
    print("   🐕 Animal Feeding:     http://localhost:8003")
    print("   🌐 Web Application:    http://localhost:3000")
    
    print("\n📖 Usage:")
    print("   1. Open http://localhost:3000 in your browser")
    print("   2. Select an activity type")
    print("   3. Upload an image")
    print("   4. Get verification results!")
    
    print("\n⚠️  Press Ctrl+C to stop all services")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down all services...")
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()