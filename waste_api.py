from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from ultralytics import YOLO
from transformers import pipeline
from PIL import Image
from PIL.ExifTags import TAGS
import cv2
import numpy as np
from datetime import datetime, timedelta
import os
import uuid
from pathlib import Path
import shutil

# Create upload directory
UPLOAD_DIR = Path("uploads/waste")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Waste Collection Verification API", version="1.0.0")

# Global variables
waste_model = None
ai_detector = None

class VerificationResponse(BaseModel):
    overall_valid: bool
    message: str
    steps: dict

def verify_ai_image(image):
    """Check if image is AI-generated"""
    try:
        if ai_detector is None:
            return basic_ai_check(image)
        
        if isinstance(image, np.ndarray):
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        results = ai_detector(image)
        
        for result in results:
            label = result['label'].lower()
            score = result['score']
            
            # Check for AI-generated indicators
            if 'artificial' in label or 'ai' in label or 'generated' in label or 'fake' in label:
                if score > 0.5:  # Lower threshold for better detection
                    return {
                        'is_valid': False,
                        'confidence': score,
                        'message': f"Image rejected: AI-generated (confidence: {score:.2%})"
                    }
            
            # Also check if "real" confidence is too low
            if 'real' in label or 'authentic' in label:
                if score < 0.3:  # If "real" confidence is very low, likely AI
                    return {
                        'is_valid': False,
                        'confidence': 1 - score,
                        'message': f"Image rejected: AI-generated (confidence: {(1-score):.2%})"
                    }
        
        # If we get here, check the highest confidence result
        if results:
            top_result = max(results, key=lambda x: x['score'])
            if top_result['score'] > 0.8:
                return {
                    'is_valid': True,
                    'confidence': top_result['score'],
                    'message': "Image passed AI detection check"
                }
        
        return {
            'is_valid': True,
            'confidence': results[0]['score'] if results else 0.5,
            'message': "Image passed AI detection check"
        }
        
    except Exception as e:
        return basic_ai_check(image)

def basic_ai_check(image):
    """Fallback AI detection"""
    try:
        if isinstance(image, np.ndarray):
            image_array = image
        else:
            image_array = np.array(image)
        
        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY) if len(image_array.shape) == 3 else image_array
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        if laplacian_var < 50:
            return {
                'is_valid': False,
                'confidence': 0.6,
                'message': "Image rejected: Possibly AI-generated (low texture variance)"
            }
        
        return {
            'is_valid': True,
            'confidence': 0.5,
            'message': "Image passed basic AI check"
        }
    except Exception:
        return {
            'is_valid': True,
            'confidence': 0.5,
            'message': "AI check failed, allowing image"
        }

def verify_exif_datetime(image_path):
    """Verify EXIF date/time is within one week"""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        
        if not exif_data:
            return {
                'is_valid': False,
                'capture_time': None,
                'message': "Image rejected: No EXIF data found"
            }
        
        datetime_str = None
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == 'DateTimeOriginal' or tag == 'DateTime':
                datetime_str = value
                break
        
        if not datetime_str:
            return {
                'is_valid': False,
                'capture_time': None,
                'message': "Image rejected: No timestamp in EXIF data"
            }
        
        capture_time = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
        current_time = datetime.now()
        time_diff = current_time - capture_time
        
        if time_diff.days < 0:
            return {
                'is_valid': False,
                'capture_time': capture_time.isoformat(),
                'message': f"Image rejected: Future timestamp detected"
            }
        
        if time_diff.days > 7:
            return {
                'is_valid': False,
                'capture_time': capture_time.isoformat(),
                'message': f"Image rejected: Image older than 7 days ({time_diff.days} days old)"
            }
        
        return {
            'is_valid': True,
            'capture_time': capture_time.isoformat(),
            'message': f"Image timestamp valid ({time_diff.days} days old)"
        }
        
    except Exception as e:
        return {
            'is_valid': False,
            'capture_time': None,
            'message': f"EXIF verification failed: {str(e)}"
        }

def verify_waste_activity(image_path):
    """Verify waste collection activity in the image"""
    try:
        if waste_model is None:
            return {
                'is_valid': False,
                'detected_classes': [],
                'message': "Waste collection model not loaded"
            }
        
        image = cv2.imread(str(image_path))
        results = waste_model(image)
        
        detected_classes = []
        person_detected = False
        waste_detected = False
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                class_name = result.names[cls_id]
                confidence = float(box.conf[0])
                
                if confidence > 0.5:
                    detected_classes.append(class_name)
                    if class_name == 'person':
                        person_detected = True
                    elif any(waste_term in class_name.lower() for waste_term in ['waste', 'trash', 'garbage', 'litter', 'bottle', 'bag']):
                        waste_detected = True
        
        if not person_detected:
            return {
                'is_valid': False,
                'detected_classes': detected_classes,
                'message': "No person detected in waste collection activity"
            }
        
        if not waste_detected:
            return {
                'is_valid': False,
                'detected_classes': detected_classes,
                'message': "No waste collection activity detected in image"
            }
        
        return {
            'is_valid': True,
            'detected_classes': detected_classes,
            'message': f"Waste collection activity verified successfully"
        }
        
    except Exception as e:
        return {
            'is_valid': False,
            'detected_classes': [],
            'message': f"Activity verification error: {str(e)}"
        }

@app.on_event("startup")
async def startup_event():
    """Initialize the waste collection model on startup"""
    global waste_model, ai_detector
    
    try:
        print("🗑️ Loading waste collection YOLO model...")
        waste_model = YOLO('waste_collection_yolov11.pt')
        print("✅ Waste collection model loaded successfully!")
        
        print("🤖 Loading AI detector...")
        ai_detector = pipeline("image-classification", model="umm-maybe/AI-image-detector")
        print("✅ AI detector loaded successfully!")
        
    except Exception as e:
        print(f"❌ Failed to initialize waste collection system: {e}")
        waste_model = None
        ai_detector = None

@app.get("/")
async def root():
    return {
        "message": "Waste Collection Verification API",
        "status": "running" if waste_model is not None else "error",
        "model_loaded": waste_model is not None
    }

@app.post("/verify-waste", response_model=VerificationResponse)
async def verify_waste(task_image: UploadFile = File(...)):
    """Verify waste collection task submission"""
    try:
        if waste_model is None:
            raise HTTPException(status_code=503, detail="Waste collection model not loaded")
        
        # Save uploaded image
        image_path = UPLOAD_DIR / f"waste_{uuid.uuid4()}.jpg"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(task_image.file, buffer)
        
        results = {'overall_valid': False, 'steps': {}}
        
        # Step 1: AI Detection
        img = Image.open(image_path)
        ai_result = verify_ai_image(img)
        results['steps']['ai_detection'] = ai_result
        
        if not ai_result['is_valid']:
            os.remove(image_path)
            results['message'] = ai_result['message']
            return VerificationResponse(**results)
        
        # Step 2: EXIF Verification
        exif_result = verify_exif_datetime(image_path)
        results['steps']['exif_verification'] = exif_result
        
        if not exif_result['is_valid']:
            os.remove(image_path)
            results['message'] = exif_result['message']
            return VerificationResponse(**results)
        
        # Step 3: Waste Collection Activity Verification
        activity_result = verify_waste_activity(image_path)
        results['steps']['activity_verification'] = activity_result
        
        if not activity_result['is_valid']:
            os.remove(image_path)
            results['message'] = activity_result['message']
            return VerificationResponse(**results)
        
        # All checks passed
        os.remove(image_path)
        results['overall_valid'] = True
        results['message'] = "Waste collection task verified successfully!"
        
        return VerificationResponse(**results)
        
    except Exception as e:
        if 'image_path' in locals() and os.path.exists(image_path):
            os.remove(image_path)
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)