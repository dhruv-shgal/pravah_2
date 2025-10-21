# PRAVAH Flask Frontend

A Flask web application that serves as the frontend connector for PRAVAH: AI Meets Conservation. This app provides the user interface and connects to the FastAPI backend for AI-powered conservation activity verification.

## 🌟 Features

- **Face Registration**: Secure user signup with face capture and embedding storage
- **Face Verification**: Login using face recognition technology
- **Activity Upload**: Upload conservation activities with AI verification
- **Real-time Verification**: 4-step verification process:
  1. AI-generated image detection
  2. EXIF timestamp verification
  3. Activity recognition (YOLO models)
  4. Face matching with registered user
- **Eco-Points System**: Earn points for verified activities
- **User Dashboard**: Track progress, view statistics, and manage activities
- **Responsive Design**: Works seamlessly on desktop and mobile

## 📁 Project Structure

```
flask_app/
├── app.py                      # Main Flask application
├── run.py                      # Startup script with backend checks
├── requirements.txt            # Python dependencies
├── templates/                  # Jinja2 templates
│   ├── signup.html            # User registration with face capture
│   ├── login.html             # Login with face verification
│   ├── profile.html           # User dashboard and activity upload
│   ├── 404.html               # 404 error page
│   └── 500.html               # 500 error page
├── static/                     # Static assets
│   ├── uploads/               # Uploaded images (auto-created)
│   ├── css/                   # Custom CSS files
│   └── js/                    # Custom JavaScript files
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

1. **FastAPI Backend**: Ensure the FastAPI backend is running on port 8000
2. **Python 3.7+**: Required for Flask application
3. **Camera Access**: For face registration and verification

### Installation & Setup

1. **Navigate to Flask app directory**:
```bash
cd flask_app
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Start the application**:
```bash
python run.py
```

The startup script will:
- Check if FastAPI backend is running
- Install requirements automatically
- Create necessary directories
- Start Flask on http://localhost:5000

### Manual Start (Alternative)

```bash
python app.py
```

## 🔗 API Integration

The Flask app connects to these FastAPI endpoints:

| Flask Route | FastAPI Endpoint | Purpose |
|-------------|------------------|---------|
| `POST /signup` | `POST /api/signup` | User registration with face |
| `POST /login` | `POST /api/login` | Face verification login |
| `POST /upload/<task_type>` | `POST /api/verify-task` | Activity verification |
| `GET /health` | `GET /health` | System health check |

## 🎯 User Journey

### 1. Signup Process (`/signup`)
- Enter username, email, and unique user ID
- Capture 5 face images using webcam
- Face embedding stored securely in FastAPI backend
- Redirect to profile page on success

### 2. Login Process (`/login`)
- Enter user ID or email
- Choose between password login or face verification
- For face login: capture image and verify against stored embedding
- Redirect to profile page on successful authentication

### 3. Profile Dashboard (`/profile/<user_id>`)
- View eco-points, activity count, and current rank
- Upload conservation activities:
  - **Tree Plantation** (+30 points)
  - **Waste Collection** (+20 points)
  - **Animal Feeding** (+15 points)
- Real-time verification using AI models
- View recent activities and achievements

## 🏆 Eco-Points System

| Activity Type | Points Earned | Verification Requirements |
|---------------|---------------|--------------------------|
| Tree Plantation | 30 points | Person + plantation detected |
| Waste Collection | 20 points | Person + waste collection detected |
| Animal Feeding | 15 points | Person + animal feeding detected |

### Ranking System
- **Beginner**: 0-49 points
- **Intermediate**: 50-199 points
- **Advanced**: 200-499 points
- **Expert**: 500+ points

## 🔧 Configuration

### Environment Variables
```python
# Flask Configuration
FASTAPI_URL = "http://localhost:8000"  # FastAPI backend URL
UPLOAD_FOLDER = 'static/uploads'       # Upload directory
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}  # Allowed file types
```

### Session Management
User data is stored in Flask sessions:
- `user_id`: Unique user identifier
- `username`: Display name
- `email`: User email address
- `eco_coins`: Current eco-points balance
- `uploads`: List of uploaded activities

## 🛡️ Security Features

- **Secure Face Storage**: Only embeddings stored, not raw images
- **File Type Validation**: Only image files accepted
- **Session Management**: Secure user authentication
- **CSRF Protection**: Built-in Flask security
- **Input Validation**: Server-side validation for all inputs

## 🎨 UI/UX Features

- **Dark/Light Mode**: Toggle between themes
- **Responsive Design**: Mobile-friendly interface
- **Real-time Feedback**: Live status updates during uploads
- **Progress Indicators**: Visual feedback for long operations
- **Flash Messages**: User-friendly error and success messages

## 📱 Mobile Support

The application is fully responsive and supports:
- Touch-friendly interface
- Mobile camera access
- Optimized layouts for small screens
- Gesture-based navigation

## 🔍 Troubleshooting

### Common Issues

1. **FastAPI Backend Not Running**
   ```
   Error: Backend service unavailable
   Solution: Start FastAPI backend first: python fastapi2.py
   ```

2. **Camera Access Denied**
   ```
   Error: Camera access denied
   Solution: Allow camera permissions in browser settings
   ```

3. **Upload Failures**
   ```
   Error: Verification timeout
   Solution: Ensure image quality and try again
   ```

4. **Session Issues**
   ```
   Error: Please login first
   Solution: Clear browser cookies and login again
   ```

### Debug Mode

Enable debug mode for development:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Health Check

Check system status:
```bash
curl http://localhost:5000/health
```

## 🚀 Production Deployment

For production deployment:

1. **Disable Debug Mode**:
```python
app.run(debug=False)
```

2. **Use Production WSGI Server**:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. **Configure HTTPS**: Required for camera access in production

4. **Environment Variables**: Set production configurations

5. **Database Integration**: Replace session storage with persistent database

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the PRAVAH: AI Meets Conservation platform.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review FastAPI backend logs
3. Ensure all dependencies are installed
4. Verify camera permissions

---

**Built with ❤️ for conservation and environmental protection** 🌱