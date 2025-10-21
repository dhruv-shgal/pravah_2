# Eco-Connect AI Verification App

Simple Flask app for AI-powered conservation activity verification.

## 🚀 Quick Start

1. **Start FastAPI backend** (in main directory):
```bash
python fastapi2.py
```

2. **Start Flask app**:
```bash
cd flask_eco
python app.py
```

3. **Open browser**:
```
http://localhost:3000
```

## 🌟 Features

- 🌳 Tree Plantation verification (+30 points)
- 🗑️ Waste Management verification (+20 points) 
- 🐾 Animal Feeding verification (+15 points)
- Real-time AI analysis using YOLO models
- No authentication required

## 🔧 API Endpoints

### Flask Endpoints
- `GET /` - Main eco-connect interface
- `POST /api/verify-task` - Verify conservation activity
- `GET /api/test-models` - Test AI model connectivity
- `GET /health` - Health check

### FastAPI Backend (Modified)
- `POST /api/verify-task-anonymous` - Anonymous task verification (NEW)
- `POST /api/verify-task` - Original user-based verification
- `GET /health` - Backend health check

## 📸 How It Works

### 1. Upload Process
1. User selects activity type (plantation/waste_management/stray_animal_feeding)
2. User uploads image of their conservation activity
3. Image is sent to Flask backend

### 2. AI Verification Pipeline
1. **Flask Processing**: Validates file and forwards to FastAPI
2. **FastAPI Anonymous Verification**:
   - AI-generated image detection
   - EXIF timestamp validation (within 7 days)
   - Activity recognition using appropriate YOLO model
   - Skip face verification (anonymous mode)
3. **Result Processing**: Points awarded based on verification success

### 3. Response Format
```json
{
  "success": true,
  "message": "Task verified successfully! Image matches plantation activity.",
  "points_earned": 30,
  "task_type": "plantation",
  "overall_valid": true,
  "verification_details": {
    "ai_detection": {"is_valid": true, "message": "Real image detected"},
    "exif_verification": {"is_valid": true, "message": "Recent timestamp"},
    "activity_verification": {"is_valid": true, "message": "Plantation activity detected"},
    "face_verification": {"is_valid": true, "message": "Skipped for anonymous usage"}
  }
}
```

## 🎯 Activity Recognition

### Plantation (30 points)
- Detects: Person + plantation/trees
- Model: plantation_yolov11.pt
- Validates: Tree planting activities

### Waste Management (20 points)  
- Detects: Person + waste collection
- Model: waste_collection_yolov11.pt
- Validates: Cleanup and waste collection activities

### Stray Animal Feeding (15 points)
- Detects: Person + animal feeding
- Model: animal_feeding_yolov11.pt  
- Validates: Animal care and feeding activities

## 🧪 Testing

### Run Integration Tests
```bash
python test_eco_integration.py
```

### Test Individual Components
```bash
# Test FastAPI directly
curl -X POST "http://localhost:8000/api/verify-task-anonymous" \
  -F "task_type=plantation" \
  -F "task_image=@test_image.jpg"

# Test Flask endpoint
curl -X POST "http://localhost:3000/api/verify-task" \
  -F "task_type=plantation" \
  -F "task_image=@test_image.jpg"
```

## 🔧 Configuration

### Environment Variables
```bash
FASTAPI_URL=http://localhost:8000  # FastAPI backend URL
FLASK_PORT=3000                    # Flask app port
```

### File Upload Limits
- Max file size: 10MB
- Supported formats: PNG, JPG, JPEG
- Image requirements: Must contain person performing activity

## 📊 Verification Process Details

### AI Detection
- Checks if image is AI-generated
- Uses transformer-based detection
- Rejects synthetic/artificial images

### EXIF Verification  
- Validates image timestamp
- Must be taken within 7 days
- Prevents old image reuse

### Activity Recognition
- Uses task-specific YOLO models
- Detects person + activity objects
- Confidence threshold: 50%

### Anonymous Mode
- No user authentication required
- Skips face verification step
- Suitable for public eco-connect usage

## 🚨 Error Handling

### Common Errors
- **Invalid task type**: Must be plantation/waste_management/stray_animal_feeding
- **No image uploaded**: Task image is required
- **AI detection failed**: Image appears to be AI-generated
- **EXIF verification failed**: Image timestamp invalid or too old
- **Activity not detected**: Image doesn't match selected activity type
- **Backend unavailable**: FastAPI service not running

### Troubleshooting
1. **Backend Connection Issues**:
   - Ensure FastAPI is running on port 8000
   - Check model files are present
   - Verify network connectivity

2. **Verification Failures**:
   - Use recent, real photos
   - Ensure person is visible in image
   - Match activity type with image content

3. **Performance Issues**:
   - Reduce image size if upload is slow
   - Check GPU availability for faster processing

## 🔄 Development

### Project Structure
```
flask_eco/
├── app.py                    # Main Flask application
├── templates/
│   └── eco-connect-site.html # Frontend interface
├── static/
│   └── uploads/              # Temporary upload storage
├── requirements.txt          # Dependencies
├── start_eco_app.py         # Startup script
├── test_eco_integration.py  # Integration tests
└── README.md                # This file
```

### Adding New Activity Types
1. Add new YOLO model to FastAPI
2. Update `valid_tasks` list in both Flask and FastAPI
3. Add activity type to frontend dropdown
4. Update points mapping and UI elements

## 📈 Performance

### Typical Response Times
- Image upload: < 1 second
- AI verification: 2-5 seconds
- Total process: 3-6 seconds

### Optimization Tips
- Use GPU for faster model inference
- Implement image compression
- Cache model loading
- Use async processing for multiple uploads

## 🔐 Security

### Image Validation
- File type checking
- Size limits enforced
- AI-generated image detection
- EXIF timestamp validation

### Anonymous Usage
- No personal data stored
- Temporary image processing
- Automatic cleanup after verification

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Run integration tests
3. Verify FastAPI backend status
4. Check model file availability

---

**Built for conservation and environmental protection** 🌱