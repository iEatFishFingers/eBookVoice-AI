"""
API Routes extracted from converter.py for better organization.
This separates route definitions from the main application logic.
"""
import os
import uuid
import threading
from datetime import datetime
from pathlib import Path
from flask import request, jsonify, send_file

# Import your existing classes and functions
# (You'll need to extract these from converter.py into separate modules)
from converter_logic import (
    IntelligentChapterExtractor,
    EnhancedAudioGenerator, 
    conversion_jobs,
    background_trail_conversion
)

def register_routes(app):
    """Register all API routes with the Flask app."""
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for monitoring."""
        try:
            current_time = datetime.now().isoformat()
            
            # Basic system checks
            directory_checks = {
                'uploads': os.path.exists(app.config['UPLOAD_FOLDER']),
                'chapters': os.path.exists(app.config['CHAPTERS_FOLDER']),
                'audiobooks': os.path.exists(app.config['AUDIOBOOKS_FOLDER'])
            }
            
            # Library availability checks
            library_status = {}
            
            # Test critical libraries
            try:
                import PyPDF2
                library_status['PyPDF2'] = {'available': True}
            except ImportError:
                library_status['PyPDF2'] = {'available': False}
                
            try:
                import ebooklib
                library_status['ebooklib'] = {'available': True}
            except ImportError:
                library_status['ebooklib'] = {'available': False}
                
            try:
                import pyttsx3
                library_status['pyttsx3'] = {'available': True}
            except ImportError:
                library_status['pyttsx3'] = {'available': False}
            
            all_dirs_ok = all(directory_checks.values())
            critical_libs_ok = all(lib['available'] for lib in library_status.values())
            
            system_health = 'healthy' if (all_dirs_ok and critical_libs_ok) else 'degraded'
            
            return jsonify({
                'status': system_health,
                'timestamp': current_time,
                'environment': os.environ.get('FLASK_ENV', 'development'),
                'directories': directory_checks,
                'libraries': library_status,
                'capabilities': {
                    'file_processing': all_dirs_ok,
                    'text_to_speech': library_status.get('pyttsx3', {}).get('available', False),
                    'pdf_support': library_status.get('PyPDF2', {}).get('available', False),
                    'epub_support': library_status.get('ebooklib', {}).get('available', False)
                }
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }), 500
    
    @app.route('/conversions/upload', methods=['POST'])
    def upload_and_convert():
        """Handle file upload and start conversion process."""
        try:
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'No file provided'
                }), 400
            
            uploaded_file = request.files['file']
            if uploaded_file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No file selected'
                }), 400
            
            # Generate conversion job ID
            job_id = str(uuid.uuid4())
            
            # Validate file type
            original_filename = uploaded_file.filename
            file_extension = Path(original_filename).suffix.lower()
            supported_extensions = {'.pdf', '.epub', '.txt', '.text'}
            
            if file_extension not in supported_extensions:
                return jsonify({
                    'success': False,
                    'error': f'Unsupported file type: {file_extension}',
                    'supported_types': list(supported_extensions)
                }), 400
            
            # Save uploaded file
            filename = f"{job_id}_{original_filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
            
            # Create conversion job record
            conversion_jobs[job_id] = {
                'id': job_id,
                'title': Path(original_filename).stem,
                'fileName': original_filename,
                'fileSize': os.path.getsize(file_path),
                'status': 'pending',
                'progress': 0,
                'current_phase': 'File uploaded, queued for processing',
                'createdAt': datetime.now().isoformat(),
                'updatedAt': datetime.now().isoformat(),
                'settings': {
                    'voice': 'premium-female-1',
                    'quality': 'standard',
                    'speed': 1.0,
                    'autoDetectChapters': True,
                    'enhanceQuality': True
                }
            }
            
            # Start background conversion
            conversion_thread = threading.Thread(
                target=background_trail_conversion,
                args=(job_id, file_path, conversion_jobs[job_id]['settings'])
            )
            conversion_thread.daemon = True
            conversion_thread.start()
            
            return jsonify({
                'success': True,
                'data': conversion_jobs[job_id]
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Upload failed: {str(e)}'
            }), 500
    
    @app.route('/conversions/<job_id>', methods=['GET'])
    def get_conversion_status(job_id):
        """Get the current status of a conversion job."""
        try:
            if job_id not in conversion_jobs:
                return jsonify({
                    'success': False,
                    'error': 'Conversion job not found'
                }), 404
            
            job = conversion_jobs[job_id]
            return jsonify({
                'success': True,
                'data': job
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to get conversion status: {str(e)}'
            }), 500
    
    @app.route('/conversions', methods=['GET'])
    def get_all_conversions():
        """Get all conversion jobs for the user."""
        try:
            # Return all conversion jobs sorted by creation time
            sorted_jobs = sorted(
                conversion_jobs.values(),
                key=lambda x: x['createdAt'],
                reverse=True
            )
            
            return jsonify({
                'success': True,
                'data': sorted_jobs
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to get conversions: {str(e)}'
            }), 500
    
    @app.route('/api/auth/profile', methods=['GET'])
    def get_user_profile():
        """Mock user profile for development."""
        return jsonify({
            'success': True,
            'data': {
                'id': 'user-1',
                'name': 'Development User',
                'email': 'dev@ebookvoice.ai',
                'subscription': 'premium',
                'avatar': None
            }
        })
    
    @app.route('/api/settings/stats', methods=['GET'])
    def get_user_stats():
        """Mock user statistics for development."""
        completed_jobs = [job for job in conversion_jobs.values() if job['status'] == 'completed']
        
        return jsonify({
            'success': True,
            'data': {
                'conversionsThisMonth': len(completed_jobs),
                'totalAudiobooks': len(completed_jobs),
                'listeningHours': len(completed_jobs) * 4.5,  # Estimate
                'storageUsed': min(85, len(completed_jobs) * 15)  # Mock percentage
            }
        })