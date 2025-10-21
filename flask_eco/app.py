from flask import Flask, render_template, request, jsonify
import requests
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

# FastAPI backend URL
FASTAPI_URL = "http://localhost:8000"

# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main eco-connect page - no authentication required"""
    return render_template('eco-connect-site.html')

@app.route('/auth')
def auth_redirect():
    """Redirect auth requests back to main page"""
    return render_template('eco-connect-site.html')

@app.route('/api/verify-task', methods=['POST'])
def verify_task():
    """Handle task verification without user_id requirement"""
    try:
        # Get task type from form
        task_type = request.form.get('task_type')
        if not task_type:
            return jsonify({
                'success': False,
                'message': 'Task type is required'
            })
        
        # Validate task type
        valid_tasks = ['plantation', 'waste_management', 'stray_animal_feeding']
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
        
        # Prepare data for FastAPI (without user_id)
        files = {'task_image': (task_image.filename, task_image.read(), task_image.content_type)}
        data = {
            'task_type': task_type,
            'user_id': 'anonymous_user'  # Use anonymous user for verification
        }
        
        # Send to FastAPI backend using the original verify-task endpoint
        response = requests.post(f"{FASTAPI_URL}/api/verify-task", 
                               files=files, 
                               data=data, 
                               timeout=60)
        
        print(f"DEBUG: FastAPI response status: {response.status_code}")
        print(f"DEBUG: FastAPI response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Process the verification result
            if result.get('overall_valid'):
                # Calculate points based on task type
                points_map = {
                    'plantation': 30,
                    'waste_management': 20,
                    'stray_animal_feeding': 15
                }
                
                points_earned = points_map.get(task_type, 10)
                
                return jsonify({
                    'success': True,
                    'message': f'Task verified successfully! Activity matches {task_type.replace("_", " ")}',
                    'points_earned': points_earned,
                    'task_type': task_type,
                    'verification_details': result.get('steps', {}),
                    'overall_valid': True
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

@app.route('/api/test-models')
def test_models():
    """Test if all AI models are working"""
    try:
        # Test FastAPI health
        response = requests.get(f"{FASTAPI_URL}/health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            return jsonify({
                'success': True,
                'backend_status': health_data.get('status', 'unknown'),
                'models_loaded': health_data.get('models_loaded', False),
                'gpu_available': health_data.get('gpu_available', False),
                'message': 'AI models are ready for verification'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Backend health check failed'
            })
            
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'message': 'Cannot connect to AI backend. Please ensure FastAPI is running.'
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
        # Check FastAPI backend
        response = requests.get(f"{FASTAPI_URL}/health", timeout=5)
        backend_health = response.json() if response.status_code == 200 else {}
        
        return jsonify({
            'status': 'healthy',
            'flask_status': 'running',
            'backend_status': backend_health.get('status', 'unknown'),
            'models_available': backend_health.get('models_loaded', False)
        })
    except:
        return jsonify({
            'status': 'partial',
            'flask_status': 'running',
            'backend_status': 'offline',
            'models_available': False
        })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🌱 Eco-Connect AI Verification App")
    print("=" * 40)
    print("🚀 Starting on: http://localhost:3000")
    print("🤖 AI Backend: http://localhost:8000 (make sure it's running)")
    print("📸 Upload images to verify conservation activities!")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=3000)