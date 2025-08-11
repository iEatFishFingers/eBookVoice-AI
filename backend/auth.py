"""
Authentication and Security Middleware
Provides JWT authentication, rate limiting, and API security features.
"""

import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt
import redis
from typing import Optional, Dict, Any
import hashlib
import time

class SecurityManager:
    """
    Centralized security manager for authentication, rate limiting, and API protection.
    """
    
    def __init__(self, app=None, redis_client=None):
        self.app = app
        self.jwt = JWTManager()
        self.redis_client = redis_client or self._init_redis()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security manager with Flask app"""
        self.app = app
        self.jwt.init_app(app)
        
        # Configure JWT
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-change-this')
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
        app.config['JWT_BLACKLIST_ENABLED'] = True
        app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']
        
        # Register JWT handlers
        self._register_jwt_handlers()
    
    def _init_redis(self):
        """Initialize Redis client for rate limiting and session management"""
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            return redis.from_url(redis_url, decode_responses=True)
        except Exception as e:
            print(f"Warning: Redis not available, rate limiting disabled: {e}")
            return None
    
    def _register_jwt_handlers(self):
        """Register JWT event handlers"""
        
        @self.jwt.token_in_blocklist_loader
        def check_if_token_revoked(jwt_header, jwt_payload):
            jti = jwt_payload['jti']
            if self.redis_client:
                return self.redis_client.get(f"blacklist:{jti}") is not None
            return False
        
        @self.jwt.expired_token_loader
        def expired_token_callback(jwt_header, jwt_payload):
            return jsonify({"error": "Token has expired"}), 401
        
        @self.jwt.invalid_token_loader
        def invalid_token_callback(error):
            return jsonify({"error": "Invalid token"}), 401
        
        @self.jwt.unauthorized_loader
        def missing_token_callback(error):
            return jsonify({"error": "Authorization token required"}), 401
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_token(self, user_id: str, additional_claims: Dict = None) -> str:
        """Create JWT access token"""
        claims = {'user_id': user_id}
        if additional_claims:
            claims.update(additional_claims)
        
        return create_access_token(identity=user_id, additional_claims=claims)
    
    def revoke_token(self, jti: str, expires_in: int = 86400):
        """Revoke token by adding to blacklist"""
        if self.redis_client:
            self.redis_client.setex(f"blacklist:{jti}", expires_in, "true")
    
    def rate_limit(self, key: str, limit: int = 60, window: int = 60) -> tuple[bool, Dict]:
        """
        Rate limiting implementation
        
        Args:
            key: Unique identifier for the rate limit (e.g., IP address, user ID)
            limit: Maximum number of requests allowed
            window: Time window in seconds
            
        Returns:
            (is_allowed, rate_limit_info)
        """
        if not self.redis_client:
            return True, {}
        
        now = time.time()
        pipeline = self.redis_client.pipeline()
        
        # Sliding window rate limiting
        window_start = now - window
        
        # Remove old entries
        pipeline.zremrangebyscore(f"rate_limit:{key}", 0, window_start)
        
        # Count current requests
        pipeline.zcard(f"rate_limit:{key}")
        
        # Add current request
        pipeline.zadd(f"rate_limit:{key}", {str(now): now})
        
        # Set expiration
        pipeline.expire(f"rate_limit:{key}", window)
        
        results = pipeline.execute()
        current_requests = results[1]
        
        rate_limit_info = {
            'limit': limit,
            'remaining': max(0, limit - current_requests - 1),
            'reset_at': int(now + window)
        }
        
        return current_requests < limit, rate_limit_info


def rate_limit_decorator(limit: int = None, per: int = 60, key_func=None):
    """
    Decorator for rate limiting endpoints
    
    Args:
        limit: Number of requests allowed (default from env)
        per: Time window in seconds
        key_func: Function to generate rate limit key (default uses IP)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(current_app, 'security_manager'):
                return f(*args, **kwargs)
            
            # Get rate limit parameters
            max_requests = limit or int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
            window = per
            
            # Generate rate limit key
            if key_func:
                key = key_func()
            else:
                key = request.remote_addr or 'unknown'
            
            # Check rate limit
            allowed, info = current_app.security_manager.rate_limit(
                key, max_requests, window
            )
            
            if not allowed:
                response = jsonify({
                    "error": "Rate limit exceeded",
                    "rate_limit": info
                })
                response.status_code = 429
                response.headers['X-RateLimit-Limit'] = str(info['limit'])
                response.headers['X-RateLimit-Remaining'] = str(info['remaining'])
                response.headers['X-RateLimit-Reset'] = str(info['reset_at'])
                return response
            
            # Add rate limit headers to response
            response = f(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = str(info['limit'])
                response.headers['X-RateLimit-Remaining'] = str(info['remaining'])
                response.headers['X-RateLimit-Reset'] = str(info['reset_at'])
            
            return response
        return decorated_function
    return decorator


def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({"error": "API key required"}), 401
        
        # Validate API key (implement your own validation logic)
        valid_keys = os.getenv('VALID_API_KEYS', '').split(',')
        if api_key not in valid_keys:
            return jsonify({"error": "Invalid API key"}), 401
        
        return f(*args, **kwargs)
    return decorated_function


def validate_file_upload(f):
    """Decorator to validate file uploads"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Check file size
        max_size = int(os.getenv('MAX_CONTENT_LENGTH', 52428800))  # 50MB
        if request.content_length > max_size:
            return jsonify({"error": "File too large"}), 413
        
        # Check file type
        allowed_extensions = {'.pdf', '.epub', '.txt'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({
                "error": "Invalid file type",
                "allowed": list(allowed_extensions)
            }), 400
        
        return f(*args, **kwargs)
    return decorated_function


def secure_headers(f):
    """Decorator to add security headers to responses"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        # Add security headers
        if hasattr(response, 'headers'):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Content-Security-Policy'] = "default-src 'self'"
        
        return response
    return decorated_function


class APIKeyManager:
    """
    Manage API keys for service-to-service authentication
    """
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
    
    def generate_api_key(self, user_id: str, name: str = "") -> str:
        """Generate a new API key"""
        key = hashlib.sha256(f"{user_id}:{name}:{time.time()}".encode()).hexdigest()
        
        if self.redis_client:
            self.redis_client.hset(
                f"api_key:{key}",
                mapping={
                    "user_id": user_id,
                    "name": name,
                    "created_at": datetime.now().isoformat(),
                    "last_used": "",
                    "active": "true"
                }
            )
        
        return key
    
    def validate_api_key(self, api_key: str) -> Optional[Dict]:
        """Validate API key and return associated data"""
        if not self.redis_client:
            return None
        
        key_data = self.redis_client.hgetall(f"api_key:{api_key}")
        
        if not key_data or key_data.get('active') != 'true':
            return None
        
        # Update last used timestamp
        self.redis_client.hset(
            f"api_key:{api_key}",
            "last_used",
            datetime.now().isoformat()
        )
        
        return key_data
    
    def revoke_api_key(self, api_key: str):
        """Revoke an API key"""
        if self.redis_client:
            self.redis_client.hset(f"api_key:{api_key}", "active", "false")