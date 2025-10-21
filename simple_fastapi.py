#!/usr/bin/env python3
"""
Simple FastAPI backend for testing Flask integration
This version doesn't require AI models and can be used for testing the Flask frontend
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import os
from pathlib import Path

# Create directories for storing data
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Simple Eco-Connect API", version="1.0.0")

class UserSignupResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None

class LoginResponse(BaseModel):
    success: bool
    message: str
    similarity: Optional[float] = None

class VerificationResponse(BaseModel):
    overall_valid: bool
    message: Optional[str] = None
    steps: dict

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Simple Eco-Connect API for Testing",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "signup": "/api/signup",
            "login": "/api/login",
            "verify_task": "/api/verify-task",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "gpu_available": False,
        "models_loaded": True,  # Fake it for testing
        "message": "Simple API - No AI models required"
    }

@app.post("/api/signup", response_model=UserSignupResponse)
async def signup(
    username: str = Form(...),
    email: str = Form(...),
    face_image: UploadFile = File(...)
):
    """
    Simple user signup (no face processing)
    """
    try:
        # Generate unique user ID
        user_id = str(uuid.uuid4())
        
        # Save uploaded face image (for testing)
        face_image_path = UPLOAD_DIR / f"{user_id}_signup.jpg"
        with open(face_image_path, "wb") as buffer:
            content = await face_image.read()
            buffer.write(content)
        
        print(f"✅ Signup successful - User: {username}, Email: {email}, Image size: {len(content)} bytes")
        
        return UserSignupResponse(
            success=True,
            message="User registered successfully! (Simple mode - no face verification)",
            user_id=user_id
        )
        
    except Exception as e:
        print(f"❌ Signup error: {e}")
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

@app.post("/api/login", response_model=LoginResponse)
async def login(
    user_id: str = Form(...),
    face_image: UploadFile = File(...)
):
    """
    Simple user login (no face verification)
    """
    try:
        # Save login face image (for testing)
        login_image_path = UPLOAD_DIR / f"{user_id}_login_{uuid.uuid4()}.jpg"
        with open(login_image_path, "wb") as buffer:
            content = await face_image.read()
            buffer.write(content)
        
        print(f"✅ Login successful - User: {user_id}, Image size: {len(content)} bytes")
        
        # Simulate successful face verification
        return LoginResponse(
            success=True,
            message="Login successful! (Simple mode - no face verification)",
            similarity=0.95  # Fake similarity score
        )
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.post("/api/verify-task", response_model=VerificationResponse)
async def verify_task(
    user_id: str = Form(...),
    task_type: str = Form(...),
    task_image: UploadFile = File(...)
):
    """
    Simple task verification (no AI processing)
    """
    try:
        # Validate task type
        valid_tasks = ['plantation', 'waste_management', 'stray_animal_feeding']
        if task_type not in valid_tasks:
            raise HTTPException(status_code=400, detail=f"Invalid task type: {task_type}")
        
        # Save task image (for testing)
        task_image_path = UPLOAD_DIR / f"{user_id}_task_{uuid.uuid4()}.jpg"
        with open(task_image_path, "wb") as buffer:
            content = await task_image.read()
            buffer.write(content)
        
        print(f"✅ Task verification - User: {user_id}, Task: {task_type}, Image size: {len(content)} bytes")
        
        # Simulate successful verification
        return VerificationResponse(
            overall_valid=True,
            message="Task verified successfully! (Simple mode - no AI verification)",
            steps={
                "ai_detection": {"is_valid": True, "message": "Simulated AI check passed"},
                "exif_verification": {"is_valid": True, "message": "Simulated EXIF check passed"},
                "activity_verification": {"is_valid": True, "message": f"Simulated {task_type} detection passed"},
                "face_verification": {"is_valid": True, "message": "Simulated face verification passed"}
            }
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Task verification error: {e}")
        raise HTTPException(status_code=500, detail=f"Task verification failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🌱 Starting Simple Eco-Connect API...")
    print("📍 This is a testing version without AI models")
    print("🚀 API will run on http://localhost:8000")
    print("📖 Docs available at http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)