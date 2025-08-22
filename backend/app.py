import os
import uuid
import threading
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from text_parser import get_text_parser
from config import config
from database import init_database, get_db_connection
from auth import init_auth_manager, require_auth, optional_auth
from voice_engine import init_voice_engine, get_voice_engine
from dashboard_api import get_dashboard_service


def create_app(config_name=None):
    """Application factory pattern."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Configure CORS with explicit settings
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         supports_credentials=True)
    
    # Configure logging for production
    if config_name == 'production':
        logging.basicConfig(level=logging.INFO)
        app.logger.setLevel(logging.INFO)
    
    # Create directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['AUDIOBOOKS_FOLDER'], exist_ok=True)
    
    # Initialize database
    init_database(app.config['DATABASE_PATH'])
    
    # Initialize authentication manager
    init_auth_manager(app.config['SECRET_KEY'], app.config['DATABASE_PATH'])
    
    # Initialize voice engine
    init_voice_engine()
    
    return app

app = create_app()

# In-memory storage for conversion jobs
conversion_jobs = {}

class EnhancedEBookConverter:
    def __init__(self):
        self.voice_engine = get_voice_engine()
        self.text_parser = get_text_parser()
        
    def extract_and_clean_text(self, file_path):
        """Extract and clean text from eBook file."""
        return self.text_parser.extract_text_from_file(file_path)
    
    def text_to_speech(self, text, output_path, voice_id='xtts_female_narrator', user_tier='free'):
        """Generate high-quality audio using Coqui XTTS v2."""
        return self.voice_engine.synthesize_speech(text, voice_id, output_path, user_tier)
    
    def get_text_statistics(self, text):
        """Get text statistics for tracking."""
        return self.text_parser.get_text_statistics(text)

def background_conversion(job_id, file_path, voice_id='xtts_female_narrator', user_tier='free', user_id=None):
    """Background conversion using Coqui XTTS v2 with enhanced text parsing."""
    try:
        converter = EnhancedEBookConverter()
        job = conversion_jobs[job_id]
        
        # Update status
        job['status'] = 'processing'
        job['progress'] = 10
        job['current_phase'] = 'Extracting and cleaning text from file'
        job['updatedAt'] = datetime.now().isoformat()
        
        # Extract and clean text using enhanced parser
        text = converter.extract_and_clean_text(file_path)
        
        if not text or len(text.strip()) < 50:
            raise ValueError("No readable text found in file or text too short")
        
        # Get text statistics
        stats = converter.get_text_statistics(text)
        job.update({
            'word_count': stats['words'],
            'character_count': stats['characters'],
            'estimated_duration_minutes': round(stats['words'] / 150)  # ~150 words per minute speech
        })
        
        job['progress'] = 30
        job['current_phase'] = f'Generating high-quality audio using {voice_id} voice'
        job['voice_used'] = voice_id
        job['updatedAt'] = datetime.now().isoformat()
        
        # Generate high-quality audio with XTTS v2
        output_filename = f"{job_id}_audiobook.wav"
        output_path = os.path.join(app.config['AUDIOBOOKS_FOLDER'], output_filename)
        
        start_time = datetime.now()
        converter.text_to_speech(text, output_path, voice_id, user_tier)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Verify audio file was created
        if not os.path.exists(output_path):
            raise ValueError("Audio file generation failed")
        
        # Store conversion data in database if user is authenticated
        if user_id:
            try:
                file_extension = Path(file_path).suffix.lower()
                conn = get_db_connection(app.config['DATABASE_PATH'])
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO conversions 
                    (user_id, job_id, original_filename, file_type, file_size, 
                     word_count, voice_used, processing_time, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, job_id, job.get('fileName', ''), file_extension[1:], 
                      job.get('file_size', 0), job['word_count'], voice_id, int(processing_time), 'completed'))
                conn.commit()
                conn.close()
                
                # Update user usage tracking
                dashboard_service = get_dashboard_service()
                dashboard_service.update_user_usage(user_id, job['word_count'])
                
                app.logger.info(f"Conversion stored and usage updated for user {user_id}")
            except Exception as db_error:
                app.logger.warning(f"Could not store conversion in database: {db_error}")
        
        # Complete conversion
        job['status'] = 'completed'
        job['progress'] = 100
        job['current_phase'] = 'Audio generation completed successfully'
        job['audioFile'] = output_filename
        job['download_url'] = f'/download/{job_id}'
        job['processing_time'] = int(processing_time)
        job['updatedAt'] = datetime.now().isoformat()
        
        app.logger.info(f"Conversion completed successfully for job {job_id} in {processing_time:.1f}s")
        
    except Exception as e:
        job['status'] = 'failed'
        job['error'] = str(e)
        job['updatedAt'] = datetime.now().isoformat()
        app.logger.error(f"Conversion failed for job {job_id}: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'eBookVoice AI Converter'
    })

# Authentication routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user."""
    from auth import auth_manager
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        display_name = data.get('display_name', '').strip()
        
        result = auth_manager.register_user(email, password, display_name)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        app.logger.error(f"Registration error: {e}")
        return jsonify({
            'success': False, 
            'error': 'Registration failed. Please try again.'
        }), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login a user."""
    from auth import auth_manager
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        result = auth_manager.login_user(email, password)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        app.logger.error(f"Login error: {e}")
        return jsonify({
            'success': False, 
            'error': 'Login failed. Please try again.'
        }), 500

@app.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user information."""
    return jsonify({
        'success': True,
        'user': request.user
    })

# Voice selection routes
@app.route('/api/voices', methods=['GET'])
@optional_auth
def get_available_voices():
    """Get available voices for current user's tier."""
    try:
        # Determine user tier
        user_tier = 'free'
        if request.user:
            user_tier = request.user.get('subscription_tier', 'free')
        
        voice_engine = get_voice_engine()
        voices = voice_engine.get_available_voices(user_tier)
        
        return jsonify({
            'success': True,
            'voices': voices,
            'user_tier': user_tier,
            'total_voices': len(voices)
        })
        
    except Exception as e:
        logger.error(f"Error getting voices: {e}")
        return jsonify({
            'success': False,
            'error': 'Could not load available voices'
        }), 500

@app.route('/api/voices/<voice_id>', methods=['GET'])
@optional_auth
def get_voice_info(voice_id):
    """Get detailed information about a specific voice."""
    try:
        user_tier = 'free'
        if request.user:
            user_tier = request.user.get('subscription_tier', 'free')
        
        voice_engine = get_voice_engine()
        voice_info = voice_engine.get_voice_info(voice_id, user_tier)
        
        if not voice_info:
            return jsonify({
                'success': False,
                'error': 'Voice not found or not accessible'
            }), 404
        
        # Check access
        has_access = voice_engine.validate_voice_access(voice_id, user_tier)
        
        return jsonify({
            'success': True,
            'voice': voice_info,
            'has_access': has_access,
            'user_tier': user_tier
        })
        
    except Exception as e:
        logger.error(f"Error getting voice info: {e}")
        return jsonify({
            'success': False,
            'error': 'Could not load voice information'
        }), 500

@app.route('/api/voices/engines/status', methods=['GET'])
def get_engine_status():
    """Get status of all TTS engines."""
    try:
        voice_engine = get_voice_engine()
        status = voice_engine.get_engine_status()
        
        return jsonify({
            'success': True,
            'engines': status
        })
        
    except Exception as e:
        logger.error(f"Error getting engine status: {e}")
        return jsonify({
            'success': False,
            'error': 'Could not load engine status'
        }), 500

# Dashboard and Analytics routes
@app.route('/api/dashboard', methods=['GET'])
@require_auth
def get_user_dashboard():
    """Get comprehensive dashboard data for authenticated user."""
    try:
        dashboard_service = get_dashboard_service()
        result = dashboard_service.get_user_dashboard_data(request.user_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to load dashboard data'
        }), 500

@app.route('/api/dashboard/conversions', methods=['GET'])
@require_auth
def get_user_conversion_history():
    """Get paginated conversion history for authenticated user."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 50)  # Max 50 per page
        
        dashboard_service = get_dashboard_service()
        result = dashboard_service.get_user_conversions(request.user_id, page, per_page)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Conversion history error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to load conversion history'
        }), 500

@app.route('/api/dashboard/analytics', methods=['GET'])
@require_auth
def get_user_analytics():
    """Get detailed usage analytics for authenticated user."""
    try:
        days = request.args.get('days', 30, type=int)
        days = min(max(days, 1), 365)  # Between 1 and 365 days
        
        dashboard_service = get_dashboard_service()
        result = dashboard_service.get_usage_analytics(request.user_id, days)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to load analytics data'
        }), 500

@app.route('/api/dashboard/usage-check', methods=['POST'])
@require_auth
def check_user_usage_limits():
    """Check if user can perform conversion based on their limits."""
    try:
        data = request.get_json() or {}
        estimated_words = data.get('estimated_words', 0)
        
        dashboard_service = get_dashboard_service()
        result = dashboard_service.check_usage_limits(request.user_id, estimated_words)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Usage check error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to check usage limits'
        }), 500

@app.route('/upload', methods=['POST'])
@optional_auth
def upload_and_convert():
    """Enhanced upload with voice selection and user tracking."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Get voice selection from form data (default to XTTS female narrator)
        voice_id = request.form.get('voice_id', 'xtts_female_narrator')
        
        # Get user info if authenticated
        user_id = None
        user_tier = 'free'
        if request.user:
            user_id = request.user['id']
            user_tier = request.user.get('subscription_tier', 'free')
            
            # Check usage limits for authenticated users
            dashboard_service = get_dashboard_service()
            usage_check = dashboard_service.check_usage_limits(user_id, 1000)  # Estimate 1000 words
            
            if not usage_check.get('can_convert', True):
                return jsonify({
                    'success': False,
                    'error': 'Usage limit exceeded',
                    'details': usage_check.get('reasons', []),
                    'current_usage': usage_check.get('current_usage', {}),
                    'suggested_action': 'upgrade' if user_tier == 'free' else 'wait_for_reset'
                }), 403
        
        # Validate voice access
        voice_engine = get_voice_engine()
        if not voice_engine.validate_voice_access(voice_id, user_tier):
            # Fallback to first available voice for user's tier
            available_voices = voice_engine.get_available_voices(user_tier)
            if available_voices:
                voice_id = available_voices[0]['id']
                app.logger.info(f"Voice access denied, using fallback: {voice_id}")
            else:
                return jsonify({
                    'success': False,
                    'error': 'No voices available for your subscription tier'
                }), 403
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Validate file type
        original_filename = uploaded_file.filename
        file_extension = Path(original_filename).suffix.lower()
        supported_extensions = {'.pdf', '.epub', '.txt', '.text'}
        
        if file_extension not in supported_extensions:
            return jsonify({
                'success': False,
                'error': f'Unsupported file type: {file_extension}. Supported types: PDF, EPUB, TXT',
                'supported_types': list(supported_extensions)
            }), 400
        
        # Get file size for tracking
        uploaded_file.seek(0, os.SEEK_END)
        file_size = uploaded_file.tell()
        uploaded_file.seek(0)
        
        # Save uploaded file
        filename = f"{job_id}_{original_filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(file_path)
        
        # Get voice info for display
        voice_info = voice_engine.get_voice_info(voice_id, user_tier)
        voice_name = voice_info['name'] if voice_info else voice_id
        
        # Create conversion job
        conversion_jobs[job_id] = {
            'id': job_id,
            'title': Path(original_filename).stem,
            'fileName': original_filename,
            'file_size': file_size,
            'voice_id': voice_id,
            'voice_name': voice_name,
            'user_id': user_id,
            'user_tier': user_tier,
            'status': 'pending',
            'progress': 0,
            'current_phase': f'File uploaded, queued for processing with {voice_name}',
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        # Start background conversion with enhanced parameters
        thread = threading.Thread(
            target=background_conversion, 
            args=(job_id, file_path, voice_id, user_tier, user_id)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True, 
            'job_id': job_id,
            'data': conversion_jobs[job_id],
            'download_url': f'/download/{job_id}'
        })
        
    except Exception as e:
        app.logger.error(f"Upload failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/conversions/<job_id>', methods=['GET'])
def get_conversion_status(job_id):
    if job_id not in conversion_jobs:
        return jsonify({'success': False, 'error': 'Conversion job not found'}), 404
    
    return jsonify({'success': True, 'data': conversion_jobs[job_id]})

@app.route('/conversions', methods=['GET'])
@optional_auth
def get_all_conversions():
    # For now, return in-memory conversions
    # In future phases, this will be enhanced with database storage per user
    sorted_jobs = sorted(
        conversion_jobs.values(),
        key=lambda x: x['createdAt'],
        reverse=True
    )
    
    # If user is authenticated, we can add their info to the response
    response = {'success': True, 'data': sorted_jobs}
    if request.user:
        response['user'] = {
            'id': request.user['id'],
            'email': request.user['email'],
            'subscription_tier': request.user['subscription_tier']
        }
    
    return jsonify(response)

@app.route('/download/<job_id>', methods=['GET'])
def download_audiobook(job_id):
    if job_id not in conversion_jobs:
        return jsonify({'success': False, 'error': 'Conversion job not found'}), 404
    
    job = conversion_jobs[job_id]
    if job['status'] != 'completed':
        return jsonify({'success': False, 'error': 'Conversion not completed'}), 400
    
    audio_file_path = os.path.join(app.config['AUDIOBOOKS_FOLDER'], job['audioFile'])
    if not os.path.exists(audio_file_path):
        return jsonify({'success': False, 'error': 'Audio file not found'}), 404
    
    return send_file(audio_file_path, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("Starting eBookVoice AI MVP")
    print("Upload eBooks and convert to audio")
    print(f"Server running on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)