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
        
        # Determine which API to call based on task type
        api_endpoints = {
            'plantation': 'http://localhost:8001/verify-plantation',
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