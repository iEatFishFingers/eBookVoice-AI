import os
from pathlib import Path

class Config:
    """Base configuration class with common settings."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    CHAPTERS_FOLDER = os.environ.get('CHAPTERS_FOLDER') or 'chapters'
    AUDIOBOOKS_FOLDER = os.environ.get('AUDIOBOOKS_FOLDER') or 'audiobooks'
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:*').split(',')
    
    # API settings
    API_BASE_URL = os.environ.get('API_BASE_URL') or '/api'
    
    @staticmethod
    def init_app(app):
        """Initialize application with this config."""
        # Create directories
        for folder in [Config.UPLOAD_FOLDER, Config.CHAPTERS_FOLDER, Config.AUDIOBOOKS_FOLDER]:
            os.makedirs(folder, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5001))
    CORS_ORIGINS = [
        'http://localhost:*',
        'http://127.0.0.1:*',
        'http://192.168.*.*:*',
        'http://10.*.*.*:*'
    ]

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))
    
    # Production CORS - only allow your domain
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Set up file logging
        if not app.debug:
            file_handler = RotatingFileHandler('logs/ebookvoice.log', maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('EbookVoice AI startup')

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    HOST = 'localhost'
    PORT = 5002

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}