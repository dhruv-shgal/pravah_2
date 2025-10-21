# Eco-Connect Flask App

A Flask web application that connects your eco-connect site to FastAPI backend routes with face registration and verification functionality.

## Features

- **Face Registration**: Users register with face capture during signup
- **Face Verification**: Users can login using face recognition
- **Activity Upload**: Upload and verify conservation activities using AI models
- **User Profile**: Track eco-points and activities
- **Responsive Design**: Works on desktop and mobile devices

## Project Structure

```
├── app.py                          # Flask application (main)
├── fastapi2.py                     # FastAPI backend with AI models
├── eco-connect-site.html           # Main eco-connect page
├── signup.html                     # User registration with face capture
├── login.html                      # User login with face verification  
├── profile.html                    # User profile page
├── start_services.py               # Startup script for both services
├── requirements.txt                # Python dependencies
├── plantation_yolov11.pt           # YOLO model for tree plantation
├── waste_collection_yolov11.pt     # YOLO model for waste collection
├── animal_feeding_yolov11.pt       # YOLO model for animal feeding
└── README.md                       # This file
```

## Quick Start

### Option 1: Use the startup script (Recommended)
```bash
python start_services.py
```

### Option 2: Manual startup

1. **Start FastAPI backend** (Terminal 1):
```bash
python fastapi2.py
```

2. **Start Flask frontend** (Terminal 2):
```bash
python app.py
```

## Access Points

- **Flask App**: http://localhost:5000
- **FastAPI Backend**: http://localhost:8000
- **FastAPI Docs**: http://localhost:8000/docs

## User Flow

1. **Signup** (`/signup`):
   - Enter username, email, user ID
   - Capture 5 face images for registration
   - Face embedding stored for future verification

2. **Login** (`/login`):
   - Enter user ID
   - Choose password login OR face verification
   - Face verification compares with stored embedding

3. **Profile** (`/profile`):
   - View eco-points and activity stats
   - Access quick actions for uploading activities

4. **Eco-Connect** (`/`):
   - Upload conservation activity photos
   - AI verification of activities (plantation, waste collection, animal feeding)
   - Earn eco-points for verified activities

## API Endpoints

### Flask Routes
- `GET /` - Main eco-connect page
- `GET /signup` - Registration page
- `GET /login` - Login page  
- `GET /profile` - User profile page
- `POST /api/signup` - Handle user registration
- `POST /api/login` - Handle user login
- `POST /api/verify-task` - Verify conservation activities
- `GET /health` - Health check

### FastAPI Backend Routes
- `POST /api/signup` - Face registration
- `POST /api/login` - Face verification
- `POST /api/verify-task` - Complete 4-step verification:
  1. AI image detection
  2. EXIF timestamp verification  
  3. Activity recognition (YOLO models)
  4. Face matching with registered user

## Requirements

### Python Packages
```
Flask==2.3.3
requests==2.31.0
Werkzeug==2.3.7
```

### FastAPI Dependencies (from fastapi2.py)
- fastapi
- uvicorn
- opencv-python
- numpy
- pillow
- insightface
- ultralytics
- torch
- transformers

### Model Files
- `plantation_yolov11.pt` - Tree plantation detection
- `waste_collection_yolov11.pt` - Waste collection detection  
- `animal_feeding_yolov11.pt` - Animal feeding detection

## Configuration

### FastAPI Model Paths
Update the model paths in `fastapi2.py` startup event:
```python
verifier = EcoConnectVerificationSystem(
    plantation_model_path='plantation_yolov11.pt',
    waste_model_path='waste_collection_yolov11.pt', 
    animal_model_path='animal_feeding_yolov11.pt'
)
```

### Flask Configuration
- Upload folder: `static/uploads`
- Allowed file types: PNG, JPG, JPEG
- Max file size: 10MB (configurable)

## Security Features

- Face embeddings stored securely (not raw images)
- Session management for user authentication
- File type validation for uploads
- EXIF timestamp verification (within 7 days)
- AI-generated image detection

## Troubleshooting

### Common Issues

1. **Models not loading**:
   - Ensure YOLO model files are in the correct directory
   - Check file permissions
   - Verify model file integrity

2. **Camera access denied**:
   - Allow camera permissions in browser
   - Use HTTPS for production (required for camera access)

3. **Backend connection failed**:
   - Ensure FastAPI is running on port 8000
   - Check firewall settings
   - Verify network connectivity

### Debug Mode
Both services run in debug mode by default for development.

## Production Deployment

For production deployment:

1. Set `debug=False` in Flask app
2. Use proper WSGI server (gunicorn, uWSGI)
3. Configure HTTPS for camera access
4. Set up proper database for user management
5. Configure environment variables for sensitive data
6. Set up proper logging and monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the PRAVAH eco-conservation platform.