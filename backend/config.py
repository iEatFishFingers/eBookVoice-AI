import os
from datetime import timedelta

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    AUDIOBOOKS_FOLDER = os.environ.get('AUDIOBOOKS_FOLDER') or 'audiobooks'
    
    # Database settings
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or 'audiobook.db'
    
    # JWT settings
    JWT_EXPIRATION_HOURS = 24 * 7  # 7 days
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Production CORS - temporarily allow all origins for testing, then restrict later
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',') if os.environ.get('CORS_ORIGINS') else ['*']

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}