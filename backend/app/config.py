"""
Configuration classes for eBookVoice-AI hybrid architecture
"""

import os
from urllib.parse import urlparse

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Supabase configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')  # Public key
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')  # Private key
    
    # Parse database URL for direct connection
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    
    # Cloudflare R2 Configuration
    # These values come from the API Token you created in Step 1.2
    R2_ACCOUNT_ID = os.getenv('R2_ACCOUNT_ID')  # From Cloudflare dashboard sidebar
    R2_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID')  # From API token creation
    R2_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY')  # From API token creation
    R2_BUCKET_NAME = os.getenv('R2_BUCKET_NAME', 'ebookvoice-audiobooks-prod')
    
    # R2 Endpoint (constructed from Account ID)
    @property
    def R2_ENDPOINT_URL(self):
        return f'https://{self.R2_ACCOUNT_ID}.r2.cloudflarestorage.com'
    
    # File upload settings
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 52428800))  # 50MB
    UPLOAD_FOLDER = 'uploads'
    CHAPTERS_FOLDER = 'chapters'
    AUDIOBOOKS_FOLDER = 'audiobooks'
    
    # Security settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
    
    # TTS Configuration
    TTS_MODEL = os.getenv('TTS_MODEL', 'tts_models/en/ljspeech/tacotron2-DDC')
    TTS_VOCODER = os.getenv('TTS_VOCODER', 'vocoder_models/en/ljspeech/hifigan_v2')
    
    @staticmethod
    def init_app(app):
        """Initialize application with this config."""
        # Create directories
        for folder in [Config.UPLOAD_FOLDER, Config.CHAPTERS_FOLDER, Config.AUDIOBOOKS_FOLDER]:
            os.makedirs(folder, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    GOOGLE_REDIRECT_URI = 'http://localhost:5000/auth/google/callback'
    
    # R2 works the same in dev and prod - same bucket, same API tokens

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    GOOGLE_REDIRECT_URI = 'https://your-api.render.com/auth/google/callback'
    
    # Security headers for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # R2 configuration remains the same as base Config class
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Set up file logging
        if not app.debug:
            os.makedirs('logs', exist_ok=True)
            file_handler = RotatingFileHandler('logs/ebookvoice.log', maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('EbookVoice AI startup')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    GOOGLE_REDIRECT_URI = 'http://localhost:5000/auth/google/callback'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}