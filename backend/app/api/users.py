"""
Users API endpoints
Handles user profile and account management
"""

from flask import Blueprint, request, jsonify, current_app
from ..services.user_service import UserManager
from .auth import require_auth

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('/profile', methods=['GET'])
@require_auth
def get_user_profile():
    """
    Get current user's profile information
    """
    try:
        user_id = request.current_user['user_id']
        user_manager = UserManager(current_app.config)
        
        user = user_manager.get_user_by_google_id(request.current_user['google_id'])
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'picture_url': user['picture_url'],
                'subscription_type': user['subscription_type'],
                'storage_used_bytes': user.get('storage_used_bytes', 0),
                'created_at': user['created_at']
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve profile',
            'message': str(e)
        }), 500

@users_bp.route('/usage', methods=['GET'])
@require_auth
def get_usage_stats():
    """
    Get user's usage statistics
    """
    try:
        user_id = request.current_user['user_id']
        user_manager = UserManager(current_app.config)
        
        # Get user info
        user = user_manager.get_user_by_google_id(request.current_user['google_id'])
        
        # Get audiobooks count
        audiobooks = user_manager.get_user_audiobooks(user_id)
        
        # Calculate quotas
        quotas = {
            'free': {
                'storage_bytes': 100 * 1024 * 1024,  # 100MB
                'audiobooks': 5
            },
            'premium': {
                'storage_bytes': 10 * 1024 * 1024 * 1024,  # 10GB
                'audiobooks': 100
            }
        }
        
        subscription = user.get('subscription_type', 'free')
        quota = quotas.get(subscription, quotas['free'])
        
        return jsonify({
            'success': True,
            'usage': {
                'storage_used_bytes': user.get('storage_used_bytes', 0),
                'storage_quota_bytes': quota['storage_bytes'],
                'audiobooks_count': len(audiobooks),
                'audiobooks_quota': quota['audiobooks'],
                'subscription_type': subscription
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve usage stats',
            'message': str(e)
        }), 500