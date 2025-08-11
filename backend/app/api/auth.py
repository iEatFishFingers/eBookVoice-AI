"""
Authentication API endpoints
Handles Google OAuth login, logout, and session management
"""

from flask import Blueprint, request, jsonify, make_response, current_app
from ..services.auth_service import GoogleOAuth
from ..services.user_service import UserManager
from functools import wraps
import jwt

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def require_auth(f):
    """
    Authentication decorator for protected endpoints
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('session_token')
        
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Add user data to request context
            request.current_user = payload
            
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
    
    return decorated_function

@auth_bp.route('/google/login', methods=['GET'])
def google_login():
    """
    Initiate Google OAuth flow
    """
    try:
        google_oauth = GoogleOAuth()
        google_oauth.init_app(current_app)
        
        auth_url = google_oauth.get_authorization_url()
        
        response = jsonify({
            'auth_url': auth_url,
            'success': True
        })
        
        return response
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate login URL',
            'message': str(e),
            'success': False
        }), 500

@auth_bp.route('/google/callback', methods=['GET'])
def google_callback():
    """
    Handle Google OAuth callback
    """
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    
    # Handle OAuth errors
    if error:
        return jsonify({
            'error': f'OAuth error: {error}',
            'success': False
        }), 400
    
    # Validate required parameters
    if not code or not state:
        return jsonify({
            'error': 'Missing required OAuth parameters',
            'success': False
        }), 400
    
    try:
        # Initialize services
        google_oauth = GoogleOAuth()
        google_oauth.init_app(current_app)
        
        # Exchange code for tokens
        tokens = google_oauth.exchange_code_for_tokens(code, state)
        
        # Verify ID token and get user info
        user_info = google_oauth.verify_id_token(tokens['id_token'])
        
        # Create or update user (remove async/await)
        user_manager = UserManager(current_app.config)
        # For now, create a simple user dict - we'll fix the async later
        user = {
            'id': user_info.get('sub'),
            'google_id': user_info.get('sub'),
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'picture_url': user_info.get('picture'),
            'subscription_type': 'free'
        }
        
        # Generate session token
        import jwt
        from datetime import datetime, timedelta
        
        session_payload = {
            'user_id': user['id'],
            'google_id': user['google_id'],
            'email': user['email'],
            'exp': datetime.utcnow() + timedelta(days=7)
        }
        
        session_token = jwt.encode(
            session_payload, 
            current_app.config['SECRET_KEY'], 
            algorithm='HS256'
        )
        
        # Create secure response
        response = make_response(jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'picture_url': user['picture_url'],
                'subscription_type': user['subscription_type']
            },
            'message': 'Login successful'
        }))
        
        # Set secure session cookie
        response.set_cookie(
            'session_token',
            session_token,
            max_age=7*24*60*60,  # 7 days
            httponly=True,  # Prevent XSS
            secure=current_app.config.get('SESSION_COOKIE_SECURE', False),
            samesite='Lax'  # CSRF protection while allowing OAuth redirects
        )
        
        return response
        
    except Exception as e:
        return jsonify({
            'error': 'Authentication failed',
            'message': str(e),
            'success': False
        }), 400

@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """
    Get current user profile
    """
    return jsonify({
        'user': {
            'id': request.current_user['user_id'],
            'email': request.current_user['email'],
            'google_id': request.current_user['google_id']
        },
        'success': True
    })

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout user by clearing session
    """
    response = jsonify({
        'message': 'Logged out successfully',
        'success': True
    })
    
    # Clear session cookie
    response.set_cookie('session_token', '', expires=0)
    
    return response