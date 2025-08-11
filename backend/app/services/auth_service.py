"""
Google OAuth Integration (No Firebase)
Secure Google authentication using Google's OAuth 2.0 API directly
"""

import os
import requests
import secrets
from datetime import datetime, timedelta
from flask import request, jsonify, session, redirect, url_for
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import jwt
from typing import Dict, Optional

class GoogleOAuth:
    """
    Direct Google OAuth integration without Firebase
    More secure and gives you full control over user data
    """
    
    def __init__(self, app=None):
        self.app = app
        self.client_id = None
        self.client_secret = None
        self.redirect_uri = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Google OAuth with Flask app"""
        self.app = app
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/auth/google/callback')
        
        if not all([self.client_id, self.client_secret]):
            raise ValueError("Google OAuth credentials not configured")
    
    def get_authorization_url(self, state: str = None) -> str:
        """
        Generate Google OAuth authorization URL
        
        Args:
            state: CSRF protection token
            
        Returns:
            Authorization URL for redirecting users
        """
        if not state:
            state = secrets.token_urlsafe(32)
            session['oauth_state'] = state
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'openid email profile',
            'response_type': 'code',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"
    
    def exchange_code_for_tokens(self, code: str, state: str = None) -> Dict:
        """
        Exchange authorization code for access tokens
        
        Args:
            code: Authorization code from Google
            state: CSRF protection token
            
        Returns:
            Token information including access_token and id_token
        """
        # Verify state for CSRF protection
        if state and session.get('oauth_state') != state:
            raise ValueError("Invalid state parameter - possible CSRF attack")
        
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code != 200:
            raise Exception(f"Token exchange failed: {response.text}")
        
        return response.json()
    
    def verify_id_token(self, id_token_str: str) -> Dict:
        """
        Verify and decode Google ID token
        
        Args:
            id_token_str: JWT ID token from Google
            
        Returns:
            Decoded user information
        """
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                id_token_str, 
                google_requests.Request(), 
                self.client_id
            )
            
            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return idinfo
            
        except ValueError as e:
            raise Exception(f"Invalid ID token: {str(e)}")
    
    def get_user_info(self, access_token: str) -> Dict:
        """
        Get user information from Google's userinfo endpoint
        
        Args:
            access_token: Valid access token
            
        Returns:
            User profile information
        """
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get user info: {response.text}")
        
        return response.json()
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke a Google OAuth token
        
        Args:
            token: Token to revoke
            
        Returns:
            Success status
        """
        try:
            response = requests.post(
                f'https://oauth2.googleapis.com/revoke?token={token}'
            )
            return response.status_code == 200
        except:
            return False


class APIKeyManager:
    """
    Manage API keys for service-to-service authentication
    """
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
    
    def generate_api_key(self, user_id: str, name: str = "") -> str:
        """Generate a new API key"""
        import hashlib
        import time
        
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