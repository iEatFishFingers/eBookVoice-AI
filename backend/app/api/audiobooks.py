"""
Audiobooks API endpoints
Handles audiobook upload, conversion, and management
"""

from flask import Blueprint, request, jsonify, current_app
from ..services.storage_service import SecureCloudStorage, FileManager
from ..services.user_service import UserManager
from .auth import require_auth
import os

audiobooks_bp = Blueprint('audiobooks', __name__, url_prefix='/api/audiobooks')

@audiobooks_bp.route('/upload', methods=['POST'])
@require_auth
def upload_audiobook():
    """
    Upload ebook file for conversion to audiobook
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    allowed_extensions = {'.pdf', '.epub', '.txt'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        return jsonify({
            'error': 'Invalid file type',
            'allowed': list(allowed_extensions)
        }), 400
    
    try:
        user_id = request.current_user['user_id']
        
        # Initialize services
        storage = SecureCloudStorage(provider='r2')  # Use Cloudflare R2
        file_manager = FileManager(storage)
        user_manager = UserManager(current_app.config)
        
        # Check storage quota
        file_size = len(file.read())
        file.seek(0)  # Reset file pointer
        
        if not user_manager.check_storage_quota(user_id, file_size):
            return jsonify({'error': 'Storage quota exceeded'}), 413
        
        # Save file to cloud storage
        upload_info = file_manager.save_uploaded_file(file, user_id)
        
        # Add audiobook record to database
        title = os.path.splitext(file.filename)[0]
        audiobook_id = user_manager.add_audiobook(
            user_id=user_id,
            title=title,
            filename=file.filename,
            storage_key=upload_info['key'],
            file_size=file_size
        )
        
        # Update user storage usage
        user_manager.update_storage_usage(user_id, file_size)
        
        return jsonify({
            'success': True,
            'audiobook_id': audiobook_id,
            'title': title,
            'status': 'uploaded',
            'message': 'File uploaded successfully. Conversion will begin shortly.'
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Upload failed',
            'message': str(e)
        }), 500

@audiobooks_bp.route('/', methods=['GET'])
@require_auth
def list_audiobooks():
    """
    Get list of user's audiobooks
    """
    try:
        user_id = request.current_user['user_id']
        user_manager = UserManager(current_app.config)
        
        audiobooks = user_manager.get_user_audiobooks(user_id)
        
        return jsonify({
            'success': True,
            'audiobooks': audiobooks,
            'count': len(audiobooks)
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve audiobooks',
            'message': str(e)
        }), 500

@audiobooks_bp.route('/<audiobook_id>', methods=['GET'])
@require_auth
def get_audiobook(audiobook_id):
    """
    Get specific audiobook details
    """
    try:
        user_id = request.current_user['user_id']
        user_manager = UserManager(current_app.config)
        
        # Get audiobook details (with user ownership check)
        audiobooks = user_manager.get_user_audiobooks(user_id)
        audiobook = next((book for book in audiobooks if book['id'] == audiobook_id), None)
        
        if not audiobook:
            return jsonify({'error': 'Audiobook not found'}), 404
        
        # Generate download URL if completed
        if audiobook['status'] == 'completed':
            storage = SecureCloudStorage(provider='r2')
            download_url = storage.generate_presigned_url(
                audiobook['storage_key'], 
                expiration=3600  # 1 hour
            )
            audiobook['download_url'] = download_url
        
        return jsonify({
            'success': True,
            'audiobook': audiobook
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve audiobook',
            'message': str(e)
        }), 500

@audiobooks_bp.route('/<audiobook_id>', methods=['DELETE'])
@require_auth
def delete_audiobook(audiobook_id):
    """
    Delete audiobook and associated files
    """
    try:
        user_id = request.current_user['user_id']
        user_manager = UserManager(current_app.config)
        
        # Get audiobook details (with user ownership check)
        audiobooks = user_manager.get_user_audiobooks(user_id)
        audiobook = next((book for book in audiobooks if book['id'] == audiobook_id), None)
        
        if not audiobook:
            return jsonify({'error': 'Audiobook not found'}), 404
        
        # Delete from cloud storage
        storage = SecureCloudStorage(provider='r2')
        storage.delete_file(audiobook['storage_key'])
        
        # Update audiobook status to deleted
        user_manager.update_audiobook_status(audiobook_id, 'deleted')
        
        return jsonify({
            'success': True,
            'message': 'Audiobook deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to delete audiobook',
            'message': str(e)
        }), 500