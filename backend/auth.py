"""JWT-based authentication system."""
import jwt
import bcrypt
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from database import get_db_connection, create_user_usage_record

logger = logging.getLogger(__name__)

class AuthManager:
    """Handles JWT token creation, validation, and user authentication."""
    
    def __init__(self, secret_key, db_path='audiobook.db'):
        self.secret_key = secret_key
        self.db_path = db_path
    
    def hash_password(self, password):
        """Hash a password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    def verify_password(self, password, hashed):
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    
    def generate_token(self, user_id, email):
        """Generate a JWT token for a user."""
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=current_app.config.get('JWT_EXPIRATION_HOURS', 168)),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token):
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    def register_user(self, email, password, display_name=None):
        """Register a new user."""
        try:
            # Validate input
            if not email or not password:
                return {'success': False, 'error': 'Email and password are required'}
            
            if len(password) < 6:
                return {'success': False, 'error': 'Password must be at least 6 characters long'}
            
            # Set display name default
            if not display_name:
                display_name = email.split('@')[0]
            
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                return {'success': False, 'error': 'User already exists'}
            
            # Hash password and create user
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (email, password_hash, display_name, created_at)
                VALUES (?, ?, ?, ?)
            ''', (email, password_hash, display_name, datetime.utcnow()))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Create usage record for new user
            create_user_usage_record(user_id, self.db_path)
            
            # Generate token
            token = self.generate_token(user_id, email)
            
            logger.info(f"New user registered: {email}")
            return {
                'success': True,
                'token': token,
                'user': {
                    'id': user_id,
                    'email': email,
                    'display_name': display_name,
                    'subscription_tier': 'free'
                }
            }
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return {'success': False, 'error': 'Registration failed'}
    
    def login_user(self, email, password):
        """Authenticate and login a user."""
        try:
            if not email or not password:
                return {'success': False, 'error': 'Email and password are required'}
            
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            # Find user
            cursor.execute('''
                SELECT id, password_hash, display_name, subscription_tier, is_active 
                FROM users WHERE email = ?
            ''', (email,))
            user = cursor.fetchone()
            
            if not user:
                return {'success': False, 'error': 'Invalid credentials'}
            
            # Check if account is active
            if not user['is_active']:
                return {'success': False, 'error': 'Account is deactivated'}
            
            # Verify password
            if not self.verify_password(password, user['password_hash']):
                return {'success': False, 'error': 'Invalid credentials'}
            
            # Update last login
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                         (datetime.utcnow(), user['id']))
            conn.commit()
            conn.close()
            
            # Generate token
            token = self.generate_token(user['id'], email)
            
            logger.info(f"User logged in: {email}")
            return {
                'success': True,
                'token': token,
                'user': {
                    'id': user['id'],
                    'email': email,
                    'display_name': user['display_name'],
                    'subscription_tier': user['subscription_tier']
                }
            }
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return {'success': False, 'error': 'Login failed'}
    
    def get_user_by_id(self, user_id):
        """Get user data by ID."""
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, email, display_name, subscription_tier, created_at, last_login, is_active
                FROM users WHERE id = ? AND is_active = 1
            ''', (user_id,))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return dict(user)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            return None

# Global auth manager instance (will be initialized in app.py)
auth_manager = None

def init_auth_manager(secret_key, db_path='audiobook.db'):
    """Initialize the global auth manager instance."""
    global auth_manager
    auth_manager = AuthManager(secret_key, db_path)
    return auth_manager

def require_auth(f):
    """Decorator to require authentication for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No valid token provided'}), 401
        
        token = auth_header.replace('Bearer ', '')
        
        # Verify token
        if not auth_manager:
            logger.error("Auth manager not initialized")
            return jsonify({'error': 'Authentication system error'}), 500
            
        payload = auth_manager.verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Get full user data
        user = auth_manager.get_user_by_id(payload['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        # Add user data to request context
        request.user = user
        request.user_id = user['id']
        
        return f(*args, **kwargs)
    
    return decorated_function

def optional_auth(f):
    """Decorator for routes that work with or without authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request.user = None
        request.user_id = None
        
        # Try to get token
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
            
            if auth_manager:
                payload = auth_manager.verify_token(token)
                if payload:
                    user = auth_manager.get_user_by_id(payload['user_id'])
                    if user:
                        request.user = user
                        request.user_id = user['id']
        
        return f(*args, **kwargs)
    
    return decorated_function