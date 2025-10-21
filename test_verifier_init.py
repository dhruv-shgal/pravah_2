#!/usr/bin/env python3
"""
Test script to debug verifier initialization
"""
import os
import sys

# Check if model files exist
plantation_path = r'C:\Users\dhruv\OneDrive\Desktop\pravah\eco_connect\plantation_yolov11.pt'
waste_path = r'C:\Users\dhruv\OneDrive\Desktop\pravah\eco_connect\waste_collection_yolov11.pt'
animal_path = r'C:\Users\dhruv\OneDrive\Desktop\pravah\eco_connect\animal_feeding_yolov11.pt'

print("Checking model files:")
print(f"Plantation model: {os.path.exists(plantation_path)} - {plantation_path}")
print(f"Waste model: {os.path.exists(waste_path)} - {waste_path}")
print(f"Animal model: {os.path.exists(animal_path)} - {animal_path}")

# Try to import required modules
try:
    from ultralytics import YOLO
    print("✅ YOLO import successful")
except ImportError as e:
    print(f"❌ YOLO import failed: {e}")

try:
    import insightface
    print("✅ InsightFace import successful")
except ImportError as e:
    print(f"❌ InsightFace import failed: {e}")

try:
    from transformers import pipeline
    print("✅ Transformers import successful")
except ImportError as e:
    print(f"❌ Transformers import failed: {e}")

try:
    import torch
    print(f"✅ PyTorch import successful - CUDA available: {torch.cuda.is_available()}")
except ImportError as e:
    print(f"❌ PyTorch import failed: {e}")

# Try to load one YOLO model
if os.path.exists(plantation_path):
    try:
        from ultralytics import YOLO
        model = YOLO(plantation_path)
        print("✅ YOLO model loading successful")
    except Exception as e:
        print(f"❌ YOLO model loading failed: {e}")
else:
    print("❌ Cannot test YOLO loading - plantation model file not found")