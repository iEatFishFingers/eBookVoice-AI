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


class UserManager:
    """
    User management without Firebase
    Stores user data in your preferred database (PostgreSQL, MySQL, etc.)
    """
    
    def __init__(self, db_connection):
        self.db = db_connection
        self._create_tables()
    
    def _create_tables(self):
        """Create user tables if they don't exist"""
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            google_id VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            picture_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            subscription_type VARCHAR(50) DEFAULT 'free'
        );
        
        CREATE TABLE IF NOT EXISTS user_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            session_token VARCHAR(255) UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address INET,
            user_agent TEXT
        );
        
        CREATE TABLE IF NOT EXISTS user_audiobooks (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            title VARCHAR(255) NOT NULL,
            original_filename VARCHAR(255) NOT NULL,
            storage_key VARCHAR(500) NOT NULL,
            file_size BIGINT,
            duration_seconds INTEGER,
            status VARCHAR(50) DEFAULT 'processing',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token);
        CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at);
        CREATE INDEX IF NOT EXISTS idx_audiobooks_user ON user_audiobooks(user_id);
        """
        
        try:
            with self.db.cursor() as cursor:
                cursor.execute(create_users_table)
            self.db.commit()
        except Exception as e:
            print(f"Warning: Could not create tables: {e}")
    
    def create_or_update_user(self, google_user_info: Dict) -> Dict:
        """
        Create new user or update existing one from Google profile
        
        Args:
            google_user_info: User info from Google OAuth
            
        Returns:
            User record
        """
        google_id = google_user_info.get('id')
        email = google_user_info.get('email')
        name = google_user_info.get('name', email)
        picture = google_user_info.get('picture')
        
        # Check if user exists
        with self.db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE google_id = %s OR email = %s",
                (google_id, email)
            )
            existing_user = cursor.fetchone()
            
            if existing_user:
                # Update existing user
                cursor.execute("""
                    UPDATE users 
                    SET name = %s, picture_url = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE google_id = %s OR email = %s
                    RETURNING *
                """, (name, picture, google_id, email))
            else:
                # Create new user
                cursor.execute("""
                    INSERT INTO users (google_id, email, name, picture_url)
                    VALUES (%s, %s, %s, %s)
                    RETURNING *
                """, (google_id, email, name, picture))
            
            user = cursor.fetchone()
            self.db.commit()
            
            return {
                'id': user[0],
                'google_id': user[1],
                'email': user[2],
                'name': user[3],
                'picture_url': user[4],
                'created_at': user[5].isoformat() if user[5] else None,
                'subscription_type': user[8]
            }
    
    def create_session(self, user_id: int, ip_address: str = None, user_agent: str = None) -> str:
        """
        Create a new user session
        
        Args:
            user_id: User ID
            ip_address: Client IP
            user_agent: Client user agent
            
        Returns:
            Session token
        """
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=30)  # 30-day sessions
        
        with self.db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO user_sessions (user_id, session_token, expires_at, ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, session_token, expires_at, ip_address, user_agent))
            
        self.db.commit()
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """
        Validate a session token
        
        Args:
            session_token: Token to validate
            
        Returns:
            User information if valid, None otherwise
        """
        with self.db.cursor() as cursor:
            cursor.execute("""
                SELECT u.*, s.expires_at 
                FROM users u
                JOIN user_sessions s ON u.id = s.user_id
                WHERE s.session_token = %s AND s.expires_at > CURRENT_TIMESTAMP
            """, (session_token,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            return {
                'id': result[0],
                'google_id': result[1],
                'email': result[2],
                'name': result[3],
                'picture_url': result[4],
                'subscription_type': result[8]
            }
    
    def revoke_session(self, session_token: str) -> bool:
        """Revoke a session token"""
        with self.db.cursor() as cursor:
            cursor.execute(
                "DELETE FROM user_sessions WHERE session_token = %s",
                (session_token,)
            )
            self.db.commit()
            return cursor.rowcount > 0
    
    def add_audiobook(self, user_id: int, title: str, filename: str, storage_key: str, file_size: int = None) -> int:
        """
        Add audiobook record for user
        
        Returns:
            Audiobook ID
        """
        with self.db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO user_audiobooks (user_id, title, original_filename, storage_key, file_size)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (user_id, title, filename, storage_key, file_size))
            
            audiobook_id = cursor.fetchone()[0]
            self.db.commit()
            return audiobook_id
    
    def get_user_audiobooks(self, user_id: int) -> list:
        """Get all audiobooks for a user"""
        with self.db.cursor() as cursor:
            cursor.execute("""
                SELECT id, title, original_filename, file_size, duration_seconds, 
                       status, created_at, completed_at
                FROM user_audiobooks 
                WHERE user_id = %s 
                ORDER BY created_at DESC
            """, (user_id,))
            
            audiobooks = []
            for row in cursor.fetchall():
                audiobooks.append({
                    'id': row[0],
                    'title': row[1],
                    'filename': row[2],
                    'file_size': row[3],
                    'duration': row[4],
                    'status': row[5],
                    'created_at': row[6].isoformat() if row[6] else None,
                    'completed_at': row[7].isoformat() if row[7] else None
                })
            
            return audiobooks


# Flask route handlers
def create_auth_routes(app, google_oauth: GoogleOAuth, user_manager: UserManager):
    """Create authentication routes"""
    
    @app.route('/auth/google/login')
    def google_login():
        """Initiate Google OAuth login"""
        auth_url = google_oauth.get_authorization_url()
        return jsonify({'auth_url': auth_url})
    
    @app.route('/auth/google/callback')
    def google_callback():
        """Handle Google OAuth callback"""
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        if error:
            return jsonify({'error': f'OAuth error: {error}'}), 400
        
        if not code:
            return jsonify({'error': 'No authorization code received'}), 400
        
        try:
            # Exchange code for tokens
            tokens = google_oauth.exchange_code_for_tokens(code, state)
            
            # Verify ID token and get user info
            user_info = google_oauth.verify_id_token(tokens['id_token'])
            
            # Create or update user
            user = user_manager.create_or_update_user(user_info)
            
            # Create session
            session_token = user_manager.create_session(
                user['id'],
                request.remote_addr,
                request.headers.get('User-Agent')
            )
            
            # Set secure cookie
            response = jsonify({
                'success': True,
                'user': user,
                'message': 'Login successful'
            })
            
            response.set_cookie(
                'session_token',
                session_token,
                max_age=30*24*60*60,  # 30 days
                httponly=True,
                secure=app.config.get('SESSION_COOKIE_SECURE', False),
                samesite='Lax'
            )
            
            return response
            
        except Exception as e:
            return jsonify({'error': f'Authentication failed: {str(e)}'}), 400
    
    @app.route('/auth/logout', methods=['POST'])
    def logout():
        """Logout user"""
        session_token = request.cookies.get('session_token')
        
        if session_token:
            user_manager.revoke_session(session_token)
        
        response = jsonify({'message': 'Logged out successfully'})
        response.set_cookie('session_token', '', expires=0)
        
        return response
    
    @app.route('/auth/me')
    def get_current_user():
        """Get current user info"""
        session_token = request.cookies.get('session_token')
        
        if not session_token:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = user_manager.validate_session(session_token)
        
        if not user:
            return jsonify({'error': 'Invalid session'}), 401
        
        return jsonify({'user': user})