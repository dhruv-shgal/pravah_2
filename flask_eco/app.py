from flask import Flask, render_template, request, jsonify, session, flash, redirect, url_for, Response
import requests
import os
from werkzeug.utils import secure_filename
import uuid
import json
from datetime import datetime
import cv2
import numpy as np
import base64
import io
from PIL import Image
from pathlib import Path
import hashlib
import re
import dns.resolver
import socket
# Try to import face_recognition, fallback to OpenCV if not available
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
    print("✅ Face recognition library loaded successfully")
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("⚠️ Face recognition library not available. Using OpenCV fallback for basic face detection.")

app = Flask(__name__)
app.secret_key = "eco-connect-secret"
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

# FastAPI backend URL
FASTAPI_URL = "http://localhost:8000"

# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Create data storage directories
DATA_DIR = Path('data')
USERS_DIR = DATA_DIR / 'users'
IMAGES_DIR = DATA_DIR / 'images'

DATA_DIR.mkdir(exist_ok=True)
USERS_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_user_data(user_data):
    """Save user data to JSON file"""
    try:
        user_id = user_data['user_id']
        user_file = USERS_DIR / f"{user_id}.json"
        
        # Add timestamp
        user_data['created_at'] = datetime.now().isoformat()
        user_data['updated_at'] = datetime.now().isoformat()
        
        with open(user_file, 'w') as f:
            json.dump(user_data, f, indent=2)
        
        print(f"DEBUG: User data saved to {user_file}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to save user data: {e}")
        return False

def save_face_images_to_disk(user_id, face_images_data):
    """Save face images to disk and return file paths"""
    try:
        user_images_dir = IMAGES_DIR / user_id
        user_images_dir.mkdir(exist_ok=True)
        
        saved_images = []
        
        for i in range(5):
            if str(i) in face_images_data:
                image_data_str = face_images_data[str(i)]
                
                # Remove data URL prefix if present
                if image_data_str.startswith('data:image'):
                    image_data_str = image_data_str.split(',')[1]
                
                # Decode base64 image
                image_data = base64.b64decode(image_data_str)
                
                # Save image to disk
                image_filename = f"face_{i+1}.jpg"
                image_path = user_images_dir / image_filename
                
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                
                # Create image info
                image_info = {
                    'filename': image_filename,
                    'path': str(image_path),
                    'size': len(image_data),
                    'index': i,
                    'created_at': datetime.now().isoformat()
                }
                
                saved_images.append(image_info)
        
        print(f"DEBUG: Saved {len(saved_images)} face images for user {user_id}")
        return saved_images
    except Exception as e:
        print(f"ERROR: Failed to save face images: {e}")
        return []

def load_user_data(user_id):
    """Load user data from JSON file"""
    try:
        user_file = USERS_DIR / f"{user_id}.json"
        if user_file.exists():
            with open(user_file, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"ERROR: Failed to load user data: {e}")
        return None

def get_all_users():
    """Get list of all registered users"""
    try:
        users = []
        for user_file in USERS_DIR.glob("*.json"):
            with open(user_file, 'r') as f:
                user_data = json.load(f)
                # Remove sensitive data for listing
                safe_data = {
                    'user_id': user_data.get('user_id'),
                    'username': user_data.get('username'),
                    'email': user_data.get('email'),
                    'created_at': user_data.get('created_at'),
                    'face_images_count': len(user_data.get('face_images', []))
                }
                users.append(safe_data)
        return users
    except Exception as e:
        print(f"ERROR: Failed to get users list: {e}")
        return []

def validate_email_format(email):
    """Validate email format using regex"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_email_domain(email):
    """Validate if email domain exists (DNS check)"""
    try:
        domain = email.split('@')[1]
        # Check if domain has MX record
        mx_records = dns.resolver.resolve(domain, 'MX')
        return len(mx_records) > 0
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, Exception):
        try:
            # Fallback: check if domain resolves to any IP
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            return False

def validate_email(email):
    """Complete email validation"""
    if not email:
        return False, "Email is required"
    
    if not validate_email_format(email):
        return False, "Invalid email format"
    
    if not validate_email_domain(email):
        return False, "Email domain does not exist"
    
    return True, "Email is valid"

def validate_password(password):
    """Validate password strength"""
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)"
    
    return True, "Password is strong"

def check_username_exists(username):
    """Check if username already exists"""
    try:
        users = get_all_users()
        for user in users:
            if user['username'].lower() == username.lower():
                return True
        return False
    except Exception as e:
        print(f"ERROR: Failed to check username: {e}")
        return False

def check_user_id_exists(user_id):
    """Check if user_id already exists"""
    try:
        users = get_all_users()
        for user in users:
            if user['user_id'].lower() == user_id.lower():
                return True
        return False
    except Exception as e:
        print(f"ERROR: Failed to check user_id: {e}")
        return False

def check_email_exists(email):
    """Check if email already exists"""
    try:
        users = get_all_users()
        for user in users:
            if user['email'].lower() == email.lower():
                return True
        return False
    except Exception as e:
        print(f"ERROR: Failed to check email: {e}")
        return False

def validate_signup_data(email, password, username, user_id):
    """Comprehensive validation for signup data"""
    errors = []
    
    # Validate email
    email_valid, email_msg = validate_email(email)
    if not email_valid:
        errors.append(email_msg)
    elif check_email_exists(email):
        errors.append("Email is already registered")
    
    # Validate password
    password_valid, password_msg = validate_password(password)
    if not password_valid:
        errors.append(password_msg)
    
    # Validate username
    if not username:
        errors.append("Username is required")
    elif len(username) < 3:
        errors.append("Username must be at least 3 characters long")
    elif check_username_exists(username):
        errors.append("Username is already taken")
    
    # Validate user_id
    if not user_id:
        errors.append("User ID is required")
    elif len(user_id) < 3:
        errors.append("User ID must be at least 3 characters long")
    elif check_user_id_exists(user_id):
        errors.append("User ID is already taken")
    
    return len(errors) == 0, errors

def verify_user_face_in_image(user_id, task_image_data):
    """Verify if the user's face appears in the uploaded task image"""
    try:
        if not FACE_RECOGNITION_AVAILABLE:
            # Fallback to basic face detection with OpenCV
            return verify_face_opencv_fallback(user_id, task_image_data)
        
        # Load user's registered face images
        user_data = load_user_data(user_id)
        if not user_data or not user_data.get('face_images'):
            return False, "No registered face images found for user"
        
        # Load user's face encodings
        user_face_encodings = []
        user_images_dir = IMAGES_DIR / user_id
        
        for face_image_info in user_data['face_images']:
            face_image_path = user_images_dir / face_image_info['filename']
            if face_image_path.exists():
                # Load and encode the registered face image
                registered_image = face_recognition.load_image_file(str(face_image_path))
                face_encodings = face_recognition.face_encodings(registered_image)
                if face_encodings:
                    user_face_encodings.append(face_encodings[0])
        
        if not user_face_encodings:
            return False, "Could not process registered face images"
        
        # Process the uploaded task image
        # Convert base64 to image if needed
        if isinstance(task_image_data, str) and task_image_data.startswith('data:image'):
            task_image_data = task_image_data.split(',')[1]
            task_image_bytes = base64.b64decode(task_image_data)
        else:
            task_image_bytes = task_image_data
        
        # Load the task image
        task_image = Image.open(io.BytesIO(task_image_bytes))
        task_image_array = np.array(task_image)
        
        # Find faces in the task image
        task_face_locations = face_recognition.face_locations(task_image_array)
        task_face_encodings = face_recognition.face_encodings(task_image_array, task_face_locations)
        
        if not task_face_encodings:
            return False, "No faces detected in the uploaded image"
        
        # Compare each face in the task image with user's registered faces
        for task_face_encoding in task_face_encodings:
            # Compare with all registered face encodings
            matches = face_recognition.compare_faces(user_face_encodings, task_face_encoding, tolerance=0.6)
            if any(matches):
                return True, "User face verified in the uploaded image"
        
        return False, "User face not found in the uploaded image"
        
    except Exception as e:
        print(f"ERROR: Face verification failed: {e}")
        return False, f"Face verification error: {str(e)}"

def verify_face_opencv_fallback(user_id, task_image_data):
    """Fallback face verification using OpenCV (basic face detection only)"""
    try:
        # Convert image data to OpenCV format
        if isinstance(task_image_data, str) and task_image_data.startswith('data:image'):
            task_image_data = task_image_data.split(',')[1]
            task_image_bytes = base64.b64decode(task_image_data)
        else:
            task_image_bytes = task_image_data
        
        # Load the task image
        task_image = Image.open(io.BytesIO(task_image_bytes))
        task_image_array = np.array(task_image)
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(task_image_array, cv2.COLOR_RGB2GRAY)
        
        # Load OpenCV face cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) > 0:
            # Basic verification: just check if any face is detected
            # This is a simplified fallback - not as secure as face_recognition
            print(f"DEBUG: OpenCV detected {len(faces)} face(s) in the uploaded image")
            return True, f"Face detected in uploaded image (basic verification - {len(faces)} face(s) found)"
        else:
            return False, "No faces detected in the uploaded image"
            
    except Exception as e:
        print(f"ERROR: OpenCV face verification failed: {e}")
        # If face verification fails, allow the upload but warn the user
        return True, "Face verification unavailable - proceeding without face check"

@app.route('/')
def index():
    """Main eco-connect page with authentication options"""
    # Check if user is logged in
    if 'user_id' in session:
        # User is logged in, show main page with user data
        return render_template('eco-connect-site.html', 
                             logged_in=True,
                             username=session.get('username'),
                             eco_coins=session.get('eco_coins', 0))
    else:
        # User not logged in, show main page with auth options
        return render_template('eco-connect-site.html', logged_in=False)

@app.route('/auth')
def auth_page():
    """Authentication page with login/signup options"""
    return render_template('auth.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user signup with face registration"""
    if request.method == 'POST':
        try:
            # Get form data
            email = request.form.get('email')
            password = request.form.get('password')
            username = request.form.get('username')
            user_id = request.form.get('userId')
            
            print(f"DEBUG: Signup attempt - email: {email}, username: {username}, user_id: {user_id}")
            
            # Comprehensive validation
            is_valid, validation_errors = validate_signup_data(email, password, username, user_id)
            
            if not is_valid:
                for error in validation_errors:
                    flash(error, 'error')
                return render_template('signup.html')
            
            # Get face images from form fields (more reliable than session)
            face_images_data = {}
            for i in range(5):
                image_field = request.form.get(f'face_image_{i}')
                if image_field and len(image_field) > 0:
                    face_images_data[str(i)] = image_field
            
            print(f"DEBUG: Retrieved {len(face_images_data)} face images from form fields")
            
            if len(face_images_data) != 5:
                # Fallback to session if form fields are empty
                session_images = session.get('face_images', {})
                print(f"DEBUG: Fallback to session - found {len(session_images)} images")
                
                if len(session_images) == 5:
                    face_images_data = session_images
                    print("DEBUG: Using session images as fallback")
                else:
                    flash(f'Please capture all 5 face images. Currently have {len(face_images_data)} images.', 'error')
                    return render_template('signup.html')
            
            # Prepare data for FastAPI
            files = []
            for i in range(5):
                if str(i) in face_images_data:
                    image_data_str = face_images_data[str(i)]
                    
                    # Remove data URL prefix if present
                    if image_data_str.startswith('data:image'):
                        image_data_str = image_data_str.split(',')[1]
                    
                    # Decode base64 image
                    image_data = base64.b64decode(image_data_str)
                    files.append(('face_images', (f'face_{i+1}.jpg', image_data, 'image/jpeg')))
            
            data = {
                'email': email,
                'password': password,
                'username': username,
                'user_id': user_id
            }
            
            print(f"DEBUG: Sending request to {FASTAPI_URL}/api/signup")
            
            # Send to FastAPI backend
            response = requests.post(f"{FASTAPI_URL}/api/signup", files=files, data=data, timeout=30)
            
            print(f"DEBUG: FastAPI response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    # Save face images to disk
                    saved_images = save_face_images_to_disk(user_id, face_images_data)
                    
                    # Prepare complete user data
                    complete_user_data = {
                        'user_id': user_id,
                        'username': username,
                        'email': email,
                        'password_hash': hashlib.sha256(password.encode()).hexdigest(),
                        'face_images': saved_images,
                        'eco_coins': 0,
                        'uploads': [],
                        'fastapi_response': result,
                        'signup_method': 'opencv_capture',
                        'total_face_images': len(saved_images)
                    }
                    
                    # Save user data to JSON file
                    if save_user_data(complete_user_data):
                        print(f"✅ User {user_id} data saved successfully")
                    
                    # Store user data in session
                    session['user_id'] = user_id
                    session['username'] = username
                    session['email'] = email
                    session['eco_coins'] = 0
                    session['uploads'] = []
                    
                    # Clear face images from session
                    if 'face_images' in session:
                        del session['face_images']
                    
                    flash('Account created successfully! Welcome to Eco-Connect!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash(result.get('message', 'Signup failed'), 'error')
            else:
                # Handle HTTP error responses
                try:
                    error_detail = response.json()
                    flash(f"Signup failed: {error_detail.get('detail', 'Unknown error')}", 'error')
                except:
                    flash(f"Signup failed: HTTP {response.status_code}", 'error')
                
        except requests.exceptions.ConnectionError:
            flash('Backend service unavailable. Please ensure FastAPI is running on port 8000.', 'error')
        except requests.exceptions.Timeout:
            flash('Request timeout. Please try again.', 'error')
        except Exception as e:
            print(f"DEBUG: Exception in signup: {str(e)}")
            flash(f'Signup error: {str(e)}', 'error')
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login with face verification"""
    if request.method == 'POST':
        try:
            # Get form data
            identifier = request.form.get('identifier')
            password = request.form.get('password')
            
            if not identifier or not password:
                flash('Email/User ID and password are required', 'error')
                return render_template('login.html')
            
            # First check local user data
            local_user = None
            
            # Search for user by email or user_id in local storage
            all_users = get_all_users()
            for user_summary in all_users:
                if user_summary['email'] == identifier or user_summary['user_id'] == identifier:
                    local_user = load_user_data(user_summary['user_id'])
                    break
            
            if local_user:
                # Verify password against stored hash
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                if local_user.get('password_hash') == password_hash:
                    # Local authentication successful
                    session['user_id'] = local_user['user_id']
                    session['username'] = local_user['username']
                    session['email'] = local_user['email']
                    session['eco_coins'] = local_user.get('eco_coins', 0)
                    session['uploads'] = local_user.get('uploads', [])
                    
                    flash('Login successful! Welcome back to Eco-Connect!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Invalid password', 'error')
                    return render_template('login.html')
            
            # Fallback to FastAPI authentication
            print("DEBUG: User not found locally, trying FastAPI authentication...")
            
            data = {
                'identifier': identifier,
                'password': password
            }
            
            try:
                response = requests.post(f"{FASTAPI_URL}/api/login", data=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get('success'):
                        user_data = result.get('user_data', {})
                        
                        session['user_id'] = user_data.get('user_id', identifier)
                        session['username'] = user_data.get('username', identifier)
                        session['email'] = user_data.get('email', '')
                        session['eco_coins'] = 0
                        session['uploads'] = []
                        
                        flash('Login successful! Welcome to Eco-Connect!', 'success')
                        return redirect(url_for('index'))
                    else:
                        flash(result.get('message', 'Login failed'), 'error')
                else:
                    try:
                        error_detail = response.json()
                        flash(f"Login failed: {error_detail.get('detail', 'Unknown error')}", 'error')
                    except:
                        flash(f"Login failed: HTTP {response.status_code}", 'error')
            except requests.exceptions.ConnectionError:
                flash('Backend service unavailable and user not found locally', 'error')
            except Exception as e:
                flash(f'Login error: {str(e)}', 'error')
                
        except Exception as e:
            flash(f'Login error: {str(e)}', 'error')
    
    return render_template('login.html')

@app.route('/guest')
def continue_as_guest():
    """Continue as guest without authentication"""
    # Set guest session
    session['guest_mode'] = True
    session['username'] = 'Guest User'
    session['eco_coins'] = 0
    session['uploads'] = []
    
    flash('Welcome! You are browsing as a guest. Sign up to save your progress!', 'info')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/api/verify-task', methods=['POST'])
def verify_task():
    """Handle task verification for both authenticated and guest users"""
    try:
        # Get task type from form
        task_type = request.form.get('task_type')
        if not task_type:
            return jsonify({
                'success': False,
                'message': 'Task type is required'
            })
        
        # Validate task type
        valid_tasks = ['tree_planting', 'waste_management', 'stray_animal_feeding']
        if task_type not in valid_tasks:
            return jsonify({
                'success': False,
                'message': f'Invalid task type. Must be one of: {", ".join(valid_tasks)}'
            })
        
        # Get task image
        if 'task_image' not in request.files:
            return jsonify({
                'success': False,
                'message': 'Task image is required'
            })
        
        task_image = request.files['task_image']
        if task_image.filename == '':
            return jsonify({
                'success': False,
                'message': 'No image selected'
            })
        
        if not allowed_file(task_image.filename):
            return jsonify({
                'success': False,
                'message': 'Invalid file type. Please use PNG, JPG, or JPEG'
            })
        
        print(f"DEBUG: Verifying {task_type} task with image: {task_image.filename}")
        
        # Face verification for authenticated users (not guests)
        if 'user_id' in session and not session.get('guest_mode'):
            print(f"DEBUG: Performing face verification for user {session['user_id']}")
            
            # Read the image data for face verification
            task_image_data = task_image.read()
            task_image.seek(0)  # Reset file pointer for later use
            
            face_verified, face_message = verify_user_face_in_image(session['user_id'], task_image_data)
            
            if not face_verified:
                return jsonify({
                    'success': False,
                    'message': f'Face verification failed: {face_message}. Please ensure you appear in the uploaded image.',
                    'face_verification_failed': True
                })
            
            print(f"DEBUG: Face verification successful: {face_message}")
        
        # Determine which API to call based on task type
        api_endpoints = {
            'tree_planting': 'http://localhost:8001/verify-plantation',
            'waste_management': 'http://localhost:8002/verify-waste',
            'stray_animal_feeding': 'http://localhost:8003/verify-animal-feeding'
        }
        
        if task_type not in api_endpoints:
            print(f"DEBUG: Invalid task type: {task_type}")
            return jsonify({
                'success': False,
                'message': f'Invalid task type: {task_type}'
            })
        
        # Prepare data for specific API (only task_image)
        files = {'task_image': (task_image.filename, task_image.read(), task_image.content_type)}
        
        # Send request to appropriate FastAPI service
        api_url = api_endpoints[task_type]
        print(f"DEBUG: Calling API: {api_url}")
        
        try:
            response = requests.post(api_url, files=files, timeout=60)
        except requests.exceptions.ConnectionError as e:
            print(f"DEBUG: Connection error to {api_url}: {e}")
            return jsonify({
                'success': False,
                'message': f'Cannot connect to {task_type} verification service. Please ensure the API is running.'
            })
        except requests.exceptions.Timeout as e:
            print(f"DEBUG: Timeout error to {api_url}: {e}")
            return jsonify({
                'success': False,
                'message': 'Verification timeout. Please try again.'
            })
        
        print(f"DEBUG: FastAPI response status: {response.status_code}")
        print(f"DEBUG: FastAPI response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Process the verification result
            if result.get('overall_valid'):
                # Calculate points based on task type
                points_map = {
                    'tree_planting': 30,
                    'waste_management': 20,
                    'stray_animal_feeding': 15
                }
                
                points_earned = points_map.get(task_type, 10)
                
                # Update user data if logged in
                if 'user_id' in session and not session.get('guest_mode'):
                    # Update session data
                    session['eco_coins'] = session.get('eco_coins', 0) + points_earned
                    
                    # Add to uploads list
                    upload_entry = {
                        'task_type': task_type,
                        'points': points_earned,
                        'timestamp': str(datetime.now()),
                        'verification_result': result
                    }
                    
                    uploads = session.get('uploads', [])
                    uploads.append(upload_entry)
                    session['uploads'] = uploads
                    
                    # Update user data file
                    user_data = load_user_data(session['user_id'])
                    if user_data:
                        user_data['eco_coins'] = session['eco_coins']
                        user_data['uploads'] = uploads
                        user_data['updated_at'] = datetime.now().isoformat()
                        save_user_data(user_data)
                    
                    message = f'Task verified successfully! +{points_earned} eco-coins earned'
                else:
                    # Guest user
                    if session.get('guest_mode'):
                        session['eco_coins'] = session.get('eco_coins', 0) + points_earned
                        message = f'Task verified successfully! +{points_earned} eco-coins earned (Sign up to save progress!)'
                    else:
                        message = f'Task verified successfully! Activity matches {task_type.replace("_", " ")} (Login to earn coins!)'
                
                return jsonify({
                    'success': True,
                    'message': message,
                    'points_earned': points_earned,
                    'total_coins': session.get('eco_coins', 0),
                    'task_type': task_type,
                    'verification_details': result.get('steps', {}),
                    'overall_valid': True,
                    'logged_in': 'user_id' in session and not session.get('guest_mode'),
                    'guest_mode': session.get('guest_mode', False)
                })
            else:
                return jsonify({
                    'success': False,
                    'message': result.get('message', 'Task verification failed'),
                    'verification_details': result.get('steps', {}),
                    'overall_valid': False
                })
        else:
            # Handle HTTP error responses
            try:
                error_detail = response.json()
                return jsonify({
                    'success': False,
                    'message': f"Verification failed: {error_detail.get('detail', 'Unknown error')}"
                })
            except:
                return jsonify({
                    'success': False,
                    'message': f"Verification failed: HTTP {response.status_code}"
                })
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'message': 'Backend service unavailable. Please ensure FastAPI is running on port 8000.'
        })
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'message': 'Verification timeout. Please try again with a smaller image.'
        })
    except Exception as e:
        print(f"DEBUG: Exception in verify_task: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Verification error: {str(e)}'
        })

# OpenCV Face Capture Routes
camera = None

@app.route('/start_camera')
def start_camera():
    """Initialize camera for face capture"""
    global camera
    try:
        if camera is None:
            camera = cv2.VideoCapture(0)
            if not camera.isOpened():
                return jsonify({'success': False, 'message': 'Could not open camera'})
        
        return jsonify({'success': True, 'message': 'Camera started successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Camera error: {str(e)}'})

@app.route('/capture_frame')
def capture_frame():
    """Capture a single frame from camera"""
    global camera
    try:
        if camera is None or not camera.isOpened():
            return jsonify({'success': False, 'message': 'Camera not initialized'})
        
        ret, frame = camera.read()
        if not ret:
            return jsonify({'success': False, 'message': 'Failed to capture frame'})
        
        # Convert frame to base64 for transmission
        _, buffer = cv2.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True, 
            'frame': frame_base64,
            'message': 'Frame captured successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Capture error: {str(e)}'})

@app.route('/save_face_image', methods=['POST'])
def save_face_image():
    """Save captured face image"""
    try:
        data = request.get_json()
        image_data = data.get('image_data')
        image_index = data.get('image_index', 0)
        
        if not image_data:
            return jsonify({'success': False, 'message': 'No image data provided'})
        
        # Remove data URL prefix if present
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Save to session for later use in signup
        if 'face_images' not in session:
            session['face_images'] = {}
        
        # Convert image to base64 for session storage
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        session['face_images'][str(image_index)] = img_str
        session.modified = True
        
        print(f"DEBUG: Saved face image {image_index} to session. Total images: {len(session['face_images'])}")
        
        return jsonify({
            'success': True, 
            'message': f'Face image {image_index + 1} saved successfully',
            'images_count': len(session['face_images'])
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Save error: {str(e)}'})

@app.route('/stop_camera')
def stop_camera():
    """Stop and release camera"""
    global camera
    try:
        if camera is not None:
            camera.release()
            camera = None
        
        return jsonify({'success': True, 'message': 'Camera stopped successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Stop camera error: {str(e)}'})

@app.route('/get_face_images_count')
def get_face_images_count():
    """Get count of captured face images"""
    face_images = session.get('face_images', {})
    count = len(face_images)
    return jsonify({'count': count, 'keys': list(face_images.keys())})

@app.route('/clear_face_images', methods=['POST'])
def clear_face_images():
    """Clear face images from session"""
    if 'face_images' in session:
        del session['face_images']
        session.modified = True
    return jsonify({'success': True, 'message': 'Face images cleared from session'})

@app.route('/api/user-stats')
def user_stats():
    """Get user statistics"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'})
    
    uploads = session.get('uploads', [])
    
    # Calculate statistics
    stats = {
        'total_coins': session.get('eco_coins', 0),
        'total_uploads': len(uploads),
        'tree_planting_count': len([u for u in uploads if u['task_type'] == 'tree_planting']),
        'waste_count': len([u for u in uploads if u['task_type'] == 'waste_management']),
        'animal_count': len([u for u in uploads if u['task_type'] == 'stray_animal_feeding']),
        'recent_uploads': uploads[-5:] if uploads else []
    }
    
    return jsonify(stats)

@app.route('/profile')
def profile():
    """User profile page"""
    if 'user_id' not in session:
        flash('Please login to access your profile', 'error')
        return redirect(url_for('login'))
    
    return render_template('profile.html', 
                         username=session.get('username'),
                         email=session.get('email', ''),
                         eco_coins=session.get('eco_coins', 0),
                         uploads=session.get('uploads', []))

@app.route('/api/test-models')
def test_models():
    """Test if all AI models are working"""
    try:
        # Test all three APIs
        api_endpoints = {
            'plantation': 'http://localhost:8001/',
            'waste_management': 'http://localhost:8002/',
            'stray_animal_feeding': 'http://localhost:8003/'
        }
        
        results = {}
        all_working = True
        
        for task_name, url in api_endpoints.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    results[task_name] = {
                        'status': 'running',
                        'model_loaded': data.get('model_loaded', False)
                    }
                else:
                    results[task_name] = {'status': 'error', 'model_loaded': False}
                    all_working = False
            except:
                results[task_name] = {'status': 'offline', 'model_loaded': False}
                all_working = False
        
        return jsonify({
            'success': all_working,
            'apis': results,
            'message': 'All AI models ready' if all_working else 'Some APIs are not responding'
        })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Model test error: {str(e)}'
        })

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Check all three API backends
        api_status = {}
        api_endpoints = {
            'plantation': 'http://localhost:8001/',
            'waste_management': 'http://localhost:8002/',
            'stray_animal_feeding': 'http://localhost:8003/'
        }
        
        for task_name, url in api_endpoints.items():
            try:
                response = requests.get(url, timeout=3)
                api_status[task_name] = 'running' if response.status_code == 200 else 'error'
            except:
                api_status[task_name] = 'offline'
        
        all_running = all(status == 'running' for status in api_status.values())
        
        return jsonify({
            'status': 'healthy' if all_running else 'partial',
            'flask_status': 'running',
            'api_services': api_status,
            'models_available': all_running
        })
    except:
        return jsonify({
            'status': 'error',
            'flask_status': 'running',
            'api_services': {'plantation': 'unknown', 'waste_management': 'unknown', 'stray_animal_feeding': 'unknown'},
            'models_available': False
        })

# Validation API Routes
@app.route('/api/validate-email', methods=['POST'])
def api_validate_email():
    """Validate email in real-time"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'valid': False, 'message': 'Email is required'})
        
        # Check format
        if not validate_email_format(email):
            return jsonify({'valid': False, 'message': 'Invalid email format'})
        
        # Check if already exists
        if check_email_exists(email):
            return jsonify({'valid': False, 'message': 'Email is already registered'})
        
        # Check domain (async in background for better UX)
        domain_valid = validate_email_domain(email)
        if not domain_valid:
            return jsonify({'valid': False, 'message': 'Email domain does not exist'})
        
        return jsonify({'valid': True, 'message': 'Email is available'})
        
    except Exception as e:
        return jsonify({'valid': False, 'message': f'Validation error: {str(e)}'})

@app.route('/api/validate-username', methods=['POST'])
def api_validate_username():
    """Validate username in real-time"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({'valid': False, 'message': 'Username is required'})
        
        if len(username) < 3:
            return jsonify({'valid': False, 'message': 'Username must be at least 3 characters long'})
        
        if check_username_exists(username):
            return jsonify({'valid': False, 'message': 'Username is already taken'})
        
        return jsonify({'valid': True, 'message': 'Username is available'})
        
    except Exception as e:
        return jsonify({'valid': False, 'message': f'Validation error: {str(e)}'})

@app.route('/api/validate-user-id', methods=['POST'])
def api_validate_user_id():
    """Validate user ID in real-time"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', '').strip()
        
        if not user_id:
            return jsonify({'valid': False, 'message': 'User ID is required'})
        
        if len(user_id) < 3:
            return jsonify({'valid': False, 'message': 'User ID must be at least 3 characters long'})
        
        if check_user_id_exists(user_id):
            return jsonify({'valid': False, 'message': 'User ID is already taken'})
        
        return jsonify({'valid': True, 'message': 'User ID is available'})
        
    except Exception as e:
        return jsonify({'valid': False, 'message': f'Validation error: {str(e)}'})

@app.route('/api/validate-password', methods=['POST'])
def api_validate_password():
    """Validate password strength in real-time"""
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        is_valid, message = validate_password(password)
        return jsonify({'valid': is_valid, 'message': message})
        
    except Exception as e:
        return jsonify({'valid': False, 'message': f'Validation error: {str(e)}'})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🌱 Eco-Connect - Integrated Conservation Platform")
    print("=" * 50)
    print("🚀 Starting on: http://localhost:3000")
    print("🤖 AI Backend: http://localhost:8000 (make sure it's running)")
    print("� Feataures: Login/Signup + Guest Mode + Face Recognition")
    print("📸 Upload images to verify conservation activities!")
    print("🎯 Earn eco-coins for verified activities!")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=3000)